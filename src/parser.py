import os
import json
import pandas as pd
from logger import logger
from datetime import datetime

def clean_nai_file(file_path):
    """
    Reads and cleans a .nai file by performing the following operations:
    - Strips leading and trailing whitespace from each line.
    - Normalizes curly apostrophes to straight quotes.
    - Removes trailing "/" characters.
    - Merges continuation lines (lines starting with '88,') with the previous line.

    Parameters:
    file_path (str): Path to the .nai file.

    Returns:
    tuple[str, str]: A tuple containing:
        - The raw file content as a single string.
        - The cleaned file content as a list of strings.
    """
    raw_lines = []  # Store raw lines
    cleaned_lines = []  # Store cleaned lines
    previous_line = ""  # Track previous line for merging

    try:
        with open(file_path, "r", encoding="utf-8") as file:

            for raw_line in file:
                raw_lines.append(raw_line) # Store raw line

                line = raw_line.strip().replace("’", "'")  # Remove leading/trailing spaces and any curly apostrophes

                if line.endswith("/"):  
                    line = line[:-1]  # Remove trailing "/"

                if line.startswith("88,"):  
                    previous_line += "," + line[3:]  # Merge continuation line (removing "88,")
                else:
                    if previous_line:
                        cleaned_lines.append(previous_line)  # Store previous complete line
                    previous_line = line  # Set current line as previous

        # Add the last processed line
        if previous_line:
            cleaned_lines.append(previous_line)

        raw_content = "".join(raw_lines)
        cleaned_content = "\n".join(cleaned_lines)

        return raw_content, cleaned_content

    except FileNotFoundError:
        raise FileNotFoundError(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        raise RuntimeError(f"An error occurred while processing the file: {e}")

def convert_implied_decimal(value):
    """ Converts a string with two implied decimal places and optional trailing sign into a float. """
    if not value:
        return None  # Handle empty values gracefully
    
    # Check if the value has a trailing negative sign
    is_negative = value.endswith("-")
    
    # Remove the negative sign before processing
    if is_negative:
        value = value[:-1]

    # Convert to float with two implied decimal places
    amount = int(value) / 100.0  

    # Apply negative sign if necessary
    return -amount if is_negative else amount

def account_parser(fields):
    """
    Parses account fields, ensuring transaction codes and amounts are correctly paired.

    Args:
        fields (list): List of fields where the first three are ignored, and the rest contain transaction code-amount
        pairs.

    Returns:
        dict: A dictionary mapping transaction codes to their corresponding amounts.
    """
    account_amount_fields = fields[3:]

    # Ensure the number of fields is even
    if len(account_amount_fields) % 2 != 0:
        logger.error("Uneven number of fields detected for Transaction Code and Amount pairs. Appending default value.")
        account_amount_fields.append("000")

    # Construct dictionary from pairs
    return {
        transaction_code: convert_implied_decimal(amount)
        for transaction_code, amount in zip(account_amount_fields[::2], account_amount_fields[1::2])
    }


def account_parser(fields):
    account_amount_fields = fields[3:]
    
    if len(account_amount_fields) % 2 != 0:
        logger.error("There are an even number of fields for the account Transaction Code and Amount field pairs")
        account_amount_fields.append("000")

    return {
        account_amount_fields[i]: convert_implied_decimal(account_amount_fields[i+1]) for i in range(
            0, len(account_amount_fields), 2)}

def nai_lines_to_dict(
        nai_lines: list,
        transaction_detail_codes: dict):
    """ Recursively processes an NAI file into a nested dictionary structure. """

    processing_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")

    data_structure = {}  # Main dictionary to store structured data
    current_file = None
    current_group = None
    current_account = None

    for line in nai_lines:
        fields = line.split(",")
        record_type = fields[0]

        if record_type == "01":  # File Header
            creation_date = datetime.strptime(fields[3], "%y%m%d").strftime("%Y%m%d")
            current_file = (
                creation_date + "_"
                + fields[4] + "_"
                + fields[5] + "_"
                + processing_datetime
            )
            data_structure[current_file] = {
                "file_metadata": {
                    "file_metadata_id": current_file,
                    "sender_identification": fields[1],
                    "receiver_identification": fields[2],
                    "creation_date": creation_date, #fields[3] -> YYYY-MM-DD
                    "creation_time": creation_date,
                    "sequence_number": fields[5],
                    "file_control_total_a": None, # Placeholder for File Trailer (99)
                    "number_of_groups": None, # Placeholder for File Trailer (99)
                    "number_of_records": None, # Placeholder for File Trailer (99)
                    "file_control_total_b": None # Placeholder for File Trailer (99)
                },
                "groups": {}  # Container for group data
            }

        elif record_type == "02":  # Group Header
            group_as_of_date = datetime.strptime(fields[4], "%y%m%d").strftime("%Y%m%d")
            current_group = (
                fields[1] + "_"
                + fields[2] + "_"
                + fields[3] + "_"
                + group_as_of_date + "_"
                + fields[5]
            )
            data_structure[current_file]["groups"][current_group] = {
                "file_metadata_id": current_file,
                "group_id": current_group,
                "ultimate_receiver_id": fields[1],
                "originator_id": fields[2],
                "group_status": fields[3],
                "as_of_date": group_as_of_date,
                "as_of_time": fields[5],
                "group_control_total_a": None, # Placeholder for Group Trailer (98)
                "number_of_accounts": None, # Placeholder for Group Trailer (98)
                "group_control_total_b": None, # Placeholder for Group Trailer (98)
                "accounts": {}
            }

        elif record_type == "03":  # Account Identifier
            current_account = fields[1]  # Use account number as key
            account_dict = account_parser(fields)
            data_structure[current_file]["groups"][current_group]["accounts"][current_account] = {
                "file_metadata_id": current_file,
                "group_id": current_group,
                "commercial_account_number": current_account,
                "currency_code": fields[2],
                "closing_balance": account_dict.get("015"),
                "total_credits": account_dict.get("100"),
                "number_of_credit_transactions": account_dict.get("102"),
                "total_debits": account_dict.get("400"),
                "number_of_debit_transactions": account_dict.get("402"),
                "accrued_(unposted)_credit_interest": account_dict.get("500"),
                "accrued_(unposted)_debit_interest": account_dict.get("501"),
                "account_limit": account_dict.get("502"),
                "available_limit": account_dict.get("503"),
                "effective_debit_interest_rate": account_dict.get("965"),
                "effective_credit_interest_rate": account_dict.get("966"),
                "accrued_state_government_duty": account_dict.get("967"),
                "accrued_government_credit_tax": account_dict.get("968"),
                "accrued_government_debit_tax": account_dict.get("969"),
                "account_control_total_a": None,
                "account_control_total_b": None,
                "transactions": []  # Container for transactions
            }

        elif record_type == "16":  # Transaction Details
            transaction_code = fields[1]
            transaction = {
                "file_metadata_id": current_file,
                "group_id": current_group,
                "commercial_account_number": current_account,
                "transaction_code": transaction_code,
                "amount": fields[2],
                "funds_type": fields[3],
                "reference_number": fields[4] if len(fields) > 4 else None,
                "text": "".join(fields[5:]) if len(fields) > 5 else None, # Concatenate remaining fields
                'dr_cr': transaction_detail_codes["dr_cr"].get(transaction_code),
                'transaction_description': transaction_detail_codes["transaction_description"].get(transaction_code),
                'statement_particulars': transaction_detail_codes["statement_particulars"].get(transaction_code),
            }

            data_structure[current_file]["groups"][current_group]["accounts"][current_account]["transactions"].append(transaction)

        elif record_type == "49":  # Account Trailer
            # Fill in missing Account Trailer details
            data_structure[current_file]["groups"][current_group]["accounts"][current_account]["account_control_total_a"] = convert_implied_decimal(fields[1])
            data_structure[current_file]["groups"][current_group]["accounts"][current_account]["account_control_total_b"] = convert_implied_decimal(fields[2])
        
        elif record_type == "98":  # Group Trailer
            # Fill in missing Group Trailer details
            data_structure[current_file]["groups"][current_group]["group_control_total_a"] = convert_implied_decimal(fields[1])
            data_structure[current_file]["groups"][current_group]["number_of_accounts"] = int(fields[2])
            data_structure[current_file]["groups"][current_group]["group_control_total_b"] = convert_implied_decimal(fields[3])

        elif record_type == "99":  # File Trailer
            # Fill in missing File Trailer details
            data_structure[current_file]["file_metadata"]["file_control_total_a"] = convert_implied_decimal(fields[1])
            data_structure[current_file]["file_metadata"]["number_of_groups"] = int(fields[2])
            data_structure[current_file]["file_metadata"]["number_of_records"] = int(fields[3])
            data_structure[current_file]["file_metadata"]["file_control_total_b"] = convert_implied_decimal(fields[4])

    return data_structure

def nai_dict_to_dfs(nai_dict):
    """Flattens the hierarchical NAI dictionary into separate DataFrames for database storage."""
    
    file_metadata_records = []
    group_records = []
    account_records = []
    transaction_records = []

    for file_id, file_data in nai_dict.items():
        # Extract File Metadata
        file_metadata = file_data["file_metadata"]
        file_metadata_records.append(file_metadata)

        for group_id, group_data in file_data["groups"].items():
            # Extract Group Data
            group_records.append({
                "file_metadata_id": group_data["file_metadata_id"],
                "group_id": group_data["group_id"],
                "ultimate_receiver_id": group_data["ultimate_receiver_id"],
                "originator_id": group_data["originator_id"],
                "group_status": group_data["group_status"],
                "as_of_date": group_data["as_of_date"],
                "as_of_time": group_data["as_of_time"],
                "group_control_total_a": group_data["group_control_total_a"],
                "group_control_total_b": group_data["group_control_total_b"]
            })

            for account_id, account_data in group_data["accounts"].items():
                # Extract Account Data
                account_records.append({
                    "file_metadata_id": account_data["file_metadata_id"],
                    "group_id": account_data["group_id"],
                    "commercial_account_number": account_data["commercial_account_number"],
                    "currency_code": account_data["currency_code"],
                    "closing_balance": account_data["closing_balance"],
                    "total_credits": account_data["total_credits"],
                    "number_of_credit_transactions": account_data["number_of_credit_transactions"],
                    "total_debits": account_data["total_debits"],
                    "number_of_debit_transactions": account_data["number_of_debit_transactions"],
                    "account_control_total_a": account_data["account_control_total_a"],
                    "account_control_total_b": account_data["account_control_total_b"]
                })

                for transaction in account_data["transactions"]:
                    # Extract Transaction Data
                    transaction_records.append({
                        "file_metadata_id": transaction["file_metadata_id"],
                        "group_id": transaction["group_id"],
                        "commercial_account_number": transaction["commercial_account_number"],
                        "transaction_code": transaction["transaction_code"],
                        "amount": float(transaction["amount"]) / 100,  # Convert implied decimal
                        "funds_type": transaction["funds_type"],
                        "reference_number": transaction["reference_number"],
                        "text": transaction["text"],
                        "dr_cr": transaction["dr_cr"],
                        "transaction_description": transaction["transaction_description"],
                        "statement_particulars": transaction["statement_particulars"]
                    })

    # Convert to Pandas DataFrames
    df_file_metadata = pd.DataFrame(file_metadata_records)
    df_groups = pd.DataFrame(group_records)
    df_accounts = pd.DataFrame(account_records)
    df_transactions = pd.DataFrame(transaction_records)

    return df_file_metadata, df_groups, df_accounts, df_transactions

def structured_dfs(df_file_metadata, df_groups, df_accounts, df_transactions):
    """
    Merges metadata and group data into the accounts DataFrame.

    Parameters:
    - df_file_metadata (pd.DataFrame): File metadata DataFrame.
    - df_groups (pd.DataFrame): Group-level data.
    - df_accounts (pd.DataFrame): Account-level data.
    - df_transactions (pd.DataFrame): Transaction-level data.

    Returns:
    - pd.DataFrame: Structured accounts DataFrame with merged metadata and group data.
    """

    # ✅ Copy df_accounts to avoid modifying the original
    df_accounts_structured = df_accounts.copy()

    # ✅ Safely extract file metadata (assuming it's a single-row DataFrame)
    if len(df_file_metadata) == 1:
        df_file_metadata = df_file_metadata.iloc[0]  # Convert to Series for direct column assignment

        df_accounts_structured["file_control_total_a"] = df_file_metadata["file_control_total_a"]
        df_accounts_structured["number_of_groups"] = df_file_metadata["number_of_groups"]
        df_accounts_structured["number_of_records"] = df_file_metadata["number_of_records"]
        df_accounts_structured["file_control_total_b"] = df_file_metadata["file_control_total_b"]
    else:
        raise ValueError("df_file_metadata must contain exactly one row.")

    # ✅ Merge group data onto accounts using "group_id"
    df_accounts_structured = df_accounts_structured.merge(
        df_groups[["group_id", "group_control_total_a", "group_control_total_b"]],
        on="group_id",
        how="left"
    )

    # ✅ Ensure column order is correct
    accounts_structured_column_order = [
        "file_metadata_id",
        "file_control_total_a",
        "number_of_groups",
        "number_of_records",
        "file_control_total_b",
        "group_id",
        "group_control_total_a",
        "group_control_total_b",
        "commercial_account_number",
        "currency_code",
        "closing_balance",
        "total_credits",
        "number_of_credit_transactions",
        "total_debits",
        "number_of_debit_transactions",
        "account_control_total_a",
        "account_control_total_b",
    ]

    # df_transactions
    df_transactions_structured = df_transactions.copy()

    # ✅ Return structured DataFrame with correct column order
    return df_accounts_structured[accounts_structured_column_order], df_transactions_structured

def process_nai_file(input_folder_path: str, file_name: str, transaction_detail_codes: dict):
    """
    Processes a .nai file by cleaning it and structuring the data.

    Parameters:
    - input_folder_path (str): The path to the folder containing the file.
    - file_name (str): The name of the file to process.

    Returns:
    - dict: A dictionary containing the raw content, cleaned content, and structured data.
    """
    file_path = os.path.join(input_folder_path, file_name)

    # Read and clean file
    raw_content, cleaned_content = clean_nai_file(file_path)

    # Process cleaned data
    nai_dict = nai_lines_to_dict(
        cleaned_content.split("\n"),
        transaction_detail_codes
    )

    # Print structured data

    # Convert dictionary to DataFrames
    df_file_metadata, df_groups, df_accounts, df_transactions = nai_dict_to_dfs(nai_dict)

    df_accounts_structured, df_transactions_structured = structured_dfs(
        df_file_metadata=df_file_metadata,
        df_groups=df_groups,
        df_accounts=df_accounts,
        df_transactions=df_transactions,
    )

    return {
        "file_name": file_name,
        "raw_content": raw_content,
        "cleaned_content": cleaned_content,
        "nai_dict": nai_dict,
        "df_file_metadata": df_file_metadata,
        "df_groups": df_groups,
        "df_accounts": df_accounts,
        "df_transactions": df_transactions,
        "df_accounts_structured": df_accounts_structured,
        "df_transactions_structured": df_transactions_structured,
    }


def nai_parser(
        input_folder_path,
        transaction_detail_codes,
    ):
    logger.info("Running nai parser")

    # List all of the files available as input
    files_list = [entry.name for entry in os.scandir(input_folder_path) if entry.is_file()]
    
    nai_dict = {}
    for file_name in files_list:
        nai_dict[file_name] = {}
        nai_dict[file_name].update(
            process_nai_file(
                input_folder_path=input_folder_path,
                file_name=file_name,
                transaction_detail_codes=transaction_detail_codes
            )
        )

    return nai_dict
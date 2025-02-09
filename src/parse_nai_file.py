import os
import json
import pandas as pd
from logger import logger
from datetime import datetime
from typing import List, Dict, Tuple, Any

import os
import logging
from typing import Tuple

# Setup Logger
logger = logging.getLogger(__name__)

def clean_nai_file(file_path: str) -> Tuple[str, str]:
    """
    Reads and cleans a .nai file by performing the following operations:
    - Strips leading and trailing whitespace from each line.
    - Normalizes curly apostrophes to straight quotes.
    - Removes trailing '/' characters.
    - Merges continuation lines (lines starting with '88,') with the previous line.

    Parameters:
        file_path (str): Path to the .nai file.

    Returns:
        Tuple[str, str]: A tuple containing:
            - The raw file content as a single string.
            - The cleaned file content as a single string.
    """

    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return "", ""

    raw_lines = []
    cleaned_lines = []
    previous_line = ""

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for raw_line in file:
                raw_lines.append(raw_line)  # Store raw content
                line = raw_line.strip().replace("’", "'")  # Normalize curly apostrophes

                if line.endswith("/"):
                    line = line.rstrip("/")  # Remove trailing '/'
                
                if line.startswith("88,"):
                    previous_line += "," + line[3:]  # Merge continuation lines
                else:
                    if previous_line:
                        cleaned_lines.append(previous_line)
                    previous_line = line

        # Append last processed line
        if previous_line:
            cleaned_lines.append(previous_line)

        raw_content = "".join(raw_lines)
        cleaned_content = "\n".join(cleaned_lines)

        logger.info(f"✅ Successfully cleaned file: {file_path}")
        return raw_content, cleaned_content

    except (OSError, IOError) as e:
        logger.error(f"❌ Error reading file {file_path}: {e}")
        return "", ""

    except Exception as e:
        logger.error(f"❌ Unexpected error while processing {file_path}: {e}")
        return "", ""

def convert_implied_decimal(value: str) -> float:
    """
    Converts a string with implied decimal places into a float.

    Parameters:
    - value (str): String representing a numeric value.

    Returns:
    - float: Converted value with two decimal places.
    """
    # Handle empty values gracefully
    if not value:
        return None

    # Check if the value has a trailing negative sign
    is_negative = value.endswith("-")

    # Remove the negative sign before processing
    if is_negative:
        value = value[:-1]

    # Convert to float with two implied decimal places
    amount = int(value) / 100.0  

    # Apply negative sign if necessary
    return -amount if is_negative else amount

def account_parser(fields: List[str]) -> Dict[str, float]:
    """
    Parses account transaction details.

    Parameters:
    - fields (List[str]): List containing transaction codes and amounts.

    Returns:
    - Dict[str, float]: Parsed transaction amounts mapped to their codes.
    """
    account_amount_fields = fields[3:]

    if len(account_amount_fields) % 2 != 0:
        logger.warning("⚠️ Uneven fields detected for Transaction Code and Amount pairs. Adding default value.")
        account_amount_fields.append("000")

    return {
        account_amount_fields[i]: convert_implied_decimal(account_amount_fields[i + 1])
        for i in range(0, len(account_amount_fields), 2)
    }

def nai_lines_to_dict(
    nai_lines: List[str],
    transaction_detail_codes: Dict[str, Dict[str, str]]
) -> Dict[str, Any]:
    """
    Parses an NAI file into a structured dictionary.

    Parameters:
    - nai_lines (List[str]): List of cleaned NAI lines.
    - transaction_detail_codes (Dict[str, Dict[str, str]]): Mapping of transaction codes.

    Returns:
    - Dict[str, Any]: Nested dictionary containing structured data.
    """
    processing_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")
    data_structure = {}  # Main dictionary to store structured data
    current_file, current_group, current_account = None , None , None

    for line in nai_lines:
        fields = line.split(",")
        record_type = fields[0]

        try:
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

        except KeyError as e:
            logger.error(f"❌ KeyError processing line '{line}': Missing {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")

    return data_structure

def nai_dict_to_dfs(nai_dict: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Converts a hierarchical NAI dictionary into structured Pandas DataFrames for database storage.

    Parameters:
        nai_dict (Dict[str, Any]): Nested dictionary representing NAI data.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: A tuple containing:
            - df_file_metadata (pd.DataFrame): File metadata records.
            - df_groups (pd.DataFrame): Group-level data.
            - df_accounts (pd.DataFrame): Account-level data.
            - df_transactions (pd.DataFrame): Transaction-level data.
    """
    
    file_metadata_records, group_records, account_records, transaction_records = [], [], [], []

    try:
        for file_id, file_data in nai_dict.items():
            # Extract File Metadata
            file_metadata = file_data.get("file_metadata", {})
            if file_metadata:
                file_metadata_records.append(file_metadata)

            for group_id, group_data in file_data.get("groups", {}).items():
                # Extract Group Data
                group_records.append({
                    "file_metadata_id": group_data.get("file_metadata_id"),
                    "group_id": group_data.get("group_id"),
                    "ultimate_receiver_id": group_data.get("ultimate_receiver_id"),
                    "originator_id": group_data.get("originator_id"),
                    "group_status": group_data.get("group_status"),
                    "as_of_date": group_data.get("as_of_date"),
                    "as_of_time": group_data.get("as_of_time"),
                    "group_control_total_a": group_data.get("group_control_total_a"),
                    "group_control_total_b": group_data.get("group_control_total_b"),
                })

                for account_id, account_data in group_data.get("accounts", {}).items():
                    # Extract Account Data
                    account_records.append({
                        "file_metadata_id": account_data.get("file_metadata_id"),
                        "group_id": account_data.get("group_id"),
                        "commercial_account_number": account_data.get("commercial_account_number"),
                        "currency_code": account_data.get("currency_code"),
                        "closing_balance": account_data.get("closing_balance"),
                        "total_credits": account_data.get("total_credits"),
                        "number_of_credit_transactions": account_data.get("number_of_credit_transactions"),
                        "total_debits": account_data.get("total_debits"),
                        "number_of_debit_transactions": account_data.get("number_of_debit_transactions"),
                        "account_control_total_a": account_data.get("account_control_total_a"),
                        "account_control_total_b": account_data.get("account_control_total_b"),
                    })

                    for transaction in account_data.get("transactions", []):
                        # Extract Transaction Data
                        transaction_records.append({
                            "file_metadata_id": transaction.get("file_metadata_id"),
                            "group_id": transaction.get("group_id"),
                            "commercial_account_number": transaction.get("commercial_account_number"),
                            "transaction_code": transaction.get("transaction_code"),
                            "amount": float(transaction.get("amount", 0)) / 100,  # Convert implied decimal
                            "funds_type": transaction.get("funds_type"),
                            "reference_number": transaction.get("reference_number"),
                            "text": transaction.get("text"),
                            "dr_cr": transaction.get("dr_cr"),
                            "transaction_description": transaction.get("transaction_description"),
                            "statement_particulars": transaction.get("statement_particulars"),
                        })

        # Convert to Pandas DataFrames
        df_file_metadata = pd.DataFrame(file_metadata_records) if file_metadata_records else pd.DataFrame()
        df_groups = pd.DataFrame(group_records) if group_records else pd.DataFrame()
        df_accounts = pd.DataFrame(account_records) if account_records else pd.DataFrame()
        df_transactions = pd.DataFrame(transaction_records) if transaction_records else pd.DataFrame()

        logger.info("✅ Successfully converted NAI dictionary to DataFrames.")
        return df_file_metadata, df_groups, df_accounts, df_transactions

    except Exception as e:
        logger.error(f"❌ Error processing NAI dictionary: {e}", exc_info=True)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def structured_dfs(
    df_file_metadata: pd.DataFrame,
    df_groups: pd.DataFrame,
    df_accounts: pd.DataFrame,
    df_transactions: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Merges metadata and group data into the accounts DataFrame to structure the data for analysis or database storage.

    Parameters:
        df_file_metadata (pd.DataFrame): File metadata DataFrame (should contain exactly one row).
        df_groups (pd.DataFrame): Group-level data DataFrame.
        df_accounts (pd.DataFrame): Account-level data DataFrame.
        df_transactions (pd.DataFrame): Transaction-level data DataFrame.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:
            - A structured DataFrame with merged metadata and group data at the account level.
            - A structured transactions DataFrame (unchanged from input but maintained for consistency).
    
    Raises:
        ValueError: If df_file_metadata does not contain exactly one row.
    """

    try:
       # ✅ Validate df_file_metadata contains exactly one row
        if df_file_metadata.shape[0] != 1:
            raise ValueError("df_file_metadata must contain exactly one row.")

        logger.info("✅ Validated df_file_metadata contains exactly one row.")

        # ✅ Extract file metadata values (convert DataFrame to Series)
        file_metadata = df_file_metadata.iloc[0]

        # ✅ Copy df_accounts to avoid modifying the original
        df_accounts_structured = df_accounts.copy()

        # ✅ Add file-level metadata to accounts
        df_accounts_structured["file_control_total_a"] = file_metadata.get("file_control_total_a", None)
        df_accounts_structured["number_of_groups"] = file_metadata.get("number_of_groups", None)
        df_accounts_structured["number_of_records"] = file_metadata.get("number_of_records", None)
        df_accounts_structured["file_control_total_b"] = file_metadata.get("file_control_total_b", None)

        logger.info("✅ Successfully merged file metadata into accounts DataFrame.")

        # ✅ Merge group data onto accounts using "group_id"
        df_accounts_structured = df_accounts_structured.merge(
            df_groups[["group_id", "group_control_total_a", "group_control_total_b"]],
            on="group_id",
            how="left"
        )

        logger.info("✅ Successfully merged group data into accounts DataFrame.")

        # ✅ Define the correct column order
        structured_account_columns = [
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

        # ✅ Ensure only existing columns are selected (avoids KeyError if a column is missing)
        df_accounts_structured = df_accounts_structured[[col for col in structured_account_columns if col in df_accounts_structured.columns]]
        df_accounts_structured = df_accounts_structured.reindex(columns=structured_account_columns)

        logger.info("✅ Ensured correct column order for structured accounts DataFrame.")

        # ✅ Copy df_transactions to maintain consistency
        df_transactions_structured = df_transactions.copy()

        # ✅ Return structured DataFrame with correct column order
        return df_accounts_structured[structured_account_columns], df_transactions_structured

    except Exception as e:
        logger.error(f"❌ Error processing structured DataFrames: {e}", exc_info=True)
        return pd.DataFrame(), pd.DataFrame()  # Return empty DataFrames on failure

def process_nai_file(
    input_folder_path: str, file_name: str, transaction_detail_codes: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Processes a .NAI file by reading, cleaning, and structuring the data into DataFrames.

    Parameters:
        input_folder_path (str): The directory path containing the NAI file.
        file_name (str): The name of the NAI file to process.
        transaction_detail_codes (dict): A dictionary mapping transaction detail codes.

    Returns:
        dict: A dictionary containing:
            - file_name (str): Name of the processed file.
            - raw_content (str): Raw file content before cleaning.
            - cleaned_content (str): Cleaned file content.
            - nai_dict (dict): Parsed hierarchical dictionary representation.
            - df_file_metadata (pd.DataFrame): File metadata DataFrame.
            - df_groups (pd.DataFrame): Group-level DataFrame.
            - df_accounts (pd.DataFrame): Account-level DataFrame.
            - df_transactions (pd.DataFrame): Transaction-level DataFrame.
            - df_accounts_structured (pd.DataFrame): Structured accounts DataFrame.
            - df_transactions_structured (pd.DataFrame): Structured transactions DataFrame.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: If any unexpected error occurs during processing.
    """
    file_path = os.path.join(input_folder_path, file_name)

    try:
        # ✅ Step 1: Read and clean the file
        raw_content, cleaned_content = clean_nai_file(file_path)

        if not raw_content:
            logger.warning(f"⚠️ Empty or unreadable file: {file_path}")
            raise ValueError("File content is empty or unreadable.")

        logger.info(f"✅ Successfully read and cleaned the file: {file_name}")

        # ✅ Step 2: Convert cleaned content into structured dictionary
        nai_dict = nai_lines_to_dict(cleaned_content.split("\n"), transaction_detail_codes)

        if not nai_dict:
            logger.warning(f"⚠️ Failed to parse structured data from: {file_name}")
            raise ValueError("Failed to parse file content into dictionary format.")

        logger.info(f"✅ Successfully converted file to structured dictionary.")

        # ✅ Step 3: Convert structured dictionary to DataFrames
        df_file_metadata, df_groups, df_accounts, df_transactions = nai_dict_to_dfs(nai_dict)

        logger.info(f"✅ Successfully converted structured dictionary to DataFrames.")

        # ✅ Step 4: Structure DataFrames for better organization
        df_accounts_structured, df_transactions_structured = structured_dfs(
            df_file_metadata=df_file_metadata,
            df_groups=df_groups,
            df_accounts=df_accounts,
            df_transactions=df_transactions,
        )

        logger.info(f"✅ Successfully structured DataFrames.")

        # ✅ Step 5: Return processed data as a structured dictionary
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

    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {file_path}", exc_info=True)
        raise e

    except ValueError as e:
        logger.error(f"❌ Data processing error: {e}", exc_info=True)
        return {
            "file_name": file_name,
            "error": str(e),
            "raw_content": "",
            "cleaned_content": "",
            "nai_dict": {},
            "df_file_metadata": pd.DataFrame(),
            "df_groups": pd.DataFrame(),
            "df_accounts": pd.DataFrame(),
            "df_transactions": pd.DataFrame(),
            "df_accounts_structured": pd.DataFrame(),
            "df_transactions_structured": pd.DataFrame(),
        }

    except Exception as e:
        logger.error(f"❌ Unexpected error processing file {file_name}: {e}", exc_info=True)
        return {
            "file_name": file_name,
            "error": f"Unexpected error: {e}",
            "raw_content": "",
            "cleaned_content": "",
            "nai_dict": {},
            "df_file_metadata": pd.DataFrame(),
            "df_groups": pd.DataFrame(),
            "df_accounts": pd.DataFrame(),
            "df_transactions": pd.DataFrame(),
            "df_accounts_structured": pd.DataFrame(),
            "df_transactions_structured": pd.DataFrame(),
        }

def nai_parser(
    input_folder_path: str,
    transaction_detail_codes: Dict[str, Dict[str, str]]
) -> Dict[str, Any]:
    """
    Parses NAI files in a given folder.

    Parameters:
    - input_folder_path (str): Path to the folder containing NAI files.

    Returns:
    - Dict[str, Any]: Processed data for each file.
    """
    logger.info("📂 Running NAI Parser")

    # List all of the files available as input
    files_list = [f.name for f in os.scandir(input_folder_path) if f.is_file()]
    nai_dict = {}

    for file_name in files_list:
        logger.info(f"📄 Processing file: {file_name}")
        
        nai_dict[file_name] = {}
        nai_dict[file_name].update(
            process_nai_file(
                input_folder_path=input_folder_path,
                file_name=file_name,
                transaction_detail_codes=transaction_detail_codes
            )
        )

    return nai_dict
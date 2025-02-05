import os
import pandas as pd
from logger import logger
from datetime import datetime

def transaction_detail_codes():
    return {
        'dr_cr': {
            "175": "CR",
            "195": "CR",
            "238": "CR",
            "252": "CR",
            "357": "CR",
            "399": "CR",
            "475": "DR",
            "495": "DR",
            "501": "DR",
            "512": "DR",
            "555": "DR",
            "564": "DR",
            "595": "DR",
            "631": "DR",
            "654": "DR",
            "699": "DR",
            "905": "CR",
            "906": "CR",
            "910": "CR",
            "911": "CR",
            "915": "CR",
            "920": "CR",
            "925": "CR",
            "930": "CR",
            "935": "CR",
            "936": "CR",
            "938": "CR",
            "950": "DR",
            "951": "DR",
            "952": "DR",
            "953": "DR",
            "955": "DR",
            "956": "DR",
            "960": "DR",
            "961": "DR",
            "962": "DR",
            "970": "DR",
            "971": "DR",
            "975": "DR",
            "980": "DR",
            "985": "DR",
            "986": "DR",
            "987": "DR",
            "988": "DR",
        },
        
        'transaction_description': {
            "175": "Cheques",
            "195": "Transfer credits",
            "238": "Dividend",
            "252": "Reversal Entry",
            "357": "Credit adjustment",
            "399": "Miscellaneous credits",
            "475": "Cheques (paid)",
            "495": "Transfer debits",
            "501": "Automatic drawings",
            "512": "Documentary L/C Drawings/Fees",
            "555": "Dishonoured cheques",
            "564": "Loan fees",
            "595": "FlexiPay",
            "631": "Debit adjustment",
            "654": "Debit Interest",
            "699": "Miscellaneous debits",
            "905": "Credit Interest",
            "906": "National nominees credits",
            "910": "Cash",
            "911": "Cash/cheques",
            "915": "Agent Credits",
            "920": "Inter-bank credits",
            "925": "Bankcard credits",
            "930": "Credit balance transfer",
            "935": "Credits summarised",
            "936": "EFTPOS",
            "938": "NFCA credit transactions",
            "950": "Loan establishment fees",
            "951": "Account keeping fees",
            "952": "Unused limit fees",
            "953": "Security fees",
            "955": "Charges",
            "956": "National nominee debits",
            "960": "Stamp duty-cheque book",
            "961": "Stamp duty",
            "962": "Stamp duty-security",
            "970": "State government tax",
            "971": "Federal government tax",
            "975": "Bankcards",
            "980": "Debit balance transfers",
            "985": "Debits summarised",
            "986": "Cheques summarised",
            "987": "Non-cheques summarised",
            "988": "NFCA debit transaction",
        },

        'statement_particulars': {
            "175": "Cash/Cheques",
            "195": "Transfer",
            "238": "Dividend",
            "252": "Reversal",
            "357": "Adjustment",
            "399": "Miscellaneous credit",
            "475": "All serial numbers",
            "495": "Transfer",
            "501": "Company's name (abbreviated)",
            "512": "Documentary L/C",
            "555": "Dishonoured cheques",
            "564": "Loan fee",
            "595": "Merchant name",
            "631": "Adjustment",
            "654": "Interest",
            "699": "Miscellaneous debit",
            "905": "Interest",
            "906": "National nominees",
            "910": "Cash",
            "911": "Cash/cheques",
            "915": "Agent number advised",
            "920": "Company's name (abbreviated)",
            "925": "Bankcard",
            "930": "Balance transfer",
            "935": "Not applicable",
            "936": "Merchant name",
            "938": "Not applicable",
            "950": "Establishment fee",
            "951": "Account keeping fee",
            "952": "Unused limit fee",
            "953": "Security fee",
            "955": "Charge (or description)",
            "956": "National nominees",
            "960": "Cheque book",
            "961": "Stamp duty",
            "962": "Security stamp duty",
            "970": "State government credit tax",
            "971": "Federal government debit tax",
            "975": "Bankcard",
            "980": "Balance transfers",
            "985": "Not applicable",
            "986": "Not applicable",
            "987": "Not applicable",
            "988": "Not applicable",
        }
    }

def clean_nai_file(file_path):
    """ Reads and cleans a .nai file by:
        - Removing trailing blank spaces
        - Removing trailing "/"
        - Merging continuation records (lines starting with '88') with the previous row
    """
    cleaned_lines = []  # Store cleaned lines
    previous_line = ""  # Track previous line for merging

    with open(file_path, "r") as file:

        for line in file:
            line = line.strip()  # Remove leading/trailing spaces
            line = line.replace("’", "'") # Remove any curly apostrophes

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

    return cleaned_lines

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

def process_nai_data(nai_lines):
    """ Recursively processes an NAI file into a nested dictionary structure. """

    transaction_detail_codes_dict = transaction_detail_codes()

    processing_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")
    part_dt = datetime.now().strftime("%Y%m%d")
    
    data_structure = {}  # Main dictionary to store structured data
    current_file = None
    current_group = None
    current_account = None

    for line in nai_lines:
        fields = line.split(",")
        record_type = fields[0]

        if record_type == "01":  # File Header
            # 01,,BNZA,120725,0400,1,78,78
            #current_file = fields[3]  # Use file date as key
            creation_date = datetime.strptime(fields[3], "%y%m%d").strftime("%Y%m%d")
            current_file = (
                creation_date + "_"
                + fields[4] + "_"
                + fields[5] + "_"
                + processing_datetime
            )
            # date_str = date_obj.strftime("%Y-%m-%d")
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
            account_amount = convert_implied_decimal(fields[4])
            account_dict = account_parser(fields)
            data_structure[current_file]["groups"][current_group]["accounts"][current_account] = {
                "file_metadata_id": current_file,
                "group_id": current_group,
                "commercial_account_number": current_account,
                "currency_code": fields[2],
                "transaction_code": fields[3],
                "amount": account_amount,
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
                'dr_cr': transaction_detail_codes_dict["dr_cr"][transaction_code],
                'transaction_description': transaction_detail_codes_dict["transaction_description"][transaction_code],
                'statement_particulars': transaction_detail_codes_dict["statement_particulars"][transaction_code],
            }
            data_structure[current_file]["groups"][current_group]["accounts"][current_account]["transactions"].append(transaction)

        elif record_type == "49":  # Account Trailer
            # Fill in missing Account Trailer details
            data_structure[current_file]["groups"][current_group]["accounts"][current_account]["account_control_total_a"] = convert_implied_decimal(fields[1])
            data_structure[current_file]["groups"][current_group]["accounts"][current_account]["account_control_total_b"] = convert_implied_decimal(fields[2])
        
        elif record_type == "98":  # Group Trailer
            # Fill in missing Group Trailer details
            data_structure[current_file]["groups"][current_group]["group_control_total_a"] = convert_implied_decimal(fields[1])
            data_structure[current_file]["groups"][current_group]["number_of_accounts"] = (fields)[2]
            data_structure[current_file]["groups"][current_group]["group_control_total_b"] = convert_implied_decimal(fields[3])

        elif record_type == "99":  # File Trailer
            # Fill in missing File Trailer details
            data_structure[current_file]["file_metadata"]["file_control_total_a"] = convert_implied_decimal(fields[1])
            data_structure[current_file]["file_metadata"]["number_of_groups"] = fields[2]
            data_structure[current_file]["file_metadata"]["number_of_records"] = fields[3]
            data_structure[current_file]["file_metadata"]["file_control_total_b"] = convert_implied_decimal(fields[4])

    return data_structure


def process_nai_file(
        input_folder,
        file_name
):
    # Convert the first 6 characters directly to a date
    date_obj = datetime.strptime(file_name[:8], "%Y%m%d")
    date_str = date_obj.strftime("%Y-%m-%d")

    cleaned_lines = clean_nai_file(file_path=os.path.join(input_folder, file_name))

    for line in cleaned_lines:
        print(line)

    # Run processing
    structured_data = process_nai_data(cleaned_lines)

    # Print structured data
    import json
    print(json.dumps(structured_data, indent=4))

    print(f"Keys: {structured_data.keys()}")

    return structured_data

def flatten_nai_data(nai_dict):
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
                    "transaction_code": account_data["transaction_code"],
                    "amount": account_data["amount"],
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

def checks(
        nai_dict,
        df_file_metadata,
        df_groups,
        df_accounts,
        df_transactions,
    ):
    
    # Checks
    logger.info("CHECKS:")

    logger.info("CHECK 1: file_control_total_a")
    file_control_total_a = df_file_metadata["file_control_total_a"]
    group_control_total_a_sum = df_groups["group_control_total_a"].sum()
    logger.info(f'file_control_total_a: {file_control_total_a}')
    logger.info(f'group_control_total_a: {group_control_total_a_sum}')
    logger.info(f'RESULT: {file_control_total_a==group_control_total_a_sum}')

    print(f'group_control_total_b: {df_groups["group_control_total_b"].sum()}')
    
    print(f'account_control_total_a: {df_accounts["account_control_total_a"].sum()}')
    print(f'account_control_total_b: {df_accounts["account_control_total_b"].sum()}')


    # 
    # number_of_groups
    # number_of_records
    # file_control_total_b

def nai_parser(
        input_folder,
        output_folder
    ):
    logger.info("Running nai parser")

    # List all of the files available as input
    files_list = [entry.name for entry in os.scandir(input_folder) if entry.is_file()]
    
    nai_dict = {}
    for file_name in files_list:
        nai_dict.update(process_nai_file(input_folder=input_folder,file_name=file_name))

    # Convert dictionary to DataFrames
    df_file_metadata, df_groups, df_accounts, df_transactions = flatten_nai_data(nai_dict)

    print(f"df_file_metadata:\n{df_file_metadata}")
    print(f"df_groups:\n{df_groups}")
    print(f"df_accounts:\n{df_accounts}")
    print(f"df_transactions:\n{df_transactions}")

    checks(
        nai_dict = nai_dict,
        df_file_metadata = df_file_metadata,
        df_groups = df_groups,
        df_accounts = df_accounts,
        df_transactions = df_transactions,
    )

    # # Display tables
    # import ace_tools as tools
    # tools.display_dataframe_to_user(name="File Metadata", dataframe=df_file_metadata)
    # tools.display_dataframe_to_user(name="Groups", dataframe=df_groups)
    # tools.display_dataframe_to_user(name="Accounts", dataframe=df_accounts)
    # tools.display_dataframe_to_user(name="Transactions", dataframe=df_transactions)


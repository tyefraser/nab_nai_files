import os
import json
import pandas as pd
from logger import logger
from datetime import datetime
from typing import List, Dict, Tuple, Any


def clean_nai_file(file_path: str) -> Tuple[str, str]:
    """
    Reads and cleans a .nai file by performing:
    - Stripping whitespace.
    - Normalizing curly apostrophes.
    - Removing trailing '/'.
    - Merging continuation lines.

    Parameters:
    - file_path (str): Path to the .nai file.

    Returns:
    - Tuple[str, str]: (raw file content, cleaned file content).
    """
    raw_lines = []
    cleaned_lines = []
    previous_line = ""

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for raw_line in file:
                raw_lines.append(raw_line)
                line = raw_line.strip().replace("’", "'")

                if line.endswith("/"):
                    line = line[:-1]

                if line.startswith("88,"):
                    previous_line += "," + line[3:]
                else:
                    if previous_line:
                        cleaned_lines.append(previous_line)
                    previous_line = line

        if previous_line:
            cleaned_lines.append(previous_line)

        return "".join(raw_lines), "\n".join(cleaned_lines)

    except FileNotFoundError:
        logger.error(f"❌ File not found: {file_path}")
        return "", ""
    except Exception as e:
        logger.error(f"❌ Error processing file {file_path}: {e}")
        return "", ""


def convert_implied_decimal(value: str) -> float:
    """
    Converts a string with implied decimal places into a float.

    Parameters:
    - value (str): String representing a numeric value.

    Returns:
    - float: Converted value with two decimal places.
    """
    if not value:
        return None

    is_negative = value.endswith("-")
    value = value[:-1] if is_negative else value
    amount = int(value) / 100.0

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


def nai_lines_to_dict(nai_lines: List[str], transaction_detail_codes: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """
    Parses an NAI file into a structured dictionary.

    Parameters:
    - nai_lines (List[str]): List of cleaned NAI lines.
    - transaction_detail_codes (Dict[str, Dict[str, str]]): Mapping of transaction codes.

    Returns:
    - Dict[str, Any]: Nested dictionary containing structured data.
    """
    processing_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")
    data_structure = {}
    current_file, current_group, current_account = None, None, None

    for line in nai_lines:
        fields = line.split(",")
        record_type = fields[0]

        try:
            if record_type == "01":
                creation_date = datetime.strptime(fields[3], "%y%m%d").strftime("%Y%m%d")
                current_file = f"{creation_date}_{fields[4]}_{fields[5]}_{processing_datetime}"
                data_structure[current_file] = {
                    "file_metadata": {
                        "file_metadata_id": current_file,
                        "creation_date": creation_date,
                        "sequence_number": fields[5]
                    },
                    "groups": {}
                }

            elif record_type == "02":
                group_as_of_date = datetime.strptime(fields[4], "%y%m%d").strftime("%Y%m%d")
                current_group = f"{fields[1]}_{fields[2]}_{fields[3]}_{group_as_of_date}_{fields[5]}"
                data_structure[current_file]["groups"][current_group] = {
                    "group_id": current_group,
                    "group_status": fields[3],
                    "as_of_date": group_as_of_date,
                    "accounts": {}
                }

            elif record_type == "03":
                current_account = fields[1]
                account_dict = account_parser(fields)
                data_structure[current_file]["groups"][current_group]["accounts"][current_account] = {
                    "commercial_account_number": current_account,
                    "closing_balance": account_dict.get("015"),
                    "transactions": []
                }

            elif record_type == "16":
                transaction_code = fields[1]
                data_structure[current_file]["groups"][current_group]["accounts"][current_account]["transactions"].append(
                    {
                        "transaction_code": transaction_code,
                        "amount": convert_implied_decimal(fields[2]),
                        "dr_cr": transaction_detail_codes["dr_cr"].get(transaction_code)
                    }
                )
        except KeyError as e:
            logger.error(f"❌ KeyError processing line '{line}': Missing {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")

    return data_structure


def nai_dict_to_dfs(nai_dict: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Converts a structured NAI dictionary into DataFrames.

    Parameters:
    - nai_dict (Dict[str, Any]): Nested dictionary containing parsed NAI data.

    Returns:
    - Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: (accounts, transactions).
    """
    account_records, transaction_records = [], []

    for file_id, file_data in nai_dict.items():
        for group_id, group_data in file_data.get("groups", {}).items():
            for account_id, account_data in group_data.get("accounts", {}).items():
                account_records.append({
                    "group_id": group_id,
                    "commercial_account_number": account_id,
                    "closing_balance": account_data.get("closing_balance"),
                })

                for transaction in account_data.get("transactions", []):
                    transaction_records.append({
                        "group_id": group_id,
                        "commercial_account_number": account_id,
                        "transaction_code": transaction.get("transaction_code"),
                        "amount": transaction.get("amount"),
                    })

    return (
        pd.DataFrame(account_records),
        pd.DataFrame(transaction_records),
    )


def nai_parser(input_folder_path: str, transaction_detail_codes: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """
    Parses NAI files in a given folder.

    Parameters:
    - input_folder_path (str): Path to the folder containing NAI files.

    Returns:
    - Dict[str, Any]: Processed data for each file.
    """
    logger.info("📂 Running NAI Parser")

    files_list = [f.name for f in os.scandir(input_folder_path) if f.is_file()]
    nai_dict = {}

    for file_name in files_list:
        logger.info(f"📄 Processing file: {file_name}")

        nai_dict[file_name] = nai_lines_to_dict(
            clean_nai_file(os.path.join(input_folder_path, file_name))[1].split("\n"),
            transaction_detail_codes
        )

    return nai_dict

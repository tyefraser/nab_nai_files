import os
import pandas as pd
import json
from logger import logger

def save_text_file(output_folder: str, file_name: str, content: str, file_type: str):
    """
    Saves text content to a file.

    Parameters:
    - output_folder (str): The folder where the file should be saved.
    - file_name (str): The base name of the file.
    - content (str): The text content to write.
    - file_type (str): Type of content (e.g., "raw" or "clean").

    Returns:
    - None
    """
    file_path = os.path.join(output_folder, f"{file_name}_{file_type}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"✅ {file_type.capitalize()} text output saved: {file_path}")

def save_dict_to_json(output_folder: str, file_name: str, data: dict):
    """
    Saves a dictionary to a JSON file.

    Parameters:
    - output_folder (str): The folder where the file should be saved.
    - file_name (str): The base name of the file.
    - data (dict): The dictionary to save.

    Returns:
    - None
    """
    file_path = os.path.join(output_folder, f"{file_name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info(f"✅ Dictionary output saved: {file_path}")


def nai_output_generator(
        file_output_folder_path: str,
        raw_content: str,
        cleaned_content: str,
        nai_dict: dict,
        df_file_metadata: pd.DataFrame,
        df_groups: pd.DataFrame,
        df_accounts: pd.DataFrame,
        df_transactions: pd.DataFrame,
        df_accounts_structured: str,
        df_transactions_structured: str,
        outputs: list
):
    """
    Generates various output files based on the specified list of outputs.

    Parameters:
    - file_output_folder_path (str): Folder where outputs will be saved.
    - raw_content (str): Raw text content.
    - cleaned_content (str): Cleaned text content.
    - nai_dict (dict): Dictionary containing file data.
    - df_file_metadata (pd.DataFrame): DataFrame containing file metadata.
    - df_groups (pd.DataFrame): DataFrame containing group-level data.
    - df_accounts (pd.DataFrame): DataFrame containing account-level data.
    - df_transactions (pd.DataFrame): DataFrame containing transaction data.
    - df_accounts_structured: str,
    - df_transactions_structured: str,
    - outputs (list): List of outputs to generate (e.g., ["raw_content", "df_accounts"]).

    Returns:
    - None
    """

    # ✅ Ensure output directory exists
    os.makedirs(file_output_folder_path, exist_ok=True)

    # ✅ Define mapping of output types to their processing functions
    output_actions = {
        "nai_dict": lambda: save_dict_to_json(file_output_folder_path, "nai_dict", nai_dict),
        "raw_content": lambda: save_text_file(file_output_folder_path, "raw", raw_content, "raw"),
        "cleaned_content": lambda: save_text_file(file_output_folder_path, "clean", cleaned_content, "clean"),
        "df_file_metadata": lambda: df_file_metadata.to_csv(os.path.join(file_output_folder_path, "df_file_metadata.csv"), index=False),
        "df_groups": lambda: df_groups.to_csv(os.path.join(file_output_folder_path, "df_groups.csv"), index=False),
        "df_accounts": lambda: df_accounts.to_csv(os.path.join(file_output_folder_path, "df_accounts.csv"), index=False),
        "df_transactions": lambda: df_transactions.to_csv(os.path.join(file_output_folder_path, "df_transactions.csv"), index=False),
        "df_accounts_structured": lambda: df_accounts_structured.to_csv(os.path.join(file_output_folder_path, "df_accounts_structured.csv"), index=False),
        "df_transactions_structured": lambda: df_transactions_structured.to_csv(os.path.join(file_output_folder_path, "df_transactions_structured.csv"), index=False),
    }

    # ✅ Process static outputs first (DataFrames & dictionary)
    for output_type in outputs:
        if output_type in output_actions:
            try:
                output_actions[output_type]()  # Execute the corresponding function
                logger.info(f"✅ {output_type} output generated successfully.")
            except Exception as e:
                logger.error(f"❌ Error generating {output_type} output: {e}")

    return None  # ✅ Ensures proper function closure


def output_generator(
        output_folder_path: str,
        files_dict: dict,
        df_nai_checks: pd.DataFrame,
        outputs: list
):
    """
    Generates various output files based on the specified list of outputs.

    Parameters:
    - output_folder_path (str): The folder where outputs will be saved.
    - files_dict (dict): Dictionary containing file data.
    - outputs (list): List of outputs to generate (e.g., ["checks", "raw_content", "df_accounts"]).

    Returns:
    - None
    """

    # Ensure the output directory exists
    os.makedirs(output_folder_path, exist_ok=True)

    # ✅ Define mapping of output types to their processing functions
    if "checks" in outputs:
        df_nai_checks.to_csv(os.path.join(output_folder_path, "checks.csv"), index=False)

    # product nai file outputs
    print(files_dict.keys())
    for file_name, file_dict in files_dict.items():

        # Specific file path
        file_name_without_ext, _ = os.path.splitext(file_name)  # Splits "example.nai" → ("example", ".nai")
        file_output_folder_path = os.path.join(output_folder_path, file_name_without_ext)
        os.makedirs(file_output_folder_path, exist_ok=True)

        nai_output_generator(
            file_output_folder_path=file_output_folder_path,
            raw_content=file_dict["raw_content"],
            cleaned_content=file_dict["cleaned_content"],
            nai_dict=file_dict["nai_dict"],
            df_file_metadata=file_dict["df_file_metadata"],
            df_groups=file_dict["df_groups"],
            df_accounts=file_dict["df_accounts"],
            df_transactions=file_dict["df_transactions"],
            df_accounts_structured=file_dict["df_accounts_structured"],
            df_transactions_structured=file_dict["df_transactions_structured"],
            outputs=outputs,
        )

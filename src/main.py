import os
from utils import get_config
from parser import nai_parser
from checks import nai_dict_checks
from logger import logger
from outputs import output_generator

def process_nai_files():
    """
    Process NAI files by parsing and saving data.
    """
    logger.info("Starting NAI file processing...")

    try:
        # Get config data
        CONFIG_DICT = get_config()
        logger.info(f"Configuration loaded: {CONFIG_DICT}")
        logger.info(f"Configuration loaded: {CONFIG_DICT.keys()}")

        # Parse NAI file
        parser_params = {key: CONFIG_DICT[key] for key in ["input_folder_path", "transaction_detail_codes"]}
        files_dict = nai_parser(**parser_params)

        # Run checks on all of the data produced
        df_nai_checks = nai_dict_checks(files_dict)

        # Write Output
        outputs = [
            "checks",
            "raw_content",
            "cleaned_content",
            "nai_dict",
            "df_file_metadata",
            "df_groups",
            "df_accounts",
            "df_transactions",
            "df_accounts_structured",
            "df_transactions_structured",
        ]
        output_generator(
            output_folder_path=CONFIG_DICT["output_folder_path"],
            files_dict=files_dict,
            df_nai_checks=df_nai_checks,
            outputs=outputs,
        )

    except Exception as e:
        logger.exception("An error occurred while processing NAI files.")

if __name__ == "__main__":
    process_nai_files()

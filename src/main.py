import os
import sys
from typing import Dict, Any, List
from utils import get_config
from parse_nai_file import nai_parser
from checks import nai_dict_checks
from logger import logger
from outputs import output_generator

# Define the default available outputs
DEFAULT_OUTPUTS = [
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

def parse_cli_args() -> List[str]:
    """
    Parse command-line arguments to get the desired output types.

    Returns:
        List[str]: A list of output types specified by the user or the default if none provided or invalid.
    """
    if len(sys.argv) > 1:
        outputs_arg = sys.argv[1]
        outputs_list = [output.strip() for output in outputs_arg.split(",") if output.strip()]
        
        # Validate outputs: ensure they are in the predefined list
        valid_outputs = [output for output in outputs_list if output in DEFAULT_OUTPUTS]
        invalid_outputs = [output for output in outputs_list if output not in DEFAULT_OUTPUTS]

        if invalid_outputs:
            logger.warning(f"Invalid output types ignored: {invalid_outputs}")

        # If no valid outputs were provided, default to all outputs
        if not valid_outputs:
            logger.warning("No valid output types provided. Defaulting to all outputs.")
            return DEFAULT_OUTPUTS

        return valid_outputs

    return DEFAULT_OUTPUTS  # Use default outputs if none provided



def process_nai_files(outputs: List[str]) -> None:
    """
    Process NAI files by parsing and saving data.

    Args:
        outputs (List[str]): The specific outputs to generate.
    """
    logger.info(f"Starting NAI file processing with outputs: {outputs}")

    try:
        # Load configuration
        config_dict: Dict[str, Any] = get_config()

        # Ensure required keys exist in config
        required_keys = ["input_folder_path", "transaction_detail_codes", "output_folder_path"]
        missing_keys = [key for key in required_keys if key not in config_dict]

        if missing_keys:
            logger.error(f"Missing required config keys: {missing_keys}")
            return

        logger.info(f"Configuration keys loaded: {list(config_dict.keys())}")

        # Parse NAI file
        parser_params = {
            "input_folder_path": config_dict["input_folder_path"],
            "transaction_detail_codes": config_dict["transaction_detail_codes"],
        }
        files_dict = nai_parser(**parser_params)

        # Run validation checks
        df_nai_checks = nai_dict_checks(files_dict)

        # Generate specified outputs
        output_generator(
            output_folder_path=config_dict["output_folder_path"],
            files_dict=files_dict,
            df_nai_checks=df_nai_checks,
            outputs=outputs,
        )

        logger.info("NAI file processing completed successfully.")

    except KeyError as ke:
        logger.error(f"Missing expected configuration key: {ke}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred while processing NAI files: {e}")

if __name__ == "__main__":
    selected_outputs = parse_cli_args()
    process_nai_files(selected_outputs)

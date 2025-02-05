import os
from utils import get_config
from parser import nai_parser
from logger import logger  # Import the logger

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

        nai_parser(
            input_folder = CONFIG_DICT['input_folder'],
            output_folder = CONFIG_DICT['output_folder']
        )

        # INPUT_FOLDER = CONFIG_DICT["PROJECT_ROOT"] / "data"  # Example input folder
        # logger.info(f"Looking for NAI files in: {INPUT_FOLDER}")

        # # Ensure input folder exists
        # if not INPUT_FOLDER.exists():
        #     logger.warning(f"Input folder does not exist: {INPUT_FOLDER}")
        #     return

        # # Process NAI files
        # for file_name in os.listdir(INPUT_FOLDER):
        #     if file_name.endswith(".nai"):
        #         file_path = INPUT_FOLDER / file_name
        #         logger.info(f"Processing file: {file_name}")

                # Simulated parser & database calls (Replace with real functions)
                # parser = NAIParser(file_path)
                # data = parser.parse()

                # db.save_data("file_metadata", pd.DataFrame([data["file_metadata"]]))
                # db.save_data("groups", data["groups"])
                # db.save_data("accounts", data["accounts"])
                # db.save_data("transactions", data["transactions"])
                # db.save_data("file_trailers", data["file_trailers"])

                # logger.info(f"Successfully processed {file_name}")

    except Exception as e:
        logger.exception("An error occurred while processing NAI files.")

if __name__ == "__main__":
    process_nai_files()

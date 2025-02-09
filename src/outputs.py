import os
import json
import pandas as pd
from logger import logger
from datetime import datetime


def nai_output_generator(
        output_folder_path: str,
        nai_dict: dict,
        df_nai_checks: pd.DataFrame,
        outputs: list
):
    if "checks" in outputs:
        # write checks output as csv
        df_nai_checks.to_csv(output_folder_path / "checks.csv")
    
    for file_name, file_dict in nai_dict.items():
        if "raw_text" in outputs:
            # write checks output as df
            return 0
    
        if "clean_text" in outputs:
            # write checks output as df
            return 0


    return 0
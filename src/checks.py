import pandas as pd
from logger import logger

# ✅ Define Check Names as Constants
CHECKS = {
    "file_control_total_a": "CHECK 01: file_control_total_a",
    "number_of_groups": "CHECK 02: number_of_groups",
    "number_of_records": "CHECK 03: number_of_records",
    "file_control_total_b": "CHECK 04: file_control_total_b",
    "group_control_total_a": "CHECK 05: group_control_total_a",
    "group_control_total_b": "CHECK 06: group_control_total_b",
    "total_credits": "CHECK 07: total credits",
    "number_of_credit_transactions": "CHECK 08: Count of credit transactions",
    "total_debits": "CHECK 09: total debits",
    "number_of_debit_transactions": "CHECK 10: Count of debit transactions",
    "account_control_total_a": "CHECK 11: account_control_total_a",
    "account_control_total_b": "CHECK 12: account_control_total_b",
}

def nai_file_checks(
    file_name: str,
    df_file_metadata: pd.DataFrame,
    df_groups: pd.DataFrame,
    df_accounts: pd.DataFrame,
    df_transactions: pd.DataFrame
) -> pd.DataFrame:
    """
    Runs validation checks between control values (expected) and calculated values.

    Returns:
    - pd.DataFrame: DataFrame containing check results.
    """

    logger.info(f"Starting validation checks for file: {file_name}")
    file_checks_list = []

    # ✅ File-Level Checks
    try:
        file_checks_list.extend([
            {
                "File Name": file_name,
                "Group Name": "NA",
                "Account Name": "NA",
                "Check Name": CHECKS["file_control_total_a"],
                "Control Value": df_file_metadata["file_control_total_a"].iloc[0],
                "Calculated Value": df_groups["group_control_total_a"].sum(),
            },
            {
                "File Name": file_name,
                "Group Name": "NA",
                "Account Name": "NA",
                "Check Name": CHECKS["number_of_groups"],
                "Control Value": df_file_metadata["number_of_groups"].iloc[0],
                "Calculated Value": len(df_groups),
            },
            {
                "File Name": file_name,
                "Group Name": "NA",
                "Account Name": "NA",
                "Check Name": CHECKS["file_control_total_b"],
                "Control Value": df_file_metadata["file_control_total_b"].iloc[0],
                "Calculated Value": df_groups["group_control_total_b"].sum(),
            }
        ])
    except KeyError as e:
        logger.error(f"Missing expected column in df_file_metadata: {e}")

    # ✅ Group-Level Checks
    for _, group_row in df_groups.iterrows():
        group_id = group_row["group_id"]

        # Pre-filtered group data
        df_group_filtered_accounts = df_accounts[df_accounts["group_id"] == group_id]
        df_group_filtered_transactions = df_transactions[df_transactions["group_id"] == group_id]

        file_checks_list.append({
            "File Name": file_name,
            "Group Name": str(group_id),
            "Account Name": "NA",
            "Check Name": CHECKS["group_control_total_a"],
            "Control Value": group_row["group_control_total_a"],
            "Calculated Value": df_group_filtered_accounts["account_control_total_a"].sum(),
        })

        file_checks_list.append({
            "File Name": file_name,
            "Group Name": str(group_id),
            "Account Name": "NA",
            "Check Name": CHECKS["group_control_total_b"],
            "Control Value": group_row["group_control_total_b"],
            "Calculated Value": df_group_filtered_accounts["account_control_total_b"].sum(),
        })

        # ✅ Account-Level Checks
        for _, account_row in df_group_filtered_accounts.iterrows():
            account_number = account_row["commercial_account_number"]

            # Pre-filtered account transactions
            df_account_filtered_transactions = df_group_filtered_transactions[
                df_group_filtered_transactions["commercial_account_number"] == account_number
            ]

            total_credits = df_account_filtered_transactions.loc[
                (df_account_filtered_transactions["dr_cr"] == "CR") &
                (~df_account_filtered_transactions["transaction_code"].astype(str).isin(["910", "915"])),
                "amount"
            ].sum()

            total_debits = df_account_filtered_transactions.loc[
                df_account_filtered_transactions["dr_cr"] == "DR", "amount"
            ].sum()

            file_checks_list.extend([
                {
                    "File Name": file_name,
                    "Group Name": str(group_id),
                    "Account Name": str(account_number),
                    "Check Name": CHECKS["total_credits"],
                    "Control Value": account_row["total_credits"],
                    "Calculated Value": total_credits,
                },
                {
                    "File Name": file_name,
                    "Group Name": str(group_id),
                    "Account Name": str(account_number),
                    "Check Name": CHECKS["total_debits"],
                    "Control Value": account_row["total_debits"],
                    "Calculated Value": total_debits,
                }
            ])

    # ✅ Convert list to DataFrame
    df_checks = pd.DataFrame(file_checks_list)

    # ✅ Compute Difference & Status
    df_checks["Difference"] = df_checks["Calculated Value"].fillna(0) - df_checks["Control Value"].fillna(0)
    df_checks["Status"] = df_checks["Difference"].apply(lambda x: "PASS" if pd.notna(x) and x == 0 else "FAIL")

    logger.info(f"Validation checks completed for file: {file_name}")
    return df_checks


def nai_dict_checks(files_dict: dict) -> pd.DataFrame:
    """
    Runs `nai_file_checks` for each file in `files_dict`.

    Returns:
    - pd.DataFrame: Aggregated validation results across all files.
    """
    df_nai_checks = []

    for file_name, file_data in files_dict.items():
        logger.info(f"Processing file: {file_name}")

        try:
            df_checks = nai_file_checks(
                file_name=file_name,
                df_file_metadata=file_data["df_file_metadata"],
                df_groups=file_data["df_groups"],
                df_accounts=file_data["df_accounts"],
                df_transactions=file_data["df_transactions"]
            )
            df_nai_checks.append(df_checks)
        except KeyError as e:
            logger.error(f"Missing expected DataFrame in {file_name}: {e}")

    return pd.concat(df_nai_checks, ignore_index=True) if df_nai_checks else pd.DataFrame()

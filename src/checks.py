import pandas as pd
from logger import logger

def nai_file_checks(
        file_name: str,
        df_file_metadata: pd.DataFrame,
        df_groups: pd.DataFrame,
        df_accounts: pd.DataFrame,
        df_transactions: pd.DataFrame
):
    """
    Runs validation checks between control values (expected) and calculated values.

    Parameters:
    - df_file_metadata: DataFrame containing file metadata.
    - df_groups: DataFrame containing group-level data.
    - df_accounts: DataFrame containing account-level data.
    - df_transactions: DataFrame containing transaction data.

    Returns:
    - pd.DataFrame: DataFrame containing check results.
    """
    
    # Initialize a list to store check results
    file_checks_list = []

    logger.info("CHECKS:")

    # ✅ Check 1: file_control_total_a
    file_checks_list.append({
        "File Name": str(file_name),
        "Group Name": "NA",
        "Account Name": "NA",
        "Check Name": "CHECK 01: file_control_total_a",
        "Control Value": df_file_metadata["file_control_total_a"].item(),
        "Control Value - Source": "df_file_metadata.file_control_total_a",
        "Calculated Value": df_groups["group_control_total_a"].sum(),
        "Calculated Value - Source": "df_groups.sum(group_control_total_a)"
    })

    # ✅ Check 2: number_of_groups
    file_checks_list.append({
        "File Name": str(file_name),
        "Group Name": "NA",
        "Account Name": "NA",
        "Check Name": "CHECK 02: number_of_groups",
        "Control Value": df_file_metadata["number_of_groups"].item(),
        "Control Value - Source": "df_file_metadata.number_of_groups",
        "Calculated Value": len(df_groups),
        "Calculated Value - Source": "len(df_groups)"
    })

    # number_of_records
    file_checks_list.append({
        "File Name": str(file_name),
        "Group Name": "NA",
        "Account Name": "NA",
        "Check Name": "CHECK 03: number_of_records",
        "Control Value": df_file_metadata["number_of_records"].item(),
        "Control Value - Source": "Number of records",
        "Calculated Value": 0,
        "Calculated Value - Source": "TBD"
    })
    

    # file_control_total_b
    file_checks_list.append({
        "File Name": str(file_name),
        "Group Name": "NA",
        "Account Name": "NA",
        "Check Name": "CHECK 04: file_control_total_b",
        "Control Value": df_file_metadata["file_control_total_b"].item(),
        "Control Value - Source": "Metadata - file control total b",
        "Calculated Value": df_groups["group_control_total_b"].sum(),
        "Calculated Value - Source": "Group df, sum of control total b"
    })

    for group in df_groups["group_id"]:

        # Filter for Group-Specific Data
        df_group_filtered_groups = df_groups.loc[df_groups["group_id"] == group]
        df_group_filtered_accounts = df_accounts.loc[df_accounts["group_id"] == group]
        df_group_filtered_transactions = df_transactions.loc[df_transactions["group_id"] == group]

        # group_control_total_a
        file_checks_list.append({
            "File Name": str(file_name),
            "Group Name": str(group),
            "Account Name": "NA",
            "Check Name": "CHECK 05: group_control_total_a",
            "Control Value": df_groups["group_control_total_a"].item(),
            "Control Value - Source": "Group df, control total a",
            "Calculated Value": 0,
            "Calculated Value - Source": "TBD",
        })
            
        # group_control_total_b
        file_checks_list.append({
            "File Name": str(file_name),
            "Group Name": str(group),
            "Account Name": "NA",
            "Check Name": "CHECK 06: group_control_total_b",
            "Control Value": df_group_filtered_groups["group_control_total_b"].item(),
            "Control Value - Source": "Group df, control total b",
            "Calculated Value": 0,
            "Calculated Value - Source": "TBD",
        })


        # Checks by account
        for account in df_group_filtered_accounts["commercial_account_number"]:
            # Filter for Account-Specific Data
            df_account_filtered_accounts = df_group_filtered_accounts.loc[df_group_filtered_accounts["commercial_account_number"] == account]
            df_account_filtered_transactions = df_group_filtered_transactions.loc[df_group_filtered_transactions["commercial_account_number"] == account]

            # total_credits
            file_checks_list.append({
                "File Name": str(file_name),
                "Group Name": str(group),
                "Account Name": str(account),
                "Check Name": "CHECK 07: total credits",
                "Control Value": df_account_filtered_accounts["total_credits"].item(),
                "Control Value - Source": "Account df, total credits column",
                "Calculated Value": df_account_filtered_transactions.loc[
                    (df_account_filtered_transactions["dr_cr"] == "CR") & 
                    (~df_account_filtered_transactions["transaction_code"].astype(str).isin(["910", "915"])), 
                    "amount"
                ].sum(),
                "Calculated Value - Source": "Transactions, sum of credit amounts",
            })

            # number_of_credit_transactions
            file_checks_list.append({
                "File Name": str(file_name),
                "Group Name": str(group),
                "Account Name": str(account),
                "Check Name": "CHECK 08: Count of credit transactions",
                "Control Value": df_account_filtered_accounts["number_of_credit_transactions"].item(),
                "Control Value - Source": "Accounts df, number of credit transaction column",
                "Calculated Value": len(df_account_filtered_transactions.loc[
                    (df_account_filtered_transactions["dr_cr"] == "CR") & 
                    (~df_account_filtered_transactions["transaction_code"].isin(["910", "915"]))
                ]),
                "Calculated Value - Source": "Transactions, sum of credit amounts",
            })

            # total_debits
            file_checks_list.append({
                "File Name": str(file_name),
                "Group Name": str(group),
                "Account Name": str(account),
                "Check Name": "CHECK 09: total debits",
                "Control Value": df_account_filtered_accounts["total_debits"].item(),
                "Control Value - Source": "Account df, total debit column",
                "Calculated Value": df_account_filtered_transactions.loc[df_account_filtered_transactions["dr_cr"] == "DR", "amount"].sum(),
                "Calculated Value - Source": "Transactions, sum of debit amounts",
            })

            # number_of_debit_transactions
            file_checks_list.append({
                "File Name": str(file_name),
                "Group Name": str(group),
                "Account Name": str(account),
                "Check Name": "CHECK 10: Count of debit transactions",
                "Control Value": df_account_filtered_accounts["number_of_debit_transactions"].item(),
                "Control Value - Source": "Accounts df, number of debit transaction column",
                "Calculated Value": len(df_account_filtered_transactions.loc[df_account_filtered_transactions["dr_cr"] == "DR"]),
                "Calculated Value - Source": "Transactions, sum of debit amounts",
            })

            # account_control_total_a
            file_checks_list.append({
                "File Name": str(file_name),
                "Group Name": str(group),
                "Account Name": str(account),
                "Check Name": f"CHECK 11: account_control_total_a",
                "Control Value": df_account_filtered_accounts["account_control_total_a"].item(),
                "Control Value - Source": "Accounts df - account_control_total_a column",
                "Calculated Value": (
                    df_account_filtered_accounts["closing_balance"].item() +
                    df_account_filtered_accounts["total_credits"].item() +
                    df_account_filtered_accounts["number_of_credit_transactions"].item() +
                    df_account_filtered_accounts["total_debits"].item() +
                    df_account_filtered_accounts["number_of_debit_transactions"].item() +
                    df_account_filtered_transactions.loc[~df_account_filtered_transactions["transaction_code"].astype(str).isin(["910", "915"]), "amount"].sum()
                ),
                "Calculated Value - Source": "Filtered Accounts df check numerical values",
            })

            # account_control_total_b
            file_checks_list.append({
                "File Name": str(file_name),
                "Group Name": str(group),
                "Account Name": str(account),
                "Check Name": f"CHECK 12: account_control_total_b",
                "Control Value": df_account_filtered_accounts["account_control_total_b"].item(),
                "Control Value - Source": "Accounts df - account_control_total_b column",
                "Calculated Value": (
                    df_account_filtered_accounts["closing_balance"].item() +
                    df_account_filtered_accounts["total_credits"].item() +
                    df_account_filtered_accounts["number_of_credit_transactions"].item() +
                    df_account_filtered_accounts["total_debits"].item() +
                    df_account_filtered_accounts["number_of_debit_transactions"].item() +
                    df_account_filtered_transactions.loc[~df_account_filtered_transactions["transaction_code"].astype(str).isin(["910", "915"]), "amount"].sum()
                ),
                "Calculated Value - Source": "Filtered Accounts df check numerical values",
            })

    # ✅ Convert list to DataFrame
    df_checks = pd.DataFrame(file_checks_list)

    # ✅ Compute Difference & Status
    df_checks["Difference"] = df_checks["Calculated Value"].fillna(0) - df_checks["Control Value"].fillna(0)
    df_checks["Status"] = df_checks["Difference"].apply(lambda x: "PASS" if pd.notna(x) and x == 0 else "FAIL")
    
    logger.info(f"CHECK - RESULTS:\n\n{df_checks}\n\n")

    return df_checks

def nai_dict_checks(files_dict):
    df_nai_checks = None
    
    for file_name, file_data in files_dict.items():

        nai_check_params = {key: file_data[key] for key in [
            "df_file_metadata",
            "df_groups",
            "df_accounts",
            "df_transactions"
            ]
        }
        nai_check_params["file_name"] = file_name # ✅ Adding file_name separately is fin
        df_nai_checks_tmp = nai_file_checks(**nai_check_params) # ✅ Call function with unpacked parameters

        # Combine dfs
        if df_nai_checks == None:
            df_nai_checks = df_nai_checks_tmp
        else:
            df_nai_checks = pd.concat([df_nai_checks, df_nai_checks_tmp], ignore_index=True)

    return df_nai_checks
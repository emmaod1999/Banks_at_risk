import numpy as np
import pandas as pd
import os
import re
from Setup import finance_data_path, NACE_letters_path, I_NACE_saving_path, L_NACE_saving_path, \
    finance_exio_region_path, impact_NACE_score_path, dependency_NACE_score_path,  \
    x_NACE_path, scope_1_impact_var_saving_path, finance_grouped_saving_path
from helper_finance_var import finance_var_calc, finance_var_calc_scope_1, finance_var_calc_scope_3_combined, \
    EXIO_var_calc_scope_1, EXIO_var_calc_scope_3_combined

# Convert descriptions to letters
NACE_letters_df = pd.read_csv(NACE_letters_path, index_col=[0], header=None)
NACE_letters_df.reset_index(inplace=True)
NACE_letters_df.rename(columns={0:"Code", 1:"Sector"}, inplace=True)

# load the finance data
finance_data_df = pd.read_csv(finance_data_path,index_col=[0], header=[0])
finance_data_df.reset_index(inplace=True)

finance_data_NACE_df = pd.merge(finance_data_df,NACE_letters_df)
finance_data_NACE_df.drop(columns={'Sector', 'GBP m'}, inplace=True)

# add exiobase regions to the finance data
# load the region table for exiobase and finance
finance_exio_region_df = pd.read_csv(finance_exio_region_path,index_col=[0], header=[0])
finance_exio_region_df.reset_index(inplace=True)
finance_exio_region_df.rename(columns={'exiobase_region':'region'}, inplace=True)
finance_data_NACE_region_df = pd.merge(finance_data_NACE_df, finance_exio_region_df)
finance_data_NACE_region_df.drop(columns={'Geography'}, inplace=True)
finance_data_NACE_region_df['EUR m adjusted'] = (finance_data_NACE_region_df['EUR m'] *
                                                 finance_data_NACE_region_df['multiplier'])
finance_data_NACE_region_df.drop(columns={'EUR m', 'multiplier'}, inplace=True)
finance_data_NACE_region_grouped_df = finance_data_NACE_region_df.groupby(['Bank', 'Code', 'region']).sum()

# calculate the total amount of loan in EUR for each bank
finance_loan_total_by_bank_df = finance_data_NACE_region_grouped_df.groupby('Bank').sum()
finance_loan_total_by_bank_df.rename(columns={"EUR m adjusted":"Total Loan"}, inplace=True)

# add total loan values to the finance_data
finance_data_NACE_region_grouped_w_total_df = pd.merge(finance_data_NACE_region_grouped_df,
                                                       finance_loan_total_by_bank_df,
                                                       left_index=True, right_index=True)
# get proportion of loans
finance_data_NACE_region_grouped_w_total_df['Proportion of Loans'] = (
        finance_data_NACE_region_grouped_w_total_df['EUR m adjusted'] /
        finance_data_NACE_region_grouped_w_total_df['Total Loan'])


# drop region data for direct dependency and impact in finance data
finance_data_NACE_grouped_df = finance_data_NACE_region_grouped_df.groupby(['Bank', 'Code']).sum()
finance_data_NACE_grouped_w_total_df = pd.merge(finance_data_NACE_grouped_df, finance_loan_total_by_bank_df, left_index=True, right_index=True)
finance_data_NACE_grouped_w_total_df['Proportion of Loans'] = finance_data_NACE_grouped_w_total_df['EUR m adjusted'] / finance_data_NACE_grouped_w_total_df['Total Loan']

# load L_NACE_df and I_NACE_df calculated from filter_for_NACE_finance.py
I_NACE_df = pd.read_csv(I_NACE_saving_path, index_col=[0, 1], header=[0, 1])
L_NACE_df = pd.read_csv(L_NACE_saving_path, index_col=[0, 1], header=[0, 1])

# calculate the weighted average for Leontief (col sums multiplier)
### calculate overlined((L -1)), relative impact dependency matrix
L_min_I = L_NACE_df - I_NACE_df
"""
# load the NACE scores
dep_score_1_scores = []
imp_score_1_scores = []
scope_1_scores = []
scope_3_scores = []
# dependency
dep_sheets = os.listdir(dependency_NACE_score_path)
for sheet in dep_sheets:
    if re.search('1', sheet):
        dep_df = pd.read_csv(f'{dependency_NACE_score_path}/{sheet}', index_col=[0], header=[0])
        dep_df.name = sheet
        scope_1_scores.append(dep_df)
        dep_score_1_scores.append(dep_df)
    if re.search('3', sheet):
        dep_df = pd.read_csv(f'{dependency_NACE_score_path}/{sheet}', index_col=[0, 1], header=[0])
        dep_df.name = sheet
        scope_3_scores.append(dep_df)
#impact
imp_sheets = os.listdir(impact_NACE_score_path)
for sheet in imp_sheets:
    if re.search('1', sheet):
        imp_df = pd.read_csv(f'{impact_NACE_score_path}/{sheet}', index_col=[0], header=[0])
        imp_df.name = sheet
        scope_1_scores.append(imp_df)
        imp_score_1_scores.append(imp_df)
    if re.search('3', sheet):
        imp_df = pd.read_csv(f'{impact_NACE_score_path}/{sheet}', index_col=[0, 1], header=[0])
        imp_df.name = sheet
        scope_3_scores.append(imp_df)

# combined
# get VaR for combined for EXIO
x_NACE_df = pd.read_csv(x_NACE_path, index_col=[0,1], header=[0])


# get the VaR for combined impact and dependency scope 3
for imp_score_df in imp_score_1_scores:
    if re.search('mean', imp_score_df.name):
        type = 'mean'
    if re.search('max', imp_score_df.name):
        type = 'max'
    if re.search('min', imp_score_df.name):
        type = 'min'
    for dep_score_df in dep_score_1_scores:
        if not re.search(type, dep_score_df.name):
            continue
        finance_var_calc_scope_3_combined(imp_score_df, dep_score_df, finance_data_NACE_region_grouped_w_total_df, "code_only", L_min_I, '')
        # EXIO_var_calc_scope_3_combined(imp_score_df, dep_score_df, x_NACE_df, "code_only", L_min_I, '')

        # combine the scope 1 impact and dependency scores
        combined_score_df = dep_score_df * imp_score_df
        combined_score_df.name = f'{dep_score_df.name} {imp_score_df.name}'
        # calculate the finance and EXIO VaR with combined value
        finance_var_calc_scope_1(combined_score_df, finance_data_NACE_region_grouped_w_total_df, "code_only", L_min_I, 'Both')
        finance_var_calc_scope_1(imp_score_df, finance_data_NACE_region_grouped_w_total_df, "code_only", L_min_I, 'Impact')
        finance_var_calc_scope_1(dep_score_df, finance_data_NACE_region_grouped_w_total_df, "code_only", L_min_I, 'Dependency')
        # EXIO_var_calc_scope_1(combined_score_df, "code_only", L_min_I,'',x_NACE_df)

# save the finance grouped total to csv
finance_data_NACE_region_grouped_w_total_df.to_csv(finance_grouped_saving_path)
"""
L_min_I.to_csv('../Data/financial_data/L_min_I.csv')



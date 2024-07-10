import numpy as np
import pandas as pd
import re
import os
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from Setup import (finance_data_path, var_finance_mul_both_path, var_finance_impact_path, var_finance_dependency_path,\
                   value_at_risk_sig_saving_path, value_at_risk_figure_saving_path)
from helper_graphing_functions import aggregate_to_region_service, proportion_transform_mul, anonymize_banks

# get the % values for the difference
financial_data_df = pd.read_csv(finance_data_path, index_col=[0, 1, 2], header=[0])
# the  total portfolio value for each bank
total_value_banks_df = financial_data_df.reset_index().drop(
    columns=['Code', 'region', 'Total Loan', 'Proportion of Loans']).groupby(['Bank']).sum()

# finance
# both
value_at_risk_finance_csvs = os.listdir(var_finance_mul_both_path)
var_path_finance_path = var_finance_mul_both_path
# imp
value_at_risk_finance_imp_csvs = os.listdir(var_finance_impact_path)
# dep
value_at_risk_finance_dep_csvs = os.listdir(var_finance_dependency_path)

# create lists to store the
scope_1_var_finance = []
scope_1_var_finance_imp = []
scope_1_var_finance_dep = []
scope_3_var_finance = []
scope_3_var_finance_imp = []
scope_3_var_finance_dep = []
# rows
scope_3_var_finance_rows = []
scope_3_var_finance_rows_comb = []
scope_3_var_finance_imp_rows = []
scope_3_var_finance_dep_rows = []

# absolute values
# create lists to store the
scope_1_var_finance_abs = []
scope_1_var_finance_imp_abs = []
scope_1_var_finance_dep_abs = []
scope_3_var_finance_abs = []
scope_1_var_finance_comb_abs = []
scope_3_var_finance_comb_abs = []
scope_3_var_finance_imp_abs = []
scope_3_var_finance_dep_abs = []
# rows
scope_3_var_finance_rows_abs = []
scope_3_var_finance_rows_comb_abs = []
scope_3_var_finance_imp_rows_abs = []
scope_3_var_finance_dep_rows_abs = []

# both finance
for sheet in value_at_risk_finance_csvs:
    if re.search('Scope 1', sheet):
        df = pd.read_csv(f'{var_path_finance_path}/{sheet}', index_col=[0, 1, 2], header=[0])
        df.name = sheet
        scope_1_var_finance_abs.append(df)
        df = proportion_transform_mul(df, total_value_banks_df, "region_code", "fin")
        df.name = sheet
        scope_1_var_finance.append(df)
        continue
    if re.search('Value Chain', sheet):
        df = pd.read_csv(f'{var_path_finance_path}/{sheet}', index_col=[0, 1], header=[0])
        df.name = sheet
        scope_3_var_finance_rows_abs.append(df)
        df = proportion_transform_mul(df, total_value_banks_df, "region_only", "fin")
        df.name = sheet
        scope_3_var_finance_rows.append(df)
        continue
    df = pd.read_csv(f'{var_path_finance_path}/{sheet}', index_col=[0, 1, 2], header=[0])
    df.name = sheet
    scope_3_var_finance_abs.append(df)
    df = proportion_transform_mul(df, total_value_banks_df, "region_code", "fin")
    df.name = sheet
    scope_3_var_finance.append(df)

# imp
# finance
for sheet in value_at_risk_finance_imp_csvs:
    if re.search('Scope 1', sheet):
        df = pd.read_csv(f'{var_finance_impact_path}/{sheet}', index_col=[0, 1, 2], header=[0])
        df.name = sheet
        scope_1_var_finance_imp_abs.append(df)
        df = proportion_transform_mul(df, total_value_banks_df, "region_code", "fin")
        df.name = sheet
        scope_1_var_finance_imp.append(df)
        continue
    if re.search('Value Chain', sheet):
        df = pd.read_csv(f'{var_finance_impact_path}/{sheet}', index_col=[0, 1, 2], header=[0])
        df.name = sheet
        scope_3_var_finance_imp_rows_abs.append(df)
        df = proportion_transform_mul(df, total_value_banks_df, "region_code", "fin")
        df.name = sheet
        scope_3_var_finance_imp_rows.append(df)
        continue
    df = pd.read_csv(f'{var_finance_impact_path}/{sheet}', index_col=[0, 1, 2], header=[0])
    df.name = sheet
    scope_3_var_finance_imp_abs.append(df)
    df = proportion_transform_mul(df, total_value_banks_df, "region_code", "fin")
    df.name = sheet
    scope_3_var_finance_imp.append(df)

# dep
# finance
for sheet in value_at_risk_finance_dep_csvs:
    if re.search('Scope 1', sheet):
        df = pd.read_csv(f'{var_finance_dependency_path}/{sheet}', index_col=[0, 1, 2], header=[0])
        df.name = sheet
        scope_1_var_finance_dep_abs.append(df)
        df = proportion_transform_mul(df, total_value_banks_df, "region_code", "fin")
        df.name = sheet
        scope_1_var_finance_dep.append(df)
        continue
    if re.search('Value Chain', sheet):
        df = pd.read_csv(f'{var_finance_dependency_path}/{sheet}', index_col=[0, 1, 2], header=[0])
        df.name = sheet
        scope_3_var_finance_dep_rows_abs.append(df)
        df = proportion_transform_mul(df, total_value_banks_df, "region_code", "fin")
        df.name = sheet
        scope_3_var_finance_dep_rows.append(df)
        continue
    df = pd.read_csv(f'{var_finance_dependency_path}/{sheet}', index_col=[0, 1, 2], header=[0])
    df.name = sheet
    scope_3_var_finance_dep_abs.append(df)
    df = proportion_transform_mul(df, total_value_banks_df, "region_code", "fin")
    df.name = sheet
    scope_3_var_finance_dep.append(df)

# anonymize the banks
banks = np.unique(total_value_banks_df.reset_index()['Bank']).tolist()
banks_anon = ["Bank A", "Bank B", "Bank C", "Bank D", "Bank E", "Bank F", "Bank G"]
df = total_value_banks_df.reset_index()
for i in range(7):
    df = df.replace({banks[i]: banks_anon[i]})
total_value_banks_df = df.set_index('Bank')
# create lists to store the
scope_1_var_finance = anonymize_banks(scope_1_var_finance, banks_anon, "region_code")
scope_1_var_finance_imp = anonymize_banks(scope_1_var_finance_imp, banks_anon, "region_code")
scope_1_var_finance_dep = anonymize_banks(scope_1_var_finance_dep, banks_anon, "region_code")
scope_3_var_finance = anonymize_banks(scope_3_var_finance, banks_anon, "region_code")
scope_3_var_finance_imp = anonymize_banks(scope_3_var_finance_imp, banks_anon, "region_code")
scope_3_var_finance_dep = anonymize_banks(scope_3_var_finance_dep, banks_anon, "region_code")
# rows
scope_3_var_finance_rows = anonymize_banks(scope_3_var_finance_rows, banks_anon, "region_only")
scope_3_var_finance_imp_rows = anonymize_banks(scope_3_var_finance_imp_rows, banks_anon, "region_code")
scope_3_var_finance_dep_rows = anonymize_banks(scope_3_var_finance_dep_rows, banks_anon, "region_code")

# absolute values
# create lists to store the
scope_1_var_finance_abs = anonymize_banks(scope_1_var_finance_abs, banks_anon, "region_code")
scope_1_var_finance_imp_abs = anonymize_banks(scope_1_var_finance_imp_abs, banks_anon, "region_code")
scope_1_var_finance_dep_abs = anonymize_banks(scope_1_var_finance_dep_abs, banks_anon, "region_code")
scope_3_var_finance_abs = anonymize_banks(scope_3_var_finance_abs, banks_anon, "region_code")
scope_3_var_finance_imp_abs = anonymize_banks(scope_3_var_finance_imp_abs, banks_anon, "region_code")
scope_3_var_finance_dep_abs = anonymize_banks(scope_3_var_finance_dep_abs, banks_anon, "region_code")
# rows
scope_3_var_finance_rows_abs = anonymize_banks(scope_3_var_finance_rows_abs, banks_anon, "region_only")
scope_3_var_finance_imp_rows_abs = anonymize_banks(scope_3_var_finance_imp_rows_abs, banks_anon, "region_code")
scope_3_var_finance_dep_rows_abs = anonymize_banks(scope_3_var_finance_dep_rows_abs, banks_anon, "region_code")

# dep
# aggregate by region and service for impact and dependency
# create lists to store the
scope_1_var_finance_region_dep = aggregate_to_region_service(scope_1_var_finance_dep, 'sum')
scope_3_var_finance_region_dep = aggregate_to_region_service(scope_3_var_finance_dep, 'sum')
# abs
# create lists to store the
scope_1_var_finance_region_abs_dep = aggregate_to_region_service(scope_1_var_finance_dep_abs, 'sum')
scope_3_var_finance_region_abs_dep = aggregate_to_region_service(scope_3_var_finance_dep_abs, 'sum')

# imp
# aggregate by region and service for impact and dependency
# create lists to store the
scope_1_var_finance_region_imp = aggregate_to_region_service(scope_1_var_finance_imp, 'sum')
scope_3_var_finance_region_imp = aggregate_to_region_service(scope_3_var_finance_imp, 'sum')
# abs
# create lists to store the
scope_1_var_finance_region_abs_imp = aggregate_to_region_service(scope_1_var_finance_imp_abs, 'sum')
scope_3_var_finance_region_abs_imp = aggregate_to_region_service(scope_3_var_finance_imp_abs, 'sum')

# both
# aggregate by region and service for impact and dependency
# create lists to store the
scope_1_var_finance_region = aggregate_to_region_service(scope_1_var_finance, 'sum')
scope_3_var_finance_region = aggregate_to_region_service(scope_3_var_finance, 'sum')

# abs
# create lists to store the
scope_1_var_finance_region_abs = aggregate_to_region_service(scope_1_var_finance_abs, 'sum')
scope_3_var_finance_region_abs = aggregate_to_region_service(scope_3_var_finance_abs, 'sum')

# get banks and services
# get a list of banks and services
banks = np.unique(scope_3_var_finance[0].reset_index()['Bank']).tolist()
services = np.unique(scope_3_var_finance[0].columns).tolist()

# test bank biting themselves compared to the economic activities biting themselves
index = pd.MultiIndex.from_product([banks, services], names=["Bank", "service"])
stats_test_df_scp3 = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=index)
stats_test_df_scp1 = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=index)
stats_test_df_scp1_vs_scp_3 = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=index)

scope_1_significance = pd.DataFrame(columns=services, index=banks)
scope_3_significance = pd.DataFrame(columns=services, index=banks)
scope_1_vs_3_significance = pd.DataFrame(columns=services, index=banks)

for bank in banks:
    scope_3_combo_mean_one_bank = scope_3_var_finance_region[1].reset_index()[
        scope_3_var_finance_region[1].reset_index()['Bank'] == bank]

    scope_1_combo_mean_one_bank = scope_1_var_finance_region[1].reset_index()[
        scope_1_var_finance_region[1].reset_index()['Bank'] == bank]

    for service in services:
        if (((scope_3_combo_mean_one_bank[service].sum() == 0) and (scope_1_combo_mean_one_bank[service].sum() == 0))):
            continue

        # compare scope 1 vs scope 3
        results = stats.wilcoxon(scope_1_combo_mean_one_bank[f'{service}'], scope_3_combo_mean_one_bank[f'{service}'],
                                 alternative="greater", method="exact")

        stats_test_df_scp1_vs_scp_3.loc[bank, service]['statistic'] = results.statistic
        stats_test_df_scp1_vs_scp_3.loc[bank, service]['p-value'] = results.pvalue
        # stats_test_df_scp1_vs_scp_3.loc[bank, service]['z'] = results.zstatistic

        if results[1] > 0.05:
            scope_1_vs_3_significance[service][bank] = "NS"
        if results[1] < 0.05 and results[1] > 0.01:
            scope_1_vs_3_significance[service][bank] = "*"
        if results[1] <= 0.01 and results[1] > 0.005:
            scope_1_vs_3_significance[service][bank] = "**"
        if results[1] <= 0.005:
            scope_1_vs_3_significance[service][bank] = "***"

    print(f"{bank} done")

stats_test_df_scp1_vs_scp_3.to_csv(f'{value_at_risk_sig_saving_path}/Finance Scope 1 vs Scope 3 Statistics.csv')
scope_1_vs_3_significance.T.to_csv(f'{value_at_risk_sig_saving_path}/Finance Scope 1 vs Scope 3 Significance.csv')

# add scope 1 vs 3 for imp and dep***
# test bank biting themselves compared to the economic activities biting themselves
# Impact
index = pd.MultiIndex.from_product([banks, services], names=["Bank", "service"])
stats_test_df_scp3 = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=index)
stats_test_df_scp1 = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=index)
stats_test_df_scp1_vs_scp_3 = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=index)

scope_1_significance = pd.DataFrame(columns=services, index=banks)
scope_3_significance = pd.DataFrame(columns=services, index=banks)
scope_1_vs_3_significance = pd.DataFrame(columns=services, index=banks)

for bank in banks:
    scope_3_combo_mean_one_bank = scope_3_var_finance_imp[1].reset_index()[
        scope_3_var_finance_imp[1].reset_index()['Bank'] == bank]

    scope_1_combo_mean_one_bank = scope_1_var_finance_imp[1].reset_index()[
        scope_1_var_finance_imp[1].reset_index()['Bank'] == bank]

    for service in services:
        if (((scope_3_combo_mean_one_bank[service].sum() == 0) and (scope_1_combo_mean_one_bank[service].sum() == 0))):
            continue

        # compare scope 1 vs scope 3
        results = stats.wilcoxon(scope_1_combo_mean_one_bank[f'{service}'], scope_3_combo_mean_one_bank[f'{service}'],
                                 alternative="greater", method="exact")

        stats_test_df_scp1_vs_scp_3.loc[bank, service]['statistic'] = results.statistic
        stats_test_df_scp1_vs_scp_3.loc[bank, service]['p-value'] = results.pvalue
        # stats_test_df_scp1_vs_scp_3.loc[bank, service]['z'] = results.zstatistic

        if results[1] > 0.05:
            scope_1_vs_3_significance[service][bank] = "NS"
        if results[1] < 0.05 and results[1] > 0.01:
            scope_1_vs_3_significance[service][bank] = "*"
        if results[1] <= 0.01 and results[1] > 0.005:
            scope_1_vs_3_significance[service][bank] = "**"
        if results[1] <= 0.005:
            scope_1_vs_3_significance[service][bank] = "***"

    print(f"{bank} done")

stats_test_df_scp1_vs_scp_3.to_csv(f'{value_at_risk_sig_saving_path}/Impact Scope 1 vs Scope 3 Statistics.csv')
scope_1_vs_3_significance.T.to_csv(f'{value_at_risk_sig_saving_path}/Impact Scope 1 vs Scope 3 Significance.csv')

# Dependency
index = pd.MultiIndex.from_product([banks, services], names=["Bank", "service"])
stats_test_df_scp3 = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=index)
stats_test_df_scp1 = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=index)
stats_test_df_scp1_vs_scp_3 = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=index)

scope_1_significance = pd.DataFrame(columns=services, index=banks)
scope_3_significance = pd.DataFrame(columns=services, index=banks)
scope_1_vs_3_significance = pd.DataFrame(columns=services, index=banks)

for bank in banks:
    scope_3_combo_mean_one_bank = scope_3_var_finance_dep[1].reset_index()[
        scope_3_var_finance_dep[1].reset_index()['Bank'] == bank]

    scope_1_combo_mean_one_bank = scope_1_var_finance_dep[1].reset_index()[
        scope_1_var_finance_dep[1].reset_index()['Bank'] == bank]

    for service in services:
        if (((scope_3_combo_mean_one_bank[service].sum() == 0) and (scope_1_combo_mean_one_bank[service].sum() == 0))):
            continue

        # compare scope 1 vs scope 3
        results = stats.wilcoxon(scope_1_combo_mean_one_bank[f'{service}'], scope_3_combo_mean_one_bank[f'{service}'],
                                 alternative="greater", method="exact")

        stats_test_df_scp1_vs_scp_3.loc[bank, service]['statistic'] = results.statistic
        stats_test_df_scp1_vs_scp_3.loc[bank, service]['p-value'] = results.pvalue
        # stats_test_df_scp1_vs_scp_3.loc[bank, service]['z'] = results.zstatistic

        if results[1] > 0.05:
            scope_1_vs_3_significance[service][bank] = "NS"
        if results[1] < 0.05 and results[1] > 0.01:
            scope_1_vs_3_significance[service][bank] = "*"
        if results[1] <= 0.01 and results[1] > 0.005:
            scope_1_vs_3_significance[service][bank] = "**"
        if results[1] <= 0.005:
            scope_1_vs_3_significance[service][bank] = "***"

    print(f"{bank} done")

stats_test_df_scp1_vs_scp_3.to_csv(f'{value_at_risk_sig_saving_path}/Dependency Scope 1 vs Scope 3 Statistics.csv')
scope_1_vs_3_significance.T.to_csv(f'{value_at_risk_sig_saving_path}/Dependency Scope 1 vs Scope 3 Significance.csv')

# plot the bar graph with the error bars for EXIO and Finance on one for system and for each bank
# or maybe just EXIO compared with each bank
## BAR CHARTS

# create a plot of scope 1 and scope 3 value at risk for all the banks and all the portfolio
# with the max and min values as the error bars
score_types = ['mean', 'min', 'max']

# var finance
plt.figure(figsize=(20, 20))
# plt.subplots(4,2,sharey=True)
i = 0
for bank in banks:
    i = i + 1
    if (i == 1):
        ax = plt.subplot(4, 2, i)
    if (i != 1):
        ax = plt.subplot(4, 2, i, sharey=ax)
    for sheet in scope_1_var_finance:
        df = sheet.copy()
        one_bank_df = df.reset_index()[df.reset_index()['Bank'] == bank]
        mydict = {}
        for service in services:
            var = np.sum(one_bank_df[service])
            mydict[service] = var
        if re.search('min', sheet.name):
            scope_1_min_values = mydict
        if re.search('mean', sheet.name):
            scope_1_mean_values = mydict
        if re.search('max', sheet.name):
            scope_1_max_values = mydict

    X_axis = np.arange(len(services))

    # scope 1
    scope_1_mean = np.array(list(scope_1_mean_values.values()))
    scope_1_min = np.array(list(scope_1_min_values.values()))
    scope_1_max = np.array(list(scope_1_max_values.values()))

    lower_err_scope_1 = (scope_1_mean) - (scope_1_min)
    higher_err_scope_1 = (scope_1_max) - (scope_1_mean)

    asymetric_error_scope_1 = np.array(list(zip(lower_err_scope_1, higher_err_scope_1))).T

    ax.bar(X_axis - 0.225, scope_1_mean_values.values(), 0.45, label=r'$\mu_{D}$')
    ax.errorbar(X_axis - 0.225, scope_1_mean_values.values(), yerr=asymetric_error_scope_1, fmt='ro')

    for sheet in scope_3_var_finance:
        if not (re.search('imp', sheet.name) and re.search('dep', sheet.name)):
            continue
        df = sheet.copy()
        one_bank_df = df.reset_index()[df.reset_index()['Bank'] == bank]
        mydict = {}
        for service in services:
            var = np.sum(one_bank_df[service])
            mydict[service] = var
        if re.search('min', sheet.name):
            scope_3_min_values = mydict
        if re.search('mean', sheet.name):
            scope_3_mean_values = mydict
        if re.search('max', sheet.name):
            scope_3_max_values = mydict

    # scope 3
    scope_3_mean = np.array(list(scope_3_mean_values.values()))
    scope_3_min = np.array(list(scope_3_min_values.values()))
    scope_3_max = np.array(list(scope_3_max_values.values()))

    lower_err_scope_3 = (scope_3_mean) - (scope_3_min)
    higher_err_scope_3 = (scope_3_max) - (scope_3_mean)

    asymetric_error_scope_3 = np.array(list(zip(lower_err_scope_3, higher_err_scope_3))).T

    ax.bar(X_axis + 0.225, scope_3_mean_values.values(), 0.45, label=r'$\mu_{U}$')
    ax.errorbar(X_axis + 0.225, scope_3_mean_values.values(), yerr=asymetric_error_scope_3, fmt='ro')
    # for item in ([ax.title, ax.xaxis.label] +
    #              ax.get_xticklabels() ):
    #     item.set_fontsize(20)
    ax.legend()
    ax.set_title(f'{bank} Impact Feedback Intensity for Direct Operations and Upstream Supply Chain')
    ax.set_xticks(X_axis, services, rotation=45, ha='right')
# plt.tight_layout()
# plt.savefig(f'{value_at_risk_figure_saving_path}/Finance Value at Risk for Banks with Error Bars Percentage')
# plt.show()
# plt.close()

# compare with system-level --> see if any different --> that might be what you need for -->
system_total = financial_data_df['EUR m adjusted'].sum()
scope_1_var_finance_region_system = []
scope_3_var_finance_region_system = []
# scope 1
for score in scope_1_var_finance_region_abs:
    df = score.copy()
    score_name = score.name
    prop_df = df.reset_index().drop(columns='Bank').groupby('region').sum()
    prop_df = (prop_df / system_total) * 100
    prop_df.name = score_name
    scope_1_var_finance_region_system.append(prop_df)
# scope 3
for score in scope_3_var_finance_abs:
    df = score.copy()
    score_name = score.name
    prop_df = df.reset_index().drop(columns=['Bank', 'Code']).groupby('region').sum()
    prop_df = (prop_df / system_total) * 100
    prop_df.name = score_name
    scope_3_var_finance_region_system.append(prop_df)

# calculate the system biting itself in the ass compared to banks
stats_test_df_scp1_vs_scp3_system = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=services)
scope_1_vs_3_significance_system = pd.DataFrame(columns=services, index=['comparison'])

scope_3_combo_mean_one_bank = scope_3_var_finance_region_system[1].reset_index()

scope_1_combo_mean_one_bank = scope_1_var_finance_region_system[1].reset_index()

for service in services:
    if (((scope_3_combo_mean_one_bank[service].sum() == 0) and (scope_1_combo_mean_one_bank[service].sum() == 0))):
        continue

    scope_3_combo_mean_one_bank_one_service = scope_3_combo_mean_one_bank[scope_3_combo_mean_one_bank[service] != 0]

    results = stats.wilcoxon(scope_1_combo_mean_one_bank[f'{service}'],
                             scope_3_combo_mean_one_bank[f'{service}'], alternative="greater", method="exact")
    stats_test_df_scp1_vs_scp3_system.loc[service]['statistic'] = results.statistic
    stats_test_df_scp1_vs_scp3_system.loc[service]['p-value'] = results.pvalue
    # stats_test_df_scp1_vs_scp3_system.loc[service]['z'] = results.zstatistic

    if results[1] > 0.05:
        scope_1_vs_3_significance_system[service] = "NS"
    if results[1] < 0.05 and results[1] > 0.01:
        scope_1_vs_3_significance_system[service]['comparison'] = "*"
    if results[1] <= 0.01 and results[1] > 0.005:
        scope_1_vs_3_significance_system[service]['comparison'] = "**"
    if results[1] <= 0.005:
        scope_1_vs_3_significance_system[service]['comparison'] = "***"

stats_test_df_scp1_vs_scp3_system.to_csv(
    f'{value_at_risk_sig_saving_path}/System Finance Scope 1 vs Scope 3 Statistics.csv')
scope_1_vs_3_significance_system.T.to_csv(
    f'{value_at_risk_sig_saving_path}/System Finance Scope 1 vs Scope 3 Significance.csv')


# compare system-level to each bank for overlap

scope_1_significance_system_vs_bank = pd.DataFrame(columns=services, index=banks)
scope_3_significance_system_vs_bank = pd.DataFrame(columns=services, index=banks)
stats_test_df_scp1_system_vs_bank = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=index)
stats_test_df_scp3_system_vs_bank = pd.DataFrame(columns=['statistic', 'p-value', 'z'], index=index)

# scope 1
scope_1_combo_mean_one_bank_system = scope_1_var_finance_region_system[1].reset_index()

for bank in banks:

    scope_1_combo_mean_one_bank = scope_1_var_finance_region[1].reset_index()[
        scope_1_var_finance_region[1].reset_index()['Bank'] == bank]

    for service in services:
        if (((scope_1_combo_mean_one_bank[service].sum() == 0) and (
                scope_1_combo_mean_one_bank_system[service].sum() == 0))):
            continue

        # compare scope 1 vs scope 1 system
        results = stats.wilcoxon(scope_1_combo_mean_one_bank[f'{service}'], scope_1_combo_mean_one_bank_system[service],
                                 alternative="less", method="approx")

        stats_test_df_scp1_system_vs_bank.loc[bank, service]['statistic'] = results.statistic
        stats_test_df_scp1_system_vs_bank.loc[bank, service]['p-value'] = results.pvalue
        stats_test_df_scp1_system_vs_bank.loc[bank, service]['z'] = results.zstatistic

        if results[1] > 0.05:
            scope_1_significance_system_vs_bank[service][bank] = "NS"
        if results[1] < 0.05 and results[1] > 0.01:
            scope_1_significance_system_vs_bank[service][bank] = "*"
        if results[1] <= 0.01 and results[1] > 0.005:
            scope_1_significance_system_vs_bank[service][bank] = "**"
        if results[1] <= 0.005:
            scope_1_significance_system_vs_bank[service][bank] = "***"

    print(f"{bank} done")

stats_test_df_scp1_system_vs_bank.to_csv(f'{value_at_risk_sig_saving_path}/System vs Finance Scope 1 Statistics.csv')
scope_1_significance_system_vs_bank.T.to_csv(
    f'{value_at_risk_sig_saving_path}/System vs Finance Scope 1 Significance.csv')

# scope 3
scope_3_combo_mean_one_bank_system = scope_3_var_finance_region_system[1].reset_index()

for bank in banks:

    scope_3_combo_mean_one_bank = scope_3_var_finance_region[1].reset_index()[
        scope_3_var_finance_region[1].reset_index()['Bank'] == bank]

    for service in services:
        if (((scope_3_combo_mean_one_bank[service].sum() == 0) and (
                scope_3_combo_mean_one_bank_system[service].sum() == 0))):
            continue

        # compare scope 1 vs scope 1 system
        results = stats.wilcoxon(scope_3_combo_mean_one_bank[f'{service}'], scope_3_combo_mean_one_bank_system[service],
                                 alternative="less", method="approx")

        stats_test_df_scp3_system_vs_bank.loc[bank, service]['statistic'] = results.statistic
        stats_test_df_scp3_system_vs_bank.loc[bank, service]['p-value'] = results.pvalue
        stats_test_df_scp3_system_vs_bank.loc[bank, service]['z'] = results.zstatistic

        if results[1] > 0.05:
            scope_3_significance_system_vs_bank[service][bank] = "NS"
        if results[1] < 0.05 and results[1] > 0.01:
            scope_3_significance_system_vs_bank[service][bank] = "*"
        if results[1] <= 0.01 and results[1] > 0.005:
            scope_3_significance_system_vs_bank[service][bank] = "**"
        if results[1] <= 0.005:
            scope_3_significance_system_vs_bank[service][bank] = "***"

    print(f"{bank} done")

stats_test_df_scp3_system_vs_bank.to_csv(f'{value_at_risk_sig_saving_path}/System vs Finance Scope 3 Statistics.csv')
scope_3_significance_system_vs_bank.T.to_csv(
    f'{value_at_risk_sig_saving_path}/System vs Finance Scope 3 Significance.csv')

# plot a bar chart
# var finance
# plt.figure(figsize=(20,20))

# i = 0
i = i + 1
ax = plt.subplot(4, 2, i, sharey=ax)
for sheet in scope_1_var_finance_region_system:
    df = sheet.copy()
    one_bank_df = df.reset_index()
    mydict = {}
    for service in services:
        var = np.sum(one_bank_df[service])
        mydict[service] = var
    if re.search('min', sheet.name):
        scope_1_min_values = mydict
    if re.search('mean', sheet.name):
        scope_1_mean_values = mydict
    if re.search('max', sheet.name):
        scope_1_max_values = mydict

X_axis = np.arange(len(services))

# scope 1
scope_1_mean = np.array(list(scope_1_mean_values.values()))
scope_1_min = np.array(list(scope_1_min_values.values()))
scope_1_max = np.array(list(scope_1_max_values.values()))

lower_err_scope_1 = (scope_1_mean) - (scope_1_min)
higher_err_scope_1 = (scope_1_max) - (scope_1_mean)

asymetric_error_scope_1 = np.array(list(zip(lower_err_scope_1, higher_err_scope_1))).T

ax.bar(X_axis - 0.225, scope_1_mean_values.values(), 0.45, label=r'$\mu_{D}$')
ax.errorbar(X_axis - 0.225, scope_1_mean_values.values(), yerr=asymetric_error_scope_1, fmt='ro')

for sheet in scope_3_var_finance_region_system:
    if not (re.search('imp', sheet.name) and re.search('dep', sheet.name)):
        continue
    df = sheet.copy()
    one_bank_df = df.reset_index()
    mydict = {}
    for service in services:
        var = np.sum(one_bank_df[service])
        mydict[service] = var
    if re.search('min', sheet.name):
        scope_3_min_values = mydict
    if re.search('mean', sheet.name):
        scope_3_mean_values = mydict
    if re.search('max', sheet.name):
        scope_3_max_values = mydict

# scope 3
scope_3_mean = np.array(list(scope_3_mean_values.values()))
scope_3_min = np.array(list(scope_3_min_values.values()))
scope_3_max = np.array(list(scope_3_max_values.values()))

lower_err_scope_3 = (scope_3_mean) - (scope_3_min)
higher_err_scope_3 = (scope_3_max) - (scope_3_mean)

asymetric_error_scope_3 = np.array(list(zip(lower_err_scope_3, higher_err_scope_3))).T

ax.bar(X_axis + 0.225, scope_3_mean_values.values(), 0.45, label=r'$\mu_{U}$')
ax.errorbar(X_axis + 0.225, scope_3_mean_values.values(), yerr=asymetric_error_scope_3, fmt='ro')
# for item in ([ax.title, ax.xaxis.label] +
#              ax.get_xticklabels()):
#     item.set_fontsize(20)

ax.legend()
ax.set_xticks(X_axis, services, rotation=45, ha='right')
ax.set_title(f' System-level Impact Feedback Intensity for Direction Operations and Upstream Supply Chain')
plt.tight_layout()
plt.savefig(f'{value_at_risk_figure_saving_path}/System Finance Value at Risk for Banks with Error Bars Percentage')
plt.show()
plt.close()


colors = sns.color_palette("Reds", as_cmap=True)

# system level
# plot sector heatmap for scope 1 and scope 3 for impact, and dependency
scores_list = []
# scope 1
imp_dep_bank_scp_1 = scope_1_var_finance[1].reset_index().drop(columns=['Bank', 'region']).groupby(['Code']).sum()
imp_dep_bank_scp_1 = imp_dep_bank_scp_1.reset_index().rename(columns={'Code': 'Sector'}).set_index(['Sector'])
imp_dep_bank_scp_1.name = 'Direct Operations'
scores_list.append(imp_dep_bank_scp_1)
# scope 3
imp_dep_bank_scp_3 = scope_3_var_finance[1].reset_index().drop(columns=['Bank', 'region']).groupby(['Code']).sum()
imp_dep_bank_scp_3 = imp_dep_bank_scp_3.reset_index().rename(columns={'Code': 'Sector'}).set_index(['Sector'])
imp_dep_bank_scp_3.name = 'Upstream Supply Chain'
scores_list.append(imp_dep_bank_scp_3)

# plot a heatmap for each
i = 1
plt.figure(figsize=(20, 20))
for score in scores_list:
    ax = plt.subplot(2, 2, i)
    color_scheme = colors
    # if i <= 3:
    #     sns.heatmap(score, ax=ax, cmap=color_scheme, xticklabels=False)
    # else:
    sns.heatmap(score, ax=ax, cmap=color_scheme, xticklabels=False)
    ax.set_title(f'{score.name}')
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(20)
    i = i + 1
# plt.suptitle(f'System-level Impact Feedback Intensity at the Sectoral Level', y=0.99)
# plt.tight_layout()
# plt.savefig(f'{value_at_risk_figure_saving_path}/Sector/System Sector Percentage Value at Risk')
# plt.show()

# system level
score_list = []

# scope 1 and scope 3
# overlap
colors = sns.color_palette("Reds", as_cmap=True)

scope_1_overlap_one_bank = scope_1_var_finance[1].reset_index().drop(columns=['Bank', 'Code']).groupby('region').sum()
scope_1_overlap_one_bank = scope_1_overlap_one_bank.reset_index().rename(columns={'region': 'Region'}).set_index(
    ['Region'])
scope_1_overlap_one_bank.name = 'System-level Direct Operations'
scope_3_overlap_one_bank = scope_3_var_finance_rows[1].reset_index().drop(columns=['Bank']).groupby('region').sum()
scope_3_overlap_one_bank = scope_3_overlap_one_bank.reset_index().rename(columns={'region': 'Region'}).set_index(
    ['Region'])
scope_3_overlap_one_bank.name = 'System-level Upstream Supply Chain'


score_list.append(scope_1_overlap_one_bank)
score_list.append(scope_3_overlap_one_bank)

# plt.figure(figsize=(20, 20))
# i = 1
for score in score_list:
    ax = plt.subplot(2, 2, i)

    # ax.set_title(f'System {score.name}')
    # if (i < 4):
    #     sns.heatmap(score.T, cmap=colors, ax=ax, xticklabels=False)
    # else:
    sns.heatmap(score, cmap=colors, ax=ax, xticklabels=True)
    i = i + 1
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels()):
        item.set_fontsize(20)
# plt.suptitle(f'System-level Impact Feedback Intensity at the Country and Sectoral Level', y=0.99)
plt.tight_layout()
plt.savefig(f'{value_at_risk_figure_saving_path}/System VaR Country Level Heatmap')
plt.show()

print("done")

# plot combined region heatmap at country level and sectoral level
# bank level
i = 1
plt.figure(figsize=(20, 20))
for bank in banks:
    # plot sector heatmap for scope 1 and scope 3 for impact, and dependency
    scores_list = []
    # scope 1
    imp_dep_bank_scp_1 = scope_1_var_finance[1].reset_index()[
        scope_1_var_finance[1].reset_index()['Bank'] == bank].drop(columns=['Bank', 'region']).groupby(['Code']).sum()
    imp_dep_bank_scp_1 = imp_dep_bank_scp_1.reset_index().rename(columns={'Code': 'Sector'}).set_index(['Sector'])
    imp_dep_bank_scp_1.name = f'Direct Operations'
    scores_list.append(imp_dep_bank_scp_1)
    # scope 3
    imp_dep_bank_scp_3 = scope_3_var_finance[1].reset_index()[
        scope_3_var_finance[1].reset_index()['Bank'] == bank].drop(columns=['Bank', 'region']).groupby(
        ['Code']).sum()
    imp_dep_bank_scp_3 = imp_dep_bank_scp_3.reset_index().rename(columns={'Code': 'Sector'}).set_index(['Sector'])
    imp_dep_bank_scp_3.name = f'Upstream Supply Chain'
    scores_list.append(imp_dep_bank_scp_3)

    # plot a heatmap for each
    for score in scores_list:
        ax = plt.subplot(7, 2, i)
        color_scheme = colors
        if i < 13:
            sns.heatmap(score, ax=ax, cmap=color_scheme, xticklabels=False)
        else:
            sns.heatmap(score, ax=ax, cmap=color_scheme, xticklabels=True)
        if i == 1 or i == 2:
            ax.set_title(f'{score.name}')
        i = i + 1
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                     ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(17)
        ax.set_ylabel(bank)
# plt.suptitle(f'Sector Impact Feedback Intensity Metric', y=0.99)
plt.tight_layout()
plt.savefig(f'{value_at_risk_figure_saving_path}/Sector/Bank-level Sector Percentage Value at Risk')
plt.show()

plt.figure(figsize=(20, 20))
i = 1
for bank in banks:
    score_list = []
    # scope 1 and scope 3
    # overlap
    scope_1_overlap_one_bank = scope_1_var_finance[1].reset_index()[
        scope_1_var_finance[1].reset_index()['Bank'] == bank].drop(columns=['Bank', 'Code']).groupby('region').sum()
    scope_1_overlap_one_bank = scope_1_overlap_one_bank.reset_index().rename(columns={'region': 'Region'}).set_index(
        ['Region'])
    scope_1_overlap_one_bank.name = f'Direct Operations'
    scope_3_overlap_one_bank = scope_3_var_finance_rows[1].reset_index()[
        scope_3_var_finance_rows[1].reset_index()['Bank'] == bank].drop(columns=['Bank']).groupby('region').sum()
    scope_3_overlap_one_bank = scope_3_overlap_one_bank.reset_index().rename(columns={'region': 'Region'}).set_index(
        ['Region'])
    scope_3_overlap_one_bank.name = f'Upstream Supply Chain'


    score_list.append(scope_1_overlap_one_bank)
    score_list.append(scope_3_overlap_one_bank)

    for score in score_list:
        ax = plt.subplot(7, 2, i)

        if i < 13:
            sns.heatmap(score, ax=ax, cmap=color_scheme, xticklabels=False)
        else:
            sns.heatmap(score, ax=ax, cmap=color_scheme, xticklabels=True)
        if i == 1 or i == 2:
            ax.set_title(f'{score.name}')
        i = i + 1
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                     ax.get_xticklabels()):
            item.set_fontsize(17)
        ax.set_ylabel(bank)
plt.tight_layout()
# plt.savefig(f'{value_at_risk_figure_saving_path}/{bank} VaR Sector and Country Level Heatmap')
plt.show()

print('Done')






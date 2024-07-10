# create a function to get the bank and ecosystem services as indices for each value at risk df to look at impacts for each bank
# use when it is ecosystem service_bank as the column titles
import pandas as pd
import re
import numpy as np


def index_transform(df_list):
    new_df_list = []
    for sheet in df_list:
        copy = sheet.copy()
        name = sheet.name
        # print(name)
        if (copy.columns[0] == 'indout'):
            copy.rename(columns={'indout': 'indout_indout'}, inplace=True)
        if ('x_adj' in copy.columns):
            copy.drop(columns='x_adj', inplace=True)
        copy = copy.T
        copy['Bank'] = [x.split("_")[1] for x in copy.index]
        copy['service'] = [x.split("_")[0] for x in copy.index]
        copy = copy.set_index(['Bank', 'service'])
        copy = copy.T
        copy.name = name
        new_df_list.append(copy)
    return new_df_list

def proportion_transform(score_df, finance_values_df):
    df = score_df.reset_index().copy()
    df_2 = finance_values_df.reset_index().copy()

    finance_score_merge_df = df.merge(df_2, right_on=['Bank'], left_on=['Bank'], how='left').set_index(
        ['Bank', 'region', 'Code'])
    proportional_score_df = finance_score_merge_df.iloc[:, 0:(finance_score_merge_df.shape[1] - 1)].div(
        finance_score_merge_df.iloc[:,(finance_score_merge_df.shape[1]-1)], axis=0)
    proportional_score_df = proportional_score_df * 100



    return proportional_score_df


def proportion_transform_mul(score_df, finance_values_df, type, fin_v_EXIO):
    if type != 'region_only' and type != 'code_only' and type != 'region_code':
        print("ERROR: type must be region_only, code_only or region_code")
        return
    if fin_v_EXIO != 'fin' and fin_v_EXIO != 'EXIO':
        print("ERROR: fin_v_EXIO must be fin or EXIO")

    if fin_v_EXIO == 'fin':
        df = score_df.reset_index().copy()
        df_2 = finance_values_df.reset_index().copy()

        if (type == 'region_code'):
            finance_score_merge_df = df.merge(df_2, right_on=['Bank'], left_on=['Bank'], how='left').set_index(
                ['Bank', 'region', 'Code'])
        if (type == 'code_only'):
            finance_score_merge_df = df.merge(df_2, right_on=['Bank'], left_on=['Bank'], how='left').set_index(
                ['Bank', 'Code'])
        if (type == 'region_only'):
            finance_score_merge_df = df.merge(df_2, right_on=['Bank'], left_on=['Bank'], how='left').set_index(
                ['Bank', 'region'])

        proportional_score_df = finance_score_merge_df.iloc[:, 0:(finance_score_merge_df.shape[1] - 1)].div(
            finance_score_merge_df.iloc[:,(finance_score_merge_df.shape[1]-1)], axis=0)
        proportional_score_df = proportional_score_df * 100

    if fin_v_EXIO == 'EXIO':
        df = score_df.copy()
        df_2 = finance_values_df.reset_index().copy()
        df_3 = df_2.drop(columns='Code').groupby('region').sum().reset_index()
        total = finance_values_df.sum()


        if (type == 'region_code'):
            indout_score_merge_df = df.reset_index().merge(df_3, right_on=['region'], left_on=['region'], how='left').set_index(
                ['region', 'Code'])
        if (type == 'code_only'):

            df_2 = finance_values_df.reset_index().copy()
            indout_score_merge_df = df.reset_index().merge(df_2, right_on=['Code'], left_on=['Code'], how='left').set_index(
                ['Code'])
        if (type == 'region_only'):
            indout_score_merge_df = df.reset_index().merge(df_3, right_on=['region'], left_on=['region'], how='left').set_index(
                ['region'])

        # proportional_score_df = indout_score_merge_df.iloc[:, 0:(indout_score_merge_df.shape[1] - 1)].div(
        #     indout_score_merge_df.iloc[:, (indout_score_merge_df.shape[1] - 1)], axis=0)
        # proportional_score_df = proportional_score_df * 100

        proportional_score_df = (df /total['indout']) * 100



    return proportional_score_df


# add the list of row data frames
def proportion_transform_rows(row_score_list, finance_values_df):
    df_list = index_transform(row_score_list)
    financial_values_copy = finance_values_df.copy()
    arrays = [["EUR m adjusted"], ["EUR m adjusted"]]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples, names=["first", "second"])
    financial_values_copy_df = pd.DataFrame(financial_values_copy.values, index=financial_values_copy.index, columns = index)

    proportional_score_rows_list = []
    for score in df_list:
        df = score.T.copy()
        name = score.name
        finance_score_merge_df = df.reset_index().merge(financial_values_copy_df.reset_index(), right_on=['Bank'], left_on=['Bank'], how='left').set_index(['Bank', 'service'])
        proportional_score_df = finance_score_merge_df.iloc[:,0:(finance_score_merge_df.shape[1]-1)].div(finance_score_merge_df.iloc[:,(finance_score_merge_df.shape[1]-1)], axis=0)
        proportional_score_df = proportional_score_df * 100
        proportional_score_rows_df = proportional_score_df.T
        proportional_score_rows_df.name = name
        proportional_score_rows_list.append(proportional_score_rows_df)

    return proportional_score_rows_list

def aggregate_to_region_service(score_list, how):
    return_list = []
    if isinstance(score_list, pd.DataFrame):
        df = score_list.copy()
        name = score_list.name
        if how == 'sum':
            if 'Bank' in df.reset_index().columns:
                df = df.reset_index().drop(columns='Code').groupby(['Bank', 'region']).sum()
            else:
                df = df.reset_index().drop(columns='Code').groupby(['region']).sum()
        if how == 'mean':
            if 'Bank' in df.reset_index().columns:
                df = df.reset_index().drop(columns='Code').groupby(['Bank', 'region']).mean()
            else:
                df = df.reset_index().drop(columns='Code').groupby(['region']).mean()
        df.name = name
        return df

    for score in score_list:
        df = score.copy()
        name = score.name
        if how == 'sum':
            if 'Bank' in df.reset_index().columns:
                df = df.reset_index().drop(columns='Code').groupby(['Bank', 'region']).sum()
            else:
                df = df.reset_index().drop(columns='Code').groupby(['region']).sum()
        if how == 'mean':
            if 'Bank' in df.reset_index().columns:
                df = df.reset_index().drop(columns='Code').groupby(['Bank', 'region']).mean()
            else:
                df = df.reset_index().drop(columns='Code').groupby(['region']).mean()
        df.name = name
        return_list.append(df)
    return return_list

def dependency_minus_impact_mean_only(score_list, threshold):
    services = score_list[0].columns.tolist()
    # find overlap between impact and dependency
    for imp_score in score_list:
        if not re.search('imp', imp_score.name):
            continue
        if not re.search('mean', imp_score.name):
            continue
        imp_df = (imp_score.copy()
                  .replace(0.0, np.nan))
        imp_df = imp_df.mask(imp_df < threshold)
        imp_name = imp_score.name
        combo_df = pd.DataFrame(index=imp_score.index, columns=imp_score.columns)
        for dep_score in score_list:
            if not re.search('dep', dep_score.name):
                continue
            if not re.search('mean', dep_score.name):
                continue
            dep_df = (dep_score.copy()
                      .replace(0.0, np.nan))
            dep_df = dep_df.mask(dep_df < threshold)
            dep_name = dep_score.name
            for service in services:
                combo_df[service] = dep_df[service] - imp_df[service]
            # combo_df = combo_df.copy().replace(0.0, np.nan)
            combo_df.name = f'{dep_name} minus {imp_name}'

    return combo_df, imp_df, dep_df

def dependency_minus_impact_scope_1_and_3(scope_1_list, scope_3_list, threshold):
    services = scope_1_list[0].columns.tolist()
    # add the scope 1 and 3 impact mean
    scope_13_impact_df = pd.DataFrame(index=scope_3_list[0].index, columns=scope_3_list[0].columns)
    for scope_1_score in scope_1_list:
        if not re.search('imp', scope_1_score.name):
            continue
        if not re.search('mean', scope_1_score.name):
            continue
        scope_1_imp_df = scope_1_score.copy()
        for scope_3_score in scope_3_list:
            if not re.search('imp', scope_3_score.name):
                continue
            if not re.search('mean', scope_3_score.name):
                continue
            scope_3_imp_df = scope_3_score.copy()
            for service in services:
                scope_13_impact_df[service] = scope_1_imp_df[service] + scope_3_imp_df[service]
        # add the scope 1 and 3 dependency mean
    # add the scope 1 and 3 impact mean
    scope_13_dep_df = pd.DataFrame(index=scope_3_list[0].index, columns=scope_3_list[0].columns)
    for scope_1_score in scope_1_list:
        if not re.search('dep', scope_1_score.name):
            continue
        if not re.search('mean', scope_1_score.name):
            continue
        scope_1_dep_df = scope_1_score.copy()
        for scope_3_score in scope_3_list:
            if not re.search('dep', scope_3_score.name):
                continue
            if not re.search('mean', scope_3_score.name):
                continue
            scope_3_dep_df = scope_3_score.copy()
            for service in services:
                scope_13_dep_df[service] = scope_1_dep_df[service] + scope_3_dep_df[service]

    # calculate the combined impact minus dependency
    imp_df = scope_13_impact_df.mask(scope_13_impact_df < threshold)
    imp_df.name = 'scope 13 impact'
    dep_df = scope_13_dep_df.mask(scope_13_dep_df < threshold)
    dep_df.name = 'scope 13 dependency'

    combo_df = pd.DataFrame(index=imp_df.index, columns=imp_df.columns)
    for service in services:
        combo_df[service] = dep_df[service] - imp_df[service]
    combo_df.name = f'combo'

    return combo_df, imp_df, dep_df

def dependency_mul_impact_mean_only(score_list, threshold):
    services = score_list[0].columns.tolist()
    # find overlap between impact and dependency
    for imp_score in score_list:
        if not re.search('imp', imp_score.name):
            continue
        if not re.search('mean', imp_score.name):
            continue
        imp_df = (imp_score.copy()
                  .replace(0.0, np.nan))
        imp_df = imp_df.mask(imp_df < threshold)
        imp_name = imp_score.name
        combo_df = pd.DataFrame(index=imp_score.index, columns=imp_score.columns)
        for dep_score in score_list:
            if not re.search('dep', dep_score.name):
                continue
            if not re.search('mean', dep_score.name):
                continue
            dep_df = (dep_score.copy()
                      .replace(0.0, np.nan))
            dep_df = dep_df.mask(dep_df < threshold)
            dep_name = dep_score.name
            for service in services:
                combo_df[service] = dep_df[service] * imp_df[service]
            # combo_df = combo_df.copy().replace(0.0, np.nan)
            combo_df.name = f'{dep_name} minus {imp_name}'

    return combo_df, imp_df, dep_df

def anonymize_banks(score_list, anonymized_names, type):
    bank_names = np.unique(score_list[0].reset_index()['Bank']).tolist()
    new_score_list = []
    for score in score_list:
        i = 0
        df = score.reset_index()
        name = score.name
        for bank in bank_names:
            df = df.replace({f'{bank}':f'{anonymized_names[i]}'})
            i = i + 1
        if type == 'region_code':
            df = df.set_index(['Bank','region', 'Code'])
        if type == 'region_only':
            df = df.set_index(['Bank', 'region'])
        if type == 'code_only':
            df = df.set_index(['Bank', 'Code'])
        df.name = name
        new_score_list.append(df)
    return new_score_list

def add_headers(
    fig,
    *,
    row_headers=None,
    col_headers=None,
    row_pad=1,
    col_pad=5,
    rotate_row_headers=True,
    **text_kwargs
):
    # Based on https://stackoverflow.com/a/25814386

    axes = fig.get_axes()

    for ax in axes:
        sbs = ax.get_subplotspec()

        # Putting headers on cols
        if (col_headers is not None) and sbs.is_first_row():
            ax.annotate(
                col_headers[sbs.colspan.start],
                xy=(0.5, 1),
                xytext=(0, col_pad),
                xycoords="axes fraction",
                textcoords="offset points",
                ha="center",
                va="baseline",
                **text_kwargs,
            )

        # Putting headers on rows
        if (row_headers is not None) and sbs.is_first_col():
            ax.annotate(
                row_headers[sbs.rowspan.start],
                xy=(0, 0.5),
                xytext=(-ax.yaxis.labelpad - row_pad, 0),
                xycoords=ax.yaxis.label,
                textcoords="offset points",
                ha="right",
                va="center",
                rotation=rotate_row_headers * 90,
                **text_kwargs,
            )
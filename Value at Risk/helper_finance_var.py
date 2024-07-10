import numpy as np
import pandas as pd
import re


def finance_var_calc(score, finance_data_df, type, L_min_I, folder):
    """
    :param score: a dataframe of the score that you want to use to calculate the value at risk
    :param finance_df: the finance of the bank you want to calculate the value at risk for
    :param type: the type of score (whether it is a scope 1 (only Code) or whether it contains region as well
    :param folder: either 'Multipled/' for the combined multipled or '' for imp or dep
    :return: a list of dataframes that correspond to the finance_var and the rows for the finance_var plus the scores
    """
    if type != 'region_code' and type != 'code_only' and type != 'region_only':
        print('ERROR: Type must be "region_code" or "code_only" or "region_only"')
        return

    storing_list = []
    ### calculate overlined((L -1)), relative impact dependency matrix
    L_min_I_numpy = L_min_I.to_numpy(dtype=float)
    col_sums = np.sum(L_min_I, axis=0)
    col_sums = col_sums.to_numpy(dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        rel_imp_array = np.where(col_sums == 0, 0, np.divide(L_min_I_numpy, col_sums[np.newaxis, :]))

    # get the weights for the contribution of each sector,region pair to the supply chain
    L_weights = pd.DataFrame(rel_imp_array, index=L_min_I.index, columns=L_min_I.columns)
    upstream_calc = L_weights.copy().reset_index()

    # multiply the weighted sum for Leontief by the impact region score (based on investment location)
    # plus the dependency score for the sector region L_weighted * (impact region) * (dependency sector)

    upstream_calc_format = upstream_calc.T.reset_index().T.rename(columns={0: 'region', 1: 'Code'})
    upstream_calc_format.loc['Code', 'region'] = 'region'
    upstream_calc_format.loc['Code', 'Code'] = 'Code'

    # get only the UK upstream supply chains
    upstream_calc_UK_format_shape = L_weights.T.reset_index()[L_weights.T.reset_index()['region'] == 'GB'].T
    upstream_calc_UK_format_shape_columns = upstream_calc_UK_format_shape.T.set_index(['region', 'Code']).T
    upstream_calc_UK_format = upstream_calc_UK_format_shape.reset_index().T.rename(columns={0: 'region', 1: 'Code'}).T
    upstream_calc_UK_format.loc['Code', 'region'] = 'region'
    upstream_calc_UK_format.loc['Code', 'Code'] = 'Code'

    # get only the international upstream supply chains
    upstream_calc_int_format_shape = L_weights.T.reset_index()[L_weights.T.reset_index()['region'] != 'GB'].T
    upstream_calc_int_format_shape_columns = upstream_calc_int_format_shape.T.set_index(['region', 'Code']).T
    upstream_calc_int_format = upstream_calc_int_format_shape.reset_index().T.rename(columns={0: 'region', 1: 'Code'}).T
    upstream_calc_int_format.loc['Code', 'region'] = 'region'
    upstream_calc_int_format.loc['Code', 'Code'] = 'Code'

    banks = np.unique(finance_data_df.reset_index()['Bank'])
    services = score.columns

    # for the storing the score-level scores
    imp_dep_compile_cols_df = pd.DataFrame(index=L_min_I.index)
    imp_dep_compile_rows_df = pd.DataFrame(index=L_min_I.index)
    # storing value at risk
    imp_dep_compile_cols_var_finance_df = pd.DataFrame(index=L_min_I.index)
    imp_dep_compile_rows_var_finance_df = pd.DataFrame(index=L_min_I.index)

    # storing score-level scores for UK only
    imp_dep_compile_cols_UK_df = pd.DataFrame(index=L_min_I.index)
    imp_dep_compile_rows_UK_df = pd.DataFrame(index=L_min_I.index)
    # storing value at risk
    imp_dep_compile_cols_var_finance_UK_df = pd.DataFrame(index=L_min_I.index)
    imp_dep_compile_rows_var_finance_UK_df = pd.DataFrame(index=L_min_I.index)

    # storing score-level scores for international only
    imp_dep_compile_cols_int_df = pd.DataFrame(index=L_min_I.index)
    imp_dep_compile_rows_int_df = pd.DataFrame(index=L_min_I.index)
    # storing value at risk
    imp_dep_compile_cols_var_finance_int_df = pd.DataFrame(index=L_min_I.index)
    imp_dep_compile_rows_var_finance_int_df = pd.DataFrame(index=L_min_I.index)

    # for storing the column sums for the score-level scores
    imp_dep_compile_cols_storing_df = pd.DataFrame(columns=services)
    # UK only
    imp_dep_compile_cols_storing_UK_df = pd.DataFrame(columns=services)
    # int only
    imp_dep_compile_cols_storing_int_df = pd.DataFrame(columns=services)

    # for storing the row sums for the score-level scores
    imp_dep_compile_rows_storing_df = pd.DataFrame(columns=services)
    # UK only
    imp_dep_compile_rows_storing_UK_df = pd.DataFrame(columns=services)
    # int only
    imp_dep_compile_rows_storing_int_df = pd.DataFrame(columns=services)

    # value at risk finance
    imp_dep_compile_cols_storing_var_finance_df = pd.DataFrame(columns=services)
    # UK only
    imp_dep_compile_cols_storing_var_finance_UK_df = pd.DataFrame(columns=services)
    # int only
    imp_dep_compile_cols_storing_var_finance_int_df = pd.DataFrame(columns=services)

    # value at risk finance rows
    imp_dep_compile_rows_storing_var_finance_df = pd.DataFrame(columns=services)
    # UK only
    imp_dep_compile_rows_storing_var_finance_UK_df = pd.DataFrame(columns=services)
    # int only
    imp_dep_compile_rows_storing_var_finance_int_df = pd.DataFrame(columns=services)



    # store score
    df = score.copy()
    score_name = score.name

    for bank in banks:
        print(bank)
        imp_dep_compile_cols_one_bank_df = imp_dep_compile_cols_df.copy()
        imp_dep_compile_cols_one_bank_df['Bank'] = [f'{bank}'] * imp_dep_compile_cols_df.shape[0]
        # UK only
        imp_dep_compile_cols_one_bank_UK_df = imp_dep_compile_cols_UK_df.copy()
        imp_dep_compile_cols_one_bank_UK_df['Bank'] = [f'{bank}'] * imp_dep_compile_cols_one_bank_UK_df.shape[0]
        # int only
        imp_dep_compile_cols_one_bank_int_df = imp_dep_compile_cols_int_df.copy()
        imp_dep_compile_cols_one_bank_int_df['Bank'] = [f'{bank}'] * imp_dep_compile_cols_one_bank_int_df.shape[0]

        # rows
        imp_dep_compile_rows_one_bank_df = imp_dep_compile_rows_df.copy()
        imp_dep_compile_rows_one_bank_df['Bank'] = [f'{bank}'] * imp_dep_compile_rows_df.shape[0]
        # UK only
        imp_dep_compile_rows_one_bank_UK_df = imp_dep_compile_rows_UK_df.copy()
        imp_dep_compile_rows_one_bank_UK_df['Bank'] = [f'{bank}'] * imp_dep_compile_rows_one_bank_UK_df.shape[0]
        # int only
        imp_dep_compile_rows_one_bank_int_df = imp_dep_compile_rows_int_df.copy()
        imp_dep_compile_rows_one_bank_int_df['Bank'] = [f'{bank}'] * imp_dep_compile_rows_one_bank_int_df.shape[0]

        # value at risk finance
        imp_dep_compile_cols_one_bank_var_finance_df = imp_dep_compile_cols_var_finance_df.copy()
        imp_dep_compile_cols_one_bank_var_finance_df['Bank'] = [f'{bank}'] * imp_dep_compile_cols_var_finance_df.shape[
            0]
        # UK only
        imp_dep_compile_cols_one_bank_var_finance_UK_df = imp_dep_compile_cols_var_finance_UK_df.copy()
        imp_dep_compile_cols_one_bank_var_finance_UK_df['Bank'] = [f'{bank}'] * \
                                                                  imp_dep_compile_cols_one_bank_var_finance_UK_df.shape[
                                                                      0]
        # int only
        imp_dep_compile_cols_one_bank_var_finance_int_df = imp_dep_compile_cols_var_finance_int_df.copy()
        imp_dep_compile_cols_one_bank_var_finance_int_df['Bank'] = [f'{bank}'] * \
                                                                   imp_dep_compile_cols_one_bank_var_finance_int_df.shape[
                                                                       0]

        # value at risk finance rows
        # value at risk finance
        imp_dep_compile_rows_one_bank_var_finance_df = imp_dep_compile_rows_var_finance_df.copy()
        imp_dep_compile_rows_one_bank_var_finance_df['Bank'] = [f'{bank}'] * imp_dep_compile_rows_var_finance_df.shape[
            0]
        # UK only
        imp_dep_compile_rows_one_bank_var_finance_UK_df = imp_dep_compile_rows_var_finance_UK_df.copy()
        imp_dep_compile_rows_one_bank_var_finance_UK_df['Bank'] = [f'{bank}'] * \
                                                                  imp_dep_compile_rows_one_bank_var_finance_UK_df.shape[
                                                                      0]
        # int only
        imp_dep_compile_rows_one_bank_var_finance_int_df = imp_dep_compile_rows_var_finance_int_df.copy()
        imp_dep_compile_rows_one_bank_var_finance_int_df['Bank'] = [f'{bank}'] * \
                                                                   imp_dep_compile_rows_one_bank_var_finance_int_df.shape[
                                                                       0]


        # get financial data for Bank
        bank_data_df = finance_data_df.reset_index()[finance_data_df.reset_index()['Bank'] == bank].set_index(
            ['region', 'Code'])
        # bank_data_df = bank_data_df['Proportion of Loans']
        full_index = pd.DataFrame(index=L_min_I.index)
        bank_data_df = bank_data_df.merge(full_index, how='right', right_index=True, left_index=True)
        bank_data_df = bank_data_df.fillna(0.0)
        # bank_data_df.drop(columns=['Bank', 'Total Loan', 'EUR m adjusted'], inplace=True)
        bank_data_dict = bank_data_df['Proportion of Loans'].to_dict()
        bank_data_absolute_dict = bank_data_df['EUR m adjusted'].to_dict()
        #
        #
        # UK only
        bank_data_UK_df = bank_data_df.reset_index()[bank_data_df.reset_index()['region'] == 'GB'].set_index(
            ['region', 'Code'])
        UK_index = pd.DataFrame(index=upstream_calc_UK_format_shape_columns.T.index)
        bank_data_UK_df = bank_data_UK_df.merge(UK_index, how='right', right_index=True, left_index=True)
        bank_data_UK_df = bank_data_UK_df.fillna(0.0)
        bank_data_UK_dict = bank_data_UK_df['Proportion of Loans'].to_dict()
        bank_data_absolute_UK_dict = bank_data_UK_df['EUR m adjusted'].to_dict()

        # International only
        bank_data_int_df = bank_data_df.reset_index()[bank_data_df.reset_index()['region'] != 'GB'].set_index(
            ['region', 'Code'])
        int_index = pd.DataFrame(index=upstream_calc_int_format_shape_columns.T.index)
        bank_data_int_df = bank_data_int_df.merge(int_index, how='right', right_index=True, left_index=True)
        bank_data_int_df = bank_data_int_df.fillna(0.0)
        bank_data_int_dict = bank_data_int_df['Proportion of Loans'].to_dict()
        bank_data_absolute_int_dict = bank_data_int_df['EUR m adjusted'].to_dict()

        for service in services:
            print(service)

            if type == 'region_code':
                # get the scores and the weighted L in one DF
                compiled_df = upstream_calc_format.merge(
                    df[service].reset_index(), how='outer', left_on=['region', 'Code'],
                    right_on=['region', 'Code'])
                compiled_df = compiled_df.fillna(0.0)

                # UK only
                compiled_UK_df = upstream_calc_UK_format.merge(
                    df[service].reset_index(), how='outer', left_on=['region', 'Code'],
                    right_on=['region', 'Code'])
                compiled_UK_df = compiled_UK_df.fillna(0.0)

                # int only
                compiled_int_df = upstream_calc_int_format.merge(
                    df[service].reset_index(), how='outer', left_on=['region', 'Code'],
                    right_on=['region', 'Code'])
                compiled_int_df = compiled_int_df.fillna(0.0)
            if type == 'code_only':
                # get the scores and the weighted L in one DF
                compiled_df = upstream_calc_format.merge(
                    df[service].reset_index(), how='outer', left_on=['Code'],
                    right_on=['Code'])
                compiled_df = compiled_df.fillna(0.0)

                # UK only
                compiled_UK_df = upstream_calc_UK_format.merge(
                    df[service].reset_index(), how='outer', left_on=['Code'],
                    right_on=['Code'])
                compiled_UK_df = compiled_UK_df.fillna(0.0)

                # int only
                compiled_int_df = upstream_calc_int_format.merge(
                    df[service].reset_index(), how='outer', left_on=[ 'Code'],
                    right_on=['Code'])
                compiled_int_df = compiled_int_df.fillna(0.0)
            if type == 'region_only':
                # get the scores and the weighted L in one DF
                compiled_df = upstream_calc_format.merge(
                    df[service].reset_index(), how='outer', left_on=['region'],
                    right_on=['region'])
                compiled_df = compiled_df.fillna(0.0)

                # UK only
                compiled_UK_df = upstream_calc_UK_format.merge(
                    df[service].reset_index(), how='outer', left_on=['region'],
                    right_on=['region'])
                compiled_UK_df = compiled_UK_df.fillna(0.0)

                # int only
                compiled_int_df = upstream_calc_int_format.merge(
                    df[service].reset_index(), how='outer', left_on=['region'],
                    right_on=['region'])
                compiled_int_df = compiled_int_df.fillna(0.0)

            # multiply the weighted average by the score
            compiled_df = compiled_df.set_index(['region', 'Code'])
            compiled_df = compiled_df.T.set_index(('region', 'Code')).T
            service_df = compiled_df[(0.0,0.0)]
            service_df = service_df[0:(L_min_I.shape[0])]
            service_df = service_df.astype(float)
            # calc_df = compiled_df.drop(columns=service).iloc[0:(L_min_I.shape[0]), 2:(L_min_I.shape[0] + 2)]
            # calc_df = calc_df.astype(float)
            calc_df = compiled_df.drop(columns =(0.0,0.0))
            calc_df = calc_df.astype(float)
            multiplied_df = np.multiply(calc_df.to_numpy(), service_df.to_numpy()[:, np.newaxis])
            imp_dep_compile_service_df = pd.DataFrame(multiplied_df, index=calc_df.index, columns=calc_df.columns)

            # UK only
            compiled_UK_df = compiled_UK_df.set_index(['region', 'Code'])
            compiled_UK_df = compiled_UK_df.T.set_index([('region', ''), ('region', 'Code')]).T
            calc_UK_df = compiled_UK_df.drop(columns=(0.0,0.0))
            calc_UK_df = calc_UK_df.astype(float)
            multiplied_df = np.multiply(calc_UK_df.to_numpy(), service_df.to_numpy()[:, np.newaxis])
            imp_dep_compile_service_UK_df = pd.DataFrame(multiplied_df, index=calc_UK_df.index,
                                                         columns=calc_UK_df.columns)

            # int only\
            compiled_int_df = compiled_int_df.set_index(['region', 'Code'])
            compiled_int_df = compiled_int_df.T.set_index([('region', ''), ('region', 'Code')]).T
            calc_int_df = compiled_int_df.drop(columns=(0.0,0.0))
            calc_int_df = calc_int_df.astype(float)
            multiplied_df = np.multiply(calc_int_df.to_numpy(), service_df.to_numpy()[:, np.newaxis])
            imp_dep_compile_service_int_df = pd.DataFrame(multiplied_df, index=calc_int_df.index,
                                                          columns=calc_int_df.columns)

            # multiply score by the absolute value of finance to sr to get VaR
            imp_dep_compile_service_finance_VaR_df = imp_dep_compile_service_df
            imp_dep_compile_service_finance_VaR_df = imp_dep_compile_service_finance_VaR_df.T.mul(
                bank_data_absolute_dict, axis='index').T
            # UK only
            imp_dep_compile_service_finance_VaR_UK_df = imp_dep_compile_service_UK_df
            imp_dep_compile_service_finance_VaR_UK_df = imp_dep_compile_service_finance_VaR_UK_df.T.mul(
                bank_data_absolute_UK_dict,
                axis='index').T
            # int only
            imp_dep_compile_service_finance_VaR_int_df = imp_dep_compile_service_int_df
            imp_dep_compile_service_finance_VaR_int_df = imp_dep_compile_service_finance_VaR_int_df.T.mul(
                bank_data_absolute_int_dict,
                axis='index').T

            # get the column sums for one bank for the scores
            imp_dep_compile_cols_one_bank_df[service] = imp_dep_compile_service_df.sum()
            # get the row sums for one bank and service into the greater the df
            imp_dep_compile_rows_one_bank_df[f'{service}'] = imp_dep_compile_service_df.T.sum()
            # UK only
            imp_dep_compile_cols_one_bank_UK_df[service] = imp_dep_compile_service_UK_df.sum()
            imp_dep_compile_rows_one_bank_UK_df[f'{service}'] = imp_dep_compile_service_UK_df.T.sum()
            # int only
            imp_dep_compile_cols_one_bank_int_df[service] = imp_dep_compile_service_int_df.sum()
            imp_dep_compile_rows_one_bank_int_df[f'{service}'] = imp_dep_compile_service_int_df.T.sum()

            # get column sums for one bank for the value at risk finance
            imp_dep_compile_cols_one_bank_var_finance_df[service] = imp_dep_compile_service_finance_VaR_df.sum()
            # get the row sums for one bank and service into the greater the df
            imp_dep_compile_rows_one_bank_var_finance_df[f'{service}'] = imp_dep_compile_service_finance_VaR_df.T.sum()
            # UK only
            imp_dep_compile_cols_one_bank_var_finance_UK_df[service] = imp_dep_compile_service_finance_VaR_UK_df.sum()
            imp_dep_compile_rows_one_bank_var_finance_UK_df[
                f'{service}'] = imp_dep_compile_service_finance_VaR_UK_df.T.sum()
            # int only
            imp_dep_compile_cols_one_bank_var_finance_int_df[service] = imp_dep_compile_service_finance_VaR_int_df.sum()
            imp_dep_compile_rows_one_bank_var_finance_int_df[
                f'{service}'] = imp_dep_compile_service_finance_VaR_int_df.T.sum()


        # load the services
        #cols
        imp_dep_compile_cols_storing_df = pd.concat(
            [imp_dep_compile_cols_storing_df.reset_index(), imp_dep_compile_cols_one_bank_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_cols_storing_df.columns:
            place_holder_df = imp_dep_compile_cols_storing_df.drop(columns='index')
            imp_dep_compile_cols_storing_df = place_holder_df.copy()

        # # UK only
        imp_dep_compile_cols_storing_UK_df = pd.concat(
            [imp_dep_compile_cols_storing_UK_df.reset_index(),
             imp_dep_compile_cols_one_bank_UK_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_cols_storing_UK_df.columns:
            place_holder_df = imp_dep_compile_cols_storing_UK_df.drop(columns='index')
            imp_dep_compile_cols_storing_UK_df = place_holder_df.copy()
        #
        # # int only
        imp_dep_compile_cols_storing_int_df = pd.concat(
            [imp_dep_compile_cols_storing_int_df.reset_index(),
             imp_dep_compile_cols_one_bank_int_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_cols_storing_int_df.columns:
            place_holder_df = imp_dep_compile_cols_storing_int_df.drop(columns='index')
            imp_dep_compile_cols_storing_int_df = place_holder_df.copy()

        # rows
        # load the services
        imp_dep_compile_rows_storing_df = pd.concat(
            [imp_dep_compile_rows_storing_df.reset_index(), imp_dep_compile_rows_one_bank_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_rows_storing_df.columns:
            place_holder_df = imp_dep_compile_rows_storing_df.drop(columns='index')
            imp_dep_compile_rows_storing_df = place_holder_df.copy()

        # # UK only
        imp_dep_compile_rows_storing_UK_df = pd.concat(
            [imp_dep_compile_rows_storing_UK_df.reset_index(),
             imp_dep_compile_rows_one_bank_UK_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_rows_storing_UK_df.columns:
            place_holder_df = imp_dep_compile_rows_storing_UK_df.drop(columns='index')
            imp_dep_compile_rows_storing_UK_df = place_holder_df.copy()
        #
        # # int only
        imp_dep_compile_rows_storing_int_df = pd.concat(
            [imp_dep_compile_rows_storing_int_df.reset_index(),
             imp_dep_compile_rows_one_bank_int_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_rows_storing_int_df.columns:
            place_holder_df = imp_dep_compile_rows_storing_int_df.drop(columns='index')
            imp_dep_compile_rows_storing_int_df = place_holder_df.copy()

        # var finance
        # load the services
        imp_dep_compile_cols_storing_var_finance_df = pd.concat(
            [imp_dep_compile_cols_storing_var_finance_df.reset_index(),
             imp_dep_compile_cols_one_bank_var_finance_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_cols_storing_var_finance_df.columns:
            place_holder_df = imp_dep_compile_cols_storing_var_finance_df.drop(columns='index')
            imp_dep_compile_cols_storing_var_finance_df = place_holder_df.copy()

            # UK only
        imp_dep_compile_cols_storing_var_finance_UK_df = pd.concat(
            [imp_dep_compile_cols_storing_var_finance_UK_df.reset_index(),
             imp_dep_compile_cols_one_bank_var_finance_UK_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_cols_storing_var_finance_UK_df.columns:
            place_holder_df = imp_dep_compile_cols_storing_var_finance_UK_df.drop(columns='index')
            imp_dep_compile_cols_storing_var_finance_UK_df = place_holder_df.copy()
        # int only
        imp_dep_compile_cols_storing_var_finance_int_df = pd.concat(
            [imp_dep_compile_cols_storing_var_finance_int_df.reset_index(),
             imp_dep_compile_cols_one_bank_var_finance_int_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_cols_storing_var_finance_int_df.columns:
            place_holder_df = imp_dep_compile_cols_storing_var_finance_int_df.drop(columns='index')
            imp_dep_compile_cols_storing_var_finance_int_df = place_holder_df.copy()


        # rows
        # var finance
        # load the services
        imp_dep_compile_rows_storing_var_finance_df = pd.concat(
            [imp_dep_compile_rows_storing_var_finance_df.reset_index(),
             imp_dep_compile_rows_one_bank_var_finance_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_rows_storing_var_finance_df.columns:
            place_holder_df = imp_dep_compile_rows_storing_var_finance_df.drop(columns='index')
            imp_dep_compile_rows_storing_var_finance_df = place_holder_df.copy()

            # UK only
        imp_dep_compile_rows_storing_var_finance_UK_df = pd.concat(
            [imp_dep_compile_rows_storing_var_finance_UK_df.reset_index(),
             imp_dep_compile_rows_one_bank_var_finance_UK_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_rows_storing_var_finance_UK_df.columns:
            place_holder_df = imp_dep_compile_rows_storing_var_finance_UK_df.drop(columns='index')
            imp_dep_compile_rows_storing_var_finance_UK_df = place_holder_df.copy()
        # int only
        imp_dep_compile_rows_storing_var_finance_int_df = pd.concat(
            [imp_dep_compile_rows_storing_var_finance_int_df.reset_index(),
             imp_dep_compile_rows_one_bank_var_finance_int_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_rows_storing_var_finance_int_df.columns:
            place_holder_df = imp_dep_compile_rows_storing_var_finance_int_df.drop(columns='index')
            imp_dep_compile_rows_storing_var_finance_int_df = place_holder_df.copy()


    # scores
    imp_dep_compile_cols_storing_df.name = f'{score_name} Score'
    imp_dep_compile_cols_storing_df.to_csv(f'../Data/Finance Scores/{folder}Both/{imp_dep_compile_cols_storing_df.name}.csv')
    storing_list.append(imp_dep_compile_cols_storing_df)
    imp_dep_compile_cols_storing_UK_df.name = f'{score_name} UK Score'
    imp_dep_compile_cols_storing_UK_df.to_csv(f'../Data/Finance Scores/{folder}UK Only/{imp_dep_compile_cols_storing_UK_df.name}.csv')
    storing_list.append(imp_dep_compile_cols_storing_UK_df)
    imp_dep_compile_cols_storing_int_df.name = f'{score_name} International Score'
    imp_dep_compile_cols_storing_int_df.to_csv(f'../Data/Finance Scores/{folder}International Only/{imp_dep_compile_cols_storing_int_df.name}.csv')
    storing_list.append(imp_dep_compile_cols_storing_int_df)

    # row scores
    imp_dep_compile_rows_storing_df.name = f'{score_name} Row Score'
    imp_dep_compile_rows_storing_df.to_csv(
        f'../Data/Finance Scores/{folder}Both/{imp_dep_compile_rows_storing_df.name}.csv')
    storing_list.append(imp_dep_compile_rows_storing_df)
    imp_dep_compile_rows_storing_UK_df.name = f'{score_name} UK Row Score'
    imp_dep_compile_rows_storing_UK_df.to_csv(
        f'../Data/Finance Scores/{folder}UK Only/{imp_dep_compile_rows_storing_UK_df.name}.csv')
    storing_list.append(imp_dep_compile_rows_storing_UK_df)
    imp_dep_compile_rows_storing_int_df.name = f'{score_name} International Row Score'
    imp_dep_compile_rows_storing_int_df.to_csv(
        f'../Data/Finance Scores/{folder}International Only/{imp_dep_compile_rows_storing_int_df.name}.csv')
    storing_list.append(imp_dep_compile_rows_storing_int_df)

    # cols
    imp_dep_compile_cols_storing_var_finance_df.name = f'{score_name} Both Finance VaR Source'
    imp_dep_compile_cols_storing_var_finance_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}Both/{imp_dep_compile_cols_storing_var_finance_df.name}.csv')
    storing_list.append(imp_dep_compile_cols_storing_var_finance_df)
    imp_dep_compile_cols_storing_var_finance_UK_df.name = f'{score_name} UK Finance VaR Source'
    imp_dep_compile_cols_storing_var_finance_UK_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}UK Only/{imp_dep_compile_cols_storing_var_finance_UK_df.name}.csv')
    storing_list.append(imp_dep_compile_cols_storing_var_finance_UK_df)
    imp_dep_compile_cols_storing_var_finance_int_df.name = f'{score_name} International Finance VaR Source'
    imp_dep_compile_cols_storing_var_finance_int_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}International Only/{imp_dep_compile_cols_storing_var_finance_int_df.name}.csv')
    storing_list.append(imp_dep_compile_cols_storing_var_finance_int_df)

    # rows
    imp_dep_compile_rows_storing_var_finance_df.name = f'{score_name} Both Finance VaR Value Chain'
    imp_dep_compile_rows_storing_var_finance_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}Both/{imp_dep_compile_rows_storing_var_finance_df.name}.csv')
    storing_list.append(imp_dep_compile_rows_storing_var_finance_df)
    imp_dep_compile_rows_storing_var_finance_UK_df.name = f'{score_name} UK Finance VaR Value Chain'
    imp_dep_compile_rows_storing_var_finance_UK_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}UK Only/{imp_dep_compile_rows_storing_var_finance_UK_df.name}.csv')
    storing_list.append(imp_dep_compile_rows_storing_var_finance_UK_df)
    imp_dep_compile_rows_storing_var_finance_int_df.name = f'{score_name} International Finance VaR Value Chain'
    imp_dep_compile_rows_storing_var_finance_int_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}International Only/{imp_dep_compile_rows_storing_var_finance_int_df.name}.csv')
    storing_list.append(imp_dep_compile_rows_storing_var_finance_int_df)

    return storing_list


def finance_var_calc_scope_3_combined(imp_score, dep_score, finance_data_df, type, L_min_I, folder):
    """
    :param score: a dataframe of the score that you want to use to calculate the value at risk
    :param finance_df: the finance of the bank you want to calculate the value at risk for
    :param type: the type of score (whether it is a scope 1 (only Code) or whether it contains region as well
    :param folder: either 'Multipled/' for the combined multipled or '' for imp or dep
    :return: a list of dataframes that correspond to the finance_var and the rows for the finance_var plus the scores
    """
    if type != 'region_code' and type != 'code_only' and type != 'region_only':
        print('ERROR: Type must be "region_code" or "code_only" or "region_only"')
        return

    storing_list = []
    ### calculate overlined((L -1)), relative impact dependency matrix
    L_min_I_numpy = L_min_I.to_numpy(dtype=float)
    col_sums = np.sum(L_min_I, axis=0)
    col_sums = col_sums.to_numpy(dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        rel_imp_array = np.where(col_sums == 0, 0, np.divide(L_min_I_numpy, col_sums[np.newaxis, :]))

    # get the weights for the contribution of each sector,region pair to the supply chain
    L_weights = pd.DataFrame(rel_imp_array, index=L_min_I.index, columns=L_min_I.columns)
    upstream_calc = L_weights.copy().reset_index()

    # multiply the weighted sum for Leontief by the impact region score (based on investment location)
    # plus the dependency score for the sector region L_weighted * (impact region) * (dependency sector)

    upstream_calc_format = upstream_calc.T.reset_index().T.rename(columns={0: 'region', 1: 'Code'})
    upstream_calc_format.loc['Code', 'region'] = 'region'
    upstream_calc_format.loc['Code', 'Code'] = 'Code'

    banks = np.unique(finance_data_df.reset_index()['Bank'])
    services = imp_score.columns

    # for the storing the score-level scores
    # both
    imp_dep_compile_cols_df = pd.DataFrame(index=L_min_I.index)
    imp_dep_compile_rows_df = pd.DataFrame(index=np.unique(L_min_I.reset_index()['region']))
    # imp
    imp_compile_cols_df = pd.DataFrame(index=L_min_I.index)
    imp_compile_rows_df = pd.DataFrame(index=L_min_I.index)
    # dep
    dep_compile_cols_df = pd.DataFrame(index=L_min_I.index)
    dep_compile_rows_df = pd.DataFrame(index=L_min_I.index)

    # storing value at risk
    # both
    imp_dep_compile_cols_var_finance_df = pd.DataFrame(index=L_min_I.index)
    imp_dep_compile_rows_var_finance_df = pd.DataFrame(index=np.unique(L_min_I.reset_index()['region']))
    # imp only
    imp_compile_cols_var_finance_df = pd.DataFrame(index=L_min_I.index)
    imp_compile_rows_var_finance_df = pd.DataFrame(index=L_min_I.index)
    # dep only
    dep_compile_cols_var_finance_df = pd.DataFrame(index=L_min_I.index)
    dep_compile_rows_var_finance_df = pd.DataFrame(index=L_min_I.index)

    # for storing the column sums for the score-level scores
    imp_dep_compile_cols_storing_df = pd.DataFrame(columns=services)
    # imp
    imp_compile_cols_storing_df = pd.DataFrame(columns=services)
    # dep
    dep_compile_cols_storing_df = pd.DataFrame(columns=services)


    # for storing the row sums for the score-level scores
    imp_dep_compile_rows_storing_df = pd.DataFrame(columns=services)
    # imp
    imp_compile_rows_storing_df = pd.DataFrame(columns=services)
    # dep
    dep_compile_rows_storing_df = pd.DataFrame(columns=services)


    # both
    # value at risk finance
    imp_dep_compile_cols_storing_var_finance_df = pd.DataFrame(columns=services)
    # value at risk finance rows
    imp_dep_compile_rows_storing_var_finance_df = pd.DataFrame(columns=services)
    # imp
    # value at risk finance
    imp_compile_cols_storing_var_finance_df = pd.DataFrame(columns=services)
    # value at risk finance rows
    imp_compile_rows_storing_var_finance_df = pd.DataFrame(columns=services)
    # dep
    # value at risk finance
    dep_compile_cols_storing_var_finance_df = pd.DataFrame(columns=services)
    # value at risk finance rows
    dep_compile_rows_storing_var_finance_df = pd.DataFrame(columns=services)

    # store scores
    imp_df = imp_score.copy()
    imp_score_name = imp_score.name

    dep_df = dep_score.copy()
    dep_score_name = dep_score.name

    for bank in banks:
        print(bank)
        imp_dep_compile_cols_one_bank_df = imp_dep_compile_cols_df.copy()
        imp_dep_compile_cols_one_bank_df['Bank'] = [f'{bank}'] * imp_dep_compile_cols_df.shape[0]
        # imp
        imp_compile_cols_one_bank_df = imp_compile_cols_df.copy()
        imp_compile_cols_one_bank_df['Bank'] = [f'{bank}'] * imp_compile_cols_df.shape[0]
        # dep
        dep_compile_cols_one_bank_df = dep_compile_cols_df.copy()
        dep_compile_cols_one_bank_df['Bank'] = [f'{bank}'] * dep_compile_cols_df.shape[0]

        # rows
        # both
        imp_dep_compile_rows_one_bank_df = imp_dep_compile_rows_df.copy()
        imp_dep_compile_rows_one_bank_df['Bank'] = [f'{bank}'] * imp_dep_compile_rows_df.shape[0]

        # imp
        imp_compile_rows_one_bank_df = imp_compile_rows_df.copy()
        imp_compile_rows_one_bank_df['Bank'] = [f'{bank}'] * imp_compile_rows_df.shape[0]

        # dep
        dep_compile_rows_one_bank_df = dep_compile_rows_df.copy()
        dep_compile_rows_one_bank_df['Bank'] = [f'{bank}'] * dep_compile_rows_df.shape[0]


        # value at risk finance
        # both
        imp_dep_compile_cols_one_bank_var_finance_df = imp_dep_compile_cols_var_finance_df.copy()
        imp_dep_compile_cols_one_bank_var_finance_df['Bank'] = [f'{bank}'] * imp_dep_compile_cols_var_finance_df.shape[
            0]
        # dep
        dep_compile_cols_one_bank_var_finance_df = dep_compile_cols_var_finance_df.copy()
        dep_compile_cols_one_bank_var_finance_df['Bank'] = [f'{bank}'] * dep_compile_cols_var_finance_df.shape[
            0]
        # imp
        imp_compile_cols_one_bank_var_finance_df = imp_compile_cols_var_finance_df.copy()
        imp_compile_cols_one_bank_var_finance_df['Bank'] = [f'{bank}'] * imp_compile_cols_var_finance_df.shape[
            0]


        # value at risk finance rows
        # value at risk finance
        # both
        imp_dep_compile_rows_one_bank_var_finance_df = imp_dep_compile_rows_var_finance_df.copy()
        imp_dep_compile_rows_one_bank_var_finance_df['Bank'] = [f'{bank}'] * imp_dep_compile_rows_var_finance_df.shape[
            0]
        # impact
        imp_compile_rows_one_bank_var_finance_df = imp_compile_rows_var_finance_df.copy()
        imp_compile_rows_one_bank_var_finance_df['Bank'] = [f'{bank}'] * imp_compile_rows_var_finance_df.shape[
            0]
        # dependency
        dep_compile_rows_one_bank_var_finance_df = dep_compile_rows_var_finance_df.copy()
        dep_compile_rows_one_bank_var_finance_df['Bank'] = [f'{bank}'] * dep_compile_rows_var_finance_df.shape[
            0]

        # get financial data for Bank
        bank_data_df = finance_data_df.reset_index()[finance_data_df.reset_index()['Bank'] == bank].set_index(
            ['region', 'Code'])
        # bank_data_df = bank_data_df['Proportion of Loans']
        full_index = pd.DataFrame(index=L_min_I.index)
        bank_data_df = bank_data_df.merge(full_index, how='right', right_index=True, left_index=True)
        bank_data_df = bank_data_df.fillna(0.0)
        # bank_data_df.drop(columns=['Bank', 'Total Loan', 'EUR m adjusted'], inplace=True)
        bank_data_dict = bank_data_df['Proportion of Loans'].to_dict()
        bank_data_absolute_dict = bank_data_df['EUR m adjusted'].to_dict()


        for service in services:
            print(service)


            # impact
            if type == 'region_code':
                # get the scores and the weighted L in one DF
                compiled_imp_df = upstream_calc_format.merge(
                    imp_df[service].reset_index(), how='outer', left_on=['region', 'Code'],
                    right_on=['region', 'Code'])
                compiled_imp_df = compiled_imp_df.fillna(0.0)

            if type == 'code_only':
                # get the scores and the weighted L in one DF
                compiled_imp_df = upstream_calc_format.merge(
                    imp_df[service].reset_index(), how='outer', left_on=['Code'],
                    right_on=['Code'])
                compiled_imp_df = compiled_imp_df.fillna(0.0)

            if type == 'region_only':
                # get the scores and the weighted L in one DF
                compiled_imp_df = upstream_calc_format.merge(
                    imp_df[service].reset_index(), how='outer', left_on=['region'],
                    right_on=['region'])
                compiled_imp_df = compiled_imp_df.fillna(0.0)


            # multiply the weighted average by the score
            compiled_imp_df = compiled_imp_df.set_index(['region', 'Code'])
            compiled_imp_df = compiled_imp_df.T.set_index(('region', 'Code')).T
            service_imp_df = compiled_imp_df[(0.0,0.0)]
            service_imp_df = service_imp_df[0:(L_min_I.shape[0])]
            service_imp_df = service_imp_df.astype(float)
            # calc_df = compiled_df.drop(columns=service).iloc[0:(L_min_I.shape[0]), 2:(L_min_I.shape[0] + 2)]
            # calc_df = calc_df.astype(float)
            calc_imp_df = compiled_imp_df.drop(columns =(0.0,0.0))
            calc_imp_df = calc_imp_df.astype(float)
            multiplied_imp_df = np.multiply(calc_imp_df.to_numpy(), service_imp_df.to_numpy()[:, np.newaxis])
            imp_dep_compile_service_imp_df = pd.DataFrame(multiplied_imp_df, index=calc_imp_df.index, columns=calc_imp_df.columns)

            # dependency
            if type == 'region_code':
                # get the scores and the weighted L in one DF
                compiled_dep_df = upstream_calc_format.merge(
                    dep_df[service].reset_index(), how='outer', left_on=['region', 'Code'],
                    right_on=['region', 'Code'])
                compiled_dep_df = compiled_dep_df.fillna(0.0)


            if type == 'code_only':
                # get the scores and the weighted L in one DF
                compiled_dep_df = upstream_calc_format.merge(
                    dep_df[service].reset_index(), how='outer', left_on=['Code'],
                    right_on=['Code'])
                compiled_dep_df = compiled_dep_df.fillna(0.0)


            if type == 'region_only':
                # get the scores and the weighted L in one DF
                compiled_dep_df = upstream_calc_format.merge(
                    dep_df[service].reset_index(), how='outer', left_on=['region'],
                    right_on=['region'])
                compiled_dep_df = compiled_dep_df.fillna(0.0)


            # multiply the weighted average by the score
            compiled_dep_df = compiled_dep_df.set_index(['region', 'Code'])
            compiled_dep_df = compiled_dep_df.T.set_index(('region', 'Code')).T
            service_dep_df = compiled_dep_df[(0.0, 0.0)]
            service_dep_df = service_dep_df[0:(L_min_I.shape[0])]
            service_dep_df = service_dep_df.astype(float)
            # calc_df = compiled_df.drop(columns=service).iloc[0:(L_min_I.shape[0]), 2:(L_min_I.shape[0] + 2)]
            # calc_df = calc_df.astype(float)
            calc_dep_df = compiled_dep_df.drop(columns=(0.0, 0.0))
            calc_dep_df = calc_dep_df.astype(float)
            multiplied_dep_df = np.multiply(calc_dep_df.to_numpy(), service_dep_df.to_numpy()[:, np.newaxis])
            imp_dep_compile_service_dep_df = pd.DataFrame(multiplied_dep_df, index=calc_dep_df.index,
                                                          columns=calc_dep_df.columns)


            # combine the impact and dependency scores
            # sum the rows by the region
            # both
            imp_dep_compile_service_dep_region_df = imp_dep_compile_service_dep_df.reset_index().drop(columns='Code').groupby('region').sum()
            imp_dep_compile_service_imp_region_df = imp_dep_compile_service_imp_df.reset_index().drop(columns='Code').groupby('region').sum()
            imp_dep_compile_service_df = imp_dep_compile_service_dep_region_df * imp_dep_compile_service_imp_region_df


            # combine the impact and dependency score value at risks
            # multiply score by the absolute value of finance to sr to get VaR
            imp_dep_compile_service_finance_VaR_df = imp_dep_compile_service_df
            imp_dep_compile_service_finance_VaR_df = imp_dep_compile_service_finance_VaR_df.mul(
                bank_data_absolute_dict, axis='columns')

            # multiply dependency/impact score separately by absolute value of finance to sr to get VaR
            # dep
            dep_compile_service_finance_VaR_df = imp_dep_compile_service_dep_df
            dep_compile_service_finance_VaR_df = imp_dep_compile_service_dep_df.mul(
                bank_data_absolute_dict, axis='columns')
            # imp
            imp_compile_service_finance_VaR_df = imp_dep_compile_service_imp_df
            imp_compile_service_finance_VaR_df = imp_dep_compile_service_imp_df.mul(
                bank_data_absolute_dict, axis='columns')

            # both
            # get the column sums for one bank for the scores
            imp_dep_compile_cols_one_bank_df[service] = imp_dep_compile_service_df.sum()
            # get the row sums for one bank and service into the greater the df
            imp_dep_compile_rows_one_bank_df[f'{service}'] = imp_dep_compile_service_df.T.sum()

            # dep
            # get the column sums for one bank for the scores
            dep_compile_cols_one_bank_df[service] = imp_dep_compile_service_dep_df.sum()
            # get the row sums for one bank and service into the greater the df
            dep_compile_rows_one_bank_df[f'{service}'] = imp_dep_compile_service_dep_df.T.sum()

            # imp
            # get the column sums for one bank for the scores
            imp_compile_cols_one_bank_df[service] = imp_dep_compile_service_imp_df.sum()
            # get the row sums for one bank and service into the greater the df
            imp_compile_rows_one_bank_df[f'{service}'] = imp_dep_compile_service_imp_df.T.sum()


            #both
            # get column sums for one bank for the value at risk finance
            imp_dep_compile_cols_one_bank_var_finance_df[service] = imp_dep_compile_service_finance_VaR_df.sum()
            # get the row sums for one bank and service into the greater the df
            imp_dep_compile_rows_one_bank_var_finance_df[f'{service}'] = imp_dep_compile_service_finance_VaR_df.T.sum()
            # imp
            # get column sums for one bank for the value at risk finance
            imp_compile_cols_one_bank_var_finance_df[service] = imp_compile_service_finance_VaR_df.sum()
            # get the row sums for one bank and service into the greater the df
            imp_compile_rows_one_bank_var_finance_df[f'{service}'] = imp_compile_service_finance_VaR_df.T.sum()
            # dep
            # get column sums for one bank for the value at risk finance
            dep_compile_cols_one_bank_var_finance_df[service] = dep_compile_service_finance_VaR_df.sum()
            # get the row sums for one bank and service into the greater the df
            dep_compile_rows_one_bank_var_finance_df[f'{service}'] = dep_compile_service_finance_VaR_df.T.sum()

        # both
        # load the services
        #cols
        imp_dep_compile_cols_storing_df = pd.concat(
            [imp_dep_compile_cols_storing_df.reset_index(), imp_dep_compile_cols_one_bank_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_cols_storing_df.columns:
            place_holder_df = imp_dep_compile_cols_storing_df.drop(columns='index')
            imp_dep_compile_cols_storing_df = place_holder_df.copy()

        # rows
        # load the services
        imp_dep_compile_rows_storing_df = pd.concat(
            [imp_dep_compile_rows_storing_df.reset_index(), imp_dep_compile_rows_one_bank_df.reset_index().rename(columns={'index':'region'})]).set_index(
            ['Bank', 'region'])
        if 'index' in imp_dep_compile_rows_storing_df.columns:
            place_holder_df = imp_dep_compile_rows_storing_df.drop(columns='index')
            imp_dep_compile_rows_storing_df = place_holder_df.copy()

        # var finance
        # load the services
        imp_dep_compile_cols_storing_var_finance_df = pd.concat(
            [imp_dep_compile_cols_storing_var_finance_df.reset_index(),
             imp_dep_compile_cols_one_bank_var_finance_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_cols_storing_var_finance_df.columns:
            place_holder_df = imp_dep_compile_cols_storing_var_finance_df.drop(columns='index')
            imp_dep_compile_cols_storing_var_finance_df = place_holder_df.copy()


        # rows
        # var finance
        # load the services
        imp_dep_compile_rows_storing_var_finance_df = pd.concat(
            [imp_dep_compile_rows_storing_var_finance_df.reset_index(),
             imp_dep_compile_rows_one_bank_var_finance_df.reset_index().rename(columns={'index':'region'})]).set_index(
            ['Bank', 'region'])
        if 'index' in imp_dep_compile_rows_storing_var_finance_df.columns:
            place_holder_df = imp_dep_compile_rows_storing_var_finance_df.drop(columns='index')
            imp_dep_compile_rows_storing_var_finance_df = place_holder_df.copy()

        # imp
        # load the services
        # cols
        imp_compile_cols_storing_df = pd.concat(
            [imp_compile_cols_storing_df.reset_index(),
             imp_compile_cols_one_bank_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_compile_cols_storing_df.columns:
            place_holder_df = imp_compile_cols_storing_df.drop(columns='index')
            imp_compile_cols_storing_df = place_holder_df.copy()

        # rows
        # load the services
        imp_compile_rows_storing_df = pd.concat(
            [imp_compile_rows_storing_df.reset_index(),
             imp_compile_rows_one_bank_df.reset_index().rename(columns={'index': 'region'})]).set_index(
            ['Bank','region', 'Code'])
        if 'index' in imp_compile_rows_storing_df.columns:
            place_holder_df = imp_compile_rows_storing_df.drop(columns='index')
            imp_compile_rows_storing_df = place_holder_df.copy()

        # var finance
        # load the services
        imp_compile_cols_storing_var_finance_df = pd.concat(
            [imp_compile_cols_storing_var_finance_df.reset_index(),
             imp_compile_cols_one_bank_var_finance_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_compile_cols_storing_var_finance_df.columns:
            place_holder_df = imp_compile_cols_storing_var_finance_df.drop(columns='index')
            imp_compile_cols_storing_var_finance_df = place_holder_df.copy()

        # rows
        # var finance
        # load the services
        imp_compile_rows_storing_var_finance_df = pd.concat(
            [imp_compile_rows_storing_var_finance_df.reset_index(),
             imp_compile_rows_one_bank_var_finance_df.reset_index().rename(
                 columns={'index': 'region'})]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_compile_rows_storing_var_finance_df.columns:
            place_holder_df = imp_compile_rows_storing_var_finance_df.drop(columns='index')
            imp_compile_rows_storing_var_finance_df = place_holder_df.copy()

        # dep
        # load the services
        # cols
        dep_compile_cols_storing_df = pd.concat(
            [dep_compile_cols_storing_df.reset_index(), dep_compile_cols_one_bank_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in dep_compile_cols_storing_df.columns:
            place_holder_df = dep_compile_cols_storing_df.drop(columns='index')
            dep_compile_cols_storing_df = place_holder_df.copy()

        # rows
        # load the services
        dep_compile_rows_storing_df = pd.concat(
            [dep_compile_rows_storing_df.reset_index(),
             dep_compile_rows_one_bank_df.reset_index().rename(columns={'index': 'region'})]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in dep_compile_rows_storing_df.columns:
            place_holder_df = dep_compile_rows_storing_df.drop(columns='index')
            dep_compile_rows_storing_df = place_holder_df.copy()

        # var finance
        # load the services
        dep_compile_cols_storing_var_finance_df = pd.concat(
            [dep_compile_cols_storing_var_finance_df.reset_index(),
             dep_compile_cols_one_bank_var_finance_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in dep_compile_cols_storing_var_finance_df.columns:
            place_holder_df = dep_compile_cols_storing_var_finance_df.drop(columns='index')
            dep_compile_cols_storing_var_finance_df = place_holder_df.copy()

        # rows
        # var finance
        # load the services
        dep_compile_rows_storing_var_finance_df = pd.concat(
            [dep_compile_rows_storing_var_finance_df.reset_index(),
             dep_compile_rows_one_bank_var_finance_df.reset_index().rename(columns={'index': 'region'})]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in dep_compile_rows_storing_var_finance_df.columns:
            place_holder_df = dep_compile_rows_storing_var_finance_df.drop(columns='index')
            dep_compile_rows_storing_var_finance_df = place_holder_df.copy()

    # both
    # cols
    imp_dep_compile_cols_storing_var_finance_df.name = f'{imp_score_name} {dep_score_name} Both Finance VaR Source'
    imp_dep_compile_cols_storing_var_finance_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}Both/{imp_dep_compile_cols_storing_var_finance_df.name}.csv')
    storing_list.append(imp_dep_compile_cols_storing_var_finance_df)

    # rows
    imp_dep_compile_rows_storing_var_finance_df.name = f'{imp_score_name} {dep_score_name} Both Finance VaR Value Chain'
    imp_dep_compile_rows_storing_var_finance_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}Both/{imp_dep_compile_rows_storing_var_finance_df.name}.csv')
    storing_list.append(imp_dep_compile_rows_storing_var_finance_df)

    # imp
    # cols
    imp_compile_cols_storing_var_finance_df.name = f'{imp_score_name} Impact Finance VaR Source'
    imp_compile_cols_storing_var_finance_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}Impact/{imp_compile_cols_storing_var_finance_df.name}.csv')
    storing_list.append(imp_compile_cols_storing_var_finance_df)

    # rows
    imp_compile_rows_storing_var_finance_df.name = f'{imp_score_name} Impact Finance VaR Value Chain'
    imp_compile_rows_storing_var_finance_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}Impact/{imp_compile_rows_storing_var_finance_df.name}.csv')
    storing_list.append(imp_compile_rows_storing_var_finance_df)

    # dep
    # cols
    dep_compile_cols_storing_var_finance_df.name = f' {dep_score_name} Dependency Finance VaR Source'
    dep_compile_cols_storing_var_finance_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}Dependency/{dep_compile_cols_storing_var_finance_df.name}.csv')
    storing_list.append(dep_compile_cols_storing_var_finance_df)

    # rows
    dep_compile_rows_storing_var_finance_df.name = f'{dep_score_name} Dependency Finance VaR Value Chain'
    dep_compile_rows_storing_var_finance_df.to_csv(
        f'../Data/Value at Risk/Finance/{folder}Dependency/{dep_compile_rows_storing_var_finance_df.name}.csv')
    storing_list.append(dep_compile_rows_storing_var_finance_df)

    return storing_list



def finance_var_calc_scope_1(score, finance_data_df, type, L_min_I, folder):
    """
    :param score: a dataframe of the score that you want to use to calculate the value at risk
    :param finance_df: the finance of the bank you want to calculate the value at risk for
    :param folder: either 'Multipled/' for the combined multipled or '' for imp or dep
    :return: a list of dataframes that correspond to the finance_var and the rows for the finance_var plus the scores
    """
    if type != 'region_code' and type != 'code_only' and type != 'region_only':
        print('ERROR: Type must be "region_code" or "code_only" or "region_only"')
        return

    storing_list = []

    banks = np.unique(finance_data_df.reset_index()['Bank'])
    services = score.columns
    # scope 1
    # for the storing the score-level scores
    imp_dep_compile_cols_scope_1_df = pd.DataFrame(index=L_min_I.index)
    # var values
    imp_dep_compile_cols_storing_var_finance_scope_1_df = pd.DataFrame(columns=services)

    # store score
    df = score.copy()
    score_name = score.name

    for bank in banks:
        print(bank)
        # scope 1 value at risk with imp_dep scores
        # finance
        imp_dep_compile_cols_one_bank_var_finance_scope_1_df = imp_dep_compile_cols_scope_1_df.copy()
        imp_dep_compile_cols_one_bank_var_finance_scope_1_df['Bank'] = [f'{bank}'] * \
                                                                imp_dep_compile_cols_one_bank_var_finance_scope_1_df.shape[
                                                                    0]

        # get finance values without converting the all to the bank values
        scope_1_score_one_bank = df.copy()

        # get financial data for Bank
        bank_data_df = finance_data_df.reset_index()[finance_data_df.reset_index()['Bank'] == bank].set_index(
            ['region', 'Code'])
        # bank_data_df = bank_data_df['Proportion of Loans']
        full_index = pd.DataFrame(index=L_min_I.index)
        bank_data_df = bank_data_df.merge(full_index, how='right', right_index=True, left_index=True)
        bank_data_df = bank_data_df.fillna(0.0).reset_index()
        # bank_data_df.drop(columns=['Bank', 'Total Loan', 'EUR m adjusted'], inplace=True)
        bank_data_dict = bank_data_df['Proportion of Loans'].to_dict()
        bank_data_absolute_dict = bank_data_df['EUR m adjusted'].to_dict()


        for service in services:
            print(service)
            # finance
            if (type == "region_code"):
                compiled_scope_1_df = bank_data_df.merge(
                    scope_1_score_one_bank[service].reset_index(), how='left', left_on=['region', 'Code'],
                    right_on=['region', 'Code'])
            if (type == "code_only"):
                compiled_scope_1_df = bank_data_df.merge(
                    scope_1_score_one_bank[service].reset_index(), how='left', left_on=['Code'],
                    right_on=['Code'])
            compiled_scope_1_df = compiled_scope_1_df.fillna(0.0).set_index(['region', 'Code'])
            imp_dep_compile_cols_one_bank_var_finance_scope_1_df[service] = compiled_scope_1_df['EUR m adjusted'] * \
                                                                         compiled_scope_1_df[service]

        # scope 1
        # finance
        imp_dep_compile_cols_storing_var_finance_scope_1_df = pd.concat(
            [imp_dep_compile_cols_storing_var_finance_scope_1_df.reset_index(),
            imp_dep_compile_cols_one_bank_var_finance_scope_1_df.reset_index()]).set_index(
            ['Bank', 'region', 'Code'])
        if 'index' in imp_dep_compile_cols_storing_var_finance_scope_1_df.columns:
            place_holder_df = imp_dep_compile_cols_storing_var_finance_scope_1_df.drop(columns='index')
            imp_dep_compile_cols_storing_var_finance_scope_1_df = place_holder_df.copy()


    # load the services
    # # scope 1
    imp_dep_compile_cols_storing_var_finance_scope_1_df.to_csv(f'../Data/Value at Risk/Finance/{folder}/{score_name} Both Finance VaR Scope 1.csv')
    storing_list.append(imp_dep_compile_cols_storing_var_finance_scope_1_df)

    return storing_list

def EXIO_var_calc_scope_1(score, type, L_min_I, folder, x_NACE_df):
    """
        :param score: a dataframe of the score that you want to use to calculate the value at risk
        :param finance_df: the finance of the bank you want to calculate the value at risk for
        :param type: the type of score (whether it is a scope 1 (only Code) or whether it contains region as well
        :param folder: either 'Multipled/' for the combined multipled or '' for imp or dep
        :return: a list of dataframes that correspond to the finance_var and the rows for the finance_var plus the scores
        """
    if type != 'region_code' and type != 'code_only' and type != 'region_only':
        print('ERROR: Type must be "region_code" or "code_only" or "region_only"')
        return

    storing_list = []

    services = score.columns
    # scope 1
    # for the storing the score-level scores
    imp_dep_compile_cols_scope_1_df = pd.DataFrame(index=L_min_I.index)
    # var values
    imp_dep_compile_cols_storing_var_finance_scope_1_df = pd.DataFrame(columns=services)

    # store score
    df = score.copy()
    score_name = score.name

    # get finance values without converting the all to the bank values
    scope_1_score_one_bank = df.copy()

    # get EXIO proportions by sector and total
    x_data_df = x_NACE_df.copy()
    x_total = x_NACE_df['indout'].sum()
    full_index = pd.DataFrame(index=x_NACE_df.index)
    x_data_df['Proportion'] = x_NACE_df['indout']/x_total
    x_data_dict = x_data_df['Proportion'].to_dict()
    bank_data_absolute_dict = x_data_df['indout'].to_dict()

    for service in services:
        print(service)
        # finance
        if (type == "region_code"):
            compiled_scope_1_df = x_data_df.merge(
                scope_1_score_one_bank[service].reset_index(), how='left', left_on=['region', 'Code'],
                right_on=['region', 'Code'])
        if (type == "code_only"):
            compiled_scope_1_df = x_data_df.reset_index().merge(
                scope_1_score_one_bank[service].reset_index(), how='left', left_on=['Code'],
                right_on=['Code'])
        compiled_scope_1_df = compiled_scope_1_df.fillna(0.0).set_index(['region', 'Code'])
        imp_dep_compile_cols_storing_var_finance_scope_1_df[service] = compiled_scope_1_df['indout'] * \
                                                                        compiled_scope_1_df[service]

    # load the services
    # # scope 1
    imp_dep_compile_cols_storing_var_finance_scope_1_df.to_csv(f'../Data/Value at Risk/EXIO/{folder}Both/{score_name} Both Finance VaR Scope 1.csv')
    storing_list.append(imp_dep_compile_cols_storing_var_finance_scope_1_df)

    return storing_list

def EXIO_var_calc_scope_3_combined(imp_score, dep_score, x_NACE_df, type, L_min_I, folder):
    """
    :param score: a dataframe of the score that you want to use to calculate the value at risk
    :param finance_df: the finance of the bank you want to calculate the value at risk for
    :param type: the type of score (whether it is a scope 1 (only Code) or whether it contains region as well
    :param folder: either 'Multipled/' for the combined multipled or '' for imp or dep
    :return: a list of dataframes that correspond to the finance_var and the rows for the finance_var plus the scores
    """
    if type != 'region_code' and type != 'code_only' and type != 'region_only':
        print('ERROR: Type must be "region_code" or "code_only" or "region_only"')
        return

    storing_list = []
    ### calculate overlined((L -1)), relative impact dependency matrix
    L_min_I_numpy = L_min_I.to_numpy(dtype=float)
    col_sums = np.sum(L_min_I, axis=0)
    col_sums = col_sums.to_numpy(dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        rel_imp_array = np.where(col_sums == 0, 0, np.divide(L_min_I_numpy, col_sums[np.newaxis, :]))

    # get the weights for the contribution of each sector,region pair to the supply chain
    L_weights = pd.DataFrame(rel_imp_array, index=L_min_I.index, columns=L_min_I.columns)
    upstream_calc = L_weights.copy().reset_index()

    # multiply the weighted sum for Leontief by the impact region score (based on investment location)
    # plus the dependency score for the sector region L_weighted * (impact region) * (dependency sector)

    upstream_calc_format = upstream_calc.T.reset_index().T.rename(columns={0: 'region', 1: 'Code'})
    upstream_calc_format.loc['Code', 'region'] = 'region'
    upstream_calc_format.loc['Code', 'Code'] = 'Code'

    services = imp_score.columns

    # for the storing the score-level scores
    imp_dep_compile_cols_df = pd.DataFrame(index=L_min_I.index)
    imp_dep_compile_rows_df = pd.DataFrame(index=np.unique(L_min_I.reset_index()['region']))
    # storing value at risk
    imp_dep_compile_cols_var_finance_df = pd.DataFrame(index=L_min_I.index)
    imp_dep_compile_rows_var_finance_df = pd.DataFrame(index=np.unique(L_min_I.reset_index()['region']))


    # for storing the column sums for the score-level scores
    imp_dep_compile_cols_storing_df = pd.DataFrame(columns=services)


    # for storing the row sums for the score-level scores
    imp_dep_compile_rows_storing_df = pd.DataFrame(columns=services)


    # value at risk finance
    imp_dep_compile_cols_storing_var_finance_df = pd.DataFrame(columns=services)


    # value at risk finance rows
    imp_dep_compile_rows_storing_var_finance_df = pd.DataFrame(columns=services)

    # store scores
    imp_df = imp_score.copy()
    imp_score_name = imp_score.name

    dep_df = dep_score.copy()
    dep_score_name = dep_score.name

    # get proportion data for EXIO sector regions
    x_data_df = x_NACE_df.copy()
    x_total = x_NACE_df['indout'].reset_index().drop(columns='Code').groupby('region').sum().rename(columns={'indout':'region_total'})
    x_total_dict = x_total['region_total'].to_dict()
    x_data_w_total_df = x_data_df.reset_index().merge(x_total, right_on='region', left_on='region', how='left')
    x_data_w_total_df['Proportion'] = x_data_w_total_df['indout'] / x_data_w_total_df['region_total']
    x_data_dict = x_data_w_total_df['Proportion'].to_dict()
    x_data_absolute_dict = x_data_w_total_df['indout'].to_dict()


    for service in services:
        print(service)

        # impact
        if type == 'region_code':
            # get the scores and the weighted L in one DF
            compiled_imp_df = upstream_calc_format.merge(
                imp_df[service].reset_index(), how='outer', left_on=['region', 'Code'],
                right_on=['region', 'Code'])
            compiled_imp_df = compiled_imp_df.fillna(0.0)

        if type == 'code_only':
            # get the scores and the weighted L in one DF
            compiled_imp_df = upstream_calc_format.merge(
                imp_df[service].reset_index(), how='outer', left_on=['Code'],
                right_on=['Code'])
            compiled_imp_df = compiled_imp_df.fillna(0.0)


        if type == 'region_only':
            # get the scores and the weighted L in one DF
            compiled_imp_df = upstream_calc_format.merge(
                imp_df[service].reset_index(), how='outer', left_on=['region'],
                right_on=['region'])
            compiled_imp_df = compiled_imp_df.fillna(0.0)


        # multiply the weighted average by the score
        # compiled_imp_df = compiled_imp_df.set_index(['region', 'Code'])
        # compiled_imp_df = compiled_imp_df.T.set_index(('region', 'Code')).T
        compiled_imp_df = compiled_imp_df.T.rename(columns={147: 'region', 148: 'Code'}).set_index(['region', 'Code']).T.set_index([('region', 'region'), ('Code', 'Code')])
        service_imp_df = compiled_imp_df[(0.0, 0.0)]
        service_imp_df = service_imp_df[0:(L_min_I.shape[0])]
        service_imp_df = service_imp_df.astype(float)
        # calc_df = compiled_df.drop(columns=service).iloc[0:(L_min_I.shape[0]), 2:(L_min_I.shape[0] + 2)]
        # calc_df = calc_df.astype(float)
        calc_imp_df = compiled_imp_df.drop(columns=(0.0, 0.0))
        calc_imp_df = calc_imp_df.astype(float)
        multiplied_imp_df = np.multiply(calc_imp_df.to_numpy(), service_imp_df.to_numpy()[:, np.newaxis])
        imp_dep_compile_service_imp_df = pd.DataFrame(multiplied_imp_df, index=calc_imp_df.index, columns=calc_imp_df.columns)


        # dependency
        if type == 'region_code':
            # get the scores and the weighted L in one DF
            compiled_dep_df = upstream_calc_format.merge(
                dep_df[service].reset_index(), how='outer', left_on=['region', 'Code'],
                right_on=['region', 'Code'])
            compiled_dep_df = compiled_dep_df.fillna(0.0)

        if type == 'code_only':
            # get the scores and the weighted L in one DF
            compiled_dep_df = upstream_calc_format.merge(
                dep_df[service].reset_index(), how='outer', left_on=['Code'],
                right_on=['Code'])
            compiled_dep_df = compiled_dep_df.fillna(0.0)

        if type == 'region_only':
            # get the scores and the weighted L in one DF
            compiled_dep_df = upstream_calc_format.merge(
                dep_df[service].reset_index(), how='outer', left_on=['region'],
                right_on=['region'])
            compiled_dep_df = compiled_dep_df.fillna(0.0)



        # multiply the weighted average by the score
        # compiled_dep_df = compiled_dep_df.set_index(['region', 'Code'])
        # compiled_dep_df = compiled_dep_df.T.set_index(('region', 'Code')).T
        compiled_dep_df = compiled_dep_df.T.rename(columns={147: 'region', 148: 'Code'}).set_index(['region', 'Code']).T.set_index([('region', 'region'), ('Code', 'Code')])
        service_dep_df = compiled_dep_df[(0.0, 0.0)]
        service_dep_df = service_dep_df[0:(L_min_I.shape[0])]
        service_dep_df = service_dep_df.astype(float)
        # calc_df = compiled_df.drop(columns=service).iloc[0:(L_min_I.shape[0]), 2:(L_min_I.shape[0] + 2)]
        # calc_df = calc_df.astype(float)
        calc_dep_df = compiled_dep_df.drop(columns=(0.0, 0.0))
        calc_dep_df = calc_dep_df.astype(float)
        multiplied_dep_df = np.multiply(calc_dep_df.to_numpy(), service_dep_df.to_numpy()[:, np.newaxis])
        imp_dep_compile_service_dep_df = pd.DataFrame(multiplied_dep_df, index=calc_dep_df.index,
                                                      columns=calc_dep_df.columns)

        # combine the impact and dependency scores
        # sum the rows by the region
        # both
        # imp_dep_compile_service_dep_region_df = imp_dep_compile_service_dep_df.reset_index().drop(
        #     columns='Code').groupby(('region', 'region')).sum()
        # imp_dep_compile_service_imp_region_df = imp_dep_compile_service_imp_df.reset_index().drop(
        #     columns='Code').groupby(('region', 'region')).sum()
        # imp_dep_compile_service_df = imp_dep_compile_service_dep_region_df * imp_dep_compile_service_imp_region_df
        imp_dep_compile_service_df = (imp_dep_compile_service_dep_df * imp_dep_compile_service_imp_df).reset_index().drop(columns=('Code', 'Code')).groupby(('region', 'region')).sum()

        # combine the impact and dependency score value at risks
        # multiply score by the absolute value of finance to sr to get VaR
        imp_dep_compile_service_finance_VaR_df = imp_dep_compile_service_df
        imp_dep_compile_service_finance_VaR_df = imp_dep_compile_service_finance_VaR_df.mul(
            x_data_w_total_df.set_index(['region', 'Code'])['indout'], axis='columns')

        # get the column sums for one bank for the scores
        imp_dep_compile_cols_storing_df[service] = imp_dep_compile_service_df.sum()
        # get the row sums for one bank and service into the greater the df
        imp_dep_compile_rows_storing_df[f'{service}'] = imp_dep_compile_service_df.T.sum()


        # get column sums for one bank for the value at risk finance
        imp_dep_compile_cols_storing_var_finance_df[service] = imp_dep_compile_service_finance_VaR_df.sum()
        # get the row sums for one bank and service into the greater the df
        imp_dep_compile_rows_storing_var_finance_df[f'{service}'] = imp_dep_compile_service_finance_VaR_df.T.sum()



    # cols
    imp_dep_compile_cols_storing_var_finance_df.name = f'{imp_score_name} {dep_score_name} Both Finance VaR Source'
    imp_dep_compile_cols_storing_var_finance_df.to_csv(
        f'../Data/Value at Risk/EXIO/{folder}Both/{imp_dep_compile_cols_storing_var_finance_df.name}.csv')
    storing_list.append(imp_dep_compile_cols_storing_var_finance_df)

    # rows
    imp_dep_compile_rows_storing_var_finance_df.name = f'{imp_score_name} {dep_score_name} Both Finance VaR Value Chain'
    imp_dep_compile_rows_storing_var_finance_df.to_csv(
        f'../Data/Value at Risk/EXIO/{folder}Both/{imp_dep_compile_rows_storing_var_finance_df.name}.csv')
    storing_list.append(imp_dep_compile_rows_storing_var_finance_df)


    return storing_list






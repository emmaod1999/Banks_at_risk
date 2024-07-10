import pandas as pd
import numpy as np
import pymrio
from Setup import (EXIO_file_path, ENCORE_imp_path_id, ENCORE_to_EXIO_path, ENCORE_imp_num_es_ass_path, \
                   ENCORE_imp_num_ass_driver_path, ENCORE_imp_driver_driver_env_change_path, \
                   scope_1_path_mean, scope_1_path_min, \
                   scope_1_path_max, scope_3_path_mean, scope_3_path_min, scope_3_path_max)

# Read the MRIO table into a pandas DataFrame
EXIO3 = pymrio.parse_exiobase3(path=EXIO_file_path)
EXIO3.calc_all()

# get EXIOBASE sectors
EXIO_sectors = EXIO3.get_sectors().to_list()
EXIO_regions = EXIO3.get_regions().to_list()

# load ENCORE sectorial impact scores
ENCORE_imp_id_df = pd.read_csv(ENCORE_imp_path_id, index_col=[0], header=0)
ENCORE_imp_id_df.index.names = ['Process']

# get ENCORE processes
ENCORE_sectors = set(ENCORE_imp_id_df.index.get_level_values(0))

# load ENCORE EXIOBASE concordance table
ENCORE_to_EXIO_df = pd.read_excel(ENCORE_to_EXIO_path, index_col=[5], header=[0], sheet_name='table_correspondance')
ENCORE_to_EXIO_df_restricted = ENCORE_to_EXIO_df.drop(labels=['Grandes catégories', 'Sector', 'Subindustry',
 'Industry_group_benchmark', 'ID_Industry_group_benchmark', 'Exiobase_industry_group'], axis=1)
ENCORE_to_EXIO_df_restricted.sort_index(inplace=True)
ENCORE_not_included_sectors = set(ENCORE_sectors) - set(ENCORE_to_EXIO_df_restricted.index.values)
EXIO_not_included_sectors = set(EXIO_sectors) - set(ENCORE_to_EXIO_df_restricted.loc[:, 'IndustryTypeName'])

# save the included sectors
ENCORE_included_sectors = ENCORE_sectors - ENCORE_not_included_sectors
EXIO_included_sectors = set(EXIO_sectors) - EXIO_not_included_sectors

# get restricted dataframe with only sectors which are included in the EXIOBASE
ENCORE_imp_restricted_df = ENCORE_imp_id_df.loc[np.unique(ENCORE_to_EXIO_df_restricted.index.values), :]
ENCORE_imp_restricted_df.sort_index(inplace=True)
ENCORE_imp_restricted_df.reset_index(inplace=True)
ENCORE_imp_restricted_df_no_duplicates = ENCORE_imp_restricted_df.drop_duplicates()
ENCORE_imp_restricted_df_no_duplicates.set_index('Process', inplace=True)

# get the impact drivers
ENCORE_imp_drivers = list(ENCORE_imp_id_df.columns.values)

# create dataframe with EXIO sectors as index and ENCORE sectors as values
EXIO_to_ENCORE_df = ENCORE_to_EXIO_df_restricted.reset_index()
EXIO_to_ENCORE_df['Count'] = EXIO_to_ENCORE_df.groupby(['IndustryTypeName', 'Process']).transform('count')
# Multiply the values by the count and drop duplicates
EXIO_to_ENCORE_df['Poids'] = EXIO_to_ENCORE_df['Poids'] * EXIO_to_ENCORE_df['Count']
EXIO_to_ENCORE_df.drop_duplicates(subset=['IndustryTypeName', 'Process'], keep='first', inplace=True)

# Set the modified DataFrame back to multi-index
EXIO_to_ENCORE_df.set_index(['IndustryTypeName', 'Process'], inplace=True)
EXIO_to_ENCORE_df.drop(columns=['Count'], inplace=True)

# Sort the index
EXIO_to_ENCORE_df.sort_index(inplace=True)

### calculate the EXIOBASE impact scores - mean, min, max - for impact drivers

# create df for storing the EXIOBASE sector dependency scores
EXIO_imp_df_mean = pd.DataFrame(0, index=ENCORE_imp_drivers, columns=EXIO_sectors)
EXIO_imp_df_min = pd.DataFrame(0, index=ENCORE_imp_drivers, columns=EXIO_sectors)
EXIO_imp_df_max = pd.DataFrame(0, index=ENCORE_imp_drivers, columns=EXIO_sectors)

# get the impact scores for the EXIOBASE sectors
# loop over drivers

for driver in ENCORE_imp_drivers:
    # loop over EXIOBASE_sectors
    for sector_EXIO in EXIO_included_sectors:
        driver_sector_array = []

        # get associated ENCORE_sectors
        associated_ENCORE_df = EXIO_to_ENCORE_df.loc[sector_EXIO, :]

        # loop over associated ENCORE_sectors
        for sector_ENCORE in associated_ENCORE_df.index.values:
            # # check if service is included
            # if driver in ENCORE_imp_restricted_df.loc[sector_ENCORE, :].index.values:
            #     poid = EXIO_to_ENCORE_df.loc[(sector_EXIO, sector_ENCORE), 'Poids']
            #     rating = ENCORE_imp_restricted_df.loc[(sector_ENCORE, driver), 'Rating Num']
            #     driver_sector_array.append(poid*rating)
            #     exit
            # else:
            #     driver_sector_array.append(0)

            poid = EXIO_to_ENCORE_df.loc[(sector_EXIO, sector_ENCORE), 'Poids']
            rating = ENCORE_imp_restricted_df_no_duplicates.loc[sector_ENCORE, driver]

            driver_sector_array.append(poid * rating)

            # store impacts in dataframe
        EXIO_imp_df_mean.loc[driver, sector_EXIO] = np.mean(np.array(driver_sector_array))
        EXIO_imp_df_min.loc[driver, sector_EXIO] = np.min(np.array(driver_sector_array))
        EXIO_imp_df_max.loc[driver, sector_EXIO] = np.max(np.array(driver_sector_array))

# save the EXIOBASE sector scope 1 impacts as they will be needed later on
# EXIO_imp_df_mean.to_csv('../Data/exiobase_download_online/EXIOBASE_sectors_scope_1_impact_scores_mean.csv', index=True, header=True)
# EXIO_imp_df_min.to_csv('../Data/exiobase_download_online/EXIOBASE_sectors_scope_1_impact_scores_min.csv', index=True, header=True)
# EXIO_imp_df_max.to_csv('../Data/exiobase_download_online/EXIOBASE_sectors_scope_1_impact_scores_max.csv', index=True, header=True)

# join the importance of the asset to the ecosystem asset driver of environment change influence
# load ENCORE ecosystem asset importance
ENCORE_imp_es_ass_df = pd.read_csv(ENCORE_imp_num_es_ass_path, index_col=[0], header=0)
ENCORE_imp_es_ass_df.reset_index(inplace=True)

# load ENCORE ecosystem driver of environmental change influence
ENCORE_imp_ass_dr_df = pd.read_csv(ENCORE_imp_num_ass_driver_path, index_col=[0], header=0)
ENCORE_imp_ass_dr_df.reset_index(inplace=True)
ENCORE_imp_ass_dr_df.rename(columns={"Ecosystem service": "Ecosystem Service"}, inplace=True)

# join the ecosystem service, asset, driver influence with the ecosystem service and asset materiality
ENCORE_es_asset_driver_join = pd.merge(ENCORE_imp_ass_dr_df,ENCORE_imp_es_ass_df,how='left',
                                       left_on=['Ecosystem Service','Asset'],right_on=['Ecosystem Service','Asset'])

# multiply the materiality (influence) by the importance
ENCORE_es_asset_driver_join['Driver Influence on Ecosystem Service'] = (ENCORE_es_asset_driver_join.Influence *
                                                                        ENCORE_es_asset_driver_join.Materiality)
ENCORE_es_asset_driver_join_clean = ENCORE_es_asset_driver_join.drop(columns = ['Influence', 'Materiality'])


# connect impact drivers to drivers of environmental change
# load the impact drivers
ENCORE_imp_dr_dr_df = pd.read_csv(ENCORE_imp_driver_driver_env_change_path, index_col=[0], header=0, usecols = ['Impact Driver', 'Driver', 'Asset'])
#reset the index
ENCORE_imp_dr_dr_df.reset_index(inplace=True)

# join the ecosystem service asset driver
ENCORE_imp_dr_dr_es_asset_driver_join = pd.merge(ENCORE_es_asset_driver_join_clean,ENCORE_imp_dr_dr_df,how='left',left_on=['Driver','Asset'],right_on=['Driver','Asset'])
ENCORE_imp_dr_dr_es_asset_driver_join.drop(columns=['Asset'], inplace=True)
ENCORE_imp_dr_dr_es_asset_driver_join.drop_duplicates(inplace=True)

# get ecosystem services
ENCORE_ecosystem_services = ENCORE_imp_dr_dr_es_asset_driver_join['Ecosystem Service'].unique().tolist()

# multiply the driver influence on ecosystem service by the impact driver score
# to get the impact score on ecosystem services

# right join EXIO_imp_df_mean and ENCORE_imp_dr_dr_es_asset_driver_join
# reset index
# mean
EXIO_imp_df_mean_no_index = EXIO_imp_df_mean.reset_index()
EXIO_imp_df_mean_no_index.rename(columns={"index": "Impact Driver"}, inplace=True)
EXIO_imp_df_mean_w_dr_es = pd.merge(ENCORE_imp_dr_dr_es_asset_driver_join, EXIO_imp_df_mean_no_index, how='inner',
                                    left_on=['Impact Driver'], right_on=['Impact Driver'])
# copy the df to edit
EXIO_imp_df_mean_w_dr_es_filtered = EXIO_imp_df_mean_w_dr_es

# min
EXIO_imp_df_min_no_index = EXIO_imp_df_min.reset_index()
EXIO_imp_df_min_no_index.rename(columns={"index": "Impact Driver"}, inplace=True)
EXIO_imp_df_min_w_dr_es = pd.merge(ENCORE_imp_dr_dr_es_asset_driver_join, EXIO_imp_df_min_no_index, how='inner',
                                    left_on=['Impact Driver'], right_on=['Impact Driver'])
# copy the df to edit
EXIO_imp_df_min_w_dr_es_filtered = EXIO_imp_df_min_w_dr_es

# max
EXIO_imp_df_max_no_index = EXIO_imp_df_max.reset_index()
EXIO_imp_df_max_no_index.rename(columns={"index": "Impact Driver"}, inplace=True)
EXIO_imp_df_max_w_dr_es = pd.merge(ENCORE_imp_dr_dr_es_asset_driver_join, EXIO_imp_df_max_no_index, how='inner',
                                    left_on=['Impact Driver'], right_on=['Impact Driver'])
# copy the df to edit
EXIO_imp_df_max_w_dr_es_filtered = EXIO_imp_df_max_w_dr_es

# multiply the impact scores by the driver influence on ES
for sector in EXIO_imp_df_mean.columns.tolist():
    for row in range(len(EXIO_imp_df_mean_w_dr_es)):
        # mean
        EXIO_imp_df_mean_w_dr_es_filtered.loc[row, sector] = \
        EXIO_imp_df_mean_w_dr_es['Driver Influence on Ecosystem Service'].iloc[row] * EXIO_imp_df_mean_w_dr_es.loc[
            row, sector]
        # min
        EXIO_imp_df_min_w_dr_es_filtered.loc[row, sector] = \
            EXIO_imp_df_mean_w_dr_es['Driver Influence on Ecosystem Service'].iloc[row] * EXIO_imp_df_min_w_dr_es.loc[
                row, sector]
        # max
        EXIO_imp_df_max_w_dr_es_filtered.loc[row, sector] = \
            EXIO_imp_df_mean_w_dr_es['Driver Influence on Ecosystem Service'].iloc[row] * EXIO_imp_df_max_w_dr_es.loc[
                row, sector]

# output a dataframe with ecosystem services as index and sectors as columns
EXIO_imp_es_df_mean = pd.DataFrame(0, index=ENCORE_ecosystem_services, columns=EXIO_sectors)
EXIO_imp_es_df_min = pd.DataFrame(0, index=ENCORE_ecosystem_services, columns=EXIO_sectors)
EXIO_imp_es_df_max = pd.DataFrame(0, index=ENCORE_ecosystem_services, columns=EXIO_sectors)

# connect the driver to impact driver for mean, max, min **** THINK ABOUT IF THIS MAKES SENSE *****
# might make more sense for the max, min, mean to be averaged at this stage... --> check...
for sector in EXIO_sectors:
    for ec_service in ENCORE_ecosystem_services:
        es_sector_array_mean = []
        es_sector_array_min = []
        es_sector_array_max = []
        for row in range(len(EXIO_imp_df_mean_w_dr_es)):
            if (EXIO_imp_df_mean_w_dr_es.loc[row, 'Ecosystem Service'] == ec_service):
                es_sector_array_mean.append(EXIO_imp_df_mean_w_dr_es.loc[row, sector])
                es_sector_array_min.append(EXIO_imp_df_min_w_dr_es.loc[row, sector])
                es_sector_array_max.append(EXIO_imp_df_max_w_dr_es.loc[row, sector])
        if (len(es_sector_array_mean) == 0):
            EXIO_imp_es_df_mean[ec_service, sector] = 0
            EXIO_imp_es_df_min[ec_service, sector] = 0
            EXIO_imp_es_df_max[ec_service, sector] = 0
        else:
            EXIO_imp_es_df_mean.loc[ec_service, sector] = np.mean(np.array(es_sector_array_mean))
            EXIO_imp_es_df_min.loc[ec_service, sector] = np.mean(np.array(es_sector_array_min))
            EXIO_imp_es_df_max.loc[ec_service, sector] = np.mean(np.array(es_sector_array_max))

# save the EXIOBASE sector scope 1 impacts as they will be needed later on
EXIO_imp_es_df_mean.to_csv('../Data/Impacts/Impact Scores/EXIOBASE_sectors_scope_1_impact_scores_mean.csv', index=True, header=True)
EXIO_imp_es_df_min.to_csv('../Data/Impacts/Impact Scores/EXIOBASE_sectors_scope_1_impact_scores_min.csv', index=True, header=True)
EXIO_imp_es_df_max.to_csv('../Data/Impacts/Impact Scores/EXIOBASE_sectors_scope_1_impact_scores_max.csv', index=True, header=True)


####################################
# Calculate upstream
###############################

# calculate Leontief inverse
# get the IO table to numpy array
L_matrix = EXIO3.L.to_numpy()

### calculate overlined((L -1)), relative impact impact matrix
L_min_I = L_matrix - np.eye(L_matrix.shape[0])
col_sums = np.sum(L_min_I, axis=0)
with np.errstate(divide='ignore', invalid='ignore'):
    rel_imp_array = np.where(col_sums == 0, 0, np.divide(L_min_I, col_sums[None, :]))


### calculate the upstream impacts matrix
# create the upstream impact dataframe from the EXIO_imp_df
upstream_imp_es_df_mean = pd.DataFrame(index=ENCORE_ecosystem_services, columns=EXIO3.L.columns)
upstream_imp_es_df_min = pd.DataFrame(index=ENCORE_ecosystem_services, columns=EXIO3.L.columns)
upstream_imp_es_df_max = pd.DataFrame(index=ENCORE_ecosystem_services, columns=EXIO3.L.columns)

# for calculating the upstream impacts, the EXIO_dep_array needs to be adjusted to the dimension 21x(163*49)
EXIO_imp_all_countries_mean = np.tile(EXIO_imp_es_df_mean.to_numpy(), (1, 49))
EXIO_imp_all_countries_min = np.tile(EXIO_imp_es_df_min.to_numpy(), (1, 49))
EXIO_imp_all_countries_max = np.tile(EXIO_imp_es_df_max.to_numpy(), (1, 49))

# calculate the upstream impacts matrix
upstream_imp_mean = np.matmul(EXIO_imp_all_countries_mean, rel_imp_array)
upstream_imp_min = np.matmul(EXIO_imp_all_countries_min, rel_imp_array)
upstream_imp_max = np.matmul(EXIO_imp_all_countries_max, rel_imp_array)

# store relative impacts in df
upstream_imp_es_df_mean.loc[:, :] = upstream_imp_mean
upstream_imp_es_df_min.loc[:, :] = upstream_imp_min
upstream_imp_es_df_max.loc[:, :] = upstream_imp_max


# save to csv file
upstream_imp_es_df_mean.to_csv('../Data/Impacts/Impact Scores/EXIOBASE_sectors_scope_3_impact_scores_mean.csv', index=True, header=True)
# upstream_dep_df.to_excel('../Data/EXIOBASE 3/EXIOBASE_sectors_scope_3_dependency_scores.xlsx', index=True, header=True)
upstream_imp_es_df_min.to_csv('../Data/Impacts/Impact Scores/EXIOBASE_sectors_scope_3_impact_scores_min.csv', index=True, header=True)
upstream_imp_es_df_max.to_csv('../Data/Impacts/Impact Scores/EXIOBASE_sectors_scope_3_impact_scores_max.csv', index=True, header=True)





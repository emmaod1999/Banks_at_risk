import pandas as pd
import numpy as np
import pymrio
from sys import exit
from Setup import EXIO_file_path, ENCORE_dep_path, ENCORE_to_EXIO_path, scope_1_path_mean, scope_1_path_min, \
    scope_1_path_max, scope_3_path_mean, scope_3_path_min, scope_3_path_max

# Read the MRIO table into a pandas DataFrame
EXIO3 = pymrio.parse_exiobase3(path=EXIO_file_path)
EXIO3.calc_all()

# get EXIOBASE sectors
EXIO_sectors = EXIO3.get_sectors().to_list()
EXIO_regions = EXIO3.get_regions().to_list()

# load ENCORE sectorial dependency scores
ENCORE_dep_df = pd.read_csv(ENCORE_dep_path, index_col=[0, 1], header=0,
                            usecols=['Process', 'Ecosystem Service', 'Rating Num'])
ENCORE_sectors = set(ENCORE_dep_df.index.get_level_values(0))

# load the ENCORE sector to EXIO sector conversion table
ENCORE_to_EXIO_df = pd.read_excel(ENCORE_to_EXIO_path, index_col=[5], header=[0], sheet_name='table_correspondance')
ENCORE_to_EXIO_df_restricted = ENCORE_to_EXIO_df.drop(labels=['Grandes catégories', 'Sector', 'Subindustry',
                                                              'Industry_group_benchmark', 'ID_Industry_group_benchmark',
                                                              'Exiobase_industry_group'], axis=1)

# drop non-unique values
# ENCORE_to_EXIO_df_restricted = ENCORE_to_EXIO_df_restricted[~ENCORE_to_EXIO_df_restricted.index.duplicated(keep='first')]
ENCORE_to_EXIO_df_restricted.sort_index(inplace=True)

# save the not included sectors
ENCORE_not_included_sectors = set(ENCORE_sectors) - set(ENCORE_to_EXIO_df_restricted.index.values)
EXIO_not_included_sectors = set(EXIO_sectors) - set(ENCORE_to_EXIO_df_restricted.loc[:, 'IndustryTypeName'])

# save the included sectors
ENCORE_included_sectors = ENCORE_sectors - ENCORE_not_included_sectors
EXIO_included_sectors = set(EXIO_sectors) - EXIO_not_included_sectors

# get restricted dataframe with only sectors which are included in the EXIOBASE
ENCORE_dep_restricted_df = ENCORE_dep_df.loc[np.unique(ENCORE_to_EXIO_df_restricted.index.values), :]
ENCORE_dep_restricted_df.sort_index(inplace=True)

# get ENCORE ecosystem services
ENCORE_ecosys_serv = np.unique(ENCORE_dep_restricted_df.index.get_level_values(1))

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

'''
### get the scope 1 dependency scores for the EXIOBASE sectors
'''
# create df for storing the EXIOBASE sector dependency scores
EXIO_dep_df_mean = pd.DataFrame(0, index=ENCORE_ecosys_serv, columns=EXIO_sectors)
EXIO_dep_df_min = pd.DataFrame(0, index=ENCORE_ecosys_serv, columns=EXIO_sectors)
EXIO_dep_df_max = pd.DataFrame(0, index=ENCORE_ecosys_serv, columns=EXIO_sectors)

# loop over services
for service in ENCORE_ecosys_serv:
    # loop over EXIOBASE_sectors
    for sector_EXIO in EXIO_included_sectors:
        service_sector_array = []

        # get associated ENCORE_sectors
        associated_ENCORE_df = EXIO_to_ENCORE_df.loc[sector_EXIO, :]

        # loop over associated ENCORE_sectors
        for sector_ENCORE in associated_ENCORE_df.index.values:

            # check if service is included
            if service in ENCORE_dep_restricted_df.loc[sector_ENCORE, :].index.values:
                poid = EXIO_to_ENCORE_df.loc[(sector_EXIO, sector_ENCORE), 'Poids']
                rating = ENCORE_dep_restricted_df.loc[(sector_ENCORE, service), 'Rating Num']
                service_sector_array.append(poid * rating)
                # exit
            else:
                service_sector_array.append(0)

        # store dependencies in dataframe
        EXIO_dep_df_mean.loc[service, sector_EXIO] = np.mean(np.array(service_sector_array))
        EXIO_dep_df_min.loc[service, sector_EXIO] = np.min(np.array(service_sector_array))
        EXIO_dep_df_max.loc[service, sector_EXIO] = np.max(np.array(service_sector_array))

# save the EXIOBASE sector scope 1 dependencies as they will be needed later on
EXIO_dep_df_mean.to_csv(scope_1_path_mean, index=True, header=True)
EXIO_dep_df_min.to_csv(scope_1_path_min, index=True, header=True)
EXIO_dep_df_max.to_csv(scope_1_path_max, index=True, header=True)

'''
### calculate scope 3 dependecy scores
'''

# calculate Leontief inverse
# get the IO table to numpy array
L_matrix = EXIO3.L.to_numpy()

### calculate overlined((L -1)), relative imapct dependency matrix
L_min_I = L_matrix - np.eye(L_matrix.shape[0])
col_sums = np.sum(L_min_I, axis=0)
with np.errstate(divide='ignore', invalid='ignore'):
    rel_imp_array = np.where(col_sums == 0, 0, np.divide(L_min_I, col_sums[None, :]))

### calcualte the upstream dependency matirx
# create the upstream dependency dataframe from the EXIO_dep_df
upstream_dep_df_mean = pd.DataFrame(index=ENCORE_ecosys_serv, columns=EXIO3.L.columns)
upstream_dep_df_min = pd.DataFrame(index=ENCORE_ecosys_serv, columns=EXIO3.L.columns)
upstream_dep_df_max = pd.DataFrame(index=ENCORE_ecosys_serv, columns=EXIO3.L.columns)

# for calculating the upstream dependencies, the EXIO_dep_array needs to be adjusted to the dimension 21x(163*49)
EXIO_dep_all_countries_mean = np.tile(EXIO_dep_df_mean.to_numpy(), (1, 49))
EXIO_dep_all_countries_min = np.tile(EXIO_dep_df_min.to_numpy(), (1, 49))
EXIO_dep_all_countries_max = np.tile(EXIO_dep_df_max.to_numpy(), (1, 49))

# calculate the upstream dependencies matrix
upstream_dep_mean = np.matmul(EXIO_dep_all_countries_mean, rel_imp_array)
upstream_dep_min = np.matmul(EXIO_dep_all_countries_min, rel_imp_array)
upstream_dep_max = np.matmul(EXIO_dep_all_countries_max, rel_imp_array)

# store relative dependencies in df
upstream_dep_df_mean.loc[:, :] = upstream_dep_mean
upstream_dep_df_min.loc[:, :] = upstream_dep_min
upstream_dep_df_max.loc[:, :] = upstream_dep_max

# save to csv file
upstream_dep_df_mean.to_csv(scope_3_path_mean, index=True, header=True)
upstream_dep_df_mean.to_excel(
    '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_dependency_scores_mean.xlsx', index=True,
    header=True)

upstream_dep_df_min.to_csv('../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_dependency_scores_min.csv',
                           index=True, header=True)
upstream_dep_df_min.to_excel(
    '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_dependency_scores_min.xlsx', index=True,
    header=True)

upstream_dep_df_max.to_csv('../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_dependency_scores_max.csv',
                           index=True, header=True)
upstream_dep_df_max.to_excel(
    '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_dependency_scores_max.xlsx', index=True,
    header=True)

'''
### get scope 3 dependencies for the UK economy
'''
# UK_sub = upstream_dep_df.loc[:, 'GB']
# UK_sub.to_csv('../../Data/EXIOBASE 3/EXIOBASE_sectors_UK_scope_3_dependency_scores.csv', index=True, header=True)
# UK_sub.to_excel('../../Data/EXIOBASE 3/EXIOBASE_sectors_UK_scope_3_dependency_scores.xlsx', index=True, header=True)
#
# # calculate the maximum influences
# max_influences_df = pd.DataFrame(index=UK_sub.columns.values, columns=['Maximum sector', 'Dependency'])
#
# max_influences_df.loc[:, 'Maximum sector'] = UK_sub.idxmax()
# max_influences_df.loc[:, 'Dependency'] = UK_sub.max()
#
# max_influences_df.to_csv('../../Data/EXIOBASE 3/EXIOBASE_sectors_UK_scope_3_max_dependency.csv', index=True, header=True)
# max_influences_df.to_excel('../../Data/EXIOBASE 3/EXIOBASE_sectors_UK_scope_3_max_dependency.xlsx', index=True, header=True)

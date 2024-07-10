import pandas as pd
import numpy as np
import re
import os
from Setup import scope_1_path_min_dep, scope_1_path_mean_dep, scope_1_path_max_dep, scope_1_path_max_imp, \
    scope_1_path_min_imp, scope_3_path_min_imp, scope_3_path_max_imp, scope_3_path_min_dep, scope_3_path_max_dep, \
    scope_1_path_mean_imp, scope_3_path_mean_imp, scope_3_path_mean_dep, NACE_to_EXIO_path, \
    NACE_letters_path,dependency_score_saving_path, \
    impact_score_saving_path
    # combined_score_saving_path
from helper_convert_to_NACE import convert_EXIO_to_NACE


# converting EXIOBASE TO NACE
# convert EXIOBASE sectors to NACE Sectors
NACE_categories_df = pd.read_excel(NACE_to_EXIO_path, index_col=[0], header=0)
NACE_categories_df.reset_index(inplace=True)
Letters_and_EXIO_sectors_df = NACE_categories_df.loc[NACE_categories_df["Level"] == 1]
Letters_and_EXIO_sectors_df.drop(columns=['Level', 'Unnamed: 2', 'Unnamed: 3'], inplace=True)

# get sectors and regions from upstream
scope_3_impact_mean_df = pd.read_csv(scope_3_path_max_imp, index_col=[0], header=[0, 1])

# get EXIO regions, sectors and ecosystem services
EXIO_regions = list(set(scope_3_impact_mean_df.columns.get_level_values(0)))
EXIO_sectors = list(set(scope_3_impact_mean_df.columns.get_level_values(1)))
ESSs = scope_3_impact_mean_df.index.values
# convert to row of sectors and letter
NACE_EXIO_sectors = pd.DataFrame(0, index=EXIO_sectors, columns=['Code'])
# add the NACE sector to code column
for code in Letters_and_EXIO_sectors_df['Code'].unique().tolist() :
    for column in Letters_and_EXIO_sectors_df.columns.tolist() :
        sector = Letters_and_EXIO_sectors_df.loc[Letters_and_EXIO_sectors_df["Code"] == code, column].item()
        if(pd.notna(sector) and sector != code) :
            NACE_EXIO_sectors['Code'].loc[sector] = code
NACE_EXIO_sectors[NACE_EXIO_sectors["Code"] == 0] = 'E'

# for upstream (with regions)
EXIO_sector_regions = pd.DataFrame(0, index=scope_3_impact_mean_df.columns, columns=['Test'])
NACE_EXIO_sectors.index.name = "sector"
EXIO_sector_regions_NACE = pd.merge(EXIO_sector_regions,NACE_EXIO_sectors, right_index=True, left_index=True)
EXIO_sector_regions_NACE.drop(columns='Test', inplace=True)

# Convert descriptions to letters
NACE_letters_df = pd.read_csv(NACE_letters_path, index_col=[0], header=None)
NACE_letters_df.reset_index(inplace=True)
NACE_letters_df.rename(columns={0:"Code", 1:"Sector"}, inplace=True)


# load dependency score pre - finance and impact score pre-finance
# dependency
# load all scope 1 and upstream impact and dependency scores from paths
# dependency
scope_1_dependency_mean_df = pd.read_csv(scope_1_path_mean_dep, index_col=[0], header=[0])
scope_1_dependency_min_df = pd.read_csv(scope_1_path_min_dep, index_col=[0], header=[0])
scope_1_dependency_max_df = pd.read_csv(scope_1_path_max_dep, index_col=[0], header=[0])

scope_3_dependency_mean_df = pd.read_csv(scope_3_path_mean_dep, index_col=[0], header=[0, 1])
scope_3_dependency_min_df = pd.read_csv(scope_3_path_min_dep, index_col=[0], header=[0, 1])
scope_3_dependency_max_df = pd.read_csv(scope_3_path_max_dep, index_col=[0], header=[0, 1])

# impact
scope_1_impact_mean_df = pd.read_csv(scope_1_path_mean_imp, index_col=[0], header=[0])
scope_1_impact_min_df = pd.read_csv(scope_1_path_min_imp, index_col=[0], header=[0])
scope_1_impact_max_df = pd.read_csv(scope_1_path_max_imp, index_col=[0], header=[0])

scope_3_impact_mean_df = pd.read_csv(scope_3_path_mean_imp, index_col=[0], header=[0, 1])
scope_3_impact_min_df = pd.read_csv(scope_3_path_min_imp, index_col=[0], header=[0, 1])
scope_3_impact_max_df = pd.read_csv(scope_3_path_max_imp, index_col=[0], header=[0, 1])


# Add another column index for NACE category for each score
# group by NACE sector and mean, min or max accordingly

# dependency
scp_1_dep_scores = []
# scope 1
# mean
scope_1_type = "code_only"
scope_1_dependency_mean_T_NACE_df = convert_EXIO_to_NACE(scope_1_dependency_mean_df,NACE_EXIO_sectors, scope_1_type, 'mean')
scope_1_dependency_mean_T_NACE_df.name = 'scope_1_dep_mean'
scp_1_dep_scores.append(scope_1_dependency_mean_T_NACE_df)
# min
scope_1_dependency_min_T_NACE_df = convert_EXIO_to_NACE(scope_1_dependency_min_df,NACE_EXIO_sectors, scope_1_type, 'min')
scope_1_dependency_min_T_NACE_df.name = 'scope_1_dep_min'
scp_1_dep_scores.append(scope_1_dependency_min_T_NACE_df)

# max
scope_1_dependency_max_T_NACE_df = convert_EXIO_to_NACE(scope_1_dependency_max_df,NACE_EXIO_sectors, scope_1_type, 'max')
scope_1_dependency_max_T_NACE_df.name = 'scope_1_dep_max'
scp_1_dep_scores.append(scope_1_dependency_max_T_NACE_df)

# scope 3
scp_3_dep_scores = []
# mean
scope_3_type = "region_code"
scope_3_dependency_mean_T_NACE_df = convert_EXIO_to_NACE(scope_3_dependency_mean_df, EXIO_sector_regions_NACE, scope_3_type, 'mean')
scope_3_dependency_mean_T_NACE_df.name = 'scope_3_dep_mean'
scp_3_dep_scores.append(scope_3_dependency_mean_T_NACE_df)
# min
scope_3_dependency_min_T_NACE_df = convert_EXIO_to_NACE(scope_3_dependency_min_df, EXIO_sector_regions_NACE, scope_3_type, 'min')
scope_3_dependency_min_T_NACE_df.name = 'scope_3_dep_min'
scp_3_dep_scores.append(scope_3_dependency_min_T_NACE_df)
# max
scope_3_dependency_max_T_NACE_df = convert_EXIO_to_NACE(scope_3_dependency_max_df, EXIO_sector_regions_NACE, scope_3_type, 'max')
scope_3_dependency_max_T_NACE_df.name = 'scope_3_dep_max'
scp_3_dep_scores.append(scope_3_dependency_max_T_NACE_df)

# impacts
# scope 1
scp_1_imp_scores = []
# mean
scope_1_impact_mean_T_NACE_df = convert_EXIO_to_NACE(scope_1_impact_mean_df,NACE_EXIO_sectors, scope_1_type, 'mean')
scope_1_impact_mean_T_NACE_df.name = 'scope_1_imp_mean'
scp_1_imp_scores.append(scope_1_impact_mean_T_NACE_df)
# min
scope_1_impact_min_T_NACE_df = convert_EXIO_to_NACE(scope_1_impact_min_df,NACE_EXIO_sectors, scope_1_type, 'min')
scope_1_impact_min_T_NACE_df.name = 'scope_1_imp_min'
scp_1_imp_scores.append(scope_1_impact_min_T_NACE_df)
# max
scope_1_impact_max_T_NACE_df = convert_EXIO_to_NACE(scope_1_impact_max_df, NACE_EXIO_sectors, scope_1_type, 'max')
scope_1_impact_max_T_NACE_df.name = 'scope_1_imp_max'
scp_1_imp_scores.append(scope_1_impact_max_T_NACE_df)

# scope 3
scp_3_imp_scores = []
# mean
scope_3_impact_mean_T_NACE_df = convert_EXIO_to_NACE(scope_3_impact_mean_df, EXIO_sector_regions_NACE, scope_3_type, 'mean')
scope_3_impact_mean_T_NACE_df.name = 'scope_3_imp_mean'
scp_3_imp_scores.append(scope_3_impact_mean_T_NACE_df)
# min
scope_3_impact_min_T_NACE_df = convert_EXIO_to_NACE(scope_3_impact_min_df, EXIO_sector_regions_NACE, scope_3_type, 'min')
scope_3_impact_min_T_NACE_df.name = 'scope_3_imp_min'
scp_3_imp_scores.append(scope_3_impact_min_T_NACE_df)
# max
scope_3_impact_max_T_NACE_df = convert_EXIO_to_NACE(scope_3_impact_max_df, EXIO_sector_regions_NACE, scope_3_type, 'max')
scope_3_impact_max_T_NACE_df.name = 'scope_3_imp_max'
scp_3_imp_scores.append(scope_3_impact_max_T_NACE_df)

for score in scp_1_dep_scores:
    score.to_csv(f'{dependency_score_saving_path}/{score.name}_NACE.csv')

for score in scp_1_imp_scores:
    score.to_csv(f'{impact_score_saving_path}/{score.name}_NACE.csv')

for score in scp_3_dep_scores:
    score.to_csv(f'{dependency_score_saving_path}/{score.name}_NACE.csv')

for score in scp_3_imp_scores:
    score.to_csv(f'{impact_score_saving_path}/{score.name}_NACE.csv')


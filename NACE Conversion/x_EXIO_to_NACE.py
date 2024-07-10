import numpy as np
import pandas as pd
import re
import os
import pymrio
from Setup import (EXIO_file_path, finance_data_path, finance_exio_region_path, upstream_impact_mean_path,\
    NACE_letters_path, NACE_to_EXIO_path, I_NACE_saving_path, L_NACE_saving_path, x_NACE_saving_path)

# load EXIOBASE for Leontief inverse - for upstream
# calculate Leontief inverse
# get the IO table to numpy array
# Read the MRIO table into a pandas DataFrame
EXIO3 = pymrio.parse_exiobase3(path=EXIO_file_path)
EXIO3.calc_all()

# get EXIOBASE sectors
EXIO_sectors = EXIO3.get_sectors().to_list()
EXIO_regions = EXIO3.get_regions().to_list()
L_matrix = EXIO3.L.to_numpy()
L_df = EXIO3.L

# convert weighted average Leontief to NACE
# filter rel_imp_array by NACE
# add le
# convert EXIOBASE sectors to NACE Sectors
NACE_categories_df = pd.read_excel(NACE_to_EXIO_path, index_col=[0], header=0)
NACE_categories_df.reset_index(inplace=True)
Letters_and_EXIO_sectors_df = NACE_categories_df.loc[NACE_categories_df["Level"] == 1]
Letters_and_EXIO_sectors_df.drop(columns=['Level', 'Unnamed: 2', 'Unnamed: 3'], inplace=True)

# get sectors and regions from upstream
scope_3_impact_mean_df = pd.read_csv(upstream_impact_mean_path, index_col=[0], header=[0, 1])

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

# # reset the index
L_flat_df = L_df.reset_index()
# transpose it
L_flat_df_T = L_flat_df.transpose()
L_flat_df_T.reset_index(inplace=True)
# add the NACE codes as a column
EXIO_sector_regions_NACE_flat = EXIO_sector_regions_NACE.reset_index()
L_NACE_T_df = pd.merge(L_flat_df_T, EXIO_sector_regions_NACE_flat, on=['sector', 'region'])
L_NACE_df_T = L_NACE_T_df.groupby(['region', 'Code']).sum()

# drop the sector column
L_NACE_df_T_2 = L_NACE_T_df.drop(columns='sector').set_index(['region', 'Code'])
# add column names
flat_region_sector = L_df.index.to_flat_index().tolist()
L_NACE_df_T_3 = L_NACE_df_T_2.set_axis(flat_region_sector, axis=1)
# transpose the group the other columns
L_NACE_one_side_df = L_NACE_df_T_3.transpose()
L_NACE_one_side_df.reset_index(inplace=True)
# B_NACE_one_side_df['sector'] = B_NACE_one_side_df['index'][5:(len(B_NACE_one_side_df['index']) - 1)]
L_NACE_one_side_df['region'] = L_NACE_one_side_df['index']
L_NACE_one_side_df['sector'] = L_NACE_one_side_df['index']

for row in range(np.shape(L_NACE_one_side_df)[0]):
    L_NACE_one_side_df.loc[row, 'region'] = L_NACE_one_side_df['index'].values[row][0]
    L_NACE_one_side_df.loc[row, 'sector'] = L_NACE_one_side_df['index'].values[row][1]

L_NACE_one_side_df.drop(columns='index', inplace=True)

# add NACE code
NACE_EXIO_dict = NACE_EXIO_sectors.to_dict('dict')
NACE_EXIO_sector_dict = NACE_EXIO_dict.get("Code")
for row in range(np.shape(L_NACE_one_side_df)[0]):
    L_NACE_one_side_df.loc[row, 'Code'] = NACE_EXIO_sector_dict.get(L_NACE_one_side_df['sector'].loc[row])
# sum by the region and code on the other side
L_NACE_df = L_NACE_one_side_df.groupby(['region', 'Code']).sum()
L_NACE_df.drop(columns='sector', inplace=True)
L_NACE_df = L_NACE_df.T.reset_index().groupby(['region', 'Code']).sum().T



# convert I_full into NACE
# collapse the Identity full matrix by the NACE categories
# get diagonal matrix
I_full = np.eye(L_df.shape[0])
I_NACE = L_df.copy()
I_NACE.loc[:, :] = I_full
# filter by NACE
# reset the index
I_NACE_flat_df = I_NACE.reset_index()
# transpose it
I_NACE_flat_df_T = I_NACE_flat_df.transpose()
I_NACE_flat_df_T.reset_index(inplace=True)
# add the NACE codes as a column
EXIO_sector_regions_NACE_flat = EXIO_sector_regions_NACE.reset_index()
I_NACE_flat_df_T = pd.merge(I_NACE_flat_df_T, EXIO_sector_regions_NACE_flat, on=['sector', 'region'])
I_NACE_flat_df_T = I_NACE_flat_df_T.groupby(['region', 'Code']).sum()
# drop the sector column
I_NACE_flat_df_T_2 = I_NACE_flat_df_T.drop(columns='sector')
# add column names
flat_region_sector = I_NACE.index.to_flat_index().tolist()
I_NACE_flat_df_T_3 = I_NACE_flat_df_T_2.set_axis(flat_region_sector, axis=1)
# transpose the group the other columns
I_NACE_one_side_df = I_NACE_flat_df_T_3.transpose()
I_NACE_one_side_df.reset_index(inplace=True)

I_NACE_one_side_df['region'] = I_NACE_one_side_df['index']
I_NACE_one_side_df['sector'] = I_NACE_one_side_df['index']

for row in range(np.shape(I_NACE_one_side_df)[0]):
    I_NACE_one_side_df.loc[row, 'region'] = I_NACE_one_side_df['index'].values[row][0]
    I_NACE_one_side_df.loc[row, 'sector'] = I_NACE_one_side_df['index'].values[row][1]

I_NACE_one_side_df.drop(columns='index', inplace=True)

for row in range(np.shape(I_NACE_one_side_df)[0]):
    I_NACE_one_side_df.loc[row, 'Code'] = NACE_EXIO_sector_dict.get(I_NACE_one_side_df['sector'].loc[row])
# sum by the region and code on the other side
I_NACE_df = I_NACE_one_side_df.groupby(['region', 'Code']).sum()
I_NACE_df.drop(columns='sector', inplace=True)

L_NACE_df.to_csv(L_NACE_saving_path)
I_NACE_df.to_csv(I_NACE_saving_path)


# convert x and v into NACE
x_df = EXIO3.x
x_df_2 = x_df.reset_index()
for row in range(np.shape(x_df_2)[0]):
    x_df_2.loc[row, 'Code'] = NACE_EXIO_sector_dict.get(x_df_2['sector'].loc[row])
x_NACE_df = x_df_2.groupby(['region', 'Code']).sum()
x_NACE_df.drop(columns='sector', inplace=True)

x_NACE_df.to_csv(x_NACE_saving_path)

# file paths for EXIOBASE and ENCORE
EXIO_file_path = '../Data/exiobase_download_online/IOT_2022_ixi.zip'
ENCORE_dep_path = '../Data/ENCORE_data/ENCORE_sector_dep_num.csv'
ENCORE_to_EXIO_path = '../Data/ENCORE_EXIOBASE_conversion/20201222_Benchmark-biodiv-systemic-risk-biodiversity_GICS-EXIOBASE-matching-table.xlsx'

# file path where the calculated dependencies are stored
scope_1_path_mean = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_1_dependency_scores_mean.csv'
scope_1_path_min = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_1_dependency_scores_min.csv'
scope_1_path_max = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_1_dependency_scores_max.csv'

scope_3_path_mean = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_dependency_scores_mean.csv'
scope_3_path_min = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_dependency_scores_min.csv'
scope_3_path_max = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_dependency_scores_max.csv'

# file path where the calculated total value at risk are stored
value_at_risk_scope_1_path_mean = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_1_value_at_risk_mean.csv'
value_at_risk_scope_1_path_min = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_1_value_at_risk_min.csv'
value_at_risk_scope_1_path_max = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_1_value_at_risk_max.csv'

value_at_risk_scope_3_path_mean = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_value_at_risk_mean.csv'
value_at_risk_scope_3_path_min = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_value_at_risk_min.csv'
value_at_risk_scope_3_path_max = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_value_at_risk_max.csv'


'''
############################################
For Sorting
############################################
'''
EXIO_categories_path = '../Data/exiobase_download_online/EXIOBASE20i_7sectors.txt'
NACE_categories_path = '../Data/exiobase_download_online/NACE2full_EXIOBASEp.xlsx'

value_at_risk_grouped_scope_1_path = \
    '../Data/Dependencies/Dependency Scores/EXIOBASE_grouped_value_at_risk_scope_1.csv'
value_at_risk_grouped_scope_3_path = \
    '../Data/Dependencies/Dependency Scores/EXIOBASE_grouped_value_at_risk_scope_3.csv'

heatmap_country_value_at_risk_sorted_scope1_path = \
    '../Data/Dependencies/Dependency Scores/Plots/{}_value_at_risk_grouped_scope_1.pdf'
heatmap_country_value_at_risk_sorted_scope3_path = \
    '../Data/Dependencies/Dependency Scores/Plots/{}_value_at_risk_grouped_scope_3.pdf'

'''
############################################
For Visualization
############################################
'''
# path for the encoding of the sectors
encoding_path = '../Data/exiobase_download_online/IOT_2022_ixi/industries.txt'

# saving path for the plots
heatmap_country_scope1_path = '../../Data/Dependencies/Dependency Scores/Plots/{}_EXIOBASE_scope1_impact_analysis.pdf'
heatmap_country_scope3_path = '../../Data/Dependencies/Dependency Scores/Plots/{}_EXIOBASE_scope3_impact_analysis.pdf'
heatmap_country_value_at_risk_scope1_path = \
    '../../Data/Dependencies/Dependency Scores/Plots/{}_value_at_risk_EXIOBASE_scope_1.pdf '
heatmap_country_value_at_risk_scope3_path = \
    '../../Data/Dependencies/Dependency Scores/Plots/{}_value_at_risk_EXIOBASE_scope_3.pdf'

# saving paths for global maps
global_map_value_at_risk_scope1_path = \
    '../../Data/Dependencies/Dependency Scores/Geo Plots/{}_{}_value_at_risk_scope_1.pdf'
global_map_value_at_risk_scope3_path = \
    '../../Data/Dependencies/Dependency Scores/Geo Plots/{}_{}_value_at_risk_scope_3.pdf'


# for tests
scope_1_path = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_1_dependency_scores_mean.csv'
scope_3_path = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_dependency_scores_mean.csv'
value_at_risk_scope_1_path = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_1_value_at_risk_mean.csv'
value_at_risk_scope_3_path = '../Data/Dependencies/Dependency Scores/EXIOBASE_sectors_scope_3_value_at_risk_mean.csv'

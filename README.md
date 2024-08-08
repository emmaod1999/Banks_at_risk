# Banks_at_risk
Code and Publicly Available Data for "Banks at Risk: Materially Increasing Risk Due to Financed Nature Degradation" paper 

This is the code for the research presented in "Banks at Risk: Materially Increasing Risk Due to Financed Nature Degradation" available at: [INSERT LINK HERE]

The code was written on a Windows 11 Home Operating System (OS Build: 22631.3880) using JetBrains PyCharm 2023.2.4 and Python 3.9.13. No non-standard hardware is required. Install time on a "normal" computer should be minimal. 

The financial data is not included here to keep the banks used in the paper anonymous but can be gathered in Pillar 3 reporting from banks in Table CQ4 and CQ5. The template for the format of the data is in the financial_data folder in the financial_data_no_K.csv file and the file should populated with relevant Bank data. A demo file is included with example bank data to run the analysis. 

The EXIOBASE depository is also not included and can be downloaded (IOT_2022_ixi.zip) here: https://zenodo.org/records/5589597

Put the EXIOBASE zipfile in the exiobase_download_online folder in the Data depository.

Install the requirements in requirements.txt 

The scripts should be run in the following order:
1. Dependencies/EXIO_Dependencies.py
2. Impacts/EXIO_impact_on_ES.py
3. NACE Conversion/EXIO_to_NACE.py
4. NACE Conversion/x_EXIO_to_NACE.py
5. Value at Risk/value_at_risk_finance.py
6. Value at Risk Analysis/value_at_risk_analysis_clean.py

Run time is approximately 30 minutes on a "normal" desktop computer. 

Expected output:

The two figures in the main text should be generated in  "Data/Value at Risk Figures/", the bank-level sector heatmap figure available in the supplementary materials should be generated in "Data/Value at Risk Figures/Sector" and the significance values should be generated in  "Data/Value at Risk Figures/Value at Risk Significance" as excel files. 

Code Description:

Dependencies/EXIO_Dependencies.py: This code converts the ENCORE materiality dependency ratings from qualitative ratings to quantitative ranks and converts the ENCORE production processes to EXIOBASE sectors for upstream value chain analysis. The resulting data is a matrix of EXIOBASE sectors and their quantitative dependency score (0-1) for each ecosystem service.  

Impacts/EXIO_impact_on_ES.py: This code converts the ENCORE materiality impact ratings for impact drivers from qualitative ratings to quantitative ranks and converts the ENCORE production processes to EXIOBASE sectors for upstream value chain analysis. The influence of the drivers of environmental change are converted from qualitative ratings to quantitative ratings and are multiplied to the impact driver ENCORE impact score. The importance of natural capital assets to the provision of ecosystem services is converted from qualitative to quantitative ranks and are multiplied by the resulting influence and impact score. The resulting data is a matrix of EXIOBASE sectors and their quantitative impact score (0-1) for each ecosystem service.  

NACE Conversion/EXIO_to_NACE.py: This code converts the EXIOBASE sectors to NACE letter categories used in the Pillar 3 reporting for the impact and dependency score. 

NACE Conversion/x_EXIO_to_NACE.py: This code converts the EXIOBASE sectors to NACE letter categories used in the Pillar 3 reporting for the EXIOBASE components (primiarly the Leontief matrix) to allow for upstream value chain analysis. 

Value at Risk/value_at_risk_finance.py

This code combines the financial information from the Pillar 3 reporting with the impact and dependency score and then combines the resulting financial impact and dependency on each ecosystem service in each region to calculate the impact feedback intensity metric for each bank's loan portfolio.

Value at Risk Analysis/value_at_risk_analysis_clean.py

This code analyzes the results of the impact feedback intensity metric calculations from above and compiles figures displaying the results and runs statistical tests. 

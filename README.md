# Banks_at_risk
Code and Publicly Available Data for "Banks at Risk: Materially Increasing Risk Due to Financed Nature Degradation" paper 

This is the code for the research presented in "Banks at Risk: Materially Increasing Risk Due to Financed Nature Degradation" available at:

The financial data is not included here to keep the banks used in the paper anonymous but can be gathered in Pillar 3 reporting from banks in Table CQ4 and CQ5. The template for the format of the data is in the financial_data folder in the financial_data_no_K.csv file and the file should populated with relevant Bank data. 

The EXIOBASE depository is also not included and can be downloaded (IOT_2022_ixi.zip) here: https://zenodo.org/records/5589597

Put the EXIOBASE zipfile in the exiobase_download_online folder in the Data depository.

The scripts should be run in the following order:
1. Dependencies/EXIO_Dependencies.py
2. Impacts/EXIO_impact_on_ES.py
3. NACE Conversion/NACE_EXIO_to_NACE.py
4. NACE Conversion/x_EXIO_to_NACE.py
5. Value at Risk/value_at_risk_finance.py
6. Value at Risk Analysis/value_at_risk_analysis_clean.py

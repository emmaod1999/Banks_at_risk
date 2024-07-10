# Banks_at_risk
Code and Publicly Available Data for "Banks at Risk: Materially Increasing Risk Due to Financed Nature Degradation" paper 

This is the code for the research presented in "Banks at Risk: Materially Increasing Risk Due to Financed Nature Degradation" available at:

The financial data is not included here to keep the banks used in the paper anonymous but can be gathered in Pillar 3 reporting from banks in Table CQ4 and CQ5. The template for the format of the data is in the financial_data folder in the financial_data_no_K.csv file and the file should populated with relevant Bank data. 

The scripts should be run in the following order:
1. EXIO_Dependencies.py
2. EXIO_impact_on_ES.py
3. EXIO_to_NACE.py
4. x_EXIO_to_NACE.py
5. value_at_risk_finance.py
6. value_at_risk_analysis_clean.py

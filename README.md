Data Analyst Intern MLS Analytics Project - IDX Exchange, 2026
Residential Real Estate Market Analytics Pipeline

This project was completed as part of my Data Analyst Internship with IDX Exchange. The goal of the project was to build an end-to-end analytics workflow for residential real estate market data from the production environment foucusing on California, starting from raw MLS transaction and listing records and transforming them into cleaned datasets, market metrics, and Tableau dashboards, then finally a qualitative report.


Project Descirption:
The project focuses on California residential MLS data, including both listing records and sold transaction records. I worked through the full data preparation and analytics pipeline: combining monthly CSV files, validating data quality, cleaning key fields, engineering real estate market indicators, detecting outliers, and preparing dashboard-ready datasets.
The final outputs support market analysis and competitive intelligence, including trends in home prices, days on market, sales volume, new listings, price-per-square-foot, and listing agent or brokerage performance.


Main Work Completed：
- Aggregated monthly MLS listing and sold transaction files into combined datasets.
- Filtered and cleaned residential real estate records for analysis.
- Standardized date, price, size, geographic, and categorical fields.
- Handled missing values and flagged invalid records without overwriting the raw data.
- Engineered key market metrics such as price ratios, price per square foot, days on market, and monthly time variables.
- Applied IQR-based outlier detection to improve the reliability of downstream analysis.
- Prepared Tableau-ready datasets for market trend and competitive analysis dashboards.


Tools Used
- Python
- Pandas
- Tableau
- CSV-based data pipeline
- FileZilla - accessing remote web server and database
- Codex


Dashboard Focus：
The Tableau portion of the project includes two main analytical views:

Market Analysis: 
Tracks monthly median close price, average days on market, close-to-original-list ratio, new listings, and closed sales.
https://public.tableau.com/app/profile/junyu.liao/viz/Market_Analysis_17879901057830/Dashboard1

Competitive Analysis: 
Identifies top listing agents and brokerages by sales volume and transaction count, with geographic views by ZIP code.
https://public.tableau.com/app/profile/junyu.liao/viz/Competitive_Analysis_17879932879190/Dashboard1

Final 1-page Report:
Week11-12/1Page_MarketIntelligenceReport_JunyuLiao.docx

P.S. For reasons of file size and information confidentiality, most of original MLS datasets are confidential and are not included in this repo. This repository focuses on the project structure, cleaning scripts, feature engineering workflow, and dashboard preparation process, with final reports and dashboards summerized.

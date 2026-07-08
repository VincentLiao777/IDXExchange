# MRE = Mortgage Rate Enrichment


import pandas as pd

sold = pd.read_csv(r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\Sold_Concated.csv", low_memory=False, encoding = 'latin1')
listings = pd.read_csv(r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\Listing_Concated.csv", low_memory=False, encoding = 'latin1')
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"

mortgage = pd.read_csv(url, parse_dates=["observation_date"])
mortgage.columns = ["date", "rate_30yr_fixed"]
mortgage["rate_30yr_fixed"] = pd.to_numeric(
    mortgage["rate_30yr_fixed"], errors="coerce"
)

mortgage["year_month"] = mortgage["date"].dt.to_period("M")

mortgage_monthly = (
    mortgage.groupby("year_month")["rate_30yr_fixed"]
    .mean()
    .reset_index()
)

sold["CloseDate"] = pd.to_datetime(sold["CloseDate"], errors="coerce")
sold["year_month"] = sold["CloseDate"].dt.to_period("M")

sold_with_rates = sold.merge(mortgage_monthly, on="year_month", how="left")

print(sold_with_rates["rate_30yr_fixed"].isna().sum())
sold_with_rates.to_csv("sold_residential_with_mortgage_rates.csv", index=False)
import pandas as pd

sold = pd.read_csv(r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\Sold_Concated.csv", low_memory=False, encoding = 'latin1')
listings = pd.read_csv(r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\Listing_Concated.csv", low_memory=False, encoding = 'latin1')

print(sold.shape)
print(sold.dtypes)
print(sold["PropertyType"].value_counts(dropna=False))

sold = sold[sold["PropertyType"] == "Residential"].copy()
listings = listings[listings["PropertyType"] == "Residential"].copy()

missing = pd.DataFrame({
    "column": sold.columns,
    "missing_count": sold.isna().sum().values,
})
missing["missing_pct"] = missing["missing_count"] / len(sold)
missing["flag_gt_90pct_missing"] = missing["missing_pct"] > 0.90
missing.to_csv("sold_missing_report.csv", index=False)

numeric_cols = ["ClosePrice", "LivingArea", "DaysOnMarket"]
summary = sold[numeric_cols].apply(pd.to_numeric, errors="coerce").describe(
    percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
)
summary.to_csv("sold_numeric_summary.csv")



# Result:
# (639941, 82)
# BuyerAgentAOR                       str
# ListAgentAOR                        str
# Flooring                            str
# ViewYN                           object
# WaterfrontYN                     object
#                                  ...
# MiddleOrJuniorSchoolDistrict    float64
# OriginatingSystemName               str
# OriginatingSystemSubName            str
# BuyerAgencyCompensationType         str
# BuyerAgencyCompensation         float64
# Length: 82, dtype: object
# PropertyType
# Residential            430462
# ResidentialLease       146570
# Land                    20728
# ManufacturedInPark      17326
# ResidentialIncome       17134
# CommercialSale           3981
# CommercialLease          3320
# BusinessOpportunity       420
# Name: count, dtype: int64
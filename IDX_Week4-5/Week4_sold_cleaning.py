import os
import pandas as pd


input_file = "D:\\Data&Documents\\Berkeley\\Internship\\IDX Exchange\\IDX_Codes\\IDX_Week3\\sold_residential_with_mortgage_rates.csv"
output_folder = "D:\\Data&Documents\\Berkeley\\Internship\\IDX Exchange\\IDX_Codes\\IDX_Week4-5"
os.makedirs(output_folder, exist_ok=True)


sold = pd.read_csv(input_file, low_memory=False)
sold.columns = sold.columns.str.strip()

initial_rows = len(sold)
initial_cols = len(sold.columns)

print("Initial rows:", initial_rows)
print("Initial columns:", initial_cols)


# Convert date columns
# Date fields must be real datetime columns before we can check transaction order.
# ListingContractDate <= PurchaseContractDate <= CloseDate

date_columns = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]

for col in date_columns:
    if col in sold.columns:
        old_non_missing = sold[col].notna()
        sold[col] = pd.to_datetime(sold[col], errors="coerce")
        sold[col + "_parse_failed_flag"] = old_non_missing & sold[col].isna()


# Convert numeric columns
# Some price or size columns may be read as text from CSV.
# We must convert them before doing comparisons such as ClosePrice <= 0.

numeric_columns = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "LotSizeSquareFeet",
    "LotSizeArea",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "Latitude",
    "Longitude",
    "rate_30yr_fixed"
]

for col in numeric_columns:
    if col in sold.columns:
        sold[col] = (
            sold[col]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        sold[col] = pd.to_numeric(sold[col], errors="coerce")


# Fill missing category labels with "Unknown"
# We should avoid dropping rows with missing categorical values.
# These fields are mainly used for groupby or Tableau filters.

category_columns = [
    "PropertySubType",
    "CountyOrParish",
    "City",
    "PostalCode",
    "MLSAreaMajor",
    "ListOfficeName",
    "BuyerOfficeName",
    "ListAgentFirstName",
    "ListAgentLastName",
    "BuyerAgentFirstName",
    "BuyerAgentLastName",
    "MlsStatus",
    "StandardStatus"
]

for col in category_columns:
    if col in sold.columns:
        sold[col] = sold[col].astype("string").str.strip()
        sold[col] = sold[col].fillna("Unknown")
        sold[col] = sold[col].replace("", "Unknown")


# Create simple full-name fields
# Later competitive analysis needs top listing agents and buyer agents.
# Full names are easier to group than first/last names separately.

if "ListAgentFirstName" in sold.columns and "ListAgentLastName" in sold.columns:
    sold["ListAgentFullName"] = (
        sold["ListAgentFirstName"].fillna("").astype(str).str.strip()
        + " "
        + sold["ListAgentLastName"].fillna("").astype(str).str.strip()
    ).str.strip()
    sold["ListAgentFullName"] = sold["ListAgentFullName"].replace("", "Unknown")

if "BuyerAgentFirstName" in sold.columns and "BuyerAgentLastName" in sold.columns:
    sold["BuyerAgentFullName"] = (
        sold["BuyerAgentFirstName"].fillna("").astype(str).str.strip()
        + " "
        + sold["BuyerAgentLastName"].fillna("").astype(str).str.strip()
    ).str.strip()
    sold["BuyerAgentFullName"] = sold["BuyerAgentFullName"].replace("", "Unknown")


# Add invalid numeric value flags
# We do not mean-impute important numeric fields.
# If ClosePrice, LivingArea, or DaysOnMarket is invalid, the row can distort later metrics.

if "ClosePrice" in sold.columns:
    sold["invalid_close_price_flag"] = sold["ClosePrice"].isna() | (sold["ClosePrice"] <= 0)
else:
    sold["invalid_close_price_flag"] = True

if "LivingArea" in sold.columns:
    sold["invalid_living_area_flag"] = sold["LivingArea"].isna() | (sold["LivingArea"] <= 0)
else:
    sold["invalid_living_area_flag"] = True

if "DaysOnMarket" in sold.columns:
    sold["invalid_days_on_market_flag"] = sold["DaysOnMarket"].isna() | (sold["DaysOnMarket"] < 0)
else:
    sold["invalid_days_on_market_flag"] = True

if "BedroomsTotal" in sold.columns:
    sold["invalid_bedrooms_flag"] = sold["BedroomsTotal"].notna() & (sold["BedroomsTotal"] < 0)
else:
    sold["invalid_bedrooms_flag"] = False

if "BathroomsTotalInteger" in sold.columns:
    sold["invalid_bathrooms_flag"] = sold["BathroomsTotalInteger"].notna() & (sold["BathroomsTotalInteger"] < 0)
else:
    sold["invalid_bathrooms_flag"] = False


# Add date consistency flags
# A normal sold transaction should not close before it was listed.
# These flags help us find impossible timelines.

if "CloseDate" in sold.columns:
    sold["missing_close_date_flag"] = sold["CloseDate"].isna()
else:
    sold["missing_close_date_flag"] = True

if "ListingContractDate" in sold.columns:
    sold["missing_listing_contract_date_flag"] = sold["ListingContractDate"].isna()
else:
    sold["missing_listing_contract_date_flag"] = True

if "ListingContractDate" in sold.columns and "CloseDate" in sold.columns:
    sold["listing_after_close_flag"] = (
        sold["ListingContractDate"].notna()
        & sold["CloseDate"].notna()
        & (sold["ListingContractDate"] > sold["CloseDate"])
    )
else:
    sold["listing_after_close_flag"] = False

if "PurchaseContractDate" in sold.columns and "CloseDate" in sold.columns:
    sold["purchase_after_close_flag"] = (
        sold["PurchaseContractDate"].notna()
        & sold["CloseDate"].notna()
        & (sold["PurchaseContractDate"] > sold["CloseDate"])
    )
else:
    sold["purchase_after_close_flag"] = False

if "ListingContractDate" in sold.columns and "PurchaseContractDate" in sold.columns:
    sold["purchase_before_listing_flag"] = (
        sold["ListingContractDate"].notna()
        & sold["PurchaseContractDate"].notna()
        & (sold["PurchaseContractDate"] < sold["ListingContractDate"])
    )
else:
    sold["purchase_before_listing_flag"] = False

sold["negative_timeline_flag"] = (
    sold["listing_after_close_flag"]
    | sold["purchase_after_close_flag"]
    | sold["purchase_before_listing_flag"]
)

# Add geographic quality flags
# Latitude/Longitude are needed for map dashboards and school district joins.
# California longitude should be negative.
# The rough California coordinate range is:
# Latitude: 32 to 42.5
# Longitude: -124.5 to -114

if "Latitude" in sold.columns and "Longitude" in sold.columns:
    sold["missing_coordinates_flag"] = sold["Latitude"].isna() | sold["Longitude"].isna()
    sold["zero_coordinates_flag"] = (sold["Latitude"] == 0) | (sold["Longitude"] == 0)
    sold["longitude_positive_flag"] = sold["Longitude"] > 0
    sold["implausible_ca_coordinates_flag"] = (
        sold["Latitude"].notna()
        & sold["Longitude"].notna()
        & (
            (sold["Latitude"] < 32.0)
            | (sold["Latitude"] > 42.5)
            | (sold["Longitude"] < -124.5)
            | (sold["Longitude"] > -114.0)
        )
    )
else:
    sold["missing_coordinates_flag"] = True
    sold["zero_coordinates_flag"] = False
    sold["longitude_positive_flag"] = False
    sold["implausible_ca_coordinates_flag"] = False

sold["invalid_coordinates_flag"] = (
    sold["missing_coordinates_flag"]
    | sold["zero_coordinates_flag"]
    | sold["longitude_positive_flag"]
    | sold["implausible_ca_coordinates_flag"]
)


# Check sold status
# This is a sold dataset, so the status should usually be Closed or Sold.
# If not, the record may not be suitable for closed-sales analysis.

if "StandardStatus" in sold.columns:
    status_col = "StandardStatus"
elif "MlsStatus" in sold.columns:
    status_col = "MlsStatus"
else:
    status_col = None

if status_col is not None:
    sold["sold_status_not_closed_flag"] = ~sold[status_col].astype(str).str.lower().isin(["closed", "sold"])
else:
    sold["sold_status_not_closed_flag"] = False


# Save the full flagged data before row deletion.
sold.to_csv(os.path.join(output_folder, "sold_flagged_full.csv"), index=False)

# Drop columns
# We drop columns with more than 90% missing values, unless they are core fields.
# We also drop address/contact/metadata fields that are not needed for aggregate analysis.

protected_columns = [
    "ListingKey",
    "ListingId",
    "PropertyType",
    "PropertySubType",
    "MlsStatus",
    "StandardStatus",
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate",
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "LotSizeSquareFeet",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "Latitude",
    "Longitude",
    "CountyOrParish",
    "City",
    "PostalCode",
    "MLSAreaMajor",
    "ListAgentFirstName",
    "ListAgentLastName",
    "ListAgentFullName",
    "BuyerAgentFirstName",
    "BuyerAgentLastName",
    "BuyerAgentFullName",
    "ListOfficeName",
    "BuyerOfficeName",
    "year_month",
    "rate_30yr_fixed"
]

manual_drop_columns = [
    "UnparsedAddress",
    "StreetNumberNumeric",
    "StreetName",
    "StreetNumber",
    "StreetSuffix",
    "UnitNumber",
    "ListAgentEmail",
    "BuyerAgentEmail",
    "CoListAgentEmail",
    "CoBuyerAgentEmail",
    "OriginatingSystemName",
    "OriginatingSystemSubName",
    "SourceSystemName",
    "SourceSystemKey",
    "BuyerAgencyCompensation",
    "BuyerAgencyCompensationType",
    "CoListAgentFirstName",
    "CoListAgentLastName",
    "CoListOfficeName",
    "CoBuyerAgentFirstName",
    "CoBuyerAgentLastName",
    "CoBuyerOfficeName",
    "BusinessType"
]

drop_rows = []

missing_pct = sold.isna().mean()

for col in sold.columns:
    if missing_pct[col] > 0.90 and col not in protected_columns and not col.endswith("_flag"):
        drop_rows.append({
            "column": col,
            "reason": "more than 90% missing and not a core field",
            "missing_pct": missing_pct[col]
        })

for col in manual_drop_columns:
    if col in sold.columns:
        drop_rows.append({
            "column": col,
            "reason": "not needed for aggregate market analysis or privacy/metadata field",
            "missing_pct": missing_pct[col]
        })

drop_report = pd.DataFrame(drop_rows)

if len(drop_report) > 0:
    drop_report = drop_report.drop_duplicates(subset=["column"])
    columns_to_drop = list(drop_report["column"])
else:
    columns_to_drop = []

sold = sold.drop(columns=columns_to_drop, errors="ignore")

drop_report.to_csv(os.path.join(output_folder, "dropped_columns_report.csv"), index=False)


# Remove invalid rows for analysis-ready dataset
# We remove rows only when they break core analysis.
# This is not outlier removal. Outlier removal is Week 7.

remove_bad_rows = (
    sold["invalid_close_price_flag"]
    | sold["invalid_living_area_flag"]
    | sold["invalid_days_on_market_flag"]
    | sold["invalid_bedrooms_flag"]
    | sold["invalid_bathrooms_flag"]
    | sold["missing_close_date_flag"]
    | sold["missing_listing_contract_date_flag"]
    | sold["negative_timeline_flag"]
    | sold["sold_status_not_closed_flag"]
)

cleaned = sold[~remove_bad_rows].copy()

cleaned.to_csv(os.path.join(output_folder, "sold_cleaned_analysis_ready.csv"), index=False)


# Save separate geo-valid dataset
# Bad coordinates should not necessarily remove the row from normal price analysis.
# But map dashboards should use only valid coordinates.

geo_valid = cleaned[~cleaned["invalid_coordinates_flag"]].copy()
geo_valid.to_csv(os.path.join(output_folder, "sold_geo_valid.csv"), index=False)


# Save reports

# Flag counts
flag_columns = [col for col in sold.columns if col.endswith("_flag")]

flag_report_rows = []

for col in flag_columns:
    flag_report_rows.append({
        "flag": col,
        "true_count": sold[col].sum(),
        "true_pct": sold[col].mean()
    })

flag_report = pd.DataFrame(flag_report_rows)
flag_report = flag_report.sort_values("true_count", ascending=False)
flag_report.to_csv(os.path.join(output_folder, "flag_counts_report.csv"), index=False)


# Data type report
dtype_report = pd.DataFrame({
    "column": cleaned.columns,
    "dtype_after_cleaning": [str(cleaned[col].dtype) for col in cleaned.columns]
})
dtype_report.to_csv(os.path.join(output_folder, "data_type_report_after_cleaning.csv"), index=False)


# Geographic report
geo_report = pd.DataFrame({
    "geo_check": [
        "missing_coordinates_flag",
        "zero_coordinates_flag",
        "longitude_positive_flag",
        "implausible_ca_coordinates_flag",
        "invalid_coordinates_flag"
    ],
    "issue_count": [
        sold["missing_coordinates_flag"].sum(),
        sold["zero_coordinates_flag"].sum(),
        sold["longitude_positive_flag"].sum(),
        sold["implausible_ca_coordinates_flag"].sum(),
        sold["invalid_coordinates_flag"].sum()
    ],
    "issue_pct": [
        sold["missing_coordinates_flag"].mean(),
        sold["zero_coordinates_flag"].mean(),
        sold["longitude_positive_flag"].mean(),
        sold["implausible_ca_coordinates_flag"].mean(),
        sold["invalid_coordinates_flag"].mean()
    ]
})
geo_report.to_csv(os.path.join(output_folder, "geographic_quality_report.csv"), index=False)


# Summary text
summary_lines = []

summary_lines.append("IDX Week 4-5 Data Cleaning Summary")
summary_lines.append("=" * 40)
summary_lines.append("")
summary_lines.append("Input file: " + input_file)
summary_lines.append("")
summary_lines.append("Row counts:")
summary_lines.append("Initial rows: " + str(initial_rows))
summary_lines.append("Rows removed from analysis-ready dataset: " + str(remove_bad_rows.sum()))
summary_lines.append("Final cleaned rows: " + str(len(cleaned)))
summary_lines.append("Geo-valid rows: " + str(len(geo_valid)))
summary_lines.append("")
summary_lines.append("Column counts:")
summary_lines.append("Initial columns: " + str(initial_cols))
summary_lines.append("Dropped columns: " + str(len(columns_to_drop)))
summary_lines.append("Final cleaned columns: " + str(len(cleaned.columns)))
summary_lines.append("")
summary_lines.append("Cleaning choices:")
summary_lines.append("- Date columns were converted to datetime.")
summary_lines.append("- Numeric columns were converted to numeric.")
summary_lines.append("- Categorical missing values were filled as Unknown.")
summary_lines.append("- Core numeric fields were not mean/median-imputed.")
summary_lines.append("- Rows with invalid ClosePrice, LivingArea, DaysOnMarket, date timeline, or status were removed from the analysis-ready dataset.")
summary_lines.append("- Bad coordinates were flagged. They were not removed from the main cleaned dataset, but a separate geo-valid dataset was saved.")
summary_lines.append("- Extreme outliers were not removed here because IQR outlier filtering belongs to Week 7.")
summary_lines.append("")
summary_lines.append("Flag counts:")

for i in range(len(flag_report)):
    row = flag_report.iloc[i]
    summary_lines.append(
        "- " + row["flag"] + ": " + str(int(row["true_count"])) + " (" + "{:.2%}".format(row["true_pct"]) + ")"
    )

summary_text = "\n".join(summary_lines)

with open(os.path.join(output_folder, "cleaning_summary.txt"), "w", encoding="utf-8") as f:
    f.write(summary_text)

print("Cleaning complete.")
print("Cleaned rows:", len(cleaned))
print("Output folder:", output_folder)




"""
Initial rows: 665539
Initial columns: 84
Cleaning complete.
Cleaned rows: 528589

"""
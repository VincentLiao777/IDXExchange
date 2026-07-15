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



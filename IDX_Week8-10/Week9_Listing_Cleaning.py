import os
import pandas as pd


# 0. File paths

input_file = r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\Listing_Concated.csv"

output_folder = r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\IDX_Week8-10"
output_file = os.path.join(output_folder, "listings_cleaned_for_tableau.csv")

os.makedirs(output_folder, exist_ok=True)


# 1. Load data

listings = pd.read_csv(input_file, low_memory=False)
listings.columns = listings.columns.str.strip()

initial_rows = len(listings)
initial_columns = len(listings.columns)

print("Initial rows:", initial_rows)
print("Initial columns:", initial_columns)


# 2. Filter to Residential

if "PropertyType" in listings.columns:
    listings = listings[listings["PropertyType"] == "Residential"].copy()

print("Rows after Residential filter:", len(listings))


# 3. Convert date columns

date_columns = [
    "ListingContractDate",
    "CloseDate",
    "PurchaseContractDate",
    "ContractStatusChangeDate",
    "ModificationTimestamp",
    "OriginalEntryTimestamp",
    "OnMarketDate",
    "OffMarketDate",
    "WithdrawnDate",
    "CancelationDate",
    "ExpirationDate"
]

for col in date_columns:
    if col in listings.columns:
        listings[col] = pd.to_datetime(listings[col], errors="coerce")


# 4. Convert numeric columns

numeric_columns = [
    "ListPrice",
    "OriginalListPrice",
    "ClosePrice",
    "LivingArea",
    "LotSizeAcres",
    "LotSizeSquareFeet",
    "LotSizeArea",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "BathroomsFull",
    "BathroomsHalf",
    "DaysOnMarket",
    "CumulativeDaysOnMarket",
    "YearBuilt",
    "Latitude",
    "Longitude",
    "GarageSpaces",
    "ParkingTotal",
    "Stories",
    "AssociationFee"
]

for col in numeric_columns:
    if col in listings.columns:
        listings[col] = (
            listings[col]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        listings[col] = pd.to_numeric(listings[col], errors="coerce")


# 5. Fill missing category fields with Unknown

category_columns = [
    "PropertyType",
    "PropertySubType",
    "StandardStatus",
    "MlsStatus",
    "CountyOrParish",
    "City",
    "PostalCode",
    "MLSAreaMajor",
    "StateOrProvince",
    "ListOfficeName",
    "ListAgentFirstName",
    "ListAgentLastName",
    "ListAgentFullName"
]

for col in category_columns:
    if col in listings.columns:
        listings[col] = listings[col].astype("string").str.strip()
        listings[col] = listings[col].fillna("Unknown")
        listings[col] = listings[col].replace("", "Unknown")


# 6. Create ListAgentFullName if needed

if "ListAgentFullName" not in listings.columns:
    if "ListAgentFirstName" in listings.columns and "ListAgentLastName" in listings.columns:
        listings["ListAgentFullName"] = (
            listings["ListAgentFirstName"].fillna("").astype(str).str.strip()
            + " "
            + listings["ListAgentLastName"].fillna("").astype(str).str.strip()
        ).str.strip()
        listings["ListAgentFullName"] = listings["ListAgentFullName"].replace("", "Unknown")


# 7. Create simple time fields for Tableau

if "ListingContractDate" in listings.columns:
    listings["listing_year"] = listings["ListingContractDate"].dt.year
    listings["listing_month"] = listings["ListingContractDate"].dt.month
    listings["listing_quarter"] = listings["ListingContractDate"].dt.quarter
    listings["listing_yrmo"] = listings["ListingContractDate"].dt.to_period("M").astype(str)


# 8. Add simple data quality flags

if "ListingKey" in listings.columns:
    listings["missing_listing_key_flag"] = listings["ListingKey"].isna()
elif "Listing Key" in listings.columns:
    listings["missing_listing_key_flag"] = listings["Listing Key"].isna()
else:
    listings["missing_listing_key_flag"] = False

if "ListingContractDate" in listings.columns:
    listings["missing_listing_contract_date_flag"] = listings["ListingContractDate"].isna()
else:
    listings["missing_listing_contract_date_flag"] = True

if "ListPrice" in listings.columns:
    listings["invalid_list_price_flag"] = listings["ListPrice"].isna() | (listings["ListPrice"] <= 0)
else:
    listings["invalid_list_price_flag"] = False

if "LivingArea" in listings.columns:
    listings["invalid_living_area_flag"] = listings["LivingArea"].notna() & (listings["LivingArea"] <= 0)
else:
    listings["invalid_living_area_flag"] = False

if "DaysOnMarket" in listings.columns:
    listings["invalid_days_on_market_flag"] = listings["DaysOnMarket"].notna() & (listings["DaysOnMarket"] < 0)
else:
    listings["invalid_days_on_market_flag"] = False

if "BedroomsTotal" in listings.columns:
    listings["invalid_bedrooms_flag"] = listings["BedroomsTotal"].notna() & (listings["BedroomsTotal"] < 0)
else:
    listings["invalid_bedrooms_flag"] = False

if "BathroomsTotalInteger" in listings.columns:
    listings["invalid_bathrooms_flag"] = listings["BathroomsTotalInteger"].notna() & (listings["BathroomsTotalInteger"] < 0)
else:
    listings["invalid_bathrooms_flag"] = False


# 9. Geographic flags

if "Latitude" in listings.columns and "Longitude" in listings.columns:
    listings["missing_coordinates_flag"] = listings["Latitude"].isna() | listings["Longitude"].isna()
    listings["zero_coordinates_flag"] = (listings["Latitude"] == 0) | (listings["Longitude"] == 0)
    listings["longitude_positive_flag"] = listings["Longitude"] > 0
    listings["implausible_ca_coordinates_flag"] = (
        listings["Latitude"].notna()
        & listings["Longitude"].notna()
        & (
            (listings["Latitude"] < 32.0)
            | (listings["Latitude"] > 42.5)
            | (listings["Longitude"] < -124.5)
            | (listings["Longitude"] > -114.0)
        )
    )
else:
    listings["missing_coordinates_flag"] = True
    listings["zero_coordinates_flag"] = False
    listings["longitude_positive_flag"] = False
    listings["implausible_ca_coordinates_flag"] = False

listings["invalid_coordinates_flag"] = (
    listings["missing_coordinates_flag"]
    | listings["zero_coordinates_flag"]
    | listings["longitude_positive_flag"]
    | listings["implausible_ca_coordinates_flag"]
)


# 10. Drop unnecessary columns

protected_columns = [
    "ListingKey",
    "ListingId",
    "ListingKeyNumeric",
    "PropertyType",
    "PropertySubType",
    "StandardStatus",
    "MlsStatus",
    "ListingContractDate",
    "listing_year",
    "listing_month",
    "listing_quarter",
    "listing_yrmo",
    "ListPrice",
    "OriginalListPrice",
    "ClosePrice",
    "CloseDate",
    "LivingArea",
    "LotSizeAcres",
    "LotSizeSquareFeet",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "CumulativeDaysOnMarket",
    "YearBuilt",
    "Latitude",
    "Longitude",
    "CountyOrParish",
    "City",
    "PostalCode",
    "MLSAreaMajor",
    "StateOrProvince",
    "ListAgentFirstName",
    "ListAgentLastName",
    "ListAgentFullName",
    "ListOfficeName"
]

manual_drop_columns = [
    "UnparsedAddress",
    "StreetNumberNumeric",
    "StreetName",
    "StreetNumber",
    "StreetSuffix",
    "UnitNumber",
    "ListAgentEmail",
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

missing_pct = listings.isna().mean()
columns_to_drop = []

for col in listings.columns:
    if missing_pct[col] > 0.90 and col not in protected_columns and not col.endswith("_flag"):
        columns_to_drop.append(col)

for col in manual_drop_columns:
    if col in listings.columns and col not in columns_to_drop:
        columns_to_drop.append(col)

listings = listings.drop(columns=columns_to_drop, errors="ignore")


# 11. Remove rows that cannot support New Listings analysis
remove_rows = listings["missing_listing_contract_date_flag"]

if "missing_listing_key_flag" in listings.columns:
    remove_rows = remove_rows | listings["missing_listing_key_flag"]

listings_cleaned = listings[~remove_rows].copy()

print("Rows after removing unusable listing records:", len(listings_cleaned))
print("Dropped columns:", len(columns_to_drop))

# 12. Save

listings_cleaned.to_csv(output_file, index=False)

print("Saved cleaned listings file:")
print(output_file)


# 13. Save summary file

summary_file = os.path.join(output_folder, "listings_cleaning_simple_summary.txt")

summary_lines = []
summary_lines.append("Simple Listing Cleaning Summary")
summary_lines.append("=" * 35)
summary_lines.append("")
summary_lines.append("Input file: " + input_file)
summary_lines.append("Output file: " + output_file)
summary_lines.append("")
summary_lines.append("Initial rows: " + str(initial_rows))
summary_lines.append("Rows after cleaning: " + str(len(listings_cleaned)))
summary_lines.append("Initial columns: " + str(initial_columns))
summary_lines.append("Dropped columns: " + str(len(columns_to_drop)))
summary_lines.append("")
summary_lines.append("Main cleaning choices:")
summary_lines.append("- Filtered to PropertyType == Residential when PropertyType exists.")
summary_lines.append("- Converted important date fields to datetime.")
summary_lines.append("- Converted important price/size/DOM fields to numeric.")
summary_lines.append("- Filled missing categorical labels with Unknown.")
summary_lines.append("- Created listing_year, listing_month, listing_quarter, listing_yrmo from ListingContractDate.")
summary_lines.append("- Flagged invalid list price, living area, DOM, bedrooms/bathrooms, and coordinates.")
summary_lines.append("- Dropped >90% missing non-core columns and unnecessary address/contact/metadata fields.")
summary_lines.append("- Removed records missing ListingContractDate or ListingKey.")
summary_lines.append("- Did not require ClosePrice or CloseDate because listings include active, pending, expired, and withdrawn records.")

with open(summary_file, "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))

print("Saved summary file:")
print(summary_file)

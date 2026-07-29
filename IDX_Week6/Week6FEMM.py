"""
Main outputs:
    sold_week6_engineered.csv
    sample_engineered_columns.csv
    segment_by_property_type.csv
    segment_by_county.csv
    segment_by_listing_office_top100.csv
    segment_by_buyer_office_top100.csv
    monthly_market_summary.csv
    week6_summary.txt
"""

import os
import pandas as pd


input_file = "D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\IDX_Week4-5/sold_cleaned_analysis_ready.csv"
output_folder = "D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\IDX_Week6"

os.makedirs(output_folder, exist_ok=True)


# Load cleaned sold dataset

sold = pd.read_csv(input_file, low_memory=False)
sold.columns = sold.columns.str.strip()

print("Loaded rows:", len(sold))
print("Loaded columns:", len(sold.columns))


#  Make sure required columns have correct data types

date_columns = ["CloseDate", "PurchaseContractDate", "ListingContractDate"]

for col in date_columns:
    if col in sold.columns:
        sold[col] = pd.to_datetime(sold[col], errors="coerce")

numeric_columns = ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea", "DaysOnMarket"]

for col in numeric_columns:
    if col in sold.columns:
        sold[col] = (
            sold[col]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        sold[col] = pd.to_numeric(sold[col], errors="coerce")


# Create price ratio metrics
# Required:
# price_ratio = ClosePrice / OriginalListPrice
# close_to_original_list_ratio = ClosePrice / OriginalListPrice
# Extra:
# close_to_list_ratio = ClosePrice / ListPrice

if "ClosePrice" in sold.columns and "OriginalListPrice" in sold.columns:
    sold["price_ratio"] = sold["ClosePrice"] / sold["OriginalListPrice"]
    sold["close_to_original_list_ratio"] = sold["ClosePrice"] / sold["OriginalListPrice"]
else:
    sold["price_ratio"] = pd.NA
    sold["close_to_original_list_ratio"] = pd.NA

if "ClosePrice" in sold.columns and "ListPrice" in sold.columns:
    sold["close_to_list_ratio"] = sold["ClosePrice"] / sold["ListPrice"]
else:
    sold["close_to_list_ratio"] = pd.NA


# Create price per square foot (PPSF)

if "ClosePrice" in sold.columns and "LivingArea" in sold.columns:
    sold["price_per_sqft"] = sold["ClosePrice"] / sold["LivingArea"]
else:
    sold["price_per_sqft"] = pd.NA


# Keep Days on Market as a metric column

if "DaysOnMarket" in sold.columns:
    sold["days_on_market_metric"] = sold["DaysOnMarket"]
else:
    sold["days_on_market_metric"] = pd.NA


# Create Year / Month / YrMo from CloseDate

if "CloseDate" in sold.columns:
    sold["close_year"] = sold["CloseDate"].dt.year
    sold["close_month"] = sold["CloseDate"].dt.month
    sold["close_quarter"] = sold["CloseDate"].dt.quarter
    sold["yrmo"] = sold["CloseDate"].dt.to_period("M").astype(str)
else:
    sold["close_year"] = pd.NA
    sold["close_month"] = pd.NA
    sold["close_quarter"] = pd.NA
    sold["yrmo"] = pd.NA


# Create transaction timeline metrics

if "PurchaseContractDate" in sold.columns and "ListingContractDate" in sold.columns:
    sold["listing_to_contract_days"] = (
        sold["PurchaseContractDate"] - sold["ListingContractDate"]
    ).dt.days
else:
    sold["listing_to_contract_days"] = pd.NA

if "CloseDate" in sold.columns and "PurchaseContractDate" in sold.columns:
    sold["contract_to_close_days"] = (
        sold["CloseDate"] - sold["PurchaseContractDate"]
    ).dt.days
else:
    sold["contract_to_close_days"] = pd.NA


# Add simple feature quality flags

sold["missing_price_ratio_flag"] = sold["price_ratio"].isna()
sold["missing_price_per_sqft_flag"] = sold["price_per_sqft"].isna()
sold["missing_listing_to_contract_days_flag"] = sold["listing_to_contract_days"].isna()
sold["missing_contract_to_close_days_flag"] = sold["contract_to_close_days"].isna()

sold["suspicious_price_ratio_flag"] = (
    sold["price_ratio"].notna()
    & ((sold["price_ratio"] <= 0) | (sold["price_ratio"] > 3))
)

sold["suspicious_price_per_sqft_flag"] = (
    sold["price_per_sqft"].notna()
    & ((sold["price_per_sqft"] <= 0) | (sold["price_per_sqft"] > 10000))
)

sold["negative_listing_to_contract_days_flag"] = (
    sold["listing_to_contract_days"].notna()
    & (sold["listing_to_contract_days"] < 0)
)

sold["negative_contract_to_close_days_flag"] = (
    sold["contract_to_close_days"].notna()
    & (sold["contract_to_close_days"] < 0)
)


# Save sample output table

sample_columns = [
    "ListingKey",
    "PropertyType",
    "PropertySubType",
    "CountyOrParish",
    "City",
    "PostalCode",
    "CloseDate",
    "ClosePrice",
    "OriginalListPrice",
    "ListPrice",
    "LivingArea",
    "price_ratio",
    "close_to_original_list_ratio",
    "close_to_list_ratio",
    "price_per_sqft",
    "DaysOnMarket",
    "days_on_market_metric",
    "close_year",
    "close_month",
    "yrmo",
    "ListingContractDate",
    "PurchaseContractDate",
    "listing_to_contract_days",
    "contract_to_close_days"
]

sample_columns_existing = []
for col in sample_columns:
    if col in sold.columns:
        sample_columns_existing.append(col)

sample = sold[sample_columns_existing].head(50)
sample.to_csv(os.path.join(output_folder, "sample_engineered_columns.csv"), index=False)


# Save full engineered dataset

sold.to_csv(os.path.join(output_folder, "sold_week6_engineered.csv"), index=False)


# Segment analysis: PropertyType / PropertySubType

if "PropertyType" in sold.columns and "PropertySubType" in sold.columns:
    segment_property = sold.groupby(["PropertyType", "PropertySubType"], dropna=False).agg(
        closed_sales=("ClosePrice", "count"),
        total_sales_volume=("ClosePrice", "sum"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_days_on_market=("days_on_market_metric", "mean"),
        average_close_to_original_list_ratio=("close_to_original_list_ratio", "mean"),
        median_listing_to_contract_days=("listing_to_contract_days", "median"),
        median_contract_to_close_days=("contract_to_close_days", "median")
    ).reset_index()
else:
    segment_property = pd.DataFrame()

segment_property.to_csv(os.path.join(output_folder, "segment_by_property_type.csv"), index=False)

# Segment analysis: County

if "CountyOrParish" in sold.columns:
    segment_county = sold.groupby("CountyOrParish", dropna=False).agg(
        closed_sales=("ClosePrice", "count"),
        total_sales_volume=("ClosePrice", "sum"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_days_on_market=("days_on_market_metric", "mean"),
        average_close_to_original_list_ratio=("close_to_original_list_ratio", "mean"),
        median_listing_to_contract_days=("listing_to_contract_days", "median"),
        median_contract_to_close_days=("contract_to_close_days", "median")
    ).reset_index()

    segment_county = segment_county.sort_values("median_close_price", ascending=False)
else:
    segment_county = pd.DataFrame()

segment_county.to_csv(os.path.join(output_folder, "segment_by_county.csv"), index=False)


# Competitive intelligence: listing office and buyer office

if "ListOfficeName" in sold.columns:
    listing_office = sold.groupby("ListOfficeName", dropna=False).agg(
        closed_sales=("ClosePrice", "count"),
        total_sales_volume=("ClosePrice", "sum"),
        median_close_price=("ClosePrice", "median"),
        average_close_to_original_list_ratio=("close_to_original_list_ratio", "mean"),
        average_days_on_market=("days_on_market_metric", "mean")
    ).reset_index()

    listing_office = listing_office.sort_values(
        ["total_sales_volume", "closed_sales"],
        ascending=False
    ).head(100)
else:
    listing_office = pd.DataFrame()

listing_office.to_csv(os.path.join(output_folder, "segment_by_listing_office_top100.csv"), index=False)


if "BuyerOfficeName" in sold.columns:
    buyer_office = sold.groupby("BuyerOfficeName", dropna=False).agg(
        closed_sales=("ClosePrice", "count"),
        total_sales_volume=("ClosePrice", "sum"),
        median_close_price=("ClosePrice", "median"),
        average_close_to_original_list_ratio=("close_to_original_list_ratio", "mean"),
        average_days_on_market=("days_on_market_metric", "mean")
    ).reset_index()

    buyer_office = buyer_office.sort_values(
        ["total_sales_volume", "closed_sales"],
        ascending=False
    ).head(100)
else:
    buyer_office = pd.DataFrame()

buyer_office.to_csv(os.path.join(output_folder, "segment_by_buyer_office_top100.csv"), index=False)


# Monthly market summary

if "yrmo" in sold.columns:
    monthly_summary = sold.groupby("yrmo", dropna=False).agg(
        closed_sales=("ClosePrice", "count"),
        total_sales_volume=("ClosePrice", "sum"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_days_on_market=("days_on_market_metric", "mean"),
        average_close_to_original_list_ratio=("close_to_original_list_ratio", "mean"),
        average_close_to_list_ratio=("close_to_list_ratio", "mean")
    ).reset_index()

    monthly_summary = monthly_summary.sort_values("yrmo")
else:
    monthly_summary = pd.DataFrame()

monthly_summary.to_csv(os.path.join(output_folder, "monthly_market_summary.csv"), index=False)



# Save summary report

flag_columns = []
for col in sold.columns:
    if col.endswith("_flag"):
        flag_columns.append(col)

summary_lines = []
summary_lines.append("IDX Week 6 Feature Engineering Summary")
summary_lines.append("=" * 45)
summary_lines.append("")
summary_lines.append("Input file: " + input_file)
summary_lines.append("Rows in engineered dataset: " + str(len(sold)))
summary_lines.append("Columns in engineered dataset: " + str(len(sold.columns)))
summary_lines.append("")
summary_lines.append("Engineered columns created:")
summary_lines.append("- price_ratio = ClosePrice / OriginalListPrice")
summary_lines.append("- close_to_original_list_ratio = ClosePrice / OriginalListPrice")
summary_lines.append("- close_to_list_ratio = ClosePrice / ListPrice")
summary_lines.append("- price_per_sqft = ClosePrice / LivingArea")
summary_lines.append("- days_on_market_metric = DaysOnMarket")
summary_lines.append("- close_year, close_month, close_quarter, yrmo from CloseDate")
summary_lines.append("- listing_to_contract_days = PurchaseContractDate - ListingContractDate")
summary_lines.append("- contract_to_close_days = CloseDate - PurchaseContractDate")
summary_lines.append("")
summary_lines.append("Output tables:")
summary_lines.append("- sold_week6_engineered.csv")
summary_lines.append("- sample_engineered_columns.csv")
summary_lines.append("- segment_by_property_type.csv")
summary_lines.append("- segment_by_county.csv")
summary_lines.append("- segment_by_listing_office_top100.csv")
summary_lines.append("- segment_by_buyer_office_top100.csv")
summary_lines.append("- monthly_market_summary.csv")
summary_lines.append("")
summary_lines.append("Feature quality flags:")

for col in flag_columns:
    summary_lines.append(
        "- " + col + ": " + str(int(sold[col].sum())) + " (" + "{:.2%}".format(sold[col].mean()) + ")"
    )

summary_lines.append("")
summary_lines.append("School district note:")
summary_lines.append("School district enrichment requires a boundary file and spatial join.")
summary_lines.append("This pandas-only script keeps the workflow simple and writes school_district_note.txt.")

with open(os.path.join(output_folder, "week6_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))


print("Week 6 feature engineering complete.")
print("Engineered rows:", len(sold))
print("Output folder:", output_folder)

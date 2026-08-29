import os
import pandas as pd


# =========================
# 0. Settings
# =========================

raw_data_folder = r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_raw_data"
output_folder = r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes"

start_month = "202401"
end_month = "202607"

sold_prefix = "CRMLSSold"
listing_prefix = "CRMLSListing"

sold_output = os.path.join(output_folder, "Sold_Concated_FIXED.csv")
listing_output = os.path.join(output_folder, "Listing_Concated_FIXED.csv")
audit_output = os.path.join(output_folder, "month_file_audit.csv")

os.makedirs(output_folder, exist_ok=True)


# =========================
# 1. Create month list
# =========================

months = pd.period_range(start=start_month, end=end_month, freq="M").strftime("%Y%m").tolist()

print("Months expected:")
print(months)


# =========================
# 2. Read monthly files
# =========================

sold_frames = []
listing_frames = []
audit_rows = []

for month in months:
    sold_file = os.path.join(raw_data_folder, sold_prefix + month + ".csv")
    listing_file = os.path.join(raw_data_folder, listing_prefix + month + ".csv")

    sold_exists = os.path.exists(sold_file)
    listing_exists = os.path.exists(listing_file)

    sold_rows = None
    listing_rows = None

    if sold_exists:
        temp_sold = pd.read_csv(sold_file, encoding="latin-1", low_memory=False)
        temp_sold["source_month"] = month
        sold_frames.append(temp_sold)
        sold_rows = len(temp_sold)
        print("Loaded sold", month, "rows:", sold_rows)
    else:
        print("MISSING sold file:", sold_file)

    if listing_exists:
        temp_listing = pd.read_csv(listing_file, encoding="latin-1", low_memory=False)
        temp_listing["source_month"] = month
        listing_frames.append(temp_listing)
        listing_rows = len(temp_listing)
        print("Loaded listing", month, "rows:", listing_rows)
    else:
        print("MISSING listing file:", listing_file)

    audit_rows.append({
        "month": month,
        "sold_file_exists": sold_exists,
        "sold_rows": sold_rows,
        "listing_file_exists": listing_exists,
        "listing_rows": listing_rows
    })


# =========================
# 3. Concatenate and save
# =========================

audit = pd.DataFrame(audit_rows)
audit.to_csv(audit_output, index=False)

if len(sold_frames) > 0:
    sold = pd.concat(sold_frames, ignore_index=True)
    sold.to_csv(sold_output, index=False, encoding="latin-1")
    print("Saved:", sold_output)
    print("Sold total rows:", len(sold))

    if "CloseDate" in sold.columns:
        sold["CloseDate"] = pd.to_datetime(sold["CloseDate"], errors="coerce")
        sold["close_yrmo_check"] = sold["CloseDate"].dt.to_period("M").astype(str)
        print("\nSold month counts by CloseDate:")
        print(sold.groupby("close_yrmo_check").size().sort_index().to_string())

    print("\nSold source file month counts:")
    print(sold.groupby("source_month").size().sort_index().to_string())
else:
    print("No sold files loaded.")

if len(listing_frames) > 0:
    listings = pd.concat(listing_frames, ignore_index=True)
    listings.to_csv(listing_output, index=False, encoding="latin-1")
    print("Saved:", listing_output)
    print("Listing total rows:", len(listings))

    if "ListingContractDate" in listings.columns:
        listings["ListingContractDate"] = pd.to_datetime(listings["ListingContractDate"], errors="coerce")
        listings["listing_yrmo_check"] = listings["ListingContractDate"].dt.to_period("M").astype(str)
        print("\nListing month counts by ListingContractDate:")
        print(listings.groupby("listing_yrmo_check").size().sort_index().to_string())

    print("\nListing source file month counts:")
    print(listings.groupby("source_month").size().sort_index().to_string())
else:
    print("No listing files loaded.")

print("\nAudit saved:")
print(audit_output)

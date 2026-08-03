import os
import pandas as pd



# File paths

input_file = r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\IDX_Week6\sold_week6_engineered.csv"
output_folder = r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\IDX_Week7"


os.makedirs(output_folder, exist_ok=True)


# Load Week 6 engineered dataset

sold = pd.read_csv(input_file, low_memory=False)
sold.columns = sold.columns.str.strip()

print("Loaded rows:", len(sold))
print("Loaded columns:", len(sold.columns))


#  Make sure key numeric fields are numeric

numeric_columns = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "price_per_sqft",
    "close_to_original_list_ratio",
    "close_to_list_ratio"
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


# Define IQR fields

required_iqr_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]

optional_iqr_fields = [
    "price_per_sqft",
    "close_to_original_list_ratio",
    "close_to_list_ratio"
]

iqr_fields = []

for col in required_iqr_fields + optional_iqr_fields:
    if col in sold.columns:
        iqr_fields.append(col)


# Apply IQR method and add outlier flags

threshold_rows = []

for col in iqr_fields:
    values = sold[col].dropna()

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    p01 = values.quantile(0.01)
    p05 = values.quantile(0.05)
    p95 = values.quantile(0.95)
    p99 = values.quantile(0.99)

    iqr_flag_col = col + "_iqr_outlier_flag"
    percentile_flag_col = col + "_outside_p01_p99_flag"

    sold[iqr_flag_col] = (
        sold[col].notna()
        & ((sold[col] < lower_bound) | (sold[col] > upper_bound))
    )

    # Percentile flag is for review only.
    sold[percentile_flag_col] = (
        sold[col].notna()
        & ((sold[col] < p01) | (sold[col] > p99))
    )

    threshold_rows.append({
        "field": col,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "p01": p01,
        "p05": p05,
        "p95": p95,
        "p99": p99,
        "missing_count": sold[col].isna().sum(),
        "iqr_outlier_count": sold[iqr_flag_col].sum(),
        "iqr_outlier_pct": sold[iqr_flag_col].mean(),
        "outside_p01_p99_count": sold[percentile_flag_col].sum(),
        "outside_p01_p99_pct": sold[percentile_flag_col].mean()
    })

threshold_report = pd.DataFrame(threshold_rows)
threshold_report.to_csv(os.path.join(output_folder, "iqr_thresholds_report.csv"), index=False)


# Create one combined outlier flag

sold["week7_required_iqr_outlier_flag"] = False

for col in required_iqr_fields:
    flag_col = col + "_iqr_outlier_flag"
    if flag_col in sold.columns:
        sold["week7_required_iqr_outlier_flag"] = (
            sold["week7_required_iqr_outlier_flag"] | sold[flag_col]
        )

sold.to_csv(os.path.join(output_folder, "sold_week7_full_flagged.csv"), index=False)


# Create clean filtered dataset

clean_filtered = sold[~sold["week7_required_iqr_outlier_flag"]].copy()
clean_filtered.to_csv(os.path.join(output_folder, "sold_week7_clean_filtered.csv"), index=False)


# Outlier counts report

count_rows = []

for col in iqr_fields:
    iqr_flag_col = col + "_iqr_outlier_flag"
    percentile_flag_col = col + "_outside_p01_p99_flag"

    count_rows.append({
        "field": col,
        "iqr_outlier_count": sold[iqr_flag_col].sum(),
        "iqr_outlier_pct": sold[iqr_flag_col].mean(),
        "outside_p01_p99_count": sold[percentile_flag_col].sum(),
        "outside_p01_p99_pct": sold[percentile_flag_col].mean()
    })

count_report = pd.DataFrame(count_rows)
count_report.to_csv(os.path.join(output_folder, "outlier_counts_report.csv"), index=False)


# Before / after comparison

comparison_fields = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "price_per_sqft",
    "close_to_original_list_ratio",
    "close_to_list_ratio"
]

comparison_rows = []

for col in comparison_fields:
    if col in sold.columns:
        comparison_rows.append({
            "field": col,
            "before_count": sold[col].count(),
            "after_count": clean_filtered[col].count(),
            "before_mean": sold[col].mean(),
            "after_mean": clean_filtered[col].mean(),
            "before_median": sold[col].median(),
            "after_median": clean_filtered[col].median(),
            "before_min": sold[col].min(),
            "after_min": clean_filtered[col].min(),
            "before_max": sold[col].max(),
            "after_max": clean_filtered[col].max()
        })

comparison_report = pd.DataFrame(comparison_rows)
comparison_report.to_csv(os.path.join(output_folder, "before_after_comparison_report.csv"), index=False)


# Save sample outlier records

sample_columns = [
    "ListingKey",
    "PropertyType",
    "PropertySubType",
    "CountyOrParish",
    "City",
    "PostalCode",
    "CloseDate",
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "price_per_sqft",
    "close_to_original_list_ratio",
    "close_to_list_ratio",
    "week7_required_iqr_outlier_flag",
    "ClosePrice_iqr_outlier_flag",
    "LivingArea_iqr_outlier_flag",
    "DaysOnMarket_iqr_outlier_flag"
]

sample_columns_existing = []

for col in sample_columns:
    if col in sold.columns:
        sample_columns_existing.append(col)

sample_outliers = sold[sold["week7_required_iqr_outlier_flag"]].copy()
sample_outliers = sample_outliers[sample_columns_existing].head(200)

sample_outliers.to_csv(os.path.join(output_folder, "sample_outlier_records.csv"), index=False)


# Monthly summary before and after filtering

if "yrmo" in sold.columns:
    monthly_before = sold.groupby("yrmo", dropna=False).agg(
        closed_sales=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_living_area=("LivingArea", "median"),
        average_days_on_market=("DaysOnMarket", "mean")
    ).reset_index()

    monthly_after = clean_filtered.groupby("yrmo", dropna=False).agg(
        closed_sales=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_living_area=("LivingArea", "median"),
        average_days_on_market=("DaysOnMarket", "mean")
    ).reset_index()

    monthly_before.to_csv(os.path.join(output_folder, "monthly_summary_before_iqr.csv"), index=False)
    monthly_after.to_csv(os.path.join(output_folder, "monthly_summary_after_iqr.csv"), index=False)


# Write summary text

removed_rows = sold["week7_required_iqr_outlier_flag"].sum()
removed_pct = removed_rows / len(sold)

summary_lines = []

summary_lines.append("IDX Week 7 Outlier Detection and Data Quality Summary")
summary_lines.append("=" * 60)
summary_lines.append("")
summary_lines.append("Input file: " + input_file)
summary_lines.append("")
summary_lines.append("Dataset size:")
summary_lines.append("Rows before filtering: " + str(len(sold)))
summary_lines.append("Rows removed by required-field IQR filter: " + str(int(removed_rows)) + " (" + "{:.2%}".format(removed_pct) + ")")
summary_lines.append("Rows after filtering: " + str(len(clean_filtered)))
summary_lines.append("")
summary_lines.append("IQR fields:")
summary_lines.append("- Required fields used for filtering: ClosePrice, LivingArea, DaysOnMarket")
summary_lines.append("- Optional fields flagged for review only: price_per_sqft, close_to_original_list_ratio, close_to_list_ratio")
summary_lines.append("")
summary_lines.append("Why flag first:")
summary_lines.append("- The script keeps sold_week7_full_flagged.csv as the audit version.")
summary_lines.append("- It saves sold_week7_clean_filtered.csv as a separate analysis-ready version.")
summary_lines.append("- This avoids permanently deleting records and makes filtering decisions transparent.")
summary_lines.append("")
summary_lines.append("Before / after median comparison:")

for i in range(len(comparison_report)):
    row = comparison_report.iloc[i]
    summary_lines.append(
        "- " + row["field"]
        + ": median before = " + "{:,.2f}".format(row["before_median"])
        + ", median after = " + "{:,.2f}".format(row["after_median"])
    )

summary_lines.append("")
summary_lines.append("IQR threshold summary:")

for i in range(len(threshold_report)):
    row = threshold_report.iloc[i]
    summary_lines.append(
        "- " + row["field"]
        + ": lower = " + "{:,.2f}".format(row["lower_bound"])
        + ", upper = " + "{:,.2f}".format(row["upper_bound"])
        + ", IQR outliers = " + str(int(row["iqr_outlier_count"]))
        + " (" + "{:.2%}".format(row["iqr_outlier_pct"]) + ")"
    )

summary_lines.append("")
summary_lines.append("Output files:")
summary_lines.append("- sold_week7_full_flagged.csv")
summary_lines.append("- sold_week7_clean_filtered.csv")
summary_lines.append("- iqr_thresholds_report.csv")
summary_lines.append("- outlier_counts_report.csv")
summary_lines.append("- before_after_comparison_report.csv")
summary_lines.append("- sample_outlier_records.csv")
summary_lines.append("- monthly_summary_before_iqr.csv / monthly_summary_after_iqr.csv, if yrmo exists")

with open(os.path.join(output_folder, "week7_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))


print("Week 7 outlier detection complete.")
print("Rows before filtering:", len(sold))
print("Rows after filtering:", len(clean_filtered))
print("Output folder:", output_folder)

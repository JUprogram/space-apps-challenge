import pandas as pd

data = pd.read_csv("BRSMACT_Campagin_1_Actigraphy")
# Convert sleep latency into minutes
latency = data["Sleep Latency (hours)"].astype("string").str.strip()

latency = latency.replace("0", "0:00")

latency = latency.where(
    latency.isna() | latency.str.count(":").ne(1),
    latency + ":00"
)

data["Sleep Latency (minutes)"] = (
    pd.to_timedelta(latency, errors="coerce").dt.total_seconds() / 60
)

# Convert sleep duration into minutes
duration = data["Sleep Duration (hours)"].astype("string").str.strip()

data["Sleep Duration (minutes)"] = (
    pd.to_timedelta(duration, errors="coerce").dt.total_seconds() / 60
)

print("\n--- CONVERTED SLEEP DATA ---")

print(data[
    [
        "Subject",
        "Sleep Latency (minutes)",
        "Sleep Duration (minutes)",
        "Sleep Efficiency (%)"
    ]
].head(10))



print("First five rows:\n")
print(data.head())

print("COLUMN NAMES: \n")
print(data.columns.tolist())

print("DATSET INFO: \n")
print(data.info())

print("STATISTICAL SUMMARY: \n")
print(data.describe(include="all"))


print("\n--- DATASET SIZE ---")
print(data.shape)

# 4. Check column types and missing values
print("\n--- DATASET INFORMATION ---")
data.info()

print("\n--- MISSING VALUES ---")
print(data.isnull().sum())    

# 6. Display the converted measurements
print("\n--- CONVERTED SLEEP MEASUREMENTS ---")
print(data[
    [
        "Subject",
        "Sleep Latency (minutes)",
        "Sleep Duration (minutes)",
        "Sleep Efficiency (%)"
    ]
].head())

# 7. Display numerical statistics
print("\n--- STATISTICAL SUMMARY ---")
print(data.describe())

#EDA

#converting data into panda-readable format
data["Date"] = pd.to_datetime(
	data["Date"],
	format="%m/%d/%Y",
	errors="coerce"
)


data = data.sort_values(["Subject", "Date"])

# Sleep measurements we want to analyze
sleep_metrics = [
    "Sleep Latency (minutes)",
    "Sleep Duration (minutes)",
    "Sleep Efficiency (%)"
]

# 1. Count records in each study phase
print("\n--- RECORDS BY STUDY PHASE ---")
print(data["Test_Phase"].value_counts())

# 2. Compare sleep measurements across subjects
print("\n--- SLEEP METRICS BY SUBJECT ---")
print(
    data.groupby("Subject")[sleep_metrics]
    .mean()
    .round(2)
)

# 3. Compare sleep measurements across study phases
print("\n--- SLEEP METRICS BY PHASE ---")
print(
    data.groupby("Test_Phase")[sleep_metrics]
    .mean()
    .round(2)
)

# 4. Examine measurements for each subject and phase
print("\n--- SUBJECT AND PHASE COMPARISON ---")
print(
    data.groupby(["Subject", "Test_Phase"])[sleep_metrics]
    .agg(["mean", "median", "count"])
    .round(2)
)


import matplotlib.pyplot as plt

# Show all columns in the statistical output
pd.set_option("display.max_columns", None)

# Plot sleep efficiency over time for each subject
plt.figure(figsize=(12, 6))

for subject in data["Subject"].unique():
    subject_data = data[data["Subject"] == subject].sort_values("Date")

    plt.plot(
        subject_data["Date"],
        subject_data["Sleep Efficiency (%)"],
        marker="o",
        label=subject
    )

plt.xlabel("Date")
plt.ylabel("Sleep Efficiency (%)")
plt.title("Sleep Efficiency Over Time by Subject")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()



analysis_data = data[
	data["Test_Phase"] == "IN_TEST"
].copy()

metrics = [
    "Sleep Latency (minutes)",
    "Sleep Duration (minutes)",
    "Sleep Efficiency (%)"
]

for metric in metrics:
    subject_mean = analysis_data.groupby("Subject")[metric].transform("mean")
    subject_std = analysis_data.groupby("Subject")[metric].transform("std")

    analysis_data[f"{metric} Z-Score"] = (
        (analysis_data[metric] - subject_mean) / subject_std
    )

z_score_columns = [f"{metric} Z-Score" for metric in metrics]

analysis_data["Potential Anomaly"] = (
    analysis_data[z_score_columns].abs().gt(2).any(axis=1)
)

print("\n--- POTENTIAL ANOMALIES ---")

print(
    analysis_data.loc[
        analysis_data["Potential Anomaly"],
        ["Subject", "Date"] + metrics + z_score_columns
    ].round(2)
)

print("\n--- ANOMALY COUNTS BY SUBJECT ---")

print(
    analysis_data.groupby("Subject")["Potential Anomaly"]
    .sum()
)


print("\n--- WHICH METRICS TRIGGERED EACH ANOMALY ---")

for metric in metrics:
    z_col = f"{metric} Z-Score"

    flagged = analysis_data[
        analysis_data[z_col].abs() > 2
    ]

    print(f"\n{metric}: {len(flagged)} potential anomalies")

    print(
        flagged[
            ["Subject", "Date", metric, z_col]
        ].round(2).to_string(index=False)
    )
print("\n--- MISSING VALUES ---")
print(analysis_data[metrics].isnull().sum())

print("\n--- TOTAL ANALYSIS RECORDS ---")
print(len(analysis_data))

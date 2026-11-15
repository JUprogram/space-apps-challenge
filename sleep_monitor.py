import pandas as pd
from ai_layer import results


def create_sleep_alerts(data: pd.DataFrame) -> pd.DataFrame:

    alerts = data.copy()

    # 1. Assign the category
    alerts["Category"] = "Sleep"

    # 2. Convert predictions into readable statuses
    alerts["Status"] = alerts["Predictions"].map({
        -1: "MONITOR",
        1: "ROUTINE"
    })

    # 3. Preserve relevant measurements
    measurement_columns = [
        "Sleep Latency (minutes)",
        "Sleep Duration (minutes)",
        "Sleep Efficiency (%)"
    ]

    # 4. Add a non-diagnostic interpretation
    alerts["Interpretation"] = alerts["Predictions"].map({
        -1: "This sleep observation was flagged as unusual by the exploratory anomaly detection model.",
        1: "This sleep observation was not flagged by the exploratory anomaly detection model."
    })

    # Return standardized monitoring records
    return alerts


sleep_alerts = create_sleep_alerts(results)

print("\n--- SLEEP MONITORING RESULTS ---")
print(sleep_alerts[
    ["Subject", "Category", "Status", "Anomaly Score", "Interpretation"]
].head())

print("\n--- ALERT COUNTS ---")
print(sleep_alerts["Status"].value_counts())

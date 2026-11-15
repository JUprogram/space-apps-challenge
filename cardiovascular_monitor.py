
import pandas as pd
from cardiovascular import results


def create_cardiovascular_alerts(data: pd.DataFrame) -> pd.DataFrame:

    alerts = data.copy()

    # 1. Assign the category
    alerts["Category"] = "Cardiovascular"

    # 2. Convert predictions into readable statuses
    alerts["Status"] = alerts["Predictions"].map({
        -1: "MONITOR",
        1: "ROUTINE"
    })

    # 3. Add a non-diagnostic interpretation
    alerts["Interpretation"] = alerts["Predictions"].map({
        -1: "This echocardiography observation was flagged as unusual by the exploratory anomaly detection model.",
        1: "This echocardiography observation was not flagged by the exploratory anomaly detection model."
    })

    return alerts


cardiovascular_alerts = create_cardiovascular_alerts(results)

print("\n--- CARDIOVASCULAR MONITORING RESULTS ---")

print(cardiovascular_alerts[
    ["Subject", "Category", "Test_Phase", "Status", "Anomaly Score", "Interpretation"]
].head())

print("\n--- ALERT COUNTS ---")
print(cardiovascular_alerts["Status"].value_counts())

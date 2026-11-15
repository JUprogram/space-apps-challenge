import pandas as pd

from sleep_monitor import sleep_alerts
from cardiovascular_monitor import cardiovascular_alerts


def generate_alerts() -> pd.DataFrame:

    # 1. Combine both monitoring pipelines
    all_alerts = pd.concat(
        [sleep_alerts, cardiovascular_alerts],
        ignore_index=True,
        sort=False
    )

    # 2. Standardize subject identifiers
    all_alerts["Subject"] = all_alerts["Subject"].astype(str)

    # 3. Assign alert priorities
    all_alerts["Priority"] = all_alerts["Status"].map({
        "MONITOR": "Monitor",
        "ROUTINE": "Routine"
    })

    # 4. Sort alerts by priority
    priority_order = {
        "Monitor": 0,
        "Routine": 1
    }

    all_alerts["_priority_order"] = (
        all_alerts["Priority"].map(priority_order)
    )

    all_alerts = all_alerts.sort_values(
        by="_priority_order"
    ).drop(columns="_priority_order")

    return all_alerts


alerts = generate_alerts()


print("\n--- UNIFIED ALERT ENGINE ---")
print(alerts[
    ["Subject", "Category", "Status", "Priority", "Interpretation"]
].head(10))

print("\n--- ALERT PRIORITY COUNTS ---")
print(alerts["Priority"].value_counts())

print("\n--- ALERT CATEGORY COUNTS ---")
print(alerts.groupby(["Category", "Priority"]).size())

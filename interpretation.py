import pandas as pd

from alert_engine import alerts


def add_interpretations(data: pd.DataFrame) -> pd.DataFrame:
    interpreted = data.copy()

    # Give each alert a readable title.
    interpreted["Alert_Title"] = interpreted.apply(
        lambda row: (
            f"{row['Category']} observation flagged for review"
            if row["Priority"] == "Monitor"
            else f"{row['Category']} observation — routine"
        ),
        axis=1
    )

    # Explain what the model's result means.
    interpreted["Explanation"] = interpreted["Priority"].map({
        "Monitor": (
            "The exploratory anomaly detection model flagged "
            "this observation as an unusual pattern within the "
            "analyzed dataset. This is not a diagnosis."
        ),
        "Routine": (
            "The exploratory model did not flag this observation "
            "as unusual. This does not establish that the "
            "observation is medically normal."
        )
    })

    # Provide a general next step.
    interpreted["Next_Step"] = interpreted["Priority"].map({
        "Monitor": (
            "Review the recorded measurements and their source "
            "context through the appropriate mission health process."
        ),
        "Routine": (
            "Continue following the established mission "
            "monitoring process."
        )
    })

    # Preserve the actual measurements for the alert detail screen.
    sleep_measurements = [
        "Sleep Latency (minutes)",
        "Sleep Duration (minutes)",
        "Sleep Efficiency (%)"
    ]

    cardiovascular_measurements = [
        column for column in interpreted.select_dtypes(
            include="number"
        ).columns
        if column not in [
            "ID",
            "Predictions",
            "Anomaly Score"
        ]
    ]

    def collect_measurements(row):
        if row["Category"] == "Sleep":
            columns = sleep_measurements
        else:
            columns = cardiovascular_measurements

        measurements = {}

        for column in columns:
            if column in row.index and pd.notna(row[column]):
                measurements[column] = float(row[column])

        return measurements

    interpreted["Measurements"] = interpreted.apply(
        collect_measurements,
        axis=1
    )

    # Explain the limits of the model's reference data.
    interpreted["Reference_Context"] = (
        "Compared with patterns in the analyzed dataset; "
        "not a validated healthy or clinical baseline."
    )

    return interpreted


interpreted_alerts = add_interpretations(alerts)


if __name__ == "__main__":
    print("\n--- INTERPRETED ALERTS ---")
    print(
        interpreted_alerts[
            [
                "Category",
                "Priority",
                "Alert_Title",
                "Explanation",
                "Next_Step"
            ]
        ].head()
    )

    print("\n--- TOTAL INTERPRETED ALERTS ---")
    print(len(interpreted_alerts))

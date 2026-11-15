
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DATA_PATH = Path(__file__).parent / "BRSMCF_CFT70_2D_Echo_All"


def load_data(path=DATA_PATH):
    return pd.read_csv(path)


def prepare_data(data):
    features = data.select_dtypes(include="number").columns.tolist()

    # note: IDs identify records and participants; they are not measurements.
    features = [
        column for column in features
        if column not in ["ID", "Subject"]
    ]

    if not features:
        raise ValueError("No numerical measurement columns found.")

    return data.copy(), features


def detect_anomalies(data, features):
    """Flag unusual cardiovascular measurement patterns."""

    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        IsolationForest(
            n_estimators=100,
            contamination=0.10,
            random_state=42
        )
    )

    predictions = model.fit_predict(data[features])
    scores = model.decision_function(data[features])

    results = data.copy()

    results["Predictions"] = predictions
    results["Anomaly Score"] = scores

    results["Model Flag"] = results["Predictions"].map({
        -1: "UNUSUAL_PATTERN",
        1: "NOT_FLAGGED"
    })

    results["Interpretation"] = results["Predictions"].map({
        -1: (
            "This observation was flagged as unusual "
            "by the exploratory anomaly detection model."
        ),
        1: (
            "This observation was not flagged as unusual "
            "by the exploratory anomaly detection model."
        )
    })

    return results


# load/process the dataset
data = load_data()

clean_data, feature_columns = prepare_data(data)

results = detect_anomalies(clean_data, feature_columns)


if __name__ == "__main__":
    print("\n--- CARDIOVASCULAR DATASET ---")
    print("Dataset shape:", data.shape)
    print("Number of measurements:", len(feature_columns))

    print("\n--- PREDICTION COUNTS ---")
    print(results["Predictions"].value_counts())

    print("\n--- ANOMALIES BY SUBJECT ---")
    print(
        results[results["Predictions"] == -1]
        .groupby("Subject")
        .size()
    )

    print("\n--- SAMPLE RESULTS ---")
    print(
        results[[
            "Subject",
            "Test_Phase",
            "Day",
            "Predictions",
            "Anomaly Score",
            "Model Flag"
        ]].head(10)
    )



anomalies = results[results["Predictions"] == -1]

print("\n--- FLAGGED OBSERVATIONS ---")

print(
    anomalies[
        ["Subject", "Treatment", "Test_Phase", "Day",
         "Anomaly Score"]
    ].sort_values("Anomaly Score")
)

print("\n--- TREATMENT GROUP COUNTS ---")
print(data["Treatment"].value_counts())

print("\n--- TEST PHASE COUNTS ---")
print(data["Test_Phase"].value_counts())


most_unusual = anomalies.sort_values(
    "Anomaly Score"
).head(3)

print("\n--- MEASUREMENTS IN MOST UNUSUAL OBSERVATIONS ---")

print(
    most_unusual[
        ["Subject", "Treatment", "Test_Phase", "Day"]
        + feature_columns
    ].T
)

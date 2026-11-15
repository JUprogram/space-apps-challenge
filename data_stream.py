import time
from datetime import datetime, timezone

import pandas as pd

from interpretation import interpreted_alerts


def clean_value(value):
    """Convert pandas and NumPy values into JSON-friendly values."""

    if isinstance(value, dict):
        return {
            key: clean_value(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [clean_value(item) for item in value]

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if hasattr(value, "item"):
        return value.item()

    return value


def create_stream(data: pd.DataFrame):
    """
    Turn existing interpreted alerts into a sequential
    historical-data replay.
    """

    for index, (_, row) in enumerate(data.iterrows(), start=1):

        record = row.to_dict()

        category = record.get("Category")

        if category == "Sleep":
            source = "NASA Bed Rest Actigraphy Research"
        elif category == "Cardiovascular":
            source = "NASA-associated Bed Rest Echocardiography Research"
        else:
            source = "Unspecified Research Source"

        record["Stream_Index"] = index
        record["Data_Mode"] = "HISTORICAL_REPLAY"
        record["Is_Live"] = False
        record["Source_Label"] = source

        # This is when the replay emits the record,
        # NOT the original measurement timestamp.
        record["Replay_Emitted_At"] = (
            datetime.now(timezone.utc).isoformat()
        )

        yield {
            key: clean_value(value)
            for key, value in record.items()
        }


def run_demo(interval=1.0, max_records=None):
    """
    Replay historical observations sequentially.

    interval: seconds between emitted observations.
    max_records: optional limit for testing.
    """

    stream = create_stream(interpreted_alerts)

    print("\n--- CONTINUOUS MONITORING DEMONSTRATION ---")
    print("Mode: HISTORICAL DATA REPLAY")
    print("Live telemetry: NOT CONNECTED")

    for index, record in enumerate(stream, start=1):

        print("\n------------------------------")
        print(f"Stream Record: {record['Stream_Index']}")
        print(f"Category: {record['Category']}")
        print(f"Priority: {record['Priority']}")
        print(f"Alert: {record['Alert_Title']}")
        print(f"Source: {record['Source_Label']}")
        print(f"Mode: {record['Data_Mode']}")
        print(f"Explanation: {record['Explanation']}")

        print("------------------------------")

        if max_records is not None and index >= max_records:
            break

        time.sleep(interval)


if __name__ == "__main__":
    run_demo(interval=1.0, max_records=10)


import pandas as pd


def create_radiation_alert() -> pd.DataFrame:
    """
    Creates a simulated radiation safety alert.

    This is a demonstration scenario, not a live radiation
    measurement or an actual assessment of astronaut exposure.
    """

    alert = {
        "Category": "Radiation",
        "Status": "ACT_NOW",
        "Priority": "Act Now",
        "Alert_Title": "Radiation Safety Scenario",
        "Explanation": (
            "A simulated radiation safety event has been activated "
            "for demonstration purposes. No live radiation readings "
            "are being monitored."
        ),
        "Next_Step": (
            "Follow the designated mission radiation emergency "
            "procedure and proceed to the designated radiation "
            "shelter when instructed."
        ),
        "Data_Source": "SIMULATED DEMONSTRATION",
        "Is_Simulated": True,
        "Measurements": {},
        "Reference_Context": (
            "No actual radiation measurement, dose threshold, "
            "or astronaut exposure assessment is available."
        )
    }

    return pd.DataFrame([alert])


radiation_alerts = create_radiation_alert()


if __name__ == "__main__":
    print("\n--- RADIATION SAFETY DEMONSTRATION ---")
    print(radiation_alerts[
        [
            "Category",
            "Priority",
            "Alert_Title",
            "Explanation",
            "Next_Step",
            "Data_Source"
        ]
    ].to_string(index=False))

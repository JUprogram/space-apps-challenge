
"""
pharmacy_data.py

Purpose:
    Stores pharmacy inventory records and medication-label metadata
    for the AWACS astronaut wellness prototype.

Data policy:
    - Demonstration records must be explicitly labeled.
    - Missing information is represented by None.
    - Medication label information requires an identifiable source.
    - No medication dosing calculations or recommendations.
"""

from datetime import date

# --------------------------------------------------
# 1. Inventory status definitions
# --------------------------------------------------

INVENTORY_STATUSES = {
    "EXPIRED",
    "LOW_STOCK",
    "MISSING_LOCATION",
    "EXPIRY_NOT_RECORDED",
    "QUANTITY_NOT_RECORDED",
    "IN_STOCK",
}

# --------------------------------------------------
# 2. Identity verification states
# --------------------------------------------------

IDENTITY_STATUSES = {
    "VERIFIED",
    "NOT_VERIFIED",
    "MISMATCH_REPORTED",
}

# --------------------------------------------------
# 3. Label verification states
# --------------------------------------------------

LABEL_STATUSES = {
    "VERIFIED",
    "NOT_VERIFIED",
    "NOT_STATED_ON_LABEL",
    "SOURCE_UNAVAILABLE",
}

# --------------------------------------------------
# 4. Pharmacy inventory records
# --------------------------------------------------

PHARMACY_INVENTORY = [
    {
        "item_id": "DEMO-001",
        "generic_name": None,
        "strength": None,
        "dosage_form": None,
        "quantity": None,
        "location": None,
        "expiry_date": date(2027, 6, 30),
        "minimum_stock": None,

        "identity_status": "NOT_VERIFIED",
        "data_source": "FICTIONAL DEMONSTRATION RECORD",
        "is_demo": True,

        "label": {
            "indications": None,
            "contraindications": None,
            "warnings": None,
            "storage": None,
            "label_source": None,
            "revision_date": None,
            "label_status": "SOURCE_UNAVAILABLE",
        },
    }
]




def validate_inventory(data):
    for item in data:
        if item["identity_status"] not in IDENTITY_STATUSES:
            raise ValueError(
                f"Invalid identity status: {item['item_id']}"
            )

        label_status = item["label"]["label_status"]

        if label_status not in LABEL_STATUSES:
            raise ValueError(
                f"Invalid label status: {item['item_id']}"
            )

    return True
# --------------------------------------------------
# 5. Module metadata
# --------------------------------------------------

PHARMACY_METADATA = {
    "module": "AWACS Pharmacy",
    "version": "1.0",
    "data_mode": "DEMONSTRATION",
    "clinical_validation": False,
    "disclaimer": (
        "Wellness support only — not a medical device / "
        "does not diagnose."
    ),
}

TOTAL_INVENTORY_RECORDS = len(PHARMACY_INVENTORY)

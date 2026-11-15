
"""
pharmacy_service.py

Purpose:
    Processes AWACS pharmacy inventory records.

Responsibilities:
    - Identify inventory and expiry flags.
    - Retrieve individual inventory items.
    - Summarize inventory status.
    - Report medication identity and label verification states.

Safety:
    - Does not prescribe medication.
    - Does not calculate medication doses.
    - Does not generate medication-label content.
"""

from datetime import date
from copy import deepcopy

from pharmacy_data import (
    PHARMACY_INVENTORY,
    INVENTORY_STATUSES,
    IDENTITY_STATUSES,
    LABEL_STATUSES,
)


# --------------------------------------------------
# 1. Retrieve inventory
# --------------------------------------------------

def get_inventory():
    """Return a copy of all pharmacy inventory records."""
    return deepcopy(PHARMACY_INVENTORY)


# --------------------------------------------------
# 2. Retrieve an individual item
# --------------------------------------------------

def get_item_by_id(item_id):
    """Find an inventory item using its unique ID."""

    for item in get_inventory():
        if item["item_id"] == item_id:
            return item

    return None


# --------------------------------------------------
# 3. Validate inventory records
# --------------------------------------------------

def validate_item(item):
    """Check basic inventory data consistency."""

    if item.get("identity_status") not in IDENTITY_STATUSES:
        raise ValueError(
            f"Invalid identity status: {item.get('item_id')}"
        )

    label = item.get("label", {})

    if label.get("label_status") not in LABEL_STATUSES:
        raise ValueError(
            f"Invalid label status: {item.get('item_id')}"
        )

    quantity = item.get("quantity")
    minimum_stock = item.get("minimum_stock")

    if quantity is not None:
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("Quantity must be an integer or None.")

        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

    if minimum_stock is not None:
        if isinstance(minimum_stock, bool) or not isinstance(minimum_stock, int):
            raise ValueError("Minimum stock must be an integer or None.")

        if minimum_stock < 0:
            raise ValueError("Minimum stock cannot be negative.")

    return True


# --------------------------------------------------
# 4. Calculate inventory flags
# --------------------------------------------------

def get_inventory_flags(item, today=None):
    """
    Identify inventory issues.

    Multiple flags can apply to one item.
    """

    if today is None:
        today = date.today()

    validate_item(item)

    flags = []

    quantity = item.get("quantity")
    minimum_stock = item.get("minimum_stock")
    location = item.get("location")
    expiry = item.get("expiry_date")

    # Missing quantity
    if quantity is None:
        flags.append("QUANTITY_NOT_RECORDED")

    # Low stock
    if (
        quantity is not None
        and minimum_stock is not None
        and quantity <= minimum_stock
    ):
        flags.append("LOW_STOCK")

    # Missing location
    if not location:
        flags.append("MISSING_LOCATION")

    # Missing expiry date
    if expiry is None:
        flags.append("EXPIRY_NOT_RECORDED")

    # Expiry check
    elif isinstance(expiry, date):
        if expiry < today:
            flags.append("EXPIRED")

    else:
        raise ValueError(
            f"Invalid expiry date for item {item['item_id']}. "
            "Use datetime.date or None."
        )

    # No identified inventory issues
    if not flags:
        flags.append("IN_STOCK")

    return flags


# --------------------------------------------------
# 5. Process all inventory records
# --------------------------------------------------

def process_inventory():
    """Return inventory records with calculated status flags."""

    processed = []

    for item in get_inventory():

        flags = get_inventory_flags(item)

        item["inventory_flags"] = flags

        item["inventory_status"] = (
            "IN_STOCK" if flags == ["IN_STOCK"]
            else "ATTENTION_REQUIRED"
        )

        processed.append(item)

    return processed


# --------------------------------------------------
# 6. Inventory summary
# --------------------------------------------------

def get_inventory_summary():
    """Return a summary of inventory records and flags."""

    inventory = process_inventory()

    summary = {
        "total_items": len(inventory),
        "in_stock": 0,
        "attention_required": 0,
        "low_stock": 0,
        "expired": 0,
        "missing_location": 0,
        "missing_expiry": 0,
        "quantity_not_recorded": 0,
    }

    for item in inventory:

        flags = item["inventory_flags"]

        if item["inventory_status"] == "IN_STOCK":
            summary["in_stock"] += 1
        else:
            summary["attention_required"] += 1

        if "LOW_STOCK" in flags:
            summary["low_stock"] += 1

        if "EXPIRED" in flags:
            summary["expired"] += 1

        if "MISSING_LOCATION" in flags:
            summary["missing_location"] += 1

        if "EXPIRY_NOT_RECORDED" in flags:
            summary["missing_expiry"] += 1

        if "QUANTITY_NOT_RECORDED" in flags:
            summary["quantity_not_recorded"] += 1

    return summary


# --------------------------------------------------
# 7. Medication label status
# --------------------------------------------------

def get_label_status(item_id):
    """Return label availability and verification information."""

    item = get_item_by_id(item_id)

    if item is None:
        return None

    label = item.get("label", {})

    return {
        "item_id": item_id,
        "label_status": label.get("label_status"),
        "label_source": label.get("label_source"),
        "revision_date": label.get("revision_date"),
        "available": (
            label.get("label_status") == "VERIFIED"
            and bool(label.get("label_source"))
            and label.get("revision_date") is not None
        ),
    }


# --------------------------------------------------
# 8. Run basic tests
# --------------------------------------------------

if __name__ == "__main__":

    print("\n--- PHARMACY INVENTORY ---")

    for item in process_inventory():
        print(
            item["item_id"],
            item["inventory_status"],
            item["inventory_flags"]
        )

    print("\n--- INVENTORY SUMMARY ---")
    print(get_inventory_summary())

    print("\n--- LABEL STATUS ---")
    print(get_label_status("DEMO-001"))

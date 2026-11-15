
from datetime import datetime, timezone
from pathlib import Path
import asyncio
import json
import math

import numpy as np
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from interpretation import interpreted_alerts
from radiation_monitor import radiation_alerts
from data_stream import create_stream, clean_value


app = FastAPI(
    title="Astronaut Health Monitoring API",
    description=(
        "Exploratory anomaly monitoring using historical "
        "spaceflight-analog research data."
    ),
    version="1.0"
)


# --------------------------------------------------
# CORS: allow the published dashboard to access API
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://site-805353b925304a718040254659b2f894.freebuff.page",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Shared data
# --------------------------------------------------

all_alerts = pd.concat(
    [interpreted_alerts, radiation_alerts],
    ignore_index=True,
    sort=False
)

stream_iterator = iter(create_stream(interpreted_alerts))


def current_time():
    return datetime.now(timezone.utc).isoformat()


def safe_records(data):
    records = data.to_dict(orient="records")
    return [
        {
            key: clean_value(value)
            for key, value in record.items()
        }
        for record in records
    ]


def get_date(record):
    value = record.get("Date")

    if value is None or pd.isna(value):
        return current_time()

    timestamp = pd.to_datetime(value, errors="coerce")

    if pd.isna(timestamp):
        return current_time()

    return timestamp.isoformat()


def format_measurements(measurements):
    if not isinstance(measurements, dict):
        return "No measurement details available."

    entries = []

    for name, value in measurements.items():
        value = clean_value(value)

        if value is not None:
            entries.append(f"{name}: {value}")

    if not entries:
        return "No measurement details available."

    return "; ".join(entries)


# --------------------------------------------------
# Convert model flags into dashboard anomalies
# --------------------------------------------------

def build_anomalies():
    flagged = interpreted_alerts[
        interpreted_alerts["Status"] == "MONITOR"
    ].copy()

    anomalies = []

    for index, (_, row) in enumerate(
        flagged.iterrows(),
        start=1
    ):
        record = row.to_dict()

        category = record.get("Category", "Research")
        subject = record.get("Subject", "Unknown")
        phase = record.get("Test_Phase", "Not specified")

        measurements = record.get("Measurements", {})
        measurement_text = format_measurements(measurements)

        explanation = record.get(
            "Explanation",
            "An unusual pattern was flagged by the exploratory model."
        )

        reference = record.get(
            "Reference_Context",
            "No validated clinical baseline is available."
        )

        next_step = record.get(
            "Next_Step",
            "Review this historical observation in its research context."
        )

        anomalies.append({
            "id": f"research-flag-{index}",

            # Model flags are informational, not clinical severity.
            "severity": "info",

            "title": f"{category} observation flagged for review",

            "summary": (
                f"Historical research observation for subject "
                f"{subject}, phase {phase}."
            ),

            "detectedAt": get_date(record),

            "explanation": {
                "summary": explanation,

                "detail": (
                    f"Recorded measurements: {measurement_text}. "
                    f"Reference context: {reference}. "
                    "The Isolation Forest identified this observation "
                    "as unusual relative to patterns in the analyzed "
                    "dataset. Individual feature contributions were "
                    "not calculated. This is not a diagnosis or a "
                    "validated clinical threshold."
                ),

                "contributing": [],

                "recommendedAction": next_step
            },

            # No confidence score or invented metric references.
            "confidence": None,
            "metricRefs": []
        })

    return anomalies


# --------------------------------------------------
# Build simulated radiation information
# --------------------------------------------------

def build_radiation_analysis():
    return {
        "status": "critical",
        "riskLabel": "SIMULATED SCENARIO",
        "headline": (
            "SIMULATED radiation safety scenario — "
            "follow designated shelter procedure"
        ),
        "subhead": (
            "Demonstration only. No live radiation telemetry "
            "is connected."
        ),
        "criticalNote": (
            "SIMULATION ONLY — no live radiation measurement "
            "or dose assessment is available."
        )
    }


# --------------------------------------------------
# Full dashboard snapshot
# --------------------------------------------------

def build_snapshot():
    now = current_time()

    anomalies = build_anomalies()

    return {
        "schemaVersion": "1.0",
        "generatedAt": now,

        "meta": {
            "source": "python-service",
            "synthetic": False,
            "label": (
                "Historical NASA-associated bed-rest research "
                "replay. Not live astronaut telemetry."
            )
        },

        # The research datasets do not represent one
        # currently monitored astronaut.
        "subject": {},

        "measurements": {
            "environment": {
                "link": {
                    "online": False
                }
            }
        },

        "analysis": {
            "status": "ok",

            "engine": {
                "name": "Isolation Forest",
                "version": "1.0"
            },

            "analyzedAt": now,

            "anomalies": anomalies,

            "environment": {
                "radiation": build_radiation_analysis()
            },

            "recommendations": [
                {
                    "id": "radiation-demo-action",
                    "priority": "immediate",
                    "title": (
                        "SIMULATED: Follow radiation "
                        "shelter procedure"
                    ),
                    "detail": (
                        "In an actual mission event, follow the "
                        "designated mission radiation emergency "
                        "procedure and proceed to the designated "
                        "radiation shelter when instructed."
                    )
                }
            ]
        }
    }


# --------------------------------------------------
# Basic endpoints
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Astronaut Health Monitoring API is running."
    }


@app.get("/health")
def health():
    return {
        "api_status": "ONLINE",
        "historical_replay_available": True,
        "live_telemetry_connected": False,
        "radiation_data_mode": "SIMULATED",
        "disclaimer": (
            "Wellness support only — not a medical device / "
            "does not diagnose."
        )
    }


# --------------------------------------------------
# Dashboard endpoint: GET /snapshot
# --------------------------------------------------

@app.get("/snapshot")
def get_snapshot():
    return build_snapshot()


# --------------------------------------------------
# Dashboard endpoint: GET /stream
# Server-sent events
# --------------------------------------------------

@app.get("/stream")
async def get_sse_stream():

    async def event_generator():
        snapshot = build_snapshot()

        yield (
            "event: snapshot\n"
            f"data: {json.dumps(snapshot, allow_nan=False)}\n\n"
        )

        # Keep the connection alive without pretending
        # historical research data is being updated.
        while True:
            await asyncio.sleep(15)
            yield ": keep-alive\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# --------------------------------------------------
# Existing research alert endpoint
# --------------------------------------------------

@app.get("/alerts")
def get_alerts():
    records = safe_records(all_alerts)

    return {
        "total_alerts": len(records),
        "alerts": records
    }


# --------------------------------------------------
# Existing sequential historical replay endpoint
# --------------------------------------------------

@app.get("/stream/next")
def get_next_observation():
    record = next(stream_iterator, None)

    if record is None:
        return {
            "stream_status": "COMPLETE",
            "data_mode": "HISTORICAL_REPLAY"
        }

    return {
        "stream_status": "RUNNING",
        "data_mode": "HISTORICAL_REPLAY",
        "live_telemetry_connected": False,
        "record": record
    }


@app.post("/stream/reset")
def reset_stream():
    global stream_iterator

    stream_iterator = iter(create_stream(interpreted_alerts))

    return {
        "message": "Historical replay restarted.",
        "data_mode": "HISTORICAL_REPLAY"
    }


# --------------------------------------------------
# Radiation demonstration endpoint
# --------------------------------------------------

@app.get("/radiation/demo")
def get_radiation_demo():
    records = safe_records(radiation_alerts)

    return {
        "data_mode": "SIMULATED",
        "is_live": False,
        "alert": records[0]
    }

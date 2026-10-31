"""
Test suite for SPORTZA FastAPI endpoints.

Verifies status codes, response structures, schema conformance, and data presence
across all 10 canonical endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "service": "sportza-backend"}


def test_get_overview():
    res = client.get("/v1/overview")
    assert res.status_code == 200
    data = res.json()
    assert "dataset" in data
    assert data["dataset"]["athletes"] > 0
    assert data["dataset"]["sessions"] > 0
    assert "kpis" in data
    assert len(data["kpis"]) >= 3
    assert "trends" in data
    assert "insights" in data


def test_get_athletes():
    res = client.get("/v1/athletes")
    assert res.status_code == 200
    data = res.json()
    assert "athletes" in data
    assert len(data["athletes"]) > 0
    first = data["athletes"][0]
    assert "id" in first
    assert "name" in first
    assert "status" in first
    assert first["status"] in ["available", "limited", "unavailable"]


def test_get_athlete_detail():
    # First get athletes list to find a valid ID
    roster_res = client.get("/v1/athletes")
    athletes = roster_res.json()["athletes"]
    assert len(athletes) > 0
    target_id = athletes[0]["id"]

    res = client.get(f"/v1/athletes/{target_id}")
    assert res.status_code == 200
    data = res.json()
    assert "athlete" in data
    assert data["athlete"]["id"] == target_id
    assert "series" in data
    assert "recentSessions" in data


def test_get_athlete_detail_not_found():
    res = client.get("/v1/athletes/non-existent-id-9999")
    assert res.status_code == 404


def test_get_readiness():
    roster_res = client.get("/v1/athletes")
    athletes = roster_res.json()["athletes"]
    target_id = athletes[0]["id"]

    res = client.get(f"/v1/readiness/{target_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["athleteId"] == target_id
    assert "score" in data
    assert "baselineScore" in data
    assert "factors" in data
    assert "recommendation" in data
    assert "disclaimer" in data


def test_get_workload():
    res = client.get("/v1/workload")
    assert res.status_code == 200
    data = res.json()
    assert "trends" in data
    assert "acuteChronic" in data
    assert "sessionsByType" in data
    assert "definitions" in data
    assert len(data["definitions"]) > 0


def test_get_injuries():
    res = client.get("/v1/injuries")
    assert res.status_code == 200
    data = res.json()
    assert "records" in data
    assert len(data["records"]) > 0
    first = data["records"][0]
    assert "bodyLocation" in first
    assert first["severity"] in ["mild", "moderate", "severe"]
    assert first["source"] in ["self_reported", "clinical"]


def test_get_forecast():
    res = client.get("/v1/forecast")
    assert res.status_code == 200
    data = res.json()
    assert "metric" in data
    assert "horizonDays" in data
    assert "points" in data
    assert len(data["points"]) > 0
    assert "metrics" in data
    assert "notes" in data


def test_get_team():
    res = client.get("/v1/team")
    assert res.status_code == 200
    data = res.json()
    assert "positions" in data
    assert len(data["positions"]) >= 4
    assert "metrics" in data
    assert len(data["metrics"]) >= 2


def test_get_correlations():
    res = client.get("/v1/correlations")
    assert res.status_code == 200
    data = res.json()
    assert "variables" in data
    assert "pairs" in data
    assert len(data["pairs"]) > 0
    for pair in data["pairs"]:
        assert -1.0 <= pair["r"] <= 1.0


def test_get_models():
    res = client.get("/v1/models")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert len(data["models"]) >= 2
    assert "activeModelId" in data


"""Unit tests for demo data generator and schema validation."""
import pandas as pd

from src.data.demo_generator import generate_demo_data
from src.data.schema import validate_dataframe


def test_generate_demo_data_structure():
    data = generate_demo_data()
    assert isinstance(data, dict)
    expected_keys = [
        "wellness_daily",
        "training_sessions",
        "injury_events",
        "illness_events",
        "game_performance",
    ]
    for key in expected_keys:
        assert key in data
        assert isinstance(data[key], pd.DataFrame)
        assert len(data[key]) > 0


def test_demo_schema_conformance():
    data = generate_demo_data()
    for name, df in data.items():
        errors = validate_dataframe(df, name)
        assert len(errors) == 0, f"Schema validation failed for {name}: {errors}"


def test_demo_reproducibility():
    data1 = generate_demo_data()
    data2 = generate_demo_data()
    # Check that deterministic seed creates identical records
    pd.testing.assert_frame_equal(data1["wellness_daily"], data2["wellness_daily"])
    pd.testing.assert_frame_equal(data1["training_sessions"], data2["training_sessions"])

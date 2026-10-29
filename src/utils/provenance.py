"""
SPORTZA Data Provenance Tracking
"""
from datetime import UTC, datetime


def get_timestamp() -> str:
    """Return current UTC timestamp as ISO string."""
    return datetime.now(UTC).isoformat()


def get_source_attribution() -> str:
    """Return the SoccerMon dataset attribution text."""
    return (
        "Data source: SoccerMon Dataset (Midoglu et al., 2024). "
        "Licensed under CC BY 4.0. "
        "DOI: https://zenodo.org/doi/10.5281/zenodo.10033832. "
        "Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC11139986/"
    )


def get_data_mode_label(is_demo: bool) -> str:
    """Return display label for current data mode."""
    if is_demo:
        return "🧪 Synthetic Demo Data — Not from real athletes"
    return "📊 SoccerMon Real Data (CC BY 4.0)"


def get_ingestion_metadata(source_file: str, source_dataset: str = "soccermon") -> dict:
    """Return standard ingestion metadata."""
    return {
        "source_file": source_file,
        "source_dataset": source_dataset,
        "ingested_at": get_timestamp(),
    }


"""Explanation formatting for decision-support recommendations.

Converts internal ``Recommendation`` objects into display-ready
dictionaries for Streamlit cards, factor-contribution strings, and
full audit-trail payloads.
"""

from typing import Any

from .rules import (
    ObservedFactor,
    Recommendation,
    RecommendationStatus,
)

# ======================================================================
# Status → visual config mappings
# ======================================================================

_STATUS_COLORS: dict[RecommendationStatus, str] = {
    RecommendationStatus.MONITOR: "#4CAF50",           # green
    RecommendationStatus.RECOVERY_FOCUSED: "#FF9800",   # orange
    RecommendationStatus.HUMAN_REVIEW: "#F44336",       # red
    RecommendationStatus.INSUFFICIENT_DATA: "#9E9E9E",  # grey
}

_STATUS_ICONS: dict[RecommendationStatus, str] = {
    RecommendationStatus.MONITOR: "✅",
    RecommendationStatus.RECOVERY_FOCUSED: "🔶",
    RecommendationStatus.HUMAN_REVIEW: "🔴",
    RecommendationStatus.INSUFFICIENT_DATA: "⚪",
}


# ======================================================================
# Public API
# ======================================================================

def format_recommendation_card(rec: Recommendation) -> dict[str, Any]:
    """Convert a ``Recommendation`` into a dictionary ready for Streamlit rendering.

    The returned dict contains keys suitable for direct use in
    ``st.metric``, ``st.info``, ``st.warning``, etc.

    Parameters
    ----------
    rec : Recommendation
        The engine's recommendation output.

    Returns
    -------
    dict
        Keys: ``status_label``, ``status_color``, ``status_icon``,
        ``recommendation_text``, ``rationale_bullets``,
        ``factor_summaries``, ``data_adequacy``, ``escalation_flags``,
        ``review_window``, ``non_medical_note``, ``cannot_infer``,
        ``baseline_period``, ``player_id``, ``date``.
    """
    return {
        "player_id": rec.player_id,
        "date": rec.date,
        "status_label": rec.status.value,
        "status_color": _STATUS_COLORS.get(rec.status, "#9E9E9E"),
        "status_icon": _STATUS_ICONS.get(rec.status, "⚪"),
        "recommendation_text": rec.recommendation_text,
        "rationale_bullets": rec.rationale,
        "factor_summaries": [
            format_factor_contribution(f) for f in rec.observed_factors
        ],
        "data_adequacy": rec.data_adequacy.value,
        "escalation_flags": rec.escalation_flags,
        "review_window": rec.suggested_review_window,
        "non_medical_note": rec.non_medical_note,
        "cannot_infer": rec.what_system_cannot_infer,
        "baseline_period": rec.baseline_comparison_period,
    }


def format_factor_contribution(factor: ObservedFactor) -> str:
    """Produce a compact, human-readable string for one observed factor.

    Examples
    --------
    >>> format_factor_contribution(factor)
    '🔻 Fatigue: 7.2 vs baseline 5.1 (+1.3 SD) — moderately worse than baseline.'
    """
    pretty_name = factor.name.replace("_", " ").title()

    # Choose direction arrow
    if factor.current_value is None or factor.deviation is None:
        arrow = "➖"
    else:
        is_adverse = (
            (factor.direction == "higher_is_better" and factor.deviation < 0)
            or (factor.direction == "higher_is_worse" and factor.deviation > 0)
        )
        if abs(factor.deviation) < 0.5:
            arrow = "➖"  # neutral
        elif is_adverse:
            arrow = "🔻"  # worse
        else:
            arrow = "🔺"  # better

    # Value text
    if factor.current_value is None:
        val_text = "no data"
    elif factor.baseline_value is not None:
        val_text = (
            f"{factor.current_value:.1f} vs baseline "
            f"{factor.baseline_value:.1f}"
        )
    else:
        val_text = f"{factor.current_value:.1f} (no baseline)"

    # Deviation text
    if factor.deviation is not None:
        sign = "+" if factor.deviation > 0 else ""
        dev_text = f" ({sign}{factor.deviation:.1f} SD)"
    else:
        dev_text = ""

    return f"{arrow} {pretty_name}: {val_text}{dev_text} — {factor.interpretation}"


def generate_decision_audit(rec: Recommendation) -> dict[str, Any]:
    """Produce a comprehensive audit-trail dictionary for a recommendation.

    This is richer than the card format and is intended for logging,
    compliance, or detailed review.

    Parameters
    ----------
    rec : Recommendation
        The engine's recommendation output.

    Returns
    -------
    dict
        Full audit payload including raw factor data, rule triggers, and
        the non-medical disclaimer.
    """
    factor_details: list[dict[str, Any]] = []
    for f in rec.observed_factors:
        factor_details.append(
            {
                "name": f.name,
                "current_value": f.current_value,
                "baseline_value": f.baseline_value,
                "deviation_sd": f.deviation,
                "direction": f.direction,
                "interpretation": f.interpretation,
                "formatted": format_factor_contribution(f),
            }
        )

    return {
        "audit_version": "1.0",
        "player_id": rec.player_id,
        "evaluation_date": rec.date,
        "status": rec.status.value,
        "status_enum": rec.status.name,
        "recommendation_text": rec.recommendation_text,
        "baseline_comparison_period": rec.baseline_comparison_period,
        "data_adequacy": rec.data_adequacy.value,
        "observed_factors": factor_details,
        "rationale": rec.rationale,
        "escalation_flags": rec.escalation_flags,
        "what_system_cannot_infer": rec.what_system_cannot_infer,
        "suggested_review_window": rec.suggested_review_window,
        "non_medical_note": rec.non_medical_note,
    }

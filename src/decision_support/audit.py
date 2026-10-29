"""In-memory audit log for decision-support recommendations.

Stores every recommendation produced by the ``DecisionEngine`` so that
coaches and analysts can review historical decisions, trace rationale,
and satisfy governance requirements.

For the demo / MVP this is a simple in-memory list.  In production it
would be backed by a database.
"""

from datetime import datetime
from typing import Any

from .explanation import generate_decision_audit
from .rules import Recommendation


class DecisionAuditLog:
    """Append-only in-memory audit log for player recommendations.

    Usage
    -----
    >>> log = DecisionAuditLog()
    >>> log.log_decision(recommendation)
    >>> trail = log.get_audit_trail("P001", ("2024-01-01", "2024-01-31"))
    """

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    # ------------------------------------------------------------------ #
    # Write
    # ------------------------------------------------------------------ #
    def log_decision(self, recommendation: Recommendation) -> None:
        """Persist a recommendation to the audit log.

        Parameters
        ----------
        recommendation : Recommendation
            The recommendation object produced by ``DecisionEngine.evaluate``.
        """
        audit_record = generate_decision_audit(recommendation)
        audit_record["logged_at"] = datetime.utcnow().isoformat() + "Z"
        self._entries.append(audit_record)

    # ------------------------------------------------------------------ #
    # Read
    # ------------------------------------------------------------------ #
    def get_audit_trail(
        self,
        player_id: str,
        date_range: tuple[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve audit entries for a player, optionally filtered by date.

        Parameters
        ----------
        player_id : str
            The player whose audit trail to retrieve.
        date_range : tuple[str, str] | None
            Optional ``(start_date, end_date)`` in ISO format (inclusive).
            If ``None``, all entries for the player are returned.

        Returns
        -------
        list[dict]
            Matching audit records in chronological order.
        """
        results: list[dict[str, Any]] = []
        for entry in self._entries:
            if entry.get("player_id") != player_id:
                continue

            if date_range is not None:
                start_str, end_str = date_range
                eval_date = entry.get("evaluation_date", "")
                if eval_date < start_str or eval_date > end_str:
                    continue

            results.append(entry)

        return results

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @property
    def total_entries(self) -> int:
        """Return the total number of logged decisions."""
        return len(self._entries)

    def get_all_entries(self) -> list[dict[str, Any]]:
        """Return all audit entries (unfiltered)."""
        return list(self._entries)

    def clear(self) -> None:
        """Clear all entries (useful for testing)."""
        self._entries.clear()

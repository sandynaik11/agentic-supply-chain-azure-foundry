"""
date.py — provides the real current date for the Purchase Order Agent.

An LLM has no access to the system clock and will guess the date (incorrectly).
The Purchase Order Agent runs this script via Code Interpreter to insert a
real, deterministic date onto every generated purchase order.
"""
from datetime import datetime, timezone


def get_current_date() -> str:
    """Return today's date in ISO format (YYYY-MM-DD), UTC."""
    return datetime.now(timezone.utc).date().isoformat()


if __name__ == "__main__":
    print(get_current_date())

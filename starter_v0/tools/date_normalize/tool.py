from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from tools._shared import fold_text


def _parse_reference_date(reference_date: str = "") -> date:
    if not reference_date:
        return date.today()
    try:
        return datetime.strptime(reference_date, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


def _range_for(timeframe: str, today: date) -> tuple[date, date]:
    if timeframe == "day":
        return today, today
    if timeframe == "week":
        return today - timedelta(days=today.weekday()), today
    if timeframe == "month":
        return today.replace(day=1), today
    if timeframe == "year":
        return today.replace(month=1, day=1), today
    return today - timedelta(days=7), today


def date_normalize(text: str, reference_date: str = "") -> dict[str, Any]:
    folded = fold_text(text or "")
    today = _parse_reference_date(reference_date)

    timeframe = "week"
    if any(token in folded for token in ["hom nay", "today", "24h", "ngay nay"]):
        timeframe = "day"
    elif any(token in folded for token in ["tuan", "week", "7 ngay"]):
        timeframe = "week"
    elif any(token in folded for token in ["thang", "month", "30 ngay"]):
        timeframe = "month"
    elif any(token in folded for token in ["nam", "year", "12 thang"]):
        timeframe = "year"

    start_date, end_date = _range_for(timeframe, today)
    return {
        "tool": "date_normalize",
        "input": text,
        "timeframe": timeframe,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }

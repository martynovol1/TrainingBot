from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(slots=True)
class StatisticsQuery:
    target_date: date | None


def parse_statistics_query(value: str | None) -> StatisticsQuery:
    if not value:
        return StatisticsQuery(target_date=date.today())

    try:
        return StatisticsQuery(target_date=datetime.strptime(value, "%Y-%m-%d").date())
    except ValueError:
        return StatisticsQuery(target_date=None)

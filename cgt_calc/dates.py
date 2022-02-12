"""Function to work with dates."""
from __future__ import annotations

import datetime
from typing import overload


def is_date(date: datetime.date) -> bool:
    """Check if date has only date but not time."""
    if not isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
        raise Exception(f'should be datetime.date: {type(date)} "{date}"')
    return True


@overload
def parse_date(date_str: str, date_format: str) -> datetime.date:
    ...


@overload
def parse_date(date_str: None, date_format: str) -> None:
    ...


def parse_date(date_str: str | None, date_format: str) -> datetime.date | None:
    """Parse date from string."""
    return (
        datetime.datetime.strptime(date_str, date_format).date()
        if date_str is not None
        else None
    )


def get_tax_year_start(tax_year: int) -> datetime.date:
    """Return tax year start date."""
    # 6 April
    return datetime.date(tax_year, 4, 6)


def get_tax_year_end(tax_year: int) -> datetime.date:
    """Return tax year end date."""
    # 5 April
    return datetime.date(tax_year + 1, 4, 5)

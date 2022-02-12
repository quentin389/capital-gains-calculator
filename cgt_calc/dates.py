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


def get_tax_year_dates(
    tax_year: int, split_year_start: str | None, split_year_end: str | None
) -> tuple[datetime.date, datetime.date]:
    """Get tax year start and end date taking into account split year treatment."""
    split_year_start_date = parse_date(split_year_start, "%Y-%m-%d")
    split_year_end_date = parse_date(split_year_end, "%Y-%m-%d")
    tax_year_start_date = get_tax_year_start(tax_year)
    tax_year_end_date = get_tax_year_end(tax_year)

    if split_year_start_date:
        tax_year_start_date = max(tax_year_start_date, split_year_start_date)
    if split_year_end_date:
        tax_year_end_date = min(tax_year_end_date, split_year_end_date)

    print(f"Tax year start date set to {tax_year_start_date}")
    print(f"Tax year end date set to {tax_year_end_date}")
    assert tax_year_start_date < tax_year_end_date
    return tax_year_start_date, tax_year_end_date


def get_tax_year_start(tax_year: int) -> datetime.date:
    """Return tax year start date."""
    # 6 April
    return datetime.date(tax_year, 4, 6)


def get_tax_year_end(tax_year: int) -> datetime.date:
    """Return tax year end date."""
    # 5 April
    return datetime.date(tax_year + 1, 4, 5)

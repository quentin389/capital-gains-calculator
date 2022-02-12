"""Custom parser."""
from __future__ import annotations

import csv
import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path

from cgt_calc.exceptions import ParsingError, UnexpectedColumnCountError
from cgt_calc.model import ActionType, BrokerTransaction


def action_from_str(label: str) -> ActionType:
    """Convert string label to ActionType."""
    label_lowercase = label.lower()
    if label_lowercase == "buy":
        return ActionType.BUY

    if label_lowercase == "sell":
        return ActionType.SELL

    raise ParsingError("custom transactions", f"Unknown action: {label}")


class CustomColumns(Enum):
    """Columns definition for the custom format, for easier modification."""

    DATE = 0
    ACTION = 1
    SYMBOL = 2
    QUANTITY = 3
    PRICE = 4
    FEES = 5
    AMOUNT = 6
    CURRENCY = 7
    BROKER = 8

    @classmethod
    def count(cls) -> int:
        """Return number of columns in the custom format."""
        return max([item.value for item in cls]) + 1


class CustomTransaction(BrokerTransaction):
    """Represent single Schwab transaction."""

    def __init__(
        self,
        row: list[str],
        file: str,
    ):
        """Create transaction from CSV row."""
        if len(row) != CustomColumns.count():
            raise UnexpectedColumnCountError(row, CustomColumns.count(), file)
        date_str = row[CustomColumns.DATE.value]
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        self.raw_action = row[CustomColumns.ACTION.value]
        action = action_from_str(self.raw_action)
        symbol = (
            row[CustomColumns.SYMBOL.value]
            if row[CustomColumns.SYMBOL.value] != ""
            else None
        )
        description = ""
        quantity = (
            Decimal(row[CustomColumns.QUANTITY.value])
            if row[CustomColumns.QUANTITY.value] != ""
            else None
        )
        price = (
            Decimal(row[CustomColumns.PRICE.value])
            if row[CustomColumns.PRICE.value] != ""
            else None
        )
        fees = (
            Decimal(row[CustomColumns.FEES.value])
            if row[CustomColumns.FEES.value] != ""
            else Decimal(0)
        )
        amount = (
            Decimal(row[CustomColumns.AMOUNT.value])
            if row[CustomColumns.AMOUNT.value] != ""
            else None
        )

        currency = row[CustomColumns.CURRENCY.value]
        broker = row[CustomColumns.BROKER.value]
        super().__init__(
            date,
            action,
            symbol,
            description,
            quantity,
            price,
            fees,
            amount,
            currency,
            broker,
        )

    @staticmethod
    def create(row: list[str], file: str) -> CustomTransaction:
        """Create and post process a CustomTransaction."""
        return CustomTransaction(row, file)


def read_custom_transactions(transactions_file: str) -> list[BrokerTransaction]:
    """Read Custom transactions from file."""
    try:
        with Path(transactions_file).open(encoding="utf-8") as csv_file:
            lines = list(csv.reader(csv_file))

            if len(lines[0]) != CustomColumns.count():
                raise ParsingError(
                    transactions_file,
                    "First line of Custom transactions file must be a header"
                    f" with {CustomColumns.count()} columns",
                )

            # Remove headers
            lines = lines[1:]
            transactions = [
                CustomTransaction.create(row, transactions_file) for row in lines
            ]
            return list(transactions)
    except FileNotFoundError:
        print(f"WARNING: Couldn't locate Custom transactions file({transactions_file})")
        return []

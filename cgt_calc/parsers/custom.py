"""Custom parser."""
from __future__ import annotations

import csv
import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path

from cgt_calc.exceptions import (
    ParsingError,
    UnexpectedColumnCountError,
)
from cgt_calc.model import ActionType, BrokerTransaction


def action_from_str(label: str) -> ActionType:
    """Convert string label to ActionType."""
    label_lowercase = label.lower()
    if label_lowercase == "buy":
        return ActionType.BUY

    if label_lowercase == "sell":
        return ActionType.SELL

    raise ParsingError("custom transactions", f"Unknown action: {label}")


class CustomRows(Enum):
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
    def columns(cls):
        return max([item.value for item in cls]) + 1


class CustomTransaction(BrokerTransaction):
    """Represent single Schwab transaction."""

    def __init__(
        self,
        row: list[str],
        file: str,
    ):
        """Create transaction from CSV row."""
        if len(row) != CustomRows.columns():
            raise UnexpectedColumnCountError(row, CustomRows.columns(), file)
        date_str = row[CustomRows.DATE.value]
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        self.raw_action = row[CustomRows.ACTION.value]
        action = action_from_str(self.raw_action)
        symbol = row[CustomRows.SYMBOL.value] if row[CustomRows.SYMBOL.value] != "" else None
        description = ""
        quantity = Decimal(row[CustomRows.QUANTITY.value]) if row[CustomRows.QUANTITY.value] != "" else None
        price = Decimal(row[CustomRows.PRICE.value]) if row[CustomRows.PRICE.value] != "" else None
        fees = Decimal(row[CustomRows.FEES.value]) if row[CustomRows.FEES.value] != "" else Decimal(0)
        amount = Decimal(row[CustomRows.AMOUNT.value]) if row[CustomRows.AMOUNT.value] != "" else None

        currency = row[CustomRows.CURRENCY.value]
        broker = row[CustomRows.BROKER.value]
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
    def create(
        row: list[str], file: str
    ) -> CustomTransaction:
        """Create and post process a CustomTransaction."""
        return CustomTransaction(row, file)


def read_custom_transactions(
    transactions_file: str
) -> list[BrokerTransaction]:
    """
    Read Custom transactions from file.
    Date,Action,Symbol,Quantity,Price,Fees,Amount,Currency,Broker
    Date = 2021-03-23 (%Y-%m-%d)
    Action = Buy | Sell | BUY | SELL
    Symbol = TSLA | etc.
    Quantity = integer > 0
    Price = price per 1 share, float > 0
    Fees = sum af all fees and commissions in the same currency as the prices, float >= 0
    Amount = gain/loss of YOUR money, including fees, positive for sale transactions, negative for buy transactions
    Currency = USD | currency symbol
    Broker = Name of the broker
    """
    try:
        with Path(transactions_file).open(encoding="utf-8") as csv_file:
            lines = list(csv.reader(csv_file))

            if len(lines[0]) != CustomRows.columns():
                raise ParsingError(
                    transactions_file,
                    "First line of Custom transactions file must be a header"
                    f" with {CustomRows.columns()} columns",
                )

            # Remove headers
            lines = lines[1:]
            transactions = [
                CustomTransaction.create(row, transactions_file)
                for row in lines
            ]
            return list(transactions)
    except FileNotFoundError:
        print(f"WARNING: Couldn't locate Custom transactions file({transactions_file})")
        return []

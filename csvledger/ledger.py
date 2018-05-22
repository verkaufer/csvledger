import csv
import json
import pathlib

from decimal import Decimal
from datetime import datetime
from collections import defaultdict

from .const import ZERO_BALANCE, TWO_DECIMAL_PLACES, TRANSACTION_DATE_FORMAT
from .exceptions import RowValidationError, EmptyLedgerError


def _decimal_encoder(obj):
    """
    Transforms Decimal types into strings during json.dumps call
    """
    if isinstance(obj, Decimal):
        return str(obj)
    return obj


def validate_csv_row(row: dict, check_transaction_date: bool = False) -> None:
    """
    Applies validation rules for each row in the CSV file.
    :param row Dictionary containing key-value pairs for a row in the CSV
    :param check_transaction_date Flag for whether Date validation needed

    :raises: RowValidationError
    """

    # Check has all columns (i.e. fields)
    if any(column_value in (None, "") for column_value in row.values()):
        raise RowValidationError

    # If checking transaction dates, validate the Date column is valid
    if check_transaction_date:
        try:
            transaction_date = datetime.strptime(
                row['Date'], TRANSACTION_DATE_FORMAT)
        except ValueError:
            raise RowValidationError


def calculate_balances(csv_path: str, max_transaction_date: str = None) -> str:
    """
    Opens and reads a CSV file, building a dictionary of accounts (by name) and total balances.
    If max_transaction_date is provided, then all transactions AFTER the provided date are excluded.

    :param csv_path: String value for filesystem location of CSV data file
    :param max_transaction_date: Specifies the max date value of transactions included in balance calulations

    :returns: str A JSON string containing the { account : balance } information
    :raises: FileNotFoundError, Exception, EmptyLedgerError
    """

    if not pathlib.Path(csv_path).is_file():
        raise FileNotFoundError("Invalid CSV file path provided.")

    if max_transaction_date:
        max_transaction_date = datetime.strptime(
            max_transaction_date, TRANSACTION_DATE_FORMAT)

    # If account name does not exist in dict at time of access, 
    # create it with a zero balance.
    account_balances = defaultdict(lambda: ZERO_BALANCE)

    with open(csv_path, 'r') as csvfile:
        ledger_reader = csv.DictReader(
            csvfile, fieldnames=['Date', 'Sender', 'Receiver', 'Amount']
        )

        for row in ledger_reader:

            try:
                # Apply validation to each row
                validate_csv_row(
                    row, check_transaction_date=bool(max_transaction_date)
                )
            except RowValidationError:
                # Future enhancement: Add logging, add counter for # of errors,
                # and collect error rows
                continue

            if max_transaction_date and \
                    datetime.strptime(row['Date'], TRANSACTION_DATE_FORMAT) > max_transaction_date:
                # Skip any transactions newer than the requested date
                continue

            # Ensure the amount in transaction log has 2 decimal places of specificity
            amount = Decimal(row['Amount']).quantize(TWO_DECIMAL_PLACES)

            # Debit the sender's balance
            account_balances[row['Sender']] -= abs(amount)
            # Credit the receiver's balance
            account_balances[row['Receiver']] += abs(amount)

    if not account_balances:
        raise EmptyLedgerError("No transactions in CSV file.")

    return json.dumps(account_balances, default=_decimal_encoder, indent=4)

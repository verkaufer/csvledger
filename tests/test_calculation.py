import csv
import json
from io import StringIO
from unittest import TestCase, mock

import csvledger


class TestCalculation(TestCase):

    def setUp(self):

        TEST_DATA = StringIO(
            "2016-12-10,john,mary,500.00\n"
            "2016-12-11,john,supermarket,50.00\n"
            "2016-12-11,mary,george,52.30\n"
            "2016-12-09,george,supermarket,23.16\n"
            "2016-12-16,john,insurance,93.53\n"
            ",john,insurance,90.00\n"
            "2016-12-24,mary,,45.45\n"
            "2016-12-24,,john,45.45\n"
            "2016-12-24,,,0.00\n"
        )

        # mock_open does not fully implement the CSV file reader spec.
        # monkey_patch the CSV reader spec instead
        # https://stackoverflow.com/a/24779923/2291333
        self.mocked_file_open = mock.mock_open(read_data=''.join(TEST_DATA))
        self.mocked_file_open.return_value.__iter__ = lambda self: self
        self.mocked_file_open.return_value.__next__ = lambda self: next(iter(self.readline, ''))

        self.pathlib_patcher = mock.patch("pathlib.Path.is_file", return_value=True).start()

    def tearDown(self):
        self.pathlib_patcher.stop()

    @mock.patch("pathlib.Path.is_file", return_value=False)
    def test_invalid_path(self, mocked_pathlib):
        """Assert an invalid path raises an exception"""
        with self.assertRaises(FileNotFoundError):
            csvledger.calculate_balances('')
        mocked_pathlib.assert_called_once()

    def test_calculation(self):
        """Assert calculate_balances returns correct balances given our test input"""
        expected_calculations = {
            "john": "-643.53",
            "mary": "447.70",
            "supermarket": "73.16",
            "george": "29.14",
            "insurance": "93.53"
        }

        with mock.patch('builtins.open', self.mocked_file_open):
            balances = csvledger.calculate_balances('valid_path')
            self.assertDictEqual(json.loads(balances), expected_calculations)

    def test_date_filter(self):
        """Assert method respects date string arg and filters out correct transactions"""
        expected_calculations = {
            "supermarket": "23.16",
            "george": "-23.16",
        }

        newest_transaction_date = "2016-12-09"

        with mock.patch('builtins.open', self.mocked_file_open):
            balances = csvledger.calculate_balances('valid_path', newest_transaction_date)
            self.assertDictEqual(json.loads(balances), expected_calculations)

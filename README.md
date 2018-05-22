# Csvledger

Calculates balances for accounts given a CSV file with the format:
```sh
YYYY-MM-DD,sender,receiver,100.00
```
The application follows a credit + debit accounting system for account balances. For example, if Sender gives $100.00 to Receiver, then Sender's account is debited -100.00 and Receiver's account is credited +100.00.

Created using only libraries found in Python3 stdlib.

### Usage Example:
**NOTE:** This application strictly requires Python 3.6+
```
$ python3 csvledger.py {~/path/to/your/csvfile.csv}
{
    "account1": 56.35,
    "account2": -56.35
}
```


# Setup
1. Clone the repository to your machine. 
2. Navigate to path of cloned repository
3. Run ``python3 csvledger.py {~/path/to/your/file.csv}``


# Usage
Given a path to a CSV file, the `csvledger.py` file will calculate balances and return a JSON representation of the accounts and balances:

If the application is called with a date string argument, the calculations are only performed on transactions that occur *on or before the date argument*:

```
# Returns account balances as of 2018-09-12
$ python3 csvledger.py {~/path/to/file.csv} 2018-09-12
```

# Tests

Inside the `csvledger` root directory, run:
```
$ python3 -m unittest tests.test_calculation
```
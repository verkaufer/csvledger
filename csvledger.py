import os
import sys
import csvledger

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        raise ValueError("Missing path for CSV data.")

    # Send output to direct to stdout
    try:
        date_arg = args[1]
    except IndexError:
        sys.stdout.write(csvledger.calculate_balances(args[0]))
    else:
        sys.stdout.write(csvledger.calculate_balances(args[0], date_arg))

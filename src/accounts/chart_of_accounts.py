# Factory for producing a chart of accounts using account and loan objects
import pandas as pd
from .account import Account
from .loan import SimpleLoan
from .er import ExpenseRevenueAccount
from .savings import SavingsAccount
from .checking import CheckingAccount


class AccountRegister:
    def __init__(self) -> None:
        self.r = {}
        self.num_loans = 0

    def register(self, acnt: Account):
        self.r[acnt.get_name()] = acnt

    def unregister(self, name: str):
        self.r.pop(name)


def get_chart_of_accounts(csvFilePath):
    register = AccountRegister()
    accounts = pd.read_csv(csvFilePath)

    for index, account in accounts.iterrows():
        if account['Type'] in ("EXPENSE", "REVENUE"):
            a = ExpenseRevenueAccount(
                account['Name'],
                _convert_dollar_str_to_float(account['AmountDue']),
                account['Type'],
                account['NextDate'],
                account['Timebase'].strip(),
                int(account['Frequency']),
                account['EndDate']
            )
            register.register(a)

        elif account['Type'] == "CASH":
            register.register(CheckingAccount(
                account['Name'], _convert_dollar_str_to_float(account['Balance'])))

        elif account['Type'] == "SAVINGS":
            register.register(
                SavingsAccount(
                    account['Name'], float(
                        account['Rate'])))

        elif account['Type'] == "SIMPLE LOAN":
            loan = SimpleLoan(
                account['Name'],
                _convert_dollar_str_to_float(account['AmountDue']),
                float(account['Rate']),
                _convert_dollar_str_to_float(account['Balance']),
                account['NextDate'],
                int(account['Frequency']),
                account['Timebase'].strip()
            )
            register.register(loan)
            register.num_loans += 1
        else:
            pass

    return register


def _convert_dollar_str_to_float(dollar_string):
    dollar_string = dollar_string.strip()
    dollar_string = dollar_string.strip('$')
    dollar_string = dollar_string.replace(',', '')
    return float(dollar_string)

from datetime import date
from transaction.transaction_states import TransactionState


class Account:
    def __init__(self, account_name: str) -> None:
        self.reset_balance()
        self.rename(account_name)

    def credit(self, amount: float) -> TransactionState:
        self._account_balance -= amount
        return TransactionState.TRANSACTION_ACCEPTED

    def debit(self, amount: float) -> TransactionState:
        self._account_balance += amount
        return TransactionState.TRANSACTION_ACCEPTED

    def accrue(self, day: date) -> None:
        pass

    def get_balance(self) -> float:
        return self._account_balance

    def get_name(self):
        return self._account_name

    def reset_balance(self):
        self._account_balance = 0.0

    def rename(self, name: str):
        self._account_name = name

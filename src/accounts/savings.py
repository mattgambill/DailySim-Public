from .constants import PERCENT_TO_DECIMAL
from .constants import DAYS_PER_YEAR
from .checking import CheckingAccount


class SavingsAccount(CheckingAccount):
    def __init__(self, name, rate) -> None:
        super().__init__(name, 0)
        self._rate = rate / (PERCENT_TO_DECIMAL * DAYS_PER_YEAR)

    def accrue(self, day):
        self.debit(self._rate * self.get_balance())

    def credit(self, amount: float):
        return super().credit(amount)

from datetime import datetime
from dateutil.relativedelta import relativedelta


from .account import Account
from transaction.transaction_states import TransactionState


class ExpenseRevenueAccount(Account):
    def __init__(
            self,
            name,
            amount,
            type: str,
            next_due_date: str,
            timebase: str,
            frequency: int,
            end_date: str) -> None:
        super().__init__(name)
        self.type = type
        self._set_time_increment(timebase, frequency)
        self._next_due_date = datetime.strptime(
            next_due_date, '%m/%d/%Y').date()
        self._end_date = datetime.strptime(end_date, '%m/%d/%Y').date()
        self._last_due_date = None
        self._amount = amount

    def accrue(self, day):
        if day < self._end_date:
            if day == self._next_due_date:
                super().debit(self._amount)
                self._last_due_date = self._next_due_date
                self._next_due_date = day + self._time_increment
        else:
            if super().get_balance() != 0:
                super().reset_balance()

    def account_type(self):
        return self.type

    def debit(self, amount: float) -> TransactionState:
        return super().credit(amount)

    def _set_time_increment(self, timebase: str, frequency: int):
        if timebase == "m":
            self._time_increment = relativedelta(months=frequency)
        elif timebase == "w":
            self._time_increment = relativedelta(weeks=frequency)

    def get_next_due_date(self):
        return self._next_due_date

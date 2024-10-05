from datetime import datetime
from dateutil.relativedelta import relativedelta

from .account import Account
from transaction.transaction_states import TransactionState
from .constants import PERCENT_TO_DECIMAL
from .constants import DAYS_PER_YEAR


class SimpleLoan(Account):
    def __init__(self,
                 name: str,
                 payment: float,
                 rate_in_percent: float,
                 principal: float,
                 first_payment_date: str,
                 payment_freq: int,
                 payment_timebase: str) -> None:

        super().__init__(name)
        super().debit(principal)

        next_due_date = datetime.strptime(
            first_payment_date, '%m/%d/%Y').date()
        self._next_due_date = next_due_date
        self._payment_timebase = payment_timebase
        self._payment_frequency = payment_freq
        self._payment = payment
        self._cumulative_interest = 0.0
        self._interest_due = 0

        self._rate = rate_in_percent / (PERCENT_TO_DECIMAL * DAYS_PER_YEAR)
        self._date = None
        self._amount_due = 0.0

    def accrue(self, day) -> None:

        self._accrue_interest_due()

        payment_is_due_today = (day >= self._next_due_date)
        if payment_is_due_today:
            self._update_amount_due()
            self._update_due_date()

    def debit(self, amount: float) -> TransactionState:
        # Handle edge cases.
        if self.is_loan_paid():
            return TransactionState.TRANSACTION_DECLINED

        payment_is_a_partial_payment = (amount < self._amount_due)
        if payment_is_a_partial_payment:
            self._handle_partial_payment(amount)
            return TransactionState.TRANSACTION_ACCEPTED

        # No Edge Cases. Apply Full Payment.
        self._apply_full_payment(amount)

        return TransactionState.TRANSACTION_ACCEPTED

    def credit(self) -> TransactionState:
        # Additions to account principle are not allowed.
        transaction_state = TransactionState.TRANSACTION_ACCEPTED

        if self.get_balance() < 0:
            super().reset_balance()
        else:
            transaction_state = TransactionState.TRANSACTION_DECLINED

        return transaction_state

    def get_cumulative_interest(self) -> float:
        return self._cumulative_interest

    def get_amt_due(self) -> float:
        return self._amount_due

    def get_name(self) -> str:
        return super().get_name()

    def get_payoff(self) -> float:
        return self.get_balance() + self._interest_due

    def is_loan_paid(self) -> bool:
        return self.get_payoff() <= 0

    def is_payment_due(self) -> bool:
        return self._amount_due > 0


# Private Functions


    def _accrue_interest_due(self) -> None:
        self._interest_due += self._rate * self.get_balance()

    def _calc_amortized_balance(self, payment: float) -> float:
        return self._interest_due - payment

    def _handle_partial_payment(self, payment: float) -> None:
        self._amount_due -= payment
        if self._interest_due > payment and self._interest_due > 0:
            self._cumulative_interest += payment
            self._interest_due -= payment
        else:
            super().debit(self._calc_amortized_balance(payment))
            self._cumulative_interest += self._interest_due
            self._interest_due = 0

    def _apply_full_payment(self, payment: float) -> None:
        super().debit(self._calc_amortized_balance(payment))
        self._cumulative_interest += self._interest_due
        self._interest_due = 0
        self._amount_due = 0

    def _update_due_date(self) -> None:
        if self._payment_timebase == "w":
            self._next_due_date += relativedelta(weeks=self._payment_frequency)
        else:
            self._next_due_date += relativedelta(months=1)

    def _update_amount_due(self) -> None:
        if self.get_payoff() <= self._payment:
            self._amount_due = self.get_payoff()
        else:
            self._amount_due = self._payment

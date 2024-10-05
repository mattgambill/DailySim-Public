from .account import Account
from transaction.transaction_states import TransactionState


class CheckingAccount(Account):
    def __init__(self, name, amount) -> None:
        super().__init__(name)
        super().debit(amount)

    def credit(self, amount: float):
        transaction_state = TransactionState.TRANSACTION_DECLINED
        if self._account_balance - amount > 0:
            super().credit(amount)
            transaction_state = TransactionState.TRANSACTION_ACCEPTED
        else:
            transaction_state = TransactionState.TRANSACTION_DECLINED
        return transaction_state

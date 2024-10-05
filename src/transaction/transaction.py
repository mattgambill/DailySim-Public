from .transaction_states import TransactionState

from accounts.account import Account


def do_transaction(money_from: Account, money_to: Account, amount: float):
    ts = money_from.credit(amount=amount)
    if ts == TransactionState.TRANSACTION_DECLINED:
        return (TransactionState.TRANSACTION_DECLINED, 1)
    ts = money_to.debit(amount=amount)
    if ts == TransactionState.TRANSACTION_DECLINED:
        return (TransactionState.TRANSACTION_DECLINED, 2)
    return (TransactionState.TRANSACTION_ACCEPTED, 0)

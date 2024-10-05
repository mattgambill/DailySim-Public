from datetime import date
from .checking import CheckingAccount
from transaction.transaction_states import TransactionState


class DAsset(CheckingAccount):
    def __init__(self, name, purchase_price, sell_price, time_years):
        super().__init__(name, purchase_price)
        self._sell_price = sell_price
        self._depreciation_rate = (
            sell_price - purchase_price) / float(time_years)

    def accrue(self, day: date) -> None:
        if self.get_balance() > self._sell_price:
            self.debit(self._depreciation_rate)

    def reset(self, purchase_price, sell_price, time_years):
        self.__init__(self.get_name(), purchase_price, sell_price, time_years)

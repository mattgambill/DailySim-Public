from datetime import datetime as dt

import pandas as pd

from accounts.chart_of_accounts import get_chart_of_accounts
from accounts.er import ExpenseRevenueAccount
from accounts.loan import SimpleLoan
from transaction.transaction_states import TransactionState
from transaction.transaction import do_transaction
from util.daterange import get_date_range


class DailySim:
    def __init__(
            self,
            accountCSVPath: str,
            sdate: str,
            edate: str,
            fast_payoff=False,
            max_chgf=7500.0
    ) -> None:
        self.ca = get_chart_of_accounts(accountCSVPath)
        self.sdate = sdate
        self.edate = edate
        self.sim_results = []
        self._scheduled_payments = []
        self._scheduled_expenses = []
        self._fast_payoff = fast_payoff
        self._piano_sold = False
        self._max_chgf = max_chgf

    def simulate(self) -> None:
        simulation_dates = get_date_range(self.sdate, self.edate)
        for day in simulation_dates:
            row = []
            self.accrue_accounts(day)
            for acnt in self.ca.r.values():
                row.append(round(acnt.get_balance(), 2))
            income = self.get_income(day)
            expense = self.get_expense(day)

            self.do_transfers(day)
            row.insert(0, round(income, 2))
            row.insert(1, round(expense, 2))
            self.sim_results.append(row)

        header = ['Income', 'Expense']
        header.extend(list(self.ca.r.keys()))
        self.sim_results = pd.DataFrame(
            data=self.sim_results, columns=header, index=simulation_dates)

    def accrue_accounts(self, day) -> None:
        for acnt in self.ca.r.values():
            acnt.accrue(day)

    def schedule_payment(
            self,
            accnt_from: str,
            accnt_to: str,
            amt: float,
            day: str) -> None:
        self._scheduled_payments.append({'date': dt.strptime(
            day, "%m/%d/%Y").date(), 'accnt_from': accnt_from, 'accnt_to': accnt_to, 'amt': amt})

    def schedule_expense(self, amt: float, day: str) -> None:
        self._scheduled_expenses.append(
            {'date': dt.strptime(day, "%m/%d/%Y").date(), 'amt': amt})

    def execute_scheduled_payments(self, day) -> float:
        sum_amt = 0
        for _, pmt in enumerate(self._scheduled_payments):
            if day == pmt['date']:
                do_transaction(self.ca.r[pmt['accnt_from']],
                               self.ca.r[pmt['accnt_to']], pmt['amt'])

                sum_amt += pmt['amt']
        return sum_amt

    def execute_scheduled_expenses(self, day) -> float:
        sum_amt = 0
        for pmt_no, pmt in enumerate(self._scheduled_expenses):
            if day == pmt['date']:
                state = self.ca.r['CHGF'].credit(pmt['amt'])
                if state == TransactionState.TRANSACTION_DECLINED:
                    fgif_bal = self.ca.r['FGIF'].get_balance()
                    chgf_bal = self.ca.r['CHGF'].get_balance()
                    if pmt['amt'] > (fgif_bal + chgf_bal):
                        msg = "Can't Make Scheduled Expense in the amount of: " + str(pmt['amt']) + ' on ' + str(day) 
                        raise ValueError(msg)
                    if pmt['amt'] > fgif_bal:
                        fgif_pmt = pmt['amt'] - fgif_bal
                        self.ca.r['FGIF'].reset_balance()
                        self.ca.r['CHGF'].credit(fgif_pmt)
                    else:
                        self.ca.r['FGIF'].credit(pmt['amt'])

                self._scheduled_expenses.pop(pmt_no)
                sum_amt += pmt['amt']
        return sum_amt

    def get_open_loan_accounts(self) -> list:
        open_loans = []
        for loan in self.get_loan_accounts():
            if not loan.is_loan_paid():
                open_loans.append(loan)
        return open_loans

    def get_loan_accounts(self) -> list:
        loans = []
        for key in self.ca.r.keys():
            if isinstance(self.ca.r[key], SimpleLoan):
                loans.append(self.ca.r[key])
        return loans

    def get_cum_int(self) -> float:
        cum_int = 0
        for loan in self.get_loan_accounts():
            cum_int += loan.get_cumulative_interest()
        return cum_int

    def get_expense(self, day) -> float:
        expense = 0.0

        for expense_account in self._get_er_accounts('EXPENSE'):
            if expense_account.get_balance() > 0:
                expense += expense_account.get_balance()
                ts, error_no = do_transaction(
                    self.ca.r["CHGF"], expense_account, expense_account.get_balance())
                if ts == TransactionState.TRANSACTION_DECLINED:
                    if self.ca.r["FGIF"].get_balance() >= expense_account.get_balance():
                       do_transaction(
                        self.ca.r["FGIF"], expense_account, expense_account.get_balance()) 
                    else:
                        raise ValueError("Transaction Error! " +
                                     expense_account.get_name() +
                                     ' ' +
                                     str(day) +
                                     ' ' +
                                     str(self.ca.r["CHGF"].get_balance()) +
                                     ' ' +
                                     str(error_no), ' ' +
                                     str(expense_account.get_balance()))

        oneshot = False

        for loan in self.get_open_loan_accounts():
            if self._fast_payoff\
                    and (loan.get_payoff() < (self.ca.r['FGIF'].get_balance()))\
                    and (loan.get_payoff() > 0)\
                    and not oneshot:
                do_transaction(self.ca.r['FGIF'], loan, loan.get_payoff())
            oneshot = True

            if loan.get_amt_due() > 0:
                expense += loan.get_amt_due()
                ts,error_no = do_transaction(self.ca.r["CHGF"], loan, loan.get_amt_due())
                if ts == TransactionState.TRANSACTION_DECLINED:
                    raise ValueError("Transaction Error! " +
                                     loan.get_name() +
                                     ' ' +
                                     str(day) +
                                     ' ' +
                                     str(self.ca.r["CHGF"].get_balance()) +
                                     ' ' +
                                     str(error_no), ' ' +
                                     str(loan.get_balance()))

        expense += self.execute_scheduled_payments(day)
        expense += self.execute_scheduled_expenses(day)

        return expense

    def do_transfers(self, day) -> None:
        chgf_balance = self.ca.r["CHGF"].get_balance()
        chgf_min = 1000
        if chgf_balance > self._max_chgf:
            do_transaction(
                self.ca.r["CHGF"],
                self.ca.r["FGIF"],
                chgf_balance - self._max_chgf)
        elif chgf_balance < chgf_min:
            amount_required = chgf_min - chgf_balance
            if self.ca.r["FGIF"].get_balance() >= amount_required:
                do_transaction(
                    self.ca.r["FGIF"],
                    self.ca.r["CHGF"],
                    amount_required)
            else:
                do_transaction(
                    self.ca.r["FGIF"],
                    self.ca.r["CHGF"],
                    self.ca.r["FGIF"].get_balance())

    def get_income(self, day) -> float:
        income = 0.0
        if (day.month == 4) and (day.day == 1) and (day.year > 2026):
            self.ca.r['CA_EMPLOYER']._amount *= 1.05
        for revenue_account in self._get_er_accounts('REVENUE'):
            if revenue_account.get_balance() > 0:
                income += revenue_account.get_balance()
                do_transaction(
                    revenue_account,
                    self.ca.r["CHGF"],
                    revenue_account.get_balance())
        return income

    def _get_er_accounts(self, account_type: str) -> ExpenseRevenueAccount:
        rev_accounts = []
        for key in self.ca.r.keys():
            if isinstance(self.ca.r[key], ExpenseRevenueAccount):
                if self.ca.r[key].account_type() == account_type:
                    rev_accounts.append(self.ca.r[key])
        return rev_accounts

import argparse
from dailysim import DailySim
from util.config import get_config
from postprocess import post_process


class SimApp():
    def __init__(self):
        self.args = self.get_args()
        self.sim = self.get_sim(self.args)

    def main(self):
        self.sim.simulate()
        post_process(self.args, self.sim)

    def get_args(self):
        parser = argparse.ArgumentParser(description='DailySim')
        parser.add_argument('configPath', help='Config yaml path.')
        parser.add_argument(
            '--save-results',
            help='Save output results.',
            action='store_true')
        return parser.parse_args()

    def get_sim(self, args):
        config = get_config(args.configPath)
        ds = DailySim(
            config['accounts'],
            config['start_date'],
            config['end_date'],
            fast_payoff=config['fast_payoff_enabled'],
            max_chgf=config['max_checking_balance']
        )
        if 'payments' in list(config.keys()):
            payments = config['payments']
            for paymentk in list(payments.keys()):
                payment = payments[paymentk]
                ds.schedule_payment(
                    payment['from'],
                    payment['to'],
                    payment['amount'],
                    payment['date']
                )
        if 'purchases' in list(config.keys()):
            purchases = config['purchases']
            for purchasek in list(purchases.keys()):
                purchase = purchases[purchasek]
                ds.schedule_expense(
                    purchase['amount'],
                    purchase['date']
                )
        return ds

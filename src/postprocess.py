from matplotlib import pyplot as plt
import os

from dailysim import DailySim
from util.money import format_currency


def post_process(args, ds: DailySim):
    save_results(args, ds)
    print_summary(ds)
    plot_results(args, ds)


def print_summary(ds: DailySim):
    print('Cumulative Interest: ' + format_currency(ds.get_cum_int()))
    print(
        'FGIF Final Balance: ' +
        format_currency(
            ds.ca.r['FGIF'].get_balance()))


def save_results(args, ds: DailySim):
    # Save CSV Results
    if args.save_results:
        if not os.path.exists('./results'):
            os.mkdir('./results')
        ds.sim_results.to_csv('./results/results.csv')


def plot_results(args, ds: DailySim):
    accounts = ds.sim_results.iloc[:, -ds.ca.num_loans:]

    chgf = ds.sim_results['CHGF']

    fgif = ds.sim_results['FGIF']

    plt.figure(figsize=[10, 8])

    plt.title('CHGF Balance Over Time')
    plt.plot(chgf.index.to_numpy(), chgf.to_numpy(), label='CHGF BALANCE')
    plt.legend()
    ax = plt.gca()
    ax.yaxis.set_major_formatter('${x:1.0f}')
    if args.save_results:
        plt.savefig('./results/chgf_v_time.png', format='png')

    plt.figure(figsize=[10, 8])
    plt.subplot(2, 1, 1)
    plt.title('Loan Balances Over Time')
    plt.plot(accounts.index.to_numpy(), accounts.to_numpy())
    plt.legend(accounts.columns.values.tolist())
    ax = plt.gca()
    ax.yaxis.set_major_formatter('${x:1.0f}')
    plt.subplot(2, 1, 2)
    plt.title('Gen. Invst. Fund Balance')
    plt.plot(
        fgif.index.to_numpy(),
        fgif.to_numpy(),
        label='GIF BAL',
        color='g')
    ax = plt.gca()
    ax.yaxis.set_major_formatter('${x:1.0f}')
    plt.legend()

    if args.save_results:
        plt.savefig('./results/loans_and_gif_v_time.png', format='png')

    plt.show()

import matplotlib.pyplot as plt
import numpy as np
import statistics
import requests
import time
import json

base_currency = 'PLN'
url = 'https://api.bitbay.net/rest/trading/transactions/'
time_interval = 3

w_volume = 2
w_mean = 2
w_rsi = 2


def get_data1(url, curr, base, end=None):
    try:
        req = requests.get(url + curr + '-' + base + end)
        req.raise_for_status()
        return req.json()

    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def calculate_rsi(data, w):
    data = data[-w:]
    rise = 0
    r_count = 0
    loss = 0
    l_count = 0
    for i in range(1, len(data)):
        if data[i - 1] < data[i]:
            rise += data[i] - data[i - 1]
            r_count += 1
        elif data[i - 1] > data[i]:
            loss += data[i - 1] - data[i]
            l_count += 1
    if r_count == 0:
        a = 1
    else:
        a = rise / r_count
    if l_count == 0:
        b = 1
    else:
        b = loss / l_count
    rsi_value = 100 - (100 / (1 + (a / b)))

    return rsi_value


def calculate_volume(data, w):
    sum_amount = 0
    for i in range(1, w + 1):
        sum_amount += data[-i]
    return sum_amount


def calculate_mean(data, w):
    sum_price = 0
    for j in range(1, w + 1):
        sum_price += data[-j]
    return sum_price / w


def user_info():
    curr = input('Waluta: ')
    ask = input('Kurs: ')
    vol = input('Ilość: ')

    return curr, int(ask), int(vol)


def read_json(file):
    f = open(file)
    data = json.load(f)
    price_ = data['price']
    volume_ = data['volume']
    amount_ = data['amount']
    mean_ = data['mean']
    rsi_ = data['rsi']
    buy_rate_ = data['buy_rate']
    buy_volume_ = data['buy_volume']
    sell_rate_ = data['sell_rate']
    sell_volume_ = data['sell_volume']
    balances_ = data['balances']
    times_ = data['times']
    t_ = data['t']
    labels_ = data['labels']

    return price_, volume_, amount_, mean_, rsi_, buy_rate_, buy_volume_, sell_rate_, sell_volume_, balances_, times_, t_, labels_


def save_data():
    data = {'price': price,
            'volume': volume,
            'amount': amount,
            'mean': mean,
            'rsi': rsi,
            'buy_rate': buy_rate,
            'buy_volume': buy_volume,
            'sell_rate': sell_rate,
            'sell_volume': sell_volume,
            'balances': balances,
            'times': times,
            't': t,
            'labels': labels}

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)


def create_plot(currency_list):
    figure, axis = plt.subplots(n, 1, figsize=(7, 9))
    figure.text(0.5, 0.04, 'time', ha='center', va='center')
    figure.tight_layout(pad=4.0, rect=[0, 0, .8, 1])

    line = []
    for i in range(len(currency_list)):
        line.append(axis[i].plot(times, price[currency_list[i]], label="price")[0])
        line.append(axis[i].plot(times, volume[currency_list[i]], label="volume")[0])
        line.append(axis[i].plot(times, mean[currency_list[i]], label="mean")[0])
        line.append(axis[i].plot(times, rsi[currency_list[i]], label="rsi")[0])
        line.append(axis[i].plot(times, buy_rate[currency_list[i]], '--', label="buy mean")[0])

        axis[i].legend(bbox_to_anchor=(1.33, -0.04), loc='lower right')

        axis[i].set_title(f'{currency_list[i] + base_currency}')

    return figure, axis, line


if __name__ == '__main__':
    currencies = ['DASH', 'OMG', 'BTC']
    n = len(currencies)

    price = {}
    volume = {}
    amount = {}
    mean = {}
    rsi = {}
    buy_rate = {}
    buy_volume = {}
    sell_rate = {}
    sell_volume = {}
    balances = {}

    for currency in currencies:
        price[currency] = []
        volume[currency] = []
        amount[currency] = []
        mean[currency] = []
        rsi[currency] = []
        buy_rate[currency] = []
        buy_volume[currency] = []
        sell_rate[currency] = []
        sell_volume[currency] = []
        balances[currency] = 0

    times = []
    t = 0
    labels = []

    plt.ion()
    fig, ax, lines = create_plot(currencies)

    # price, volume, amount, mean, rsi, buy_rate, buy_volume, sell_rate, sell_volume, balances, times, t, labels = read_json('data.json')
    # print(price, volume, amount, mean, rsi, buy_rate, buy_volume, sell_rate, sell_volume, balances, times, t, labels)

    while True:
        for i in range(50):
            # times.append(t)
            # t += 1
            # labels.append(time.strftime("%H:%M:%S", time.localtime()))

            if t % 5 == 0:
                czy = ''
                data_write = input('Czy chcesz zapisać dane do pliku?')
                if data_write == 't':
                    save_data()

                while czy != 'n':
                    czy = input('Czy chcesz dodać tranzakcję?[t/n]: ')
                    if czy == 't':
                        czy2 = input('Kupno czy sprzedaż?[k/s]: ')
                        if czy2 == 'k':
                            curre, asks, volu = user_info()
                            buy_rate[curre].append(asks)
                            buy_volume[curre].append(volu)

                        elif czy2 == 's':
                            curre, asks, volu = user_info()

                            available_volume = 0
                            for voulm in buy_volume[curre]:
                                available_volume += voulm

                            if volu > available_volume:
                                print('Nie masz wystarczająco dużo waluty!')

                            else:
                                balance = 0
                                temp_volume = volu
                                while temp_volume > 0:

                                    if buy_volume[curre][0] < temp_volume:
                                        temp_volume -= buy_volume[curre][0]

                                        balance += buy_volume[curre][0] * buy_rate[curre][0]

                                        del buy_volume[curre][0]
                                        del buy_rate[curre][0]

                                    else:
                                        buy_volume[curre][0] -= temp_volume

                                        balance += temp_volume * buy_rate[curre][0]

                                        if buy_volume[curre][0] == 0:
                                            del buy_volume[curre][0]
                                            del buy_rate[curre][0]

                                        sell_rate[curre].append(asks)
                                        sell_volume[curre].append(volu)
                                        break

                                final_balance = sell_rate[curre][-1] * sell_volume[curre][-1] - balance
                                balances[curre] = final_balance

            times.append(t)
            t += 1
            labels.append(time.strftime("%H:%M:%S", time.localtime()))

            for currency in currencies:
                r3 = get_data1(url, currency, base_currency, '?limit=100')['items'][i]
                price[currency].append(float(r3['r']))
                amount[currency].append(float(r3['a']))

                if len(price[currency]) >= w_volume:
                    volume[currency].append(calculate_volume(amount[currency], w_volume))

                if len(price[currency]) >= w_mean:
                    mean[currency].append(calculate_mean(price[currency], w_mean))

                if len(price[currency]) >= w_rsi:
                    rsi[currency].append(calculate_rsi(price[currency], w_rsi))

            p = 0
            for j in range(n):
                lines[0 + p].set_data(times, price[currencies[j]])
                lines[1 + p].set_data(times[w_volume - 1:], volume[currencies[j]])
                lines[2 + p].set_data(times[w_mean - 1:], mean[currencies[j]])
                lines[3 + p].set_data(times[w_rsi - 1:], rsi[currencies[j]])
                lines[4 + p].set_data(times, [statistics.mean(buy_rate[currencies[j]]) if len(buy_rate[currencies[j]]) > 0 else 0 for i in range(len(times))])
                p += 5

                minim = min(price[currencies[j]] +
                            volume[currencies[j]] +
                            mean[currencies[j]] +
                            rsi[currencies[j]]) * 0.01
                maxim = max(price[currencies[j]] +
                            volume[currencies[j]] +
                            mean[currencies[j]] +
                            rsi[currencies[j]]) * 1.3

                ax[j].set_ylim(minim, maxim)
                ax[j].set_xlim(0, max(times) + 5)
                ax[j].set_xticks(times)
                ax[j].set_xticklabels(labels, fontdict={'fontsize': 8}, rotation=45)
                if j == 0:
                    ax[j].yaxis.set_ticks(np.arange(0, maxim, 150))
                if j == 1:
                    ax[j].yaxis.set_ticks(np.arange(0, maxim, 25))
                if j == 2:
                    ax[j].yaxis.set_ticks(np.arange(0, maxim, 25000))

                ax[j].text(1.03, .85, '                                       ', fontsize=10, transform=ax[j].transAxes,
                           bbox=dict(facecolor='white', edgecolor="none", alpha=1))

                if balances[currencies[j]] < 0:
                    ax[j].text(1.03, .85, f'strata: {abs(balances[currencies[j]])}', fontsize=10, transform=ax[j].transAxes)
                elif balances[currencies[j]] > 0:
                    ax[j].text(1.03, .85, f'zysk: {abs(balances[currencies[j]])}', fontsize=10, transform=ax[j].transAxes)

            fig.canvas.draw()
            fig.canvas.flush_events()

            time.sleep(time_interval)

from typing import List, Tuple, Dict
from collections import defaultdict, OrderedDict
from dateutil.parser import parse as dateparser
import math
import datetime
import sys
import csv

def get_mean_of_stocks(stocks: List[float]) -> float:
    return sum(stocks)/len(stocks)

def get_sd_of_stocks(stocks: List[float]) -> float:
    mean = get_mean_of_stocks(stocks)

    deviations = list(map(lambda x: pow(x-mean, 2), stocks))
    variance = sum(deviations)/len(stocks)

    return math.sqrt(variance)

def find_buy_sell_price_index(stock_prices: List[float]) -> Tuple[int, int]:
    if len(stock_prices) == 0:
        raise 'Cannot compute buy sell over non existant prices!'

    min_i = -1
    max_i = -1

    def diff(buyd: int, selld: int) -> float:
        if buyd < 0 or selld < 0:
            return -1.0
        return stock_prices[selld] - stock_prices[buyd]

    mini = 0
    maxi = 0

    def update_actual_max_min(mini: float,
                              maxi: float,
                              min_i:float,
                              max_i:float) -> (float, float):
        if maxi != mini:
            if diff(min_i, max_i) < diff(mini, maxi):
                return (mini, maxi)
        return (min_i, max_i)

    for i, x in enumerate(stock_prices):
        if stock_prices[maxi] < x:
            maxi = i
        if stock_prices[mini] > x:
            min_i, max_i = update_actual_max_min(mini, maxi, min_i, max_i)
            mini = i
            maxi = i
    min_i, max_i = update_actual_max_min(mini, maxi, min_i, max_i)

    if min_i == -1:
        return (0, 0)
    return (min_i, max_i)

def find_profit_for_buy_sell(buyp: float, sellp: float, stock_units: int) -> float:
    return (sellp - buyp)*stock_units

def build_stock_dict(csv_filename: str) -> Dict[str, Dict[datetime.datetime, float]]:
    stocks = defaultdict(OrderedDict)
    with open(csv_filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                try:
                    stocks[row[0]][dateparser(row[1])] = float(row[2])
                except ValueError:
                    print('Invalid data found in csv file. Exiting...')
                    sys.exit(1)
                line_count += 1
    for stock in stocks:
        stocks[stock] = OrderedDict(sorted(stocks[stock].items(), key=lambda x: x[0]))
    return stocks

def take_action(stocks: Dict[str, Dict[datetime.datetime, float]],
                stock_name: str,
                start_date: datetime.datetime,
                end_date: datetime.datetime
                ) -> Tuple[float, float, datetime.datetime, datetime.datetime, float]:
    if stock_name not in stocks:
        raise 'Stock name not in DS error!'
    contextual_stocks = stocks[stock_name]

    # Stock list generation. We should be fine using this kinda logic up until
    # something around 10 mil userbase in terms of memory.
    stock_list = []
    last_date = start_date
    for date in contextual_stocks:
        if date <= start_date:
            last_date = date
        else:
            break
    last_price = contextual_stocks[last_date]
    delta = datetime.timedelta(days=1)
    date = start_date
    dates = set(contextual_stocks.keys())
    while date <= end_date:
        if date in dates:
            stock_list.append(contextual_stocks[date])
            last_price = stock_list[-1]
        else:
            stock_list.append(last_price)
        date = date + delta

    mean = get_mean_of_stocks(stock_list)
    sd = get_sd_of_stocks(stock_list)
    buydelta, selldelta = find_buy_sell_price_index(stock_list)
    buyd = start_date + datetime.timedelta(days=buydelta)
    selld = start_date + datetime.timedelta(days=selldelta)
    profit = find_profit_for_buy_sell(stock_list[buydelta], stock_list[selldelta], 100)

    return (mean, sd, buyd, selld, profit)

def editdistance(s1: str, i1: int, s2: str, i2: int, mem: Dict[Tuple[int,int], int]) -> int:
    if i1 == len(s1):
        return len(s2) - i2
    if i2 == len(s2):
        return len(s1) - i1
    if (i1, i2) in mem:
        return mem[(i1, i2)]

    if s1[i1] == s2[i2]:
        mem[(i1, i2)] = editdistance(s1, i1+1, s2, i2+1, mem)
    else:
        mem[(i1, i2)] = 1 + min(editdistance(s1, i1, s2, i2+1, mem), editdistance(s1, i1+1, s2, i2, mem))
    return mem[(i1, i2)]

def match_stock(stock_name: str,
                stocks: Dict[str, Dict[datetime.datetime, float]]) -> (str, bool):
    min_dis = len(stock_name)*100
    min_dis_stock_name = stock_name
    for stock in stocks:
        mem = defaultdict(int)
        dis = editdistance(stock, 0, stock_name, 0, mem)
        if dis < min_dis:
            min_dis = dis
            min_dis_stock_name = stock
    if min_dis_stock_name == stock_name:
        return (min_dis_stock_name, 1)
    return (min_dis_stock_name, 0)

def main():
    csv_filename = sys.argv[1]

    print('Loading...')
    stocks = build_stock_dict(csv_filename)
    print('Loaded!!!')

    while True:
        print('Which stock you need to process?')
        stock_name = input()

        possible_stock_name, found = match_stock(stock_name, stocks)
        if not found:
            print('Oops Did you mean %s? Press y or n' % (possible_stock_name))
            val = input()
            if val.lower() in ('y', 'yes'):
                stock_name = possible_stock_name
            else:
                continue

        print('From which date you want to start')
        start_date = dateparser(input())
        print('Till which date you want to analyze')
        end_date = dateparser(input())

        if end_date <= start_date or (end_date - start_date) > datetime.timedelta(days=90):
            print('Invalid date range! Please make sure start date is before end date with maximum range of 90 days.')
            continue

        if start_date < list(stocks[stock_name].keys())[0]:
            print("Stock didn't start trading until %s Please enter a valid start date.", (stocks[stock_name].keys()[0]))
            continue

        mean, sd, buyd, selld, profit = take_action(stocks, stock_name, start_date, end_date)
        print("-----------Here is you result------------------")
        print("Mean: %f, Std: %f, Buy date: %s, Sell Date: %s, Profit: %f" % (
            mean, sd, buyd.strftime('%d %b %Y'), selld.strftime('%d %b %Y'), profit
        ))
        print("-----------------------------------------------")
        print('Do you want to continue? (y or n)')
        should_exit = input()
        if should_exit.lower() not in ('y', 'yes'):
            print('Quiting....')
            break

if __name__ == "__main__":
    main()

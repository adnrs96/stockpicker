from typing import List, Tuple
from collections import defaultdict, OrderedDict
from dateutil.parser import parse as dateparser
import math
import datetime

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

    def update_actual_max_min(mini: int, maxi: int) -> None:
        if maxi != mini:
            if diff(min_i, max_i) < diff(mini, maxi):
                min_i = mini
                max_i = maxi

    for i, x in enumeration(stock_prices):
        if stock_prices[maxi] < x:
            maxi = i
        if stock_prices[mini] > x:
            update_actual_max_min(mini, maxi)
            mini = i
            maxi = i
    update_actual_max_min(mini, maxi)

    if min_i == -1:
        return (0, 0)
    return (min_i, max_i)

def find_profit_for_buy_sell(buyp: float, sellp: float, stock_units: int) -> float:
    return (sellp - buyp)*stock_units

def build_stock_dict(csv_filename: str) -> Dict[str: Dict[datetime.datetime, float]]:
    stocks = defaultdict(OrderedDict())
    with open(csv_filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                stocks[row[0]][dateparser(row[1])] = row[2]
                line_count += 1
    return stocks

def take_action(stocks: Dict[str: Dict[datetime.datetime, float]],
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
    delta = date + datetime.timedelta(days=1)
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

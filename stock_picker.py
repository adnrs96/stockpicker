from typing import List
import math

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

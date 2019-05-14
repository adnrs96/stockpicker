from typing import List, Tuple
from stock_picker import find_buy_sell_price_index

def test_find_buy_sell_price(stocks: List[float], eres: Tuple[int, int]) -> None:
    res = find_buy_sell_price_index(stocks)
    assert res == eres

def run_tests_find_buy_sell_price_index():
    stocks = [89.5462076445604, 18.667677160930054, 61.056835835764296, 71.25611795600992, 40.865290270112354, 49.060244300752416, 17.537156592839423, 51.078354026293006, 84.91978690267001, 92.78118376779014, 13.69601856126346, 16.637425080748546, 24.644581693445915, 45.906824353853644, 11.11344858471691]
    ans = (6, 9)
    test_find_buy_sell_price(stocks, ans)

    stocks = [397.1978053680469, 747.9404007734663, 620.7899549747495, 619.3607014077894, 373.6124211093437, 739.9528223013061, 928.3043798854002, 293.9435252917064, 657.2325446646397, 465.1502889205764]
    ans = (4, 6)
    test_find_buy_sell_price(stocks, ans)

def main():
    run_tests_find_buy_sell_price_index()

if __name__ == "__main__":
    main()

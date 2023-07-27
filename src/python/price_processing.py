import python.test_prices as test_prices
import copy

def get_texts():

    prices = copy.deepcopy(test_prices.prices)
    price_number = len(prices)

    displayable_texts = []

    for i in prices:
        tags = "#" * i
        displayable_texts.append(f"{i}snt {tags}")
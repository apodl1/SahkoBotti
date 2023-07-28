import test_prices
import tokens

import copy
import requests

def get_prices():
    get_url = f"https://web-api.tp.entsoe.eu/api?securityToken={tokens.entsoe_token}\
        documentType=A44&in_Domain=10YFI-1--------U&out_Domain=10YFI-1--------U&periodStart=202301010000&periodEnd=202312310000"
    response_text = requests.get(get_url).text
    return response_text

def get_texts():

    prices = copy.deepcopy(get_prices())
    price_number = len(prices)

    displayable_text = ""

    for i in prices:
        tags = "#" * i
        displayable_text += f"{i}snt    {tags}\n"

    return displayable_text

print(get_prices())
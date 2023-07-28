import tokens

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def get_prices():
    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y%m%d%H%M')
    print(formatted_time)
    get_url = f"https://web-api.tp.entsoe.eu/api?securityToken={tokens.entsoe_token}&documentType=A44&in_Domain=10YFI-1--------U&out_Domain=10YFI-1--------U&periodStart=202307282200&periodEnd=202312310000"
    response_text = requests.get(get_url).text
    print(response_text)
    return response_text

def get_texts():

    try:
        root = ET.fromstring(get_prices())
    except ET.ParseError as e:
        print("XML Parsing Error:", e)

    displayable_text = ""

    for day in root.findall('{*}TimeSeries'):
        for point in day.find("{*}Period").findall('{*}Point'):
            hour = int(point.find('{*}position').text)
            price = float(point.find('{*}price.amount').text)
            price_snt_kwh = price / 10
            price_snt_kwh_formatted = format(price_snt_kwh, '.2f')
            tags = "#" * int(price_snt_kwh)
            displayable_text += f"{hour}: {price_snt_kwh_formatted}snt    {tags}\n"

    return displayable_text

print(get_texts())
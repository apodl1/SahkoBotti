import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, time, timezone

prices = ""

def get_prices():
    current_UTC = datetime.now(timezone.utc).replace(tzinfo=None)
    previous_UTC = datetime.combine(current_UTC, time.min) - timedelta(days=1)
    previous_UTC_formatted = previous_UTC.strftime("%Y%m%d%H%M")

    with open('entsoe_token.txt', 'r') as file:
        entsoe_token = file.read().rstrip()

    get_url = f"https://web-api.tp.entsoe.eu/api?securityToken={entsoe_token}&documentType=A44&in_Domain=10YFI-1--------U&out_Domain=10YFI-1--------U&periodStart={previous_UTC_formatted}&periodEnd=202312310000"
    try:
        print("Request sent")
        response_text = requests.get(get_url).text
    except requests.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return None
    
    print("Answer received")

    global prices
    prices_updated_flag = (response_text == prices)
    prices = response_text


    return prices_updated_flag



def construct_texts():

    current_UTC = datetime.now(timezone.utc).replace(tzinfo=None)
    current_HEL = datetime.now()
    timezone_difference_h = (current_HEL - current_UTC).seconds / 3600
    current_HEL_hour = current_HEL.strftime("%H")

    try:
        root = ET.fromstring(prices)
    except ET.ParseError as e:
        print("XML Parsing Error:", e)

    displayable_text = ""

    start_hour = 23
    prices_printed = 0
    prices_to_print = 20

    for day in root.findall('{*}TimeSeries'):
        end_date = day.find("{*}Period").find("{*}timeInterval").find("{*}end").text[:10]
        now_date = current_HEL.strftime("%Y-%m-%d")[:10]
        if now_date <= end_date:
            for point in day.find("{*}Period").findall('{*}Point'):
                if prices_printed >= prices_to_print:
                    break
                index_of_point = int(point.find('{*}position').text)
                hour_abs = (start_hour + index_of_point - 1)
                HEL_hour_abs = int(hour_abs + timezone_difference_h)
                HEL_hour_real = HEL_hour_abs % 24
                if now_date < end_date or HEL_hour_real >= int(current_HEL_hour) or HEL_hour_abs == 48: #a bit of a band-aid :D
                    price = float(point.find('{*}price.amount').text)
                    price_snt_kwh = price / 10
                    price_snt_kwh_formatted = format(price_snt_kwh, '.2f')
                    tags = "#" * round(price_snt_kwh * 2)
                    hours_to_price = (prices_printed)
                    displayable_text += f"{HEL_hour_real:0{2}d} [{hours_to_price:0{2}d}]:   {price_snt_kwh_formatted}snt    {tags}\n"
                    prices_printed += 1

    return displayable_text
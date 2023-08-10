import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, time, timezone

prices = ""

def get_prices():
    current_UTC = datetime.now(timezone.utc).replace(tzinfo=None)
    previous_UTC = datetime.combine(current_UTC, time.min) - timedelta(days=1)
    previous_UTC_formatted = previous_UTC.strftime("%Y%m%d%H%M")

    with open('../../entsoe_token.txt', 'r') as file:
        entsoe_token = file.read()

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

    previous_day = True
    later_than_now = False
    time_diff_in_data_h = 3
    prices_printed = 0
    prices_to_print = 30

    for day in root.findall('{*}TimeSeries'):
        for point in day.find("{*}Period").findall('{*}Point'):
            hour = int(point.find('{*}position').text)
            if prices_printed >= prices_to_print:
                break
            if (not previous_day) or hour == 24:
                previous_day = False
                if hour == 24:
                    HEL_hour = 0
                else:
                    HEL_hour = int(hour + time_diff_in_data_h - timezone_difference_h)
                if HEL_hour >= int(current_HEL_hour):
                    later_than_now = True
                if later_than_now:
                    price = float(point.find('{*}price.amount').text)
                    price_snt_kwh = price / 10
                    price_snt_kwh_formatted = format(price_snt_kwh, '.2f')
                    tags = "#" * round(price_snt_kwh * 2)
                    hours_to_hour = (prices_printed)
                    displayable_text += f"{HEL_hour:0{2}d} [{hours_to_hour:0{2}d}]:   {price_snt_kwh_formatted}snt    {tags}\n"
                    prices_printed += 1

    return displayable_text
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, time, timezone

prices = ""

current_UTC = datetime.now(timezone.utc).replace(tzinfo=None)
previous_UTC = datetime.combine(current_UTC, time.min) - timedelta(days=1)
previous_UTC_formatted = previous_UTC.strftime("%Y%m%d%H%M")

with open('entsoe_token.txt', 'r') as file:
    entsoe_token = file.read().rstrip()

get_url = f"https://web-api.tp.entsoe.eu/api?securityToken={entsoe_token}&documentType=A44&in_Domain=10YFI-1--------U&out_Domain=10YFI-1--------U&periodStart={previous_UTC_formatted}&periodEnd=202312310000"
print("Request sent")
response_text = requests.get(get_url).text

print("Answer received")

prices_updated_flag = (response_text == prices)
prices = response_text

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
start_hour = 23
prices_printed = 0
prices_to_print = 20

for day in root.findall('{*}TimeSeries'):
    start_date = day.find("{*}Period").find("{*}timeInterval").find("{*}start").text[:10]
    end_dt = day.find("{*}Period").find("{*}timeInterval").find("{*}end").text
    end_date  = end_dt[:10]
    now_date = current_HEL.strftime("%Y-%m-%d")[:10]
    if now_date <= end_date:
        print(start_date)
        print(end_date)
        for point in day.find("{*}Period").findall('{*}Point'):
            if prices_printed >= prices_to_print:
                break
            index_of_point = int(point.find('{*}position').text)
            hour_abs = (start_hour + index_of_point - 1)
            HEL_hour_abs = int(hour_abs + timezone_difference_h)
            HEL_hour_real = HEL_hour_abs % 24
            if now_date < end_date or HEL_hour_real >= int(current_HEL_hour) or HEL_hour_abs == 48: #a bit of a band-aid :D
                print(hour_abs)
                print(HEL_hour_abs)
                print(HEL_hour_real)
                print("\n")
                price = float(point.find('{*}price.amount').text)
                price_snt_kwh = price / 10
                price_snt_kwh_formatted = format(price_snt_kwh, '.2f')
                tags = "#" * round(price_snt_kwh * 2)
                hours_to_hour = (prices_printed)
                displayable_text += f"{HEL_hour_real:0{2}d} [{hours_to_hour:0{2}d}]:   {price_snt_kwh_formatted}snt    {tags}\n"
                prices_printed += 1

print(displayable_text) 
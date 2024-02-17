import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, time, timezone

#initial value
prices = ""

#function to get prices from API
def get_prices():
    current_UTC = datetime.now(timezone.utc).replace(tzinfo=None)
    previous_UTC = datetime.combine(current_UTC, time.min) - timedelta(days=1)
    previous_UTC_formatted = previous_UTC.strftime("%Y%m%d%H%M")
    period_end = datetime.combine(current_UTC, time.min) + timedelta(days=3)
    period_end_formatted = period_end.strftime("%Y%m%d%H%M")

    #read api-token for ENTSOE
    with open('entsoe_token.txt', 'r') as file:
        entsoe_token = file.read().rstrip()

    #url for api-request
    get_url = f"https://web-api.tp.entsoe.eu/api?securityToken={entsoe_token}&documentType=A44&in_Domain=10YFI-1--------U&out_Domain=10YFI-1--------U&periodStart={previous_UTC_formatted}&periodEnd={period_end_formatted}"
    
    try:
        print(f"Request sent at {datetime.now()}") #log
        response_text = requests.get(get_url).text
    except requests.RequestException as e:
        print(f"An error occurred during the request: {e}") #log
        return None
    
    print(f"Answer received at at {datetime.now()}") #log

    global prices
    prices_updated_flag = (response_text == prices) #set flag if new prices (currently not used)
    prices = response_text #update the prices with the response


    return prices_updated_flag



def construct_texts():

    current_UTC = datetime.now(timezone.utc).replace(tzinfo=None)
    current_HEL = datetime.now()
    timezone_difference_h = (current_HEL - current_UTC).seconds / 3600
    current_HEL_hour = current_HEL.strftime("%H")

    #parse to XML
    try:
        root = ET.fromstring(prices)
    except ET.ParseError as e:
        print("XML Parsing Error:", e)

    #initial value
    displayable_text = ""

    #hour at which the API-data starts each day
    start_hour = 23
    #collector
    prices_printed = 0
    #maximum number of prices in the response
    prices_to_print = 20

    #construct the reponse-message by parsing XML
    for day in root.findall('{*}TimeSeries'):
        end_date = day.find("{*}Period").find("{*}timeInterval").find("{*}end").text[:10] #find date of last day
        now_date = current_HEL.strftime("%Y-%m-%d")[:10]
        if now_date <= end_date: #if future prices exist
            for point in day.find("{*}Period").findall('{*}Point'): #find all points (= hourly prices)
                if prices_printed >= prices_to_print: #if enough prices
                    break
                index_of_point = int(point.find('{*}position').text) #the points are only indexed starting from day 1 23:00 UTC and go until day 2 22:00 UTC, points do not contain time info other than the start
                hour_abs = (start_hour + index_of_point - 1) #get hours from start by 23 (start of data) + index - 1
                HEL_hour_abs = int(hour_abs + timezone_difference_h) #convert to UTC+2
                HEL_hour_real = HEL_hour_abs % 24 #convert to real hours (eg. 24 -> 00, 25 -> 01...)
                if now_date < end_date or HEL_hour_real >= int(current_HEL_hour) or HEL_hour_abs == 48: #if hour in the future -> add to message
                    price = float(point.find('{*}price.amount').text) #get price from point
                    price_snt_kwh = price / 10 #to snt/kwh
                    price_snt_kwh_formatted = format(price_snt_kwh, '.2f') #format
                    tags = "#" * round(price_snt_kwh * 2) #visualize with "#...#"
                    hours_to_point = prices_printed #hours until current point
                    displayable_text += f"{HEL_hour_real:0{2}d} [{hours_to_point:0{2}d}]:   {price_snt_kwh_formatted}snt    {tags}\n" #construct final text
                    prices_printed += 1 #increment

    #display error-message if displayable text is empty after loop
    if len(displayable_text) == 0:
        displayable_text = "Virhe hintojen hakemisessa ENTSOE:sta, ota yhteyttä @antonpodlozny ja kokeile myöhemmin uudelleen."
    
    #return to caller
    return displayable_text
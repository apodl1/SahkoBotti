import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
import math
from typing import Optional

PRICES_TO_PRINT = 20
TAGS_PER_EUR = 2

class ElecPrices():
  def __init__(self) -> None:
    self.prices_dict: Optional[dict[datetime, float]] = None
    self.current_error: Optional[str] = None
    self.logger = logging.getLogger("sahkobotti")

    self.fetch_prices_to_dict() #get initial prices


  # Get prices from API in xml format (as string response). Returns true if new prices retrieved successfully
  def fetch_prices_to_dict(self) -> bool:
    current_local_time = datetime.now(ZoneInfo("Europe/Helsinki"))
    start_of_previous_day = datetime.combine(current_local_time, time.min) - timedelta(days=1)
    start_of_previous_day_formatted = start_of_previous_day.strftime("%Y%m%d%H%M")
    period_end = datetime.combine(current_local_time, time.min) + timedelta(days=3) #arbitary value far enough in the future, the api will then give latest info
    period_end_formatted = period_end.strftime("%Y%m%d%H%M")

    #read api-token for ENTSOE
    with open(".entsoe_token", "r") as file:
      entsoe_token = file.read().rstrip()

    #construct url for api-request
    get_url = f"https://web-api.tp.entsoe.eu/api?securityToken={entsoe_token}&documentType=A44&in_Domain=10YFI-1--------U&out_Domain=10YFI-1--------U&periodStart={start_of_previous_day_formatted}&periodEnd={period_end_formatted}"

    try:
      to_log = "ENTSOE Request sent."
      print(to_log)
      self.logger.info(to_log)
      response_text = requests.get(get_url).text
    except requests.RequestException as e:
      to_log = f"An error occurred during the request: {e}"
      print(to_log)
      self.logger.error(to_log)
      self.current_error = "Virhe tietojen haussa ENTSOE:lta, yritä myöhemmin uudelleen."
      return False

    self.current_error = ""
    to_log = "Answer received."
    print(to_log)
    self.logger.info(to_log)

    prices_dict: Optional[dict[datetime, float]] = self.extract_prices_into_dict(response_text)
    if prices_dict is not None:
      if (self.prices_dict is None) or (max(self.prices_dict) < max(prices_dict)):
        self.prices_dict = prices_dict
        to_log = "Prices updated"
        print(to_log)
        self.logger.info(to_log)
        return True
      else:
        to_log = "No new prices received!"
        print(to_log)
        self.logger.debug(to_log)
        return False
    else:
      to_log = "No prices extracted in parsing!"
      print(to_log)
      self.logger.error(to_log)
      return False


  def extract_prices_into_dict(self, prices_text: str) -> Optional[dict]:
    try:
        root = ET.fromstring(prices_text)
        self.current_error = ""
    except ET.ParseError as e:
      to_log = f"XML Parsing Error: {e}"
      print(to_log)
      self.logger.error(to_log)
      self.current_error = "Virhe ENTSOE:n palauttamassa datassa, yritä myöhemmin uudelleen."
      return None

    prices_dict: dict[datetime, float] = dict()

    for timeseries in root.findall("{*}TimeSeries"):
      period = timeseries.find("{*}Period")
      if period is not None:
        timeInterval = period.find("{*}timeInterval")
        if timeInterval is not None:
          start_time_UTC = timeInterval.find("{*}start")
          if start_time_UTC is not None and start_time_UTC.text is not None:
            period_start_time_local = datetime.fromisoformat(start_time_UTC.text).astimezone(ZoneInfo("Europe/Helsinki"))
          else:
            self.current_error = "Virhe ENTSOE:n palauttamassa datassa, yritä myöhemmin uudelleen."
            return None
        else:
          self.current_error = "Virhe ENTSOE:n palauttamassa datassa, yritä myöhemmin uudelleen."
          return None
        for point in period.findall("{*}Point"):
          position = point.find("{*}position")
          price = point.find("{*}price.amount")
          if position is not None and price is not None:
            if position.text and price.text is not None:
              hour = int(position.text) - 1
              point_time = period_start_time_local + timedelta(hours=hour)
              prices_dict[point_time] = float(price.text)

    return prices_dict

  def get_price_text(self) -> str:
    text_to_return = ""
    now = datetime.now(ZoneInfo("Europe/Helsinki"))
    hour_ago = now - timedelta(hours=1)
    if self.prices_dict is not None:
      coming_prices = [(time_of_price, price) for (time_of_price, price) in self.prices_dict.items() if time_of_price > hour_ago]
      coming_prices_sorted = sorted(coming_prices, key=lambda x: x[0])

      if len(coming_prices_sorted) != 0:
        text_to_return += f"Hinnat {now.strftime("%d.%m. %H:")}00->\n"
        added = 0
        for time_of_price, price in coming_prices_sorted:
          price_snt_kwh = price / 10 #EUR/MWh to snt/kWhx
          price_snt_kwh_rounded = format(price_snt_kwh, ".2f")
          tags = "#" * round(price_snt_kwh * TAGS_PER_EUR) #visualize price with "#" per every 0.50snt
          hours_to_point = math.ceil((time_of_price - now).total_seconds() / 3600) #hours until the price
          text_to_return += f"{time_of_price.hour:0{2}d} [{hours_to_point:0{2}d}]:   {price_snt_kwh_rounded}snt    {tags}\n"
          added += 1
          if added >= PRICES_TO_PRINT:
            return text_to_return
        return text_to_return
      else:
        return "Ei ajantasaisia hintoja, yritä myöhemmin uudelleen."
    else:
      return "Ei ajantasaisia hintoja, yritä myöhemmin uudelleen."



if __name__ == '__main__':
  test = ElecPrices()
  print(test.get_price_text())

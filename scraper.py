
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import pandas as pd
from itertools import product
import sys


def get_flights_details(result):
    price = int(result.find_element(By.CLASS_NAME, 'price-text').text.replace('$', '').replace(',', '_'))
    flights = result.find_element(By.CLASS_NAME, 'flights')
    departure_flight, return_flight = flights.find_elements(By.TAG_NAME, 'li')
    link = result.find_element(By.CLASS_NAME, 'booking-link').get_attribute('href')

    flights_details = [price]
    for flight in [departure_flight, return_flight]:
        times, airline = flight.find_element(By.CLASS_NAME, 'section.times').text.split('\n')
        n_stops, stops = flight.find_element(By.CLASS_NAME, 'section.stops').text.split('\n')
        duration, frm, _, to = flight.find_element(By.CLASS_NAME, 'section.duration.allow-multi-modal-icons').text.split('\n')
        flights_details += [times, airline, n_stops, stops, duration, frm, to]
    flights_details += [link]
    return flights_details


def get_table(RESULTS):
    records = []
    for result in RESULTS:
        records.append(get_flights_details(result))
    columns = [
        (col, fl) for col, fl in 
        product(
            ['departure', 'return'],
            ['times', 'airline', 'n_stops', 'stops', 'duration', 'from', 'to'], 
        )
    ]
    columns = [(None, 'price')] + columns + [(None, 'link')]

    DF = pd.DataFrame(records, columns=pd.MultiIndex.from_tuples(columns))
    return DF


def scrap_kayak(departure=None, retrn=None, frm=None, to=None, URL=False):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    if not URL:
        DEPARTURE = departure.strftime('%Y-%m-%d')
        RETURN = retrn.strftime('%Y-%m-%d')
        FROM = frm
        TO = to
        URL = f'https://www.kayak.com/flights/{FROM}-{TO}/{DEPARTURE}/{RETURN}?sort=price_a'


    wd = webdriver.Chrome(executable_path='chromedriver', options=chrome_options)
    wd.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    #Setting up Chrome/83.0.4103.53 as useragent
    wd.execute_cdp_cmd(
        'Network.setUserAgentOverride',
        {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'}
    )
    # wd.implicitly_wait(10)
    wd.get(URL)
    try:
        WebDriverWait(wd, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'moreButton')))
    except TimeoutException:
        sys.stdout.write('TimeoutException Error\n')
        return
    MORE_BUTTON = wd.find_element(By.CLASS_NAME, 'moreButton')
    MORE_BUTTON.click()

    RESULTS = wd.find_elements(By.CLASS_NAME, 'inner-grid.keel-grid')
    table = get_table(RESULTS)
    wd.close()
    table['dep_date'] = departure
    table['ret_date'] = retrn
    return table
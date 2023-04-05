from datetime import datetime
from pandas import date_range, concat, DataFrame
from itertools import product

from scraper import scrap_kayak
import threading
import os

def wrapper(df_list, index, **kwargs):
    df_list[index] = scrap_kayak(**kwargs)

# Flights from Chicago:
DEPARTURE_DATES = date_range(start='2022-12-16', end='2022-12-17')
RETURN_DATES = date_range(start='2023-01-03', end='2023-01-07')
FROM_AIRPORTS = ['ORD', 'MDW']

threads = []
OPTS = list(product(DEPARTURE_DATES, RETURN_DATES, FROM_AIRPORTS))
N_OPTS = len(OPTS)
dfs = [None] * N_OPTS

for n, (DEPARTURE, RETURN, FROM) in enumerate(OPTS):
    print(f'[{n+1}/{N_OPTS}]', DEPARTURE, RETURN, FROM)
    DEPARTURE = DEPARTURE.strftime('%Y-%m-%d')
    RETURN = RETURN.strftime('%Y-%m-%d')
    TO = 'BOG'
    URL = f'https://www.kayak.com/flights/{FROM}-{TO}/{DEPARTURE}/{TO}-HSV/{RETURN}?sort=price_a'
    threads.append(
        threading.Thread(
            target=wrapper, 
            kwargs={'df_list': dfs, 'index': n, 'URL': URL, 'departure': DEPARTURE, 'retrn': RETURN}
        )
    )
    threads[-1].start()
    if (n + 1) % 4 == 0: # Run by 4 threads
        for thr in threads:
            thr.join()
        threads = []
    
# Flights from Huntsville
DEPARTURE_DATES = date_range(start='2022-12-18', end='2022-12-19')
RETURN_DATES = date_range(start='2023-01-03', end='2023-01-07')
FROM_AIRPORTS = ['HSV']

threads = []
n_prev = N_OPTS
OPTS = list(product(DEPARTURE_DATES, RETURN_DATES, FROM_AIRPORTS))
N_OPTS = len(OPTS)
dfs = dfs + ([None] * N_OPTS)

for n, (DEPARTURE, RETURN, FROM) in enumerate(OPTS):
    n += n_prev
    print(f'[{n+1}/{N_OPTS}]', DEPARTURE, RETURN, FROM)
    TO = 'BOG'
    threads.append(
        threading.Thread(
            target=wrapper, 
            kwargs={'df_list': dfs, 'index': n, 'departure': DEPARTURE, 'retrn': RETURN, 'to': 'BOG', 'frm': FROM}
        )
    )
    threads[-1].start()
    if (n + 1) % 4 == 0: # Run by 4 threads
        for thr in threads:
            thr.join()
        threads = []
    

dfs = [df for df in dfs if isinstance(df, DataFrame)]
DF = concat(dfs, ignore_index=True).sort_values(by=dfs[0].columns[0], ascending=True)
DF.to_excel(f'/mnt/c/Users/daqui/OneDrive/Escritorio/Flights/flights_{datetime.now().strftime("%m%d")}.xlsx')

under_th = sum(DF.iloc[:, 0] <= 1000)
min_val = DF.iloc[:, 0].min()

if under_th:
    os.system(f'powershell.exe -Command "python C:/Users/daqui/OneDrive/Escritorio/Flight_scrapper/notify.py {under_th} {min_val}"')



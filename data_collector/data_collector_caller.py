import data_collector
import time
import threading
import datetime

jal_collection_list = [
    ['NRT', ['CTS', 'NGO', 'ITM']],
    ['HND', ['ITM', 'CTS', 'FUK', 'AOJ', 'MMB', 'AKJ', 'KUH', 'OBO', 'HKD', 'MSJ', 'AXT', 'KMQ']],
    ['CTS', ['MMB', 'AOJ', 'HNA', 'SDJ', 'KIJ', 'NGO']],
    ['OKD', ['RIS', 'MMB', 'KUH', 'HKD', 'MSJ', 'AXT']]
]
ana_collection_list = [
    ['NRT', ['SPK', 'NGO', 'ITM']],
    ['HND', ['SPK', 'FUK', 'WKJ', 'KUH', 'HKD', 'AXT', 'TOY', 'KMQ', 'KIX']],
    ['NGO', ['SPK', 'AXT']],
    ['KIX', ['SPK']],
    ['ITM', ['SPK', 'HKD', 'AOJ', 'AXT']],
    ['SPK', ['WKJ', 'MMB', 'KUH', 'HKD', 'AOJ', 'AXT', 'SDJ', 'KIJ', 'TOY', 'KMQ', 'HIJ', 'FUK']]
]

def scrape_jal(date="prev", sufix = ""):
    collector = data_collector.JalScraper()
    for collection in jal_collection_list:
        for to in collection[1]:
            # 往路
            collector.set_from(collection[0])
            collector.set_to(to)
            collector.set_date(date)
            collector.scrape(f"jal{sufix}.csv")
            time.sleep(3)
            # 復路
            collector.set_from(to)
            collector.set_to(collection[0])
            collector.set_date(date)
            collector.scrape(f"jal{sufix}.csv")
            time.sleep(3)

def scrape_ana(date="prev", sufix=""):
    collector = data_collector.AnaScraper()
    for collection in ana_collection_list:
        for to in collection[1]:
            # 往路
            collector.set_from(collection[0])
            collector.set_to(to)
            collector.set_date(date)
            collector.scrape(f"ana{sufix}.csv")
            time.sleep(3)
            # 復路
            collector.set_from(to)
            collector.set_to(collection[0])
            collector.set_date(date)
            collector.scrape(f"ana{sufix}.csv")
            time.sleep(3)

import sys

if len(sys.argv) > 1:
    date = sys.argv[1]
    date_str = ""
    if date == "prev":
        date_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    elif date == "today":
        date_str = datetime.date.today().strftime('%Y%m%d')
    elif date == "next":
        date_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y%m%d')
    thread_jal = threading.Thread(target=scrape_jal, args=(date,date_str))
    thread_ana = threading.Thread(target=scrape_ana, args=(date,date_str))
else:
    # this will be called when no sys args placed.
    # this means that the target to get is "prev"
    date_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    thread_jal = threading.Thread(target=scrape_jal, args=("prev", date_str))
    thread_ana = threading.Thread(target=scrape_ana, args=("prev", date_str))

thread_jal.start()
thread_ana.start()

thread_jal.join()
thread_ana.join()


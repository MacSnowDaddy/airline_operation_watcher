import data_collector
import time
import threading
import datetime

jal_collection_list = [
    ['NRT', ['CTS', 'NGO', 'ITM']],
    ['HND', ['ITM', 'CTS', 'FUK', 'AOJ', 'MMB', 'AKJ', 'KUH', 'OBO', 'HKD', 'MSJ', 'AXT', 'KMQ', 'OKA']],
    ['CTS', ['MMB', 'AOJ', 'HNA', 'SDJ', 'KIJ', 'NGO']],
    ['OKD', ['RIS', 'MMB', 'KUH', 'HKD', 'MSJ', 'AXT']]
]
ana_collection_list = [
    ['NRT', ['SPK', 'NGO', 'ITM']],
    ['HND', ['SPK', 'FUK', 'WKJ', 'KUH', 'HKD', 'AXT', 'TOY', 'KMQ', 'KIX', 'OKA']],
    ['NGO', ['SPK', 'AXT']],
    ['KIX', ['SPK']],
    ['ITM', ['SPK', 'HKD', 'AOJ', 'AXT']],
    ['SPK', ['WKJ', 'MMB', 'KUH', 'HKD', 'AOJ', 'AXT', 'SDJ', 'KIJ', 'TOY', 'KMQ', 'HIJ', 'FUK']]
]
ado_collection_list = [
    ['HND', ['SPK']],
]

sky_collection_list = [
    ['HND', ['CTS', 'FUK', 'OKA']],
    ['CTS', ['NGO', 'FUK']],
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
    move_to_data_dir(f"jal{sufix}.csv")
    print("jal done")

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
    # move file created into data folder
    move_to_data_dir(f"ana{sufix}.csv")
    print("ana done")
    
def scrape_ado(date="prev", sufix=""):
    collector = data_collector.AdoScraper()
    for collection in ado_collection_list:
        for to in collection[1]:
            # 往路
            collector.set_from(collection[0])
            collector.set_to(to)
            collector.set_date(date)
            collector.scrape(f"ado{sufix}.csv")
            time.sleep(3)
    # move file created into data folder
    move_to_data_dir(f"ado{sufix}.csv")
    print("ado done")

def scrape_sky(date="prev", sufix=""):
    collector = data_collector.SkyScraper()
    for collection in sky_collection_list:
        for to in collection[1]:
            # 往路
            collector.set_from(collection[0])
            collector.set_to(to)
            collector.set_date(date)
            collector.scrape(f"sky{sufix}.csv")
            time.sleep(3)
            # 復路
            collector.set_from(to)
            collector.set_to(collection[0])
            collector.set_date(date)
            collector.scrape(f"sky{sufix}.csv")
            time.sleep(3)
    # move file created into data folder
    move_to_data_dir(f"sky{sufix}.csv")
    print("sky done")

def move_to_data_dir(filename):
    import shutil
    import os
    # define dir name to move
    # dir name should be yyyymmdd-mmdd
    # first mmdd is the first date of the week of the date
    # (first day of the week is Sunday)
    # second mmdd is the last date of the week of the date
    # (last day of the week is Saturday)
    date = filename[-12:-4]
    date = datetime.datetime.strptime(date, '%Y%m%d')
    first_day_of_week = date - datetime.timedelta(days=(date.weekday()+1))
    last_day_of_week = date + datetime.timedelta(days=(5-date.weekday()))
    date_str = first_day_of_week.strftime('%Y%m%d') + "-" + last_day_of_week.strftime('%m%d')
    # move file
    if filename == "":
        return
    elif "ana" in filename:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ana", 'analyze_target', date_str)
        if not os.path.exists(path):
            os.makedirs(path)
        shutil.move(filename, os.path.join(path, filename))
    elif "jal" in filename:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jal", 'analyze_target', date_str)
        if not os.path.exists(path):
            os.makedirs(path)
        shutil.move(filename, os.path.join(path, filename))
    elif "ado" in filename:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ado", 'analyze_target', date_str)
        if not os.path.exists(path):
            os.makedirs(path)
        shutil.move(filename, os.path.join(path, filename))
    elif "sky" in filename:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sky", 'analyze_target', date_str)
        if not os.path.exists(path):
            os.makedirs(path)
        shutil.move(filename, os.path.join(path, filename))


import sys

if len(sys.argv) > 1:
    date = sys.argv[1]
else:
    date = "prev"
date_str = ""
if date == "prev":
    date_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
elif date == "today":
    date_str = datetime.date.today().strftime('%Y%m%d')
elif date == "next":
    date_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y%m%d')

thread_jal = threading.Thread(target=scrape_jal, args=(date,date_str))
thread_ana = threading.Thread(target=scrape_ana, args=(date,date_str))
thread_ado = threading.Thread(target=scrape_ado, args=(date,date_str))
thread_sky = threading.Thread(target=scrape_sky, args=(date,date_str))

thread_sky.start()
thread_jal.start()
thread_ana.start()
thread_ado.start()

thread_sky.join()
thread_jal.join()
thread_ana.join()
thread_ado.join()

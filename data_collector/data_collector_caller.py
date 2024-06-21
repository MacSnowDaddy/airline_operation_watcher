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

def scrape(class_, list, date="prev", sufix=""):
    collector = class_()
    for collection in list:
        for to in collection[1]:
            #jalの場合は路線ごとにインスタンスを作り直す
            if class_ == data_collector.JalScraper:
                collector = class_()
            # 往路
            collector.set_from(collection[0])
            collector.set_to(to)
            collector.set_date(date)
            collector.scrape(f"{collector.file_name_header()}{sufix}.csv")
            time.sleep(3)
            if class_ == data_collector.JalScraper:
                collector = class_()
            # 復路
            collector.set_from(to)
            collector.set_to(collection[0])
            collector.set_date(date)
            collector.scrape(f"{collector.file_name_header()}{sufix}.csv")
            time.sleep(3)
    move_to_data_dir(f"{collector.file_name_header()}{sufix}.csv")
    print(f"{collector.file_name_header()} done")
    
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

def move_to_data_dir(filename:str):
    '''move file to data directory.

    Args:
        filename (str): file name to move. file name should be like "xxxyyyymmdd.csv".
        xxx is the airline's icao code.
    '''
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
    first_day_of_week, last_day_of_week = first_last_day_of_week(date)
    date_str = first_day_of_week.strftime('%Y%m%d') + "-" + last_day_of_week.strftime('%m%d')
    # move file
    if filename == "":
        return
    icaocode = filename[:3]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), icaocode, 'analyze_target', date_str)
    if not os.path.exists(path):
        os.makedirs(path)
    shutil.move(filename, os.path.join(path, filename))

def first_last_day_of_week(date:datetime.datetime) -> tuple[datetime.datetime, datetime.datetime]:
    first_day_of_week = date - datetime.timedelta(days=((date.weekday()+1)%7))
    last_day_of_week = date + datetime.timedelta(days=((5-date.weekday())%7))
    return first_day_of_week, last_day_of_week


def main():
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

    thread_jal = threading.Thread(target=scrape, args=(data_collector.JalScraper, jal_collection_list, date, date_str))
    thread_ana = threading.Thread(target=scrape, args=(data_collector.AnaScraper, ana_collection_list, date, date_str))
    thread_ado = threading.Thread(target=scrape_ado, args=(date,date_str)) # adoは往路のみ呼べば復路も取得できる
    thread_sky = threading.Thread(target=scrape, args=(data_collector.SkyScraper, sky_collection_list, date, date_str))

    thread_sky.start()
    thread_jal.start()
    thread_ana.start()
    thread_ado.start()

    thread_sky.join()
    thread_jal.join()
    thread_ana.join()
    thread_ado.join()


if __name__ == "__main__":
    main()
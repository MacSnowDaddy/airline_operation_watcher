import os
import sys
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG
import boto3
from . import data_collector
import time
import datetime

logger = getLogger(__name__)
if os.getenv('ENV') == 'ec2':
    handler = FileHandler(f'/var/log/daily_aviation_analyzer.log')
else:
    handler = StreamHandler()
handler = StreamHandler()
handler.setLevel(DEBUG)
handler.setFormatter(Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

target = os.getenv('TARGET', 'production')
if target == 'production':
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
elif target == 'test':
    jal_collection_list = [
        ['HND', ['ITM', 'CTS',]],
    ]
    ana_collection_list = [
        ['HND', ['SPK', 'FUK',]],
    ]
    ado_collection_list = [
        ['HND', ['SPK']],
    ]
    sky_collection_list = [
        ['HND', ['CTS', 'FUK',]],
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
            # print progress
            logger.debug(f"{collector.file_name_header()} {collection[0]} -> {to} done")
            if class_ == data_collector.JalScraper:
                time.sleep(1)
            else:
                time.sleep(3)
            if class_ == data_collector.JalScraper:
                collector = class_()
            # 復路
            collector.set_from(to)
            collector.set_to(collection[0])
            collector.set_date(date)
            collector.scrape(f"{collector.file_name_header()}{sufix}.csv")
            # print progress
            logger.debug(f"{collector.file_name_header()} {collection[0]} -> {to} done")
            if class_ == data_collector.JalScraper:
                time.sleep(1)
            else:
                time.sleep(3)
    save_to_s3(f"{collector.file_name_header()}{sufix}.csv")
    move_to_data_dir(f"{collector.file_name_header()}{sufix}.csv")
    logger.info(f"{collector.file_name_header()} done")
    
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
    save_to_s3(f"ado{sufix}.csv")
    move_to_data_dir(f"ado{sufix}.csv")
    logger.info("ado done")

def save_to_s3(filename:str):
    if target == 'test':
        up_filename = "test_" + filename
    else:
        up_filename = filename
    s3_client = boto3.client('s3')
    bucket_name = "airline-operation-watcher"
    try:
        s3_client.upload_file(filename, bucket_name, up_filename)
    except boto3.exceptions.S3UploadFailedError as e:
        logger.error(f"Upload failed: {e}")
        return False
    logger.info(f"{filename} uploaded to s3")
    return True

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
    if target == 'test':
        shutil.move(filename, os.path.join(path, f'test_{filename}'))
    else:
        shutil.move(filename, os.path.join(path, f'{filename}'))
        

def first_last_day_of_week(date:datetime.datetime) -> tuple[datetime.datetime, datetime.datetime]:
    first_day_of_week = date - datetime.timedelta(days=((date.weekday()+1)%7))
    last_day_of_week = date + datetime.timedelta(days=((5-date.weekday())%7))
    return first_day_of_week, last_day_of_week


def main(operator:str, date:str="prev"):
    import sys

    if date == "prev":
        date_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    elif date == "today":
        date_str = datetime.date.today().strftime('%Y%m%d')
    elif date == "next":
        date_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y%m%d')

    if operator == "jal":
        logger.info("jal scraping start.")
        scrape(data_collector.JalScraper, jal_collection_list, date, date_str)
        logger.info("jal scraping finished.")
    elif operator == "ana":
        logger.info("ana scraping start.")
        scrape(data_collector.AnaScraper, ana_collection_list, date, date_str)
        logger.info("ana scraping finished.")
    elif operator == "sky":
        logger.info("sky scraping start.")
        scrape(data_collector.SkyScraper, sky_collection_list, date, date_str)
        logger.info("sky scraping finished.")
    elif operator == "ado":
        logger.info("ado scraping start.")
        scrape_ado(date, date_str)
        logger.info("ado scraping finished.")


if __name__ == "__main__":
    '''usage: python data_collector_caller.py [operator1] [operator2] ... [date]

    example: python data_collector_caller.py jal ana sky prev
    operator: jal, ana, sky, ado
    date: prev, today, next
    at least one operator should be passed.
    date is mandatory.
    '''
    if len(sys.argv) > 1:
        for operator in sys.argv[1:-1]:
            main(operator, date=sys.argv[-1])
    else:
        print("operator is not passed.\nusage: python data_collector_caller.py [operator1] [operator2] ... [date]")
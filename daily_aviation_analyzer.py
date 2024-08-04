import os
import datetime
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG
import threading
import 会社別RJTT2RJCC定時到着率
from data_collector import data_collector_caller

logger = getLogger(__name__)
if os.getenv('ENV') == 'ec2':
    handler = FileHandler(os.path.join(os.path.dirname(__file__), 'daily_aviation_analyzer.log'))
else:
    handler = StreamHandler()
handler.setLevel(DEBUG)
handler.setFormatter(Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

def main():
    logger.info("start daily aviation analyzer.main().")
    start_time = datetime.datetime.now()

    thread_jal = threading.Thread(target=data_collector_caller.main, args=("jal",))
    thread_ana = threading.Thread(target=data_collector_caller.main, args=("ana",))
    thread_sky = threading.Thread(target=data_collector_caller.main, args=("sky",))
    thread_ado = threading.Thread(target=data_collector_caller.main, args=("ado",))

    thread_jal.start()
    thread_ana.start()
    thread_sky.start()
    thread_ado.start()

    thread_jal.join()
    thread_ana.join()
    thread_sky.join()
    thread_ado.join()

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    会社別RJTT2RJCC定時到着率.main(yesterday.year, yesterday.month, yesterday.day, "HND", "CTS")
    会社別RJTT2RJCC定時到着率.main(yesterday.year, yesterday.month, yesterday.day, "CTS", "HND")

    end_time = datetime.datetime.now()
    duration = end_time - start_time
    logger.debug(f"duration: {duration}sec.")
    logger.info("end daily aviation analyzer.main().")
    
if __name__ == "__main__":
    main()

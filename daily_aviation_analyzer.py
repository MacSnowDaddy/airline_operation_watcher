import os
import datetime
import logging
import threading
import 会社別RJTT2RJCC定時到着率
from data_collector import data_collector_caller

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def main():
    logging.info("start daily aviation analyzer.main().")
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
    logging.debug(f"duration: {duration}sec.")
    logging.info("end daily aviation analyzer.main().")
    
if __name__ == "__main__":
    # I want to see logging only from my script.
    selenium_logger = logging.getLogger('selenium')
    null_handler = logging.FileHandler(os.devnull)
    selenium_logger.addHandler(null_handler)
    main()

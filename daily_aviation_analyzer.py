import datetime
import logging
import 会社別RJTT2RJCC定時到着率
import data_collector_caller

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def main():
    logging.info("start daily aviation analyzer.main().")
    start_time = datetime.datetime.now()

    data_collector_caller.main()
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    会社別RJTT2RJCC定時到着率.main(yesterday.year, yesterday.month, yesterday.day, "HND", "CTS")
    会社別RJTT2RJCC定時到着率.main(yesterday.year, yesterday.month, yesterday.day, "CTS", "HND")

    end_time = datetime.datetime.now()
    duration = end_time - start_time
    logging.debug(f"duration: {duration}sec.")
    logging.info("end daily aviation analyzer.main().")
    
if __name__ == "__main__":
    main()

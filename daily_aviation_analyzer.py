import datetime
import 会社別RJTT2RJCC定時到着率
import data_collector_caller

def main():
    start_time = datetime.datetime.now()

    data_collector_caller.main()
    import datetime
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    会社別RJTT2RJCC定時到着率.main(yesterday.year, yesterday.month, yesterday.day, "HND", "CTS")
    会社別RJTT2RJCC定時到着率.main(yesterday.year, yesterday.month, yesterday.day, "CTS", "HND")

    end_time = datetime.datetime.now()
    duration = end_time - start_time
    print(f"duration: {duration}sec.")
    
if __name__ == "__main__":
    main()

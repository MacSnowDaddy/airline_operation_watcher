import 会社別RJTT2RJCC定時到着率
import data_collector_caller

def main():
    data_collector_caller.main()
    import datetime
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    会社別RJTT2RJCC定時到着率.main(yesterday.year, yesterday.month, yesterday.day, "HND", "CTS")
    会社別RJTT2RJCC定時到着率.main(yesterday.year, yesterday.month, yesterday.day, "CTS", "HND")
    


if __name__ == "__main__":
    main()

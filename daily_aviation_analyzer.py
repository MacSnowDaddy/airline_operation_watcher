import 会社別RJTT2RJCC定時到着率
import data_collector_caller

def main():
    data_collector_caller.main()
    import datetime
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    会社別RJTT2RJCC定時到着率.main(yesterday)


if __name__ == "__main__":
    main()

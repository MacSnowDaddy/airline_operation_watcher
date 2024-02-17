import data_collector
import time

collector = data_collector.JalScraper()
jal_collection_list = [
    ['HND', ['CTS', 'FUK', 'AOJ', 'MMB', 'AKJ']],
    ['CTS', ['AOJ', 'HNA', 'SDJ', 'KIJ']]
]
ana_collection_list = [
    ['HND', ['CTS', 'FUK', '']]
]
for collection in jal_collection_list:
    for to in collection[1]:
        # 往路
        collector.set_from(collection[0])
        collector.set_to(to)
        collector.set_date("prev")
        collector.scrape("jal.csv")
        time.sleep(3)
        # 復路
        collector.set_from(to)
        collector.set_to(collection[0])
        collector.set_date("prev")
        collector.scrape("jal.csv")
        time.sleep(3)

collector = data_collector.AnaScraper()
collector.set_from("HND")
collector.set_to("CTS")
collector.set_date("prev")
collector.scrape("ana.csv")
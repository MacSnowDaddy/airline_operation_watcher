import data_collector
import time

jal_collection_list = [
    ['NRT', ['CTS', 'NGO', 'ITM']],
    ['HND', ['ITM', 'CTS', 'FUK', 'AOJ', 'MMB', 'AKJ', 'KUH', 'OBO', 'HKD', 'MSJ', 'AXT', 'KMQ']],
    ['CTS', ['MMB', 'AOJ', 'HNA', 'SDJ', 'KIJ', 'NGO']],
    ['OKD', ['RIS', 'MMB', 'KUH', 'HKD', 'MSJ', 'AXT']]
]
ana_collection_list = [
    ['NRT', ['SPK', 'NGO', 'ITM']],
    ['HND', ['SPK', 'FUK', 'WKJ', 'KUH', 'HKD', 'AXT', 'TOY', 'KMQ', 'KIX']],
    ['NGO', ['SPK', 'AXT']],
    ['KIX', ['SPK']],
    ['ITM', ['SPK', 'HKD', 'AOJ', 'AXT']],
    ['SPK', ['WKJ', 'MMB', 'KUH', 'HKD', 'AOJ', 'AXT', 'SDJ', 'FSZ', 'KIJ', 'TOY', 'KMQ', 'HIJ', 'FUK']]
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
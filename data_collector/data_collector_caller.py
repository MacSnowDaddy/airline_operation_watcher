import data_collector

collector = data_collector.JalScraper()
collector.set_from("HND")
collector.set_to("CTS")
collector.set_date("prev")
collector.scrape("jal.csv")
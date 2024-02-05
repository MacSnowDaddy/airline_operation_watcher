from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

# set list of scrap
scrap_dict = {"jal" : "https://www.jal.co.jp/jp/ja/other/weather_info_dom/",
              "ana" : "https://www.ana.co.jp/fs/dom/jp/",
              "fda" : "https://www.fujidream.co.jp/sp/flight_info/",
              "sky" : "https://www.res.skymark.co.jp/mercury/fis/flight_announce_i18n",
              }

class Scraper(object):
    """Scrapeするための抽象クラス。実装は各航空会社ごとに行う。"""

    def __init__(self):
        # ブラウザを初期化する。
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--single-process")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--window-size=880x996")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--homedir=/tmp")
        self.options.add_argument(
            f'user-agent=mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/77.0.3865.120 safari/537.36')
        self.browser = webdriver.Chrome(options=self.options)
        self.url = ""

    def set_from(self, from_ap):
        self.from_ap = from_ap
    
    def set_to(self, to_ap):
        self.to_ap = to_ap
    
    def scrape(self, out_file):
        pass

class JalScraper(Scraper):

    def __init__(self):
        super().__init__()
        self.url = scrap_dict["jal"]
    
    def scrape(self, out_file):
        self.browser.get(self.url)
        # set the dep ap
        dep_ap_select = self.browser.find_element(By.ID, "dep")
        select_dep = Select(dep_ap_select)
        select_dep.select_by_value(self.from_ap)
        # set the dest ap
        dest_ap_select = self.browser.find_element(By.ID, "arr")
        select_dest = Select(dest_ap_select)
        select_dest.select_by_value(self.to_ap)
        # do search
        search_btn = self.browser.find_element(By.XPATH, '//*[@id="wrapper"]/div/div/div[2]/div[2]/div/div/div[2]/div/div[4]/div/div/div[1]/div/div/div/div/div/form/div[2]/ul/li[3]/input[1]')
        search_btn.click()

        # save the result
        with open(out_file, "w") as f:
            f.write(self.browser.page_source)
        
        input()

if __name__ == "__main__":
    jal_scraper = JalScraper()
    jal_scraper.set_from("HND")
    jal_scraper.set_to("CTS")
    jal_scraper.scrape("test_jal.txt")
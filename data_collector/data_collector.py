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

    class FlightInfo(object):
        """各便の情報を格納するクラス。"""
        def __init__(self,
                    flight_number,
                    dep_ap,
                    arr_ap,
                    dep_time,
                    arr_time,
                    act_dep_time,
                    act_arr_time):
            self.flight_number = flight_number
            self.dep_ap = dep_ap
            self.arr_ap = arr_ap
            self.dep_time = dep_time
            self.arr_time = arr_time
            self.act_dep_time = act_dep_time
            self.act_arr_time = act_arr_time

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

        JalScraper.parse_result(self.browser.page_source)
    
    @classmethod
    def parse_result(cls, page_source) -> list:
        '''JALの運航案内のページの結果から、各便の定刻、実際の出発時刻、到着時刻を取得する。
        
        dataのサンプルページはtest_jal.txtを参照。
        return: list(FlightInfo)'''

        parsed_flights_info = []
        soup = BeautifulSoup(page_source, "html.parser")
        # 出発地を取得する。
        # 出発地はid="JA_FSDepAirportArea"を持つdivの子要素のうち、
        # class="col_txt-btmを持つdiv elementのvalueで取得できる。
        dep_ap = soup.find("div", id="JS_FSDepAirportArea").find("div", class_="col_txt-btm").text
        # 到着地を取得する。
        # 到着地はid="JA_FSArrAirportArea"を持つdivの子要素のうち、
        # class="col_txt-btmを持つdiv elementのvalueで取得できる。
        arr_ap = soup.find("div", id="JS_FSArrAirportArea").find("div", class_="col_txt-btm").text

        # 各便の情報を取得する。
        # 各便の情報はclass="JS_FSDetailTable"を持つtbodyの子要素のtrで取得できる。
        flight_all_info = soup.find("tbody", class_="JS_FSDetailTable").find_all("tr")
        for flight_info in flight_all_info:
            # get flight_number
            # you can get flight_number using span element whose class is "flight_number_txt"
            flight_number = flight_info.find("span", class_="flight_number_txt").text
            # get original dep time and arr time
            # you can get original dep time and arr time using seconde td element
            dep_time = flight_info.find_all("td")[1].text.split("—")[0].strip()
            arr_time = flight_info.find_all("td")[1].text.split("—")[1].strip()
            # get actual dep time
            # you can get actual dep time using third td element
            act_dep_time = flight_info.find_all("td")[2].text
            # get actual arr time
            # you can get actual arr time using forth td element
            act_arr_time = flight_info.find_all("td")[3].text
            parsed_flights_info.append(Scraper.FlightInfo(flight_number, dep_ap, arr_ap, dep_time, arr_time, act_dep_time, act_arr_time))
        
        return parsed_flights_info

if __name__ == "__main__":
    jal_scraper = JalScraper()
    jal_scraper.set_from("HND")
    jal_scraper.set_to("CTS")
    jal_scraper.scrape("test_jal.txt")
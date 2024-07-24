import logging
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import ap_dict
import re
from abc import abstractmethod

# set list of scrap
scrap_dict = {"jal" : "https://www.jal.co.jp/flight-status/dom/",
              "ana" : "https://www.ana.co.jp/fs/dom/jp/",
              "ado" : "https://www.airdo.jp/flight-status/",
              "fda" : "https://www.fujidream.co.jp/sp/flight_info/",
              "sky" : "https://www.res.skymark.co.jp/mercury/fis/flight_announce_i18n",
              "tok" : "https://tokiair.com",
              }

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

class Scraper(object):
    """Scrapeするための抽象クラス。実装は各航空会社ごとに行う。"""

    def __init__(self):
        # ブラウザを初期化する。
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--single-process")
        self.options.add_argument("--ignore-certificate-errors")
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
    
    def set_date(self, date:any):
        self.date = date
    
    @abstractmethod
    def file_name_header() -> str:
        pass

    def scrape(self, out_file):
        pass

    class FlightInfo(object):
        """各便の情報を格納するクラス。"""
        def __init__(self,
                    flight_date,
                    flight_number,
                    dep_ap,
                    arr_ap,
                    dep_time,
                    arr_time,
                    act_dep_time,
                    act_arr_time,
                    **kwargs):
            self.flight_date = flight_date
            self.flight_number = flight_number
            self.dep_ap = dep_ap
            self.arr_ap = arr_ap
            self.dep_time = dep_time
            self.arr_time = arr_time
            self.act_dep_time = act_dep_time
            self.act_arr_time = act_arr_time
            self.kwargs = kwargs
        
        def to_csv(self, header=True):
            '''各便の情報をcsv形式で返す。
            
            @param header: bool, default=True'''
            csv = ""
            kwargs_key = ",".join([f"{k}" for k in self.kwargs.keys()])
            kwgars_value = ",".join([f"{v}" for v in self.kwargs.values()])
            if header:
                csv = "flight_date,flight_number,dep_ap,arr_ap,dep_time,arr_time,act_dep_time,act_arr_time," + kwargs_key + "\n"
            csv = csv + f"{self.flight_date},{self.flight_number},{self.dep_ap},{self.arr_ap},{self.dep_time},{self.arr_time},{self.act_dep_time},{self.act_arr_time},"+kwgars_value

            return csv

class JalScraper(Scraper):
    '''JALの運航情報を取得するためのクラス。
    
    JALの運航状況は以下のURLに対して出発空港、到着空港、日付を指定することで取得できる。
    https://www.jal.co.jp/flight-status/dom/?FsBtn=route&DATEFLG=1&DPORT=CTS&APORT=HND&DATEFLG_temp=1&DATEFLG_temp='''

    def __init__(self):
        super().__init__()
        self.url = scrap_dict["jal"]
    
    def scrape(self, out_file):
        assert self.from_ap is not None, "出発地を設定してください。"
        assert self.to_ap is not None, "到着地を設定してください。"
        if self.date is None:
            self.date = "today"
        
        if self.date == "today":
            date_flg = ""
        elif self.date == "prev":
            date_flg = "1"
        elif self.date == "next":
            date_flg = "2"
        url = f'{self.url}?FsBtn=route&DATEFLG={date_flg}&DPORT={self.from_ap}&APORT={self.to_ap}&DATEFLG_temp=1&DATEFLG_temp='
        self.browser.get(url)
        self.browser.implicitly_wait(20)

        # this is fake object to wait until the page is loaded
        try:
            element = self.browser.find_element(By.XPATH, '//*[@id="JS_FSDetailArea"]/tbody/tr[1]')
        except:
            logging.error(f"timeout jal {self.from_ap} to {self.to_ap} on {self.date}")
            

        # save as html
        with open("jal.html", "w") as f:
            f.write(self.browser.page_source)

        parsed_list = JalScraper.parse_result(self.browser.page_source)

        # save the result to csv
        with open(out_file, "a") as f:
            for flight_info in parsed_list:
                f.write(flight_info.to_csv(header=False))
                f.write("\n")
    
    def file_name_header(self) -> str:
        return "jal"
    
    @classmethod
    def parse_result(cls, page_source) -> list:
        '''JALの運航案内のページの結果から、各便の定刻、実際の出発時刻、到着時刻を取得する。
        
        dataのサンプルページはtest_jal.txtを参照。
        return: list(FlightInfo)'''

        parsed_flights_info = []
        soup = BeautifulSoup(page_source, "html.parser")
        # 運航日を取得する。
        # 運航日はclass="information-date JS_FSDate"を持つdiv elementのvalueで取得できる。
        # 曜日を含めずに抽出する。
        flight_date_element = soup.find("div", class_="information-date JS_FSDate")
        if flight_date_element is not None:
            flight_date = flight_date_element.text.split("（")[0]
        else:
            flight_date = "ERROR" 
        # 出発地を取得する。
        # 出発地はid="JA_FSDepAirportArea"を持つdivの子要素のうち、
        # class="col_txt-btmを持つdiv elementのvalueで取得できる。
        dep_ap_element = soup.find("div", id="JS_FSDepAirportArea").find("div", class_="col_txt-btm")
        if dep_ap_element is not None:
            dep_ap = dep_ap_element.text
        else:
            dep_ap = "ERROR"
        # 到着地を取得する。
        # 到着地はid="JA_FSArrAirportArea"を持つdivの子要素のうち、
        # class="col_txt-btmを持つdiv elementのvalueで取得できる。
        arr_ap_element = soup.find("div", id="JS_FSArrAirportArea").find("div", class_="col_txt-btm")
        if arr_ap_element is not None:
            arr_ap = arr_ap_element.text
        else:
            arr_ap = "ERROR"

        # 各便の情報を取得する。
        # 各便の情報はclass="JS_FSDetailTable"を持つtbodyの子要素のtrで取得できる。
        flight_all_info = soup.find("tbody", class_="JS_FSDetailTable").find_all("tr")
        for flight_info in flight_all_info:
            # get flight_number
            # you can get flight_number using span element whose class is "flight_number_txt"
            flight_number_element = flight_info.find("span", class_="flight_number_txt")
            if flight_number_element is not None:
                flight_number = flight_number_element.text
            else:
                flight_number = "ERROR"
            # get original dep time and arr time
            # you can get original dep time and arr time using seconde td element
            time_element = flight_info.find_all("td")
            if len(time_element) > 1 and time_element[1] is not None :
                try:
                    dep_time = time_element[1].text.split("—")[0].strip()
                    arr_time = time_element[1].text.split("—")[1].strip()
                except IndexError:
                    dep_time = "ERROR"
                    arr_time = "ERROR"
            else:
                dep_time = "ERROR"
                arr_time = "ERROR"
            # get actual dep time
            # you can get actual dep time using third td element
            try:
                act_dep_time = flight_info.find_all("td")[2].text.split()[0]
                dep_other = "".join(flight_info.find_all("td")[2].text.split()[1:]).strip().replace("\n", "")
            except IndexError:
                act_dep_time = "ERROR"
                dep_other = "ERROR"
            # get actual arr time
            # you can get actual arr time using forth td element
            try:
                act_arr_time = flight_info.find_all("td")[3].text.split()[0]
                arr_other = "".join(flight_info.find_all("td")[3].text.split()[1:]).strip().replace("\n", "")
            except IndexError:
                act_arr_time = "ERROR"
                arr_other = "ERROR"
            
            # get info
            try:
                info = flight_info.find_all("td")[4].text.strip().replace("\n", "")
            except IndexError:
                info = "ERROR"
            
            # get other
            try:
                other = flight_info.find_all("td")[5].text.strip().replace("\n", "")
            except IndexError:
                other = "ERROR"
            parsed_flights_info.append(
                Scraper.FlightInfo(
                    flight_date,
                    flight_number,
                    dep_ap,
                    arr_ap,
                    dep_time,
                    arr_time,
                    act_dep_time,
                    act_arr_time,
                    dep_other=dep_other,
                    arr_other=arr_other,
                    info=info,
                    other=other))
        
        return parsed_flights_info

class AnaScraper(Scraper):
    '''ANAの運航情報を取得するためのクラス。

    ANAの運航状況は以下のURLに対して出発空港、到着空港、日付を指定することで取得できる。
    https://www.ana.co.jp/fs/dom/jp/result.html?mode=1&depAirportSelect=ITM&txtDepAirport=%E5%A4%A7%E9%98%AA%28%E4%BC%8A%E4%B8%B9%29&arrAirportSelect=AOJ&txtArrAirport=%E9%9D%92%E6%A3%AE&requestDate=20240215
    '''
    def __init__(self):
        # launch AnaScraper as headless mode.
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--single-process")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--homedir=/tmp")
        self.options.add_argument("--headless")
        self.options.add_argument(
            f'user-agent=mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/77.0.3865.120 safari/537.36')
        self.browser = webdriver.Chrome(options=self.options)
        self.url = ""
        
        self.url = scrap_dict["ana"]
    
    def scrape(self, out_file):
        assert self.from_ap is not None, "出発地を設定してください。"
        assert self.to_ap is not None, "到着地を設定してください。"
        if self.date is None:
            self.date = "today"
        
        from_ap_jp = ap_dict.decode(self.from_ap, company="ana")
        from_ap_jp = ap_dict.decode(self.from_ap, company="ana")
        self.date = date_formatter(self.date, "%Y%m%d")

        url = f"{self.url}result.html?mode=1&depAirportSelect={self.from_ap}&txtDepAirport={from_ap_jp}&arrAirportSelect={self.to_ap}&txtArrAirport={self.to_ap}&requestDate={self.date}"

        self.browser.get(url)

        # save as html
        with open("ana.html", "w") as f:
            f.write(self.browser.page_source)

        parsed_list = AnaScraper.parse_result(self.browser.page_source)
        self.inject_year(parsed_list)
        
        with open(out_file, "a") as f:
            for flight_info in parsed_list:
                f.write(flight_info.to_csv(header=False))
                f.write("\n")

    def file_name_header(self) -> str:
        return "ana"
    
    def inject_year(self, parsed_list:list[Scraper.FlightInfo]) -> list[Scraper.FlightInfo]:
        for flight_info in parsed_list:
            flight_info.flight_date = self.date[0:4] + "年" + flight_info.flight_date
        return parsed_list
    
    @classmethod
    def parse_result(cls, page_source) -> list[Scraper.FlightInfo]:
        '''ANAの運航案内のページの結果から、各便の定刻、実際の出発時刻、到着時刻を取得する。
        
        dataのサンプルページはtest_ana.txtを参照。
        return: list(FlightInfo)'''

        parsed_flights_info = []
        soup = BeautifulSoup(page_source, "html.parser")
        # 運航日を取得する。
        # 運航日はid="board"を持つspan elementのtextで取得できる。
        # 曜日を含めずに抽出する。
        flight_date_element = soup.find("span", id="Board")
        if flight_date_element is not None:
            flight_date = flight_date_element.text.split("(")[0]
        else:
            flight_date = "ERROR" 
        # 出発地を取得する。
        # 出発地はid="Head_DepAirport"を持つspan elementのtextで取得できる。
        dep_ap_element = soup.find("span", id="Head_DepAirport")
        if dep_ap_element is not None:
            dep_ap = dep_ap_element.text
        else:
            dep_ap = "ERROR"
        # 到着地を取得する。
        # 到着地はid="Head_ArrAirport"を持つspan elementのtextで取得できる。
        arr_ap_element = soup.find("span", id="Head_ArrAirport")
        if arr_ap_element is not None:
            arr_ap = arr_ap_element.text
        else:
            arr_ap = "ERROR"

        # 各便の情報を取得する。
        # 各便の情報はid="resultC"を持つtableのtbody element内にあるclass="fs_detailRow"を持つtrで取得できる。
        flight_all_info = soup.find("table", id="resultC").find("tbody").find_all("tr", class_="fs_dateilRow")
        for flight_info in flight_all_info:
            # get flight_number
            # you can get flight_number using span element 
            flight_number_element = flight_info.find_all("td")[0].find("span")
            if flight_number_element is not None:
                flight_number = flight_number_element.text.replace(" ", "")
            else:
                flight_number = "ERROR"
            # get type of aircraft
            # you can get type of aircraft using second td element
            aircraft_type_element = flight_info.find_all("td")[1].find("span")
            if aircraft_type_element is not None:
                aircraft_type = aircraft_type_element.text
            else:
                aircraft_type = "ERROR"
            # get original dep time and arr time
            original_dep_element = flight_info.find_all("td")[2].find("span", class_="SkdDepTime")
            if original_dep_element is not None:
                dep_time = original_dep_element.text
            else:
                dep_time = "ERROR"
            # get other dep info
            bordingGate_element = flight_info.find_all("td")[3].find("span", class_="BordingGate")
            if bordingGate_element is not None:
                dep_other = "搭乗口" + bordingGate_element.text
            else:
                dep_other = "搭乗口情報なし"
            # get actual dep time
            act_dep_element = flight_info.find_all("td")[4].find("span", class_="ActDep")
            if act_dep_element is not None:
                act_dep_time = act_dep_element.text[:5]
                try:
                    dep_other = act_dep_element.text[5:] + dep_other
                except IndexError:
                    pass
            else:
                act_dep_time = "ERROR"
            
            # get original dep time and arr time
            original_arr_element = flight_info.find_all("td")[5].find("span", class_="SkdArrTime")
            if original_arr_element is not None:
                arr_time = original_arr_element.text
            else:
                arr_time = "ERROR"
            # get actual arr time
            act_arr_element = flight_info.find_all("td")[7].find("span", class_="ActArr")
            if act_arr_element is not None:
                act_arr_time = act_arr_element.text[:5]
                try:
                    arr_other = act_arr_element.text[5:]
                except IndexError:
                    arr_other = "到着other情報なし"
            else:
                act_arr_time = "ERROR"
            
            #get other info
            info_element = flight_info.find_all("td")[8].find("span", class_="Remarks")
            if info_element is not None:
                info = info_element.text
            else:
                info = "ERROR"
            
            #get other info
            other_element = flight_info.find_all("td")[9].find("span", class_="DetailRemarks")
            if other_element is not None:
                other = other_element.text
                # add code share info if exists
                # code share info is in the flight_number_element
                # if the flight_number_element has <a> tag, it means that the flight is code share flight
                # get <img> tag's alt attribute in the <a> tag

                if flight_number_element.find("a") is not None:
                    code_share_info = flight_number_element.find("a").find("img").get("alt")
                    other = other + " " + code_share_info

            else:
                other = "ERROR"
            parsed_flights_info.append(
                Scraper.FlightInfo(
                    flight_date,
                    flight_number,
                    dep_ap,
                    arr_ap,
                    dep_time,
                    arr_time,
                    act_dep_time,
                    act_arr_time,
                    dep_other=dep_other,
                    arr_other=arr_other,
                    info=info,
                    other=other,
                    aircraft_type=aircraft_type))
        return parsed_flights_info
            
class AdoScraper(Scraper):
    '''AIRDOの運航情報を取得するためのクラス。
    
    scrap_dict["ado"]のURLに対して出発地、到着地、日付を指定し結果のページに遷移し、情報を取得する。
    '''
    def __init__(self):
        super().__init__()
        self.url = scrap_dict["ado"]
    
    def scrape(self, out_file):
        assert self.from_ap is not None, "出発地を設定してください。"
        assert self.to_ap is not None, "到着地を設定してください。"
        if self.date is None:
            self.date = "today"
        
        self.date = date_formatter(self.date, "%Y-%m-%d")
        
        self.browser.get(self.url)

        search_form = self.browser.find_element(By.ID, "cus011001Form")

        date_selection = Select(self.browser.find_element(By.ID, "depDate"))
        date_selection.select_by_value(self.date)

        from_selection = Select(self.browser.find_element(By.ID, "depApo"))
        from_selection.select_by_value(self.from_ap)

        to_selection = Select(self.browser.find_element(By.ID, "arrApo"))
        to_selection.select_by_value(self.to_ap)

        search_btn = search_form.find_element(By.TAG_NAME, "button")
        search_btn.click()

        self.browser.implicitly_wait(10)

        # save as html
        with open("ado.html", "w") as f:
            f.write(self.browser.page_source)
        
        parsed_list = AdoScraper.parse_result(self.browser.page_source)

        self.inject_year(parsed_list)

        with open(out_file, "a") as f:
            for flight_info in parsed_list:
                f.write(flight_info.to_csv(header=False))
                f.write("\n")
        
        # get inverse flights
        inverse_btn = self.browser.find_element(By.ID, "cus011002Form").find_element(By.TAG_NAME, "a").click()
        self.browser.implicitly_wait(10)
        parsed_list = AdoScraper.parse_result(self.browser.page_source)
        self.inject_year(parsed_list)
        
        with open(out_file, "a") as f:
            for flight_info in parsed_list:
                f.write(flight_info.to_csv(header=False))
                f.write("\n")
    
    def file_name_header(self) -> str:
        return "ado"

    def inject_year(self, parsed_list:list[Scraper.FlightInfo]) -> list[Scraper.FlightInfo]:
        for flight_info in parsed_list:
            flight_info.flight_date = self.date[0:4] + "年" + flight_info.flight_date
        return parsed_list
        
    @classmethod
    def parse_result(cls, page_source) -> list:
        '''AIRDOの運航案内のページの結果から、各便の定刻、実際の出発時刻、到着時刻を取得する。
        
        dataのサンプルページはtest_ado.txtを参照。
        return: list(FlightInfo)'''
        parsed_flights_info = []
        soup = BeautifulSoup(page_source, "html.parser")
        #運航情報を取得する。
        #運航情報はid="cur011002Form"を持つform element内にある。
        todays_all_flights = soup.find("form", id="cus011002Form")
        #運航日を取得する。
        #運航日はclass="dep-date"を持つspan elementのtextで取得できる。
        flight_date_element =todays_all_flights.find("span", class_="dep-date")
        if flight_date_element is not None:
            flight_date = flight_date_element.text
        else:
            flight_date = "ERROR"
        #出発地,到着地を取得する。
        dep_and_arr_ap_element =todays_all_flights.find("div", class_="section")
        dep_ap_element = dep_and_arr_ap_element.find_all("span")[0]
        if dep_ap_element is not None:
            dep_ap = dep_ap_element.text
        else:
            dep_ap = "ERROR"
        arr_ap_element = dep_and_arr_ap_element.find_all("span")[1]
        if arr_ap_element is not None:
            arr_ap = arr_ap_element.text
        else:
            arr_ap = "ERROR"

        #各便の情報を取得する。
        #各便の情報はid=tableIDを持つtable element内にある。
        flight_all_info =todays_all_flights.find("table", id="tableID").find("tbody").find_all("tr")
        for flight_info in flight_all_info:
            #便名を取得する。
            flight_number:str = flight_info.find_all("td")[0].text
            flight_number = flight_number.replace("\n", "").replace(" ","")
            #搭乗口を取得する。
            onboard_gate = flight_info.find_all("td")[1].text
            onboard_gate = onboard_gate.replace("\n", "").replace(" ","")
            #出発定刻を取得]する。
            scheduled_dep_time = flight_info.find_all("td")[2].text
            scheduled_dep_time = scheduled_dep_time.replace("\n", "").replace(" ","")
            #出発実時刻を取得する。
            actual_dep_time = flight_info.find_all("td")[3].text.split()[0]
            actual_dep_time = actual_dep_time.replace("\n", "").replace(" ","")
            #出発状況を取得する。
            dep_info_span = flight_info.find_all("td")[3].find_all("span")
            if len(dep_info_span) > 1:
                dep_info = dep_info_span[1].text
                dep_info = dep_info.replace("\n", "").replace(" ","")
            else:
                dep_info = "ERROR"
            #到着定刻を取得する。
            scheduled_arr_time = flight_info.find_all("td")[4].text
            scheduled_arr_time = scheduled_arr_time.replace("\n", "").replace(" ","")
            #到着実時刻を取得する。
            actual_arr_time = flight_info.find_all("td")[5].text.split()[0]
            actual_arr_time = actual_arr_time.replace("\n", "").replace(" ","")
            #到着状況を取得する。
            arr_info_span = flight_info.find_all("td")[5].find_all("span")
            if len(arr_info_span) > 1:
                arr_info = arr_info_span[1].text
                arr_info = arr_info.replace("\n", "").replace(" ","")
            else:
                arr_info = "ERROR"
            #出口を取得する。
            exit = flight_info.find_all("td")[6].text
            exit = exit.replace("\n", "").replace(" ","")
            #備考を取得する。
            remarks = flight_info.find_all("td")[7].text
            remarks = remarks.replace("\n", "").replace(" ","")
            # i want to make clear code above


            parsed_flights_info.append(
                Scraper.FlightInfo(
                    flight_date,
                    flight_number,
                    dep_ap,
                    arr_ap,
                    scheduled_dep_time,
                    scheduled_arr_time,
                    actual_dep_time,
                    actual_arr_time,
                    dep_other=dep_info + onboard_gate,
                    arr_info=arr_info + exit,
                    info=remarks))
        return parsed_flights_info


class SkyScraper(Scraper):
    '''スカイマークの運航情報を取得するためのクラス。
    
    '''
    def __init__(self):
        super().__init__()
        self.url = scrap_dict["sky"]
    
    def scrape(self, out_file):
        assert self.from_ap is not None, "出発地を設定してください。"
        assert self.to_ap is not None, "到着地を設定してください。"
        if self.date is None:
            self.date = "today"
        
        if self.date == "prev":
            date_flg = "-1"
        elif self.date == "today":
            date_flg = "0"
        elif self.date == "next":
            date_flg = "1"
        
        self.url = scrap_dict["sky"]
        self.browser.get(self.url)

        # set route
        route_selection = Select(self.browser.find_element(By.NAME, "airline"))
        route_selection.select_by_value(str(SkyScraper.sky_root_coder(self.from_ap, self.to_ap)))

        #set date
        date_selection = Select(self.browser.find_element(By.NAME, "select_day"))
        date_selection.select_by_value(date_flg)

        #search
        send_btn = self.browser.find_element(By.XPATH, "//input[@value='発着案内']")
        send_btn.click()

        self.browser.implicitly_wait(10)

        #save as html
        with open("sky.html", "w") as f:
            f.write(self.browser.page_source)
        
        parsed_list = SkyScraper.parse_result(self.browser.page_source)

        #save the result to csv
        with open(out_file, "a") as f:
            for flight_info in parsed_list:
                f.write(flight_info.to_csv(header=False))
                f.write("\n")
    
    def file_name_header(self) -> str:
        return "sky"
        
    @classmethod
    def parse_result(cls, page_source) -> list:
        '''スカイマークの運航案内のページの結果から、各便の定刻、実際の出発時刻、到着時刻を取得する。
        
        dataのサンプルページはtest_sky.txtを参照。
        return: list(FlightInfo)'''
        parsed_flights_info = []
        soup = BeautifulSoup(page_source, "html.parser")
        #運航日を取得する。
        #運航日はclass="md"を持つspan elementのtextで取得できる。
        flight_date_element = soup.find("span", class_="md")
        if flight_date_element is not None:
            flight_date = flight_date_element.text.replace("\n", "").replace(" ","")
        else:
            flight_date = "ERROR"
        #出発地を取得する。
        #出発地はclass="da"を持つspan elementのtextで取得できる。
        dep_ap_element = soup.find("span", class_="da")
        if dep_ap_element is not None:
            dep_ap = dep_ap_element.text.replace("\n", "").replace(" ","").replace("出発地：", "")
        else:
            dep_ap = "ERROR"
        #到着地を取得する。
        #到着地はclass="aa"を持つspan elementのtextで取得できる。
        arr_ap_element = soup.find("span", class_="aa")
        if arr_ap_element is not None:
            arr_ap = arr_ap_element.text.replace("\n", "").replace(" ","").replace("到着地：", "")
        else:
            arr_ap = "ERROR"
        #各便の情報を取得する。
        #各便の情報はid="infotb"を持つdiv element内にある。
        flights_info = soup.find("div", id="infotb").find_all("tr")
        for flight_info in flights_info:
            #flight_infoに<td>が含まれているか確認する。
            if flight_info.find("td") is None:
                continue
            #便名を取得する。
            flight_number = flight_info.find_all("td")[0].text
            #定刻を取得する。
            scheduled_dep_time = flight_info.find_all("td")[2].text
            #実時刻を取得する。
            actual_dep_time_search = re.search(r"[0-9]{2}:[0-9]{2}",flight_info.find_all("td")[3].text)
            if actual_dep_time_search is not None:
                actual_dep_time = actual_dep_time_search[0]
            else:
                actual_dep_time = "ERROR"
            dep_info_span = flight_info.find_all("td")[3].find("span")
            if dep_info_span is not None:
                dep_info = dep_info_span.text.replace("\n", "").replace(" ","")
            else:
                dep_info = flight_info.find_all("td")[3].text.replace("\xa0", "").replace("\n", "").replace(" ","")
            scheduled_arr_time = flight_info.find_all("td")[5].text
            actual_arr_time_search = re.search(r"[0-9]{2}:[0-9]{2}",flight_info.find_all("td")[6].text)
            if actual_arr_time_search is not None:
                actual_arr_time = actual_arr_time_search[0]
            else:
                actual_arr_time = "ERROR"
            arr_info_span = flight_info.find_all("td")[6].find("span")
            if arr_info_span is not None:
                arr_info = arr_info_span.text.replace("\n", "").replace(" ","")
            else:
                arr_info = flight_info.find_all("td")[6].text.replace("\xa0", "").replace("\n", "").replace(" ","")
            other_info = flight_info.find_all("td")[7].text.replace("\xa0", "").replace("\n", "").replace(" ","")

            #状況を取得する。
            parsed_flights_info.append(
                Scraper.FlightInfo(
                    flight_date,
                    flight_number,
                    dep_ap,
                    arr_ap,
                    scheduled_dep_time,
                    scheduled_arr_time,
                    actual_dep_time,
                    actual_arr_time,
                    dep_other=dep_info,
                    arr_other=arr_info,
                    info=other_info))
        return parsed_flights_info
    

        
    @classmethod
    def sky_root_coder(cls, from_ap, to_ap):
        '''スカイマークの運航情報を取得するためのURLを生成する。
        
        @param from_ap: str, 出発地の空港コード
        @param to_ap: str, 到着地の空港コード
        return: str, URL'''
        if from_ap == "HND":
            if to_ap == "CTS":
                return 57
            elif to_ap == "FUK":
                return 34
            elif to_ap == "OKA":
                return 52
        if from_ap == "CTS":
            if to_ap == "HND":
                return 58
            elif to_ap == "FUK":
                return 132
            elif to_ap == "NGO":
                return 104
        if from_ap == "FUK":
            if to_ap == "HND":
                return 49
            elif to_ap == "CTS":
                return 131
        if from_ap == "NGO":
            if to_ap == "CTS":
                return 100
        if from_ap == "OKA":
            if to_ap == "HND":
                return 53

class TokScraper(Scraper):
    '''TOKIAIRの運航情報を取得するためのクラス。
    
    '''
    def __init__(self):
        super().__init__()
        self.url = scrap_dict["tok"]
    
    def file_name_header() -> str:
        return "tok"

    def scrape(self, out_file):
        pass


def date_formatter(date, format):
    import datetime
    if date == "today":
        date = datetime.date.today().strftime(format)
    elif date == "prev":
        date = (datetime.date.today() - datetime.timedelta(days=1)).strftime(format)
    elif date == "next":
        date = (datetime.date.today() + datetime.timedelta(days=1)).strftime(format)
    return date
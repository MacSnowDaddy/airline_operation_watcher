from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import ap_dict

# set list of scrap
scrap_dict = {"jal" : "https://www.jal.co.jp/flight-status/dom/",
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
    
    def set_date(self, date:any):
        self.date = date
    
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

        # save as html
        with open("jal.html", "w") as f:
            f.write(self.browser.page_source)

        parsed_list = JalScraper.parse_result(self.browser.page_source)

        # save the result to csv
        with open(out_file, "a") as f:
            for flight_info in parsed_list:
                f.write(flight_info.to_csv(header=False))
                f.write("\n")
    
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
            # get actual arr time
            # you can get actual arr time using forth td element
            try:
                act_arr_time = flight_info.find_all("td")[3].text.split()[0]
                arr_other = "".join(flight_info.find_all("td")[3].text.split()[1:]).strip().replace("\n", "")
            except IndexError:
                act_arr_time = "ERROR"
            
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
        super().__init__()
        self.url = scrap_dict["ana"]
    
    def scrape(self, out_file):
        assert self.from_ap is not None, "出発地を設定してください。"
        assert self.to_ap is not None, "到着地を設定してください。"
        if self.date is None:
            self.date = "today"
        
        from_ap_jp = ap_dict.decode(self.from_ap)
        to_ap_jp = ap_dict.decode(self.to_ap)
        import datetime
        if self.date == "today":
            self.date = datetime.date.today().strftime("%Y%m%d")
        elif self.date == "prev":
            self.date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        elif self.date == "next":
            self.date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y%m%d")

        url = f"{self.url}result.html?mode=1&depAirportSelect={self.from_ap}&txtDepAirport={from_ap_jp}&arrAirportSelect={self.to_ap}&txtArrAirport={to_ap_jp}&requestDate={self.date}"

        self.browser.get(url)

        # save as html
        with open("ana.html", "w") as f:
            f.write(self.browser.page_source)

        parsed_list = AnaScraper.parse_result(self.browser.page_source)

        with open(out_file, "a") as f:
            for flight_info in parsed_list:
                f.write(flight_info.to_csv(header=False))
                f.write("\n")

    
    @classmethod
    def parse_result(cls, page_source) -> list:
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
                    other=other))
        return parsed_flights_info
            


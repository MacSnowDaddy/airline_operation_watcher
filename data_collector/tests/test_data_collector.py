import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_collector import JalScraper
from data_collector import AnaScraper
from data_collector import AdoScraper
from data_collector import SkyScraper

class TestFlightInfo(unittest.TestCase):
    def setUp(self):
        pass

    def test_to_csv(self):
        flight_info = JalScraper.FlightInfo("2024年1月17日", "JAL141", "東京（羽田）", "青森", "7:40", "9:05", "7:44", "9:01", dep_other="出発済み（搭乗口34）",arr_other="到着済み", info="出発遅延", other="使用する飛行機の到着遅れのため出発に遅延が生じています。")
        csv = flight_info.to_csv()
        self.assertEqual(csv, "flight_date,flight_number,dep_ap,arr_ap,dep_time,arr_time,act_dep_time,act_arr_time,dep_other,arr_other,info,other\n2024年1月17日,JAL141,東京（羽田）,青森,7:40,9:05,7:44,9:01,出発済み（搭乗口34）,到着済み,出発遅延,使用する飛行機の到着遅れのため出発に遅延が生じています。")
        csv = flight_info.to_csv(header=False)
        self.assertEqual(csv, "2024年1月17日,JAL141,東京（羽田）,青森,7:40,9:05,7:44,9:01,出発済み（搭乗口34）,到着済み,出発遅延,使用する飛行機の到着遅れのため出発に遅延が生じています。")


class TestJalScraper(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_result(self):
        print(os.path.dirname(__file__))
        # Read the HTML content from test_jal.txt
        with open(os.path.join(os.path.dirname(__file__), 'test_jal.txt'), 'r') as file:
            html_content = file.read()
        parsed_list = JalScraper.parse_result(html_content)

        self.assertEqual(len(parsed_list), 6)
        self.assertEqual(parsed_list[0].flight_date, "2024年1月17日")
        self.assertEqual(parsed_list[0].flight_number, "JAL141")
        self.assertEqual(parsed_list[0].dep_ap, "東京（羽田）")
        self.assertEqual(parsed_list[0].arr_ap, "青森")
        self.assertEqual(parsed_list[0].dep_time, "7:40")
        self.assertEqual(parsed_list[0].arr_time, "9:05")
        self.assertEqual(parsed_list[0].act_dep_time, "7:44")
        self.assertEqual(parsed_list[0].act_arr_time, "9:01")
        csv_expected = "2024年1月17日,JAL141,東京（羽田）,青森,7:40,9:05,7:44,9:01,出発済み（搭乗口34）,到着済み,出発遅延,使用する飛行機の到着遅れのため出発に遅延が生じています。"
        self.assertEqual(parsed_list[0].to_csv(header=False), csv_expected)
        self.assertEqual(parsed_list[5].act_arr_time, "ERROR")

class TestAnaScraper(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_result(self):
        print(os.path.dirname(__file__))
        # Read the HTML content from test_jal.txt
        with open(os.path.join(os.path.dirname(__file__), 'test_ana.txt'), 'r') as file:
            html_content = file.read()
        parsed_list = AnaScraper.parse_result(html_content)

        self.assertEqual(len(parsed_list), 3)
        self.assertEqual(parsed_list[0].flight_date, "2月15日")
        self.assertEqual(parsed_list[0].dep_ap, "大阪(伊丹)")
        self.assertEqual(parsed_list[0].arr_ap, "青森")
        self.assertEqual(parsed_list[0].flight_number, "ANA1851")
        self.assertEqual(parsed_list[0].dep_time, "09:00")
        self.assertEqual(parsed_list[0].arr_time, "10:45")
        self.assertEqual(parsed_list[0].act_dep_time, "09:01")
        self.assertEqual(parsed_list[0].act_arr_time, "10:38")
        csv_expected = "2月15日,ANA1851,大阪(伊丹),青森,09:00,10:45,09:01,10:38,出発済み搭乗口13,到着済み,-,-,Q84"
        self.assertEqual(parsed_list[0].to_csv(header=False), csv_expected)
        self.assertEqual(parsed_list[2].act_arr_time, "-")

class TestAdoSelenium(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_result(self):
        print(os.path.dirname(__file__))
        # Read the HTML content from test_jal.txt
        with open(os.path.join(os.path.dirname(__file__), 'test_ado.txt'), 'r') as file:
            html_content = file.read()
        print(html_content)
        parsed_list = AdoScraper.parse_result(html_content)

        self.assertEqual(len(parsed_list), 13)
        self.assertEqual(parsed_list[0].flight_date, "4月10日(水)")
        self.assertEqual(parsed_list[0].dep_ap, "札幌(新千歳)")
        self.assertEqual(parsed_list[0].arr_ap, "東京(羽田)")
        self.assertEqual(parsed_list[0].flight_number, "ADO12")
        self.assertEqual(parsed_list[0].dep_time, "08:00")
        self.assertEqual(parsed_list[0].arr_time, "09:35")
        self.assertEqual(parsed_list[0].act_dep_time, "07:58")
        self.assertEqual(parsed_list[0].act_arr_time, "09:27")
        csv_expected = "4月10日(水),ADO12,札幌(新千歳),東京(羽田),08:00,09:35,07:58,09:27,出発済み10,到着済み1・2・3(第2ターミナル),-"
        self.assertEqual(parsed_list[0].to_csv(header=False), csv_expected)


class TestSkyScraper(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_result(self):
        print(os.path.dirname(__file__))
        # Read the HTML content from test_jal.txt
        with open(os.path.join(os.path.dirname(__file__), 'test_sky.txt'), 'r') as file:
            html_content = file.read()
        parsed_list = SkyScraper.parse_result(html_content)

        self.assertEqual(len(parsed_list), 9)
        self.assertEqual(parsed_list[0].flight_date, "2024年4月13日(土)")
        self.assertEqual(parsed_list[0].dep_ap, "羽田")
        self.assertEqual(parsed_list[0].arr_ap, "新千歳")
        self.assertEqual(parsed_list[0].flight_number, "SKY703")
        self.assertEqual(parsed_list[0].dep_time, "06:45")
        self.assertEqual(parsed_list[0].arr_time, "08:20")
        self.assertEqual(parsed_list[0].act_dep_time, "06:44")
        self.assertEqual(parsed_list[0].act_arr_time, "08:20")
        csv_expected = "2024年4月13日(土),SKY703,羽田,新千歳,06:45,08:20,06:44,08:20,出発済,到着済,"
        self.assertEqual(parsed_list[0].to_csv(header=False), csv_expected)



if __name__ == "__main__":
    unittest.main()
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_collector import JalScraper

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
        self.assertEqual(parsed_list[0].flight_number, "JAL141")
        self.assertEqual(parsed_list[0].dep_ap, "東京（羽田）")
        self.assertEqual(parsed_list[0].arr_ap, "青森")
        self.assertEqual(parsed_list[0].dep_time, "7:40")
        self.assertEqual(parsed_list[0].arr_time, "9:05")
        self.assertEqual(parsed_list[0].act_dep_time, "7:44")
        self.assertEqual(parsed_list[0].act_arr_time, "9:01")


if __name__ == "__main__":
    unittest.main()
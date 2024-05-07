import unittest
import os
import shutil
import datetime
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_collector_caller import move_to_data_dir
from data_collector_caller import first_last_day_of_week


class TestFirstAndLastDayOfWeek(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self) -> None:
        pass

    def test_first_and_last_day_of_week(self):
        #incase of Sunday
        date = datetime.datetime(2024, 4, 21)
        first_day_of_week, last_day_of_week = first_last_day_of_week(date)
        self.assertEqual(first_day_of_week, datetime.datetime(2024, 4, 21))
        self.assertEqual(last_day_of_week, datetime.datetime(2024, 4, 27))

        #incase of Monday
        date = datetime.datetime(2024, 4, 22)
        first_day_of_week, last_day_of_week = first_last_day_of_week(date)
        self.assertEqual(first_day_of_week, datetime.datetime(2024, 4, 21))
        self.assertEqual(last_day_of_week, datetime.datetime(2024, 4, 27))

        #incase of Saturday
        date = datetime.datetime(2024, 4, 27)
        first_day_of_week, last_day_of_week = first_last_day_of_week(date)
        self.assertEqual(first_day_of_week, datetime.datetime(2024, 4, 21))
        self.assertEqual(last_day_of_week, datetime.datetime(2024, 4, 27))
# class TestMoveToDataDir(unittest.TestCase):
#     def setUp(self):
#         self.test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_dir')
#         os.makedirs(self.test_dir, exist_ok=True)
#         self.test_file = os.path.join(self.test_dir, 'abc20220101.csv')
#         with open(self.test_file, 'w') as f:
#             f.write('test')

#     def tearDown(self):
#         shutil.rmtree(self.test_dir)

#     def test_move_to_data_dir(self):
#         move_to_data_dir('abc20220101.csv')
#         self.assertFalse(os.path.exists(self.test_file))
#         self.assertTrue(os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'abc', 'analyze_target', '20220101-0107', 'abc20220101.csv')))

#     def test_move_to_data_dir_empty_filename(self):
#         move_to_data_dir('')
#         self.assertTrue(os.path.exists(self.test_file))  # file should not be moved

#     def test_move_to_data_dir_new_directory(self):
#         new_file = os.path.join(self.test_dir, 'abc20220108.csv')
#         with open(new_file, 'w') as f:
#             f.write('test')
#         move_to_data_dir('abc20220108.csv')
#         self.assertFalse(os.path.exists(new_file))
#         self.assertTrue(os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'abc', 'analyze_target', '20220108-0114', 'abc20220108.csv')))

if __name__ == "__main__":
    unittest.main()
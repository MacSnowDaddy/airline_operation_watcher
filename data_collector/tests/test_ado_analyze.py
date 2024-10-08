import datetime
import unittest
import sys, os
from unittest.mock import patch
#import parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pandas as pd
import ado_analyze
from ado_analyze import Ado_analyzer


class TestAdoAnalyzer(unittest.TestCase):

    def setUp(self):
        self.sample_csv = 'sample_ado20991231.csv'
        pass

    def tearDown(self):
        # Add any necessary cleanup code here
        pass

    def test_init(self):
        # Test the __init__ method
        analyzer = Ado_analyzer([os.path.join(os.path.dirname(__file__), f'./{self.sample_csv}')])

        df = analyzer.df

        self.assertIsNotNone(df)
        self.assertEqual(len(df), 24)
    
    def test_init_with_empty_files_will_makes_len0_df(self):
        analyzer = Ado_analyzer([])

        df = analyzer.df

        self.assertIsNotNone(df)
        self.assertEqual(len(df), 0)

    def test_drop_codeshare(self):
        # Test the drop_codeshare method
        analyzer = Ado_analyzer([os.path.join(os.path.dirname(__file__), f'./{self.sample_csv}')])

        analyzer.drop_codeshare()

        df = analyzer.df
        self.assertEqual(len(df), 24)
    
    def test_drop_codeshare_does_not_change_when_called_twice(self):
        # Test the drop_codeshare method
        analyzer = Ado_analyzer([os.path.join(os.path.dirname(__file__), f'./{self.sample_csv}')])

        analyzer.drop_codeshare()
        analyzer.drop_codeshare()

        df = analyzer.df
        self.assertEqual(len(df), 24)

    def test_edit_date(self):
        # Test the edit_date function
        df = pd.DataFrame({'date': ['2022年01月01日', '2022年01月02日', '2022年01月03日']})
        expected_df = pd.DataFrame({'date': ['2022/01/01', '2022/01/02', '2022/01/03']})
        expected_df['date'] = pd.to_datetime(expected_df['date'])

        df = ado_analyze._edit_date(df)

        self.assertEqual(df['date'].tolist(), expected_df['date'].tolist())

    def test_add_delay_column(self):
        # Add your test code here
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), self.sample_csv), header=None)
        df.columns = ['date', 'name', 'from', 'to', 'schedule_dep', 'schedule_arr', 'actual_dep', 'actual_arr', 'dep_info', 'arr_info', 'info_other']
        df = ado_analyze._edit_date(df)
        df = ado_analyze._add_delay_column(df)
        self.assertEqual(df[df['name'] == 'ADO28']['dep_delay'].values[0], -5)
        self.assertEqual(df[df['name'] == 'ADO28']['arr_delay'].values[0], -10)
        self.assertEqual(df[df['name'] == 'ADO36']['dep_delay'].values[0], 17)
        self.assertEqual(df[df['name'] == 'ADO36']['arr_delay'].values[0], 8)

    def test_time_deltaer_returns_correct_delta_with_two_time_beyond_24h(self):
        # Act
        actual = ado_analyze.time_deltaer("23:55", "24:05")
        expected = datetime.timedelta(minutes=10)

        # Assert
        self.assertEqual(actual, expected)
    
    def test_time_deltaer_returns_correct_delta_with_two_time_earlier_24h(self):
        # Act
        actual = ado_analyze.time_deltaer("23:50", "23:55")
        expected = datetime.timedelta(minutes=5)

        # Assert
        self.assertEqual(actual,expected )
    
    def test_time_deltaer_returns_correct_delta_with_two_time_later_24h(self):
        # Act
        actual = ado_analyze.time_deltaer("24:05", "24:10")
        expected = datetime.timedelta(minutes=5)

        # Assert
        self.assertEqual(actual, expected)

    def test_time_deltaer_returns_correct_delta_with_two_time_beyond_24h_inverse(self):
        # Act
        actual = ado_analyze.time_deltaer("24:05", "23:55")
        expected = datetime.timedelta(minutes=-10)

        # Assert
        self.assertEqual(actual, expected)
    
    def test_time_deltaer_returns_correct_delta_with_two_time_earlier_24h_inverse(self):
        # Act
        actual = ado_analyze.time_deltaer("23:55", "23:50")
        expected = datetime.timedelta(minutes=-5)

        # Assert
        self.assertEqual(actual, expected)
    
    def test_time_deltaer_returns_correct_delta_with_two_time_later_24h_inverse(self):
        # Act
        actual = ado_analyze.time_deltaer("24:10", "24:05")
        expected = datetime.timedelta(minutes=-5)

        # Assert
        self.assertEqual(actual, expected)
    

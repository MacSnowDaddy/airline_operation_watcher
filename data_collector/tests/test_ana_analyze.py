import unittest
import datetime
import sys, os
from unittest.mock import patch
#import parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pandas as pd
import ana_analyze
from ana_analyze import Ana_analyzer


class TestAnaAnalyzer(unittest.TestCase):

    def setUp(self):
        self.sample_csv = 'sample_ana20991231.csv'
        pass

    def tearDown(self):
        # Add any necessary cleanup code here
        pass

    def test_init(self):
        # Test the __init__ method
        analyzer = Ana_analyzer([os.path.join(os.path.dirname(__file__), f'./{self.sample_csv}')])

        df = analyzer.df

        self.assertIsNotNone(df)
        self.assertEqual(len(df), 130)
    
    def test_init_with_empty_files_will_makes_len0_df(self):
        analyzer = Ana_analyzer([])

        df = analyzer.df

        self.assertIsNotNone(df)
        self.assertEqual(len(df), 0)

    def test_drop_codeshare(self):
        # Test the drop_codeshare method
        analyzer = Ana_analyzer([os.path.join(os.path.dirname(__file__), f'./{self.sample_csv}')])

        analyzer.drop_codeshare()

        df = analyzer.df
        self.assertEqual(len(df), 83)
    
    def test_drop_codeshare_does_not_change_when_called_twice(self):
        # Test the drop_codeshare method
        analyzer = Ana_analyzer([os.path.join(os.path.dirname(__file__), f'./{self.sample_csv}')])

        analyzer.drop_codeshare()
        analyzer.drop_codeshare()

        df = analyzer.df
        self.assertEqual(len(df), 83)

    def test_edit_date(self):
        # Test the edit_date function
        df = pd.DataFrame({'date': ['2022年01月01日', '2022年01月02日', '2022年01月03日']})
        expected_df = pd.DataFrame({'date': ['2022/01/01', '2022/01/02', '2022/01/03']})
        expected_df['date'] = pd.to_datetime(expected_df['date'])

        df = ana_analyze.edit_date(df)

        self.assertEqual(df['date'].tolist(), expected_df['date'].tolist())

    def test_add_delay_column(self):
        # Add your test code here
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), self.sample_csv), header=None)
        df.columns = ['date', 'name', 'from', 'to', 'schedule_dep', 'schedule_arr', 'actual_dep', 'actual_arr', 'dep_info', 'arr_info', 'info_other', 'info_detail', 'type_of_aircraft']
        df = ana_analyze.edit_date(df)
        df = ana_analyze.add_delay_column(df)
        self.assertEqual(df[df['name'] == 'ANA055']['dep_delay'].values[0], -5)
        self.assertEqual(df[df['name'] == 'ANA055']['arr_delay'].values[0], -10)
        self.assertEqual(df[df['name'] == 'ANA065']['dep_delay'].values[0], 15)
        self.assertEqual(df[df['name'] == 'ANA065']['arr_delay'].values[0], 25)
        self.assertEqual(df[df['name'] == 'ANA4743']['dep_delay'].values[0], 240)
        self.assertEqual(df[df['name'] == 'ANA4743']['arr_delay'].values[0], 240)
    
    def test_time_deltaer_returns_correct_delta_with_two_time_beyond_24h(self):
        # Act
        actual = ana_analyze.time_deltaer("23:55", "24:05")
        expected = datetime.timedelta(minutes=10)

        # Assert
        self.assertEqual(actual, expected)
    
    def test_time_deltaer_returns_correct_delta_with_two_time_earlier_24h(self):
        # Act
        actual = ana_analyze.time_deltaer("23:50", "23:55")
        expected = datetime.timedelta(minutes=5)

        # Assert
        self.assertEqual(actual,expected )
    
    def test_time_deltaer_returns_correct_delta_with_two_time_later_24h(self):
        # Act
        actual = ana_analyze.time_deltaer("24:05", "24:10")
        expected = datetime.timedelta(minutes=5)

        # Assert
        self.assertEqual(actual, expected)

    def test_time_deltaer_returns_correct_delta_with_two_time_beyond_24h_inverse(self):
        # Act
        actual = ana_analyze.time_deltaer("24:05", "23:55")
        expected = datetime.timedelta(minutes=-10)

        # Assert
        self.assertEqual(actual, expected)
    
    def test_time_deltaer_returns_correct_delta_with_two_time_earlier_24h_inverse(self):
        # Act
        actual = ana_analyze.time_deltaer("23:55", "23:50")
        expected = datetime.timedelta(minutes=-5)

        # Assert
        self.assertEqual(actual, expected)
    
    def test_time_deltaer_returns_correct_delta_with_two_time_later_24h_inverse(self):
        # Act
        actual = ana_analyze.time_deltaer("24:10", "24:05")
        expected = datetime.timedelta(minutes=-5)

        # Assert
        self.assertEqual(actual, expected)
    # def test_add_ac_type_column(self):
    #     # Test the add_ac_type_column function
    #     # Add your test code here

    # def test_find_type_and_volume_csv(self):
    #     # Test the find_type_and_volume_csv function
    #     # Add your test code here

    # def test_analyze_by_seat_cat(self):
    #     # Test the analyze_by_seat_cat function
    #     # Add your test code here

    # def test_analyze_by_date(self):
    #     # Test the analyze_by_date function
    #     # Add your test code here

    # def test_word_analyze(self):
    #     # Test the word_analyze function
    #     # Add your test code here

    # def test_file_name_of_wordcloud(self):
    #     # Test the file_name_of_wordcloud function
    #     # Add your test code here

if __name__ == '__main__':
    unittest.main()
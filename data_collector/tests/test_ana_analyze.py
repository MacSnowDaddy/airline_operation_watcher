import unittest
import sys, os
from unittest.mock import patch
#import parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pandas as pd
import ana_analyze
from ana_analyze import Ana_analyzer


class TestAnaAnalyzer(unittest.TestCase):

    @patch('ana_analyze.find_analyze_target_dir')
    @patch('glob.glob')
    def setUp(self, mock_glob, mock_find_analyze_target_dir):
        self.sample_csv = 'sample_ana20991231.csv'
        mock_find_analyze_target_dir.return_value = os.path.join(os.path.dirname(__file__))
        mock_glob.return_value = [os.path.join(os.path.dirname(__file__), self.sample_csv)]
        self.analyzer = Ana_analyzer(2022, 1, 1)

    def tearDown(self):
        # Add any necessary cleanup code here
        pass

    def test_init(self):
        # Test the __init__ method
        df = self.analyzer.df
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 130)

    def test_drop_codeshare(self):
        # Test the drop_codeshare method
        self.analyzer.drop_codeshare()
        df = self.analyzer.df
        self.assertEqual(len(df), 98)

        # numbers of line will not change even if you call drop_codeshare method twice.
        self.analyzer.drop_codeshare()
        df = self.analyzer.df
        self.assertEqual(len(df), 98)

    def test_get_df(self):
        # Test the get_df method
        df = self.analyzer.get_df()
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 130)
        self.assertEqual(df.columns.tolist(), self.analyzer.df.columns.tolist())

    def test_make_dataframe(self):
        # Test the make_dataframe function
        files = [os.path.join(os.path.dirname(__file__), self.sample_csv)]
        df = ana_analyze.make_dataframe(files)
        self.assertIsNotNone(df)

        # return empty dataframe if files is empty.
        files = []
        df = ana_analyze.make_dataframe(files)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 0)

    def test_edit_date(self):
        # Test the edit_date function
        df = pd.DataFrame({'date': ['2022年01月01日', '2022年01月02日', '2022年01月03日']})
        df = ana_analyze.edit_date(df)
        expected_df = pd.DataFrame({'date': ['2022/01/01', '2022/01/02', '2022/01/03']})
        expected_df['date'] = pd.to_datetime(expected_df['date'])
        self.assertEqual(df['date'].tolist(), expected_df['date'].tolist())

    def test_add_delay_column(self):
        # Add your test code here
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), self.sample_csv), header=None)
        df.columns = ['date', 'name', 'from', 'to', 'schedule_dep', 'schedule_arr', 'actual_dep', 'actual_arr', 'dep_info', 'arr_info', 'info_other', 'info_detail', 'type_of_aircraft']
        df = ana_analyze.edit_date(df)
        df = ana_analyze.add_delay_column(df)
        self.assertEqual(df[df['name'] == 'ANA065']['dep_delay'].values[0], 15)
        self.assertEqual(df[df['name'] == 'ANA065']['arr_delay'].values[0], 25)
        self.assertEqual(df[df['name'] == 'ANA4743']['dep_delay'].values[0], 240)
        self.assertEqual(df[df['name'] == 'ANA4743']['arr_delay'].values[0], 240)
      

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
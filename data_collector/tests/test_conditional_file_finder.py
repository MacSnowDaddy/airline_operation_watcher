import unittest
import conditional_file_finder

class TestConditionalFileFinder(unittest.TestCase):

    def setUp(self) -> None:
        self.file_paths = [
            "./data_collector/jal/analyze_target/20240804-0810/jal20240808.csv",
            "./data_collector/jal/analyze_target/20240804-0810/jal20240806.csv",
            "./data_collector/jal/analyze_target/20240804-0810/jal20240807.csv",
            "./data_collector/jal/analyze_target/20240714-0720/jal20240717.csv",
            "./data_collector/jal/analyze_target/20240714-0720/jal20240716.csv",
            "./data_collector/jal/analyze_target/20240714-0720/jal20240714.csv",
            "./data_collector/jal/analyze_target/20240714-0720/jal20240715.csv",
            "./data_collector/jal/analyze_target/20240714-0720/jal20240718.csv",
            "./data_collector/jal/analyze_target/20240714-0720/jal20240719.csv",
            "./data_collector/jal/analyze_target/20240721-0727/jal20240724.csv",
            "./data_collector/jal/analyze_target/20240721-0727/jal20240725.csv",
            "./data_collector/jal/analyze_target/20240721-0727/jal20240727.csv",
            "./data_collector/jal/analyze_target/20240721-0727/jal20240726.csv",
            "./data_collector/jal/analyze_target/20240721-0727/jal20240722.csv",
            "./data_collector/jal/analyze_target/20240721-0727/jal20240721.csv",
            "./data_collector/jal/analyze_target/20240818-0824/jal20240823.csv",
            "./data_collector/jal/analyze_target/20240818-0824/jal20240824.csv",
            "./data_collector/jal/analyze_target/20240728-0803/jal20240728.csv",
            "./data_collector/jal/analyze_target/20240728-0803/jal20240729.csv",
            "./data_collector/jal/analyze_target/20240728-0803/jal20240730.csv",
            "./data_collector/jal/analyze_target/20240728-0803/jal20240731.csv",
            "./data_collector/jal/analyze_target/20240728-0803/jal20240801.csv",
            "./data_collector/jal/analyze_target/20240728-0803/jal20240803.csv",
            "./data_collector/jal/analyze_target/20240728-0803/jal20240802.csv",
            "./data_collector/jal/analyze_target/20230811-0817/jal20230817.csv",
        ]

    def test_find_files_from_valid_path_lists_with_all_int_conditions(self):
        # Arrange
        condition = conditional_file_finder.FileFindCondition(2024, 8, 8)
        sut = conditional_file_finder.ConditionalFileFinder()

        # Act
        actual = sut.pick_files_from_with(self.file_paths, condition)
        expected =  ["./data_collector/jal/analyze_target/20240804-0810/jal20240808.csv"]

        # Assert
        self.assertCountEqual(actual, expected)
    
    def test_find_flies_from_valid_path_lists_with_numeric_string_conditions(self):
        # Arrange
        condition = conditional_file_finder.FileFindCondition("2024", "08", "08")
        sut = conditional_file_finder.ConditionalFileFinder()

        # Act
        actual = sut.pick_files_from_with(self.file_paths, condition)
        expected =  ["./data_collector/jal/analyze_target/20240804-0810/jal20240808.csv"]

        # Assert
        self.assertCountEqual(actual, expected)
    
    def test_find_files_from_vlaid_path_lists_with_wildcard_conditions(self):
        # Arrange
        condition = conditional_file_finder.FileFindCondition("*", 8, "*")
        sut = conditional_file_finder.ConditionalFileFinder()

        # Act
        actual = sut.pick_files_from_with(self.file_paths, condition)
        expected = ["./data_collector/jal/analyze_target/20240804-0810/jal20240808.csv",
                    "./data_collector/jal/analyze_target/20240804-0810/jal20240806.csv",
                    "./data_collector/jal/analyze_target/20240804-0810/jal20240807.csv",
                    "./data_collector/jal/analyze_target/20240818-0824/jal20240823.csv",
                    "./data_collector/jal/analyze_target/20240818-0824/jal20240824.csv",
                    "./data_collector/jal/analyze_target/20240728-0803/jal20240801.csv",
                    "./data_collector/jal/analyze_target/20240728-0803/jal20240803.csv",
                    "./data_collector/jal/analyze_target/20240728-0803/jal20240802.csv",
                    "./data_collector/jal/analyze_target/20230811-0817/jal20230817.csv"]

        # Assert
        self.assertCountEqual(actual, expected)

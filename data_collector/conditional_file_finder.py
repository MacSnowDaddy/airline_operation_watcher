import re
from typing import List, Optional

class FileFindCondition(object):
    '''This class represents the condition to find files.
    
    The condition is represented by year, month, and day.
    If you set the condition as '2020', '08', '01', the condition you want to set is '20200801'.
    If you set the condition as '2020', '*', '*', the condition you want to set is '2020**'.'''

    def __init__(self, year, month, day):
        '''Initialize the condition with year, month, and day.
        
        @param year: year of the data you want to analyze. accept regex.
        @param month: month of the data you want to analyze. accept regex.
        @param day: day of the data you want to analyze. accept regex.
        If you want to use regex, you should use 2-digit number for month and day. e.g. '(07|08)' for month, '(01|02|03)' for day.
        '''
        self.year = year
        self.month = month
        self.day = day
    
    def set_condition(self, year, month, day):
        '''You can reset the condition with year, month, and day using this function.'''
        self.year = year
        self.month = month
        self.day = day
    
    def match(self, file_path:str) -> bool:
        '''Return True if the file_path matches the condition, else return False.'''
        pattern = self._condition_former()
        return re.match(pattern, file_path)

    def _condition_former(self) -> str:
        # try year, month, day to convert to int
        # it may fail because of wildcard, in that case, pass
        # this is to avoid "08" to consider as wildcard
        try:
            _year = int(self.year)
        except:
            _year = self.year
        try:
            _month = int(self.month)
        except:
            _month = self.month
        try:
            _day = int(self.day)
        except:
            _day = self.day

        if isinstance(_year, int):
            _year = "{:04d}".format(_year)
        elif _year == "*":
            _year = "[0-9]{4}"
        if isinstance(_month, int):
            _month = "{:02d}".format(_month)
        elif _month == "*":
            _month = "[0-9]{2}"
        if isinstance(_day, int):
            _day = "{:02d}".format(_day)
        elif _day == "*":
            _day = "[0-9]{2}"
        
        return f'.*{_year}{_month}{_day}.csv'

class ConditionalFileFinder(object):
    '''This class is used to find files with the condition.
    
    You can find files with the condition using this class.
    You should pass condition:FileFindCondition object to pick_files_from_with function.'''

    def pick_files_from_with(self, file_paths:list[str], condition:FileFindCondition) -> List[str]:
        result = []
        for file_path in file_paths:
            if condition.match(file_path):
                result.append(file_path)
        return result

import datetime
import pandas as pd

class Jal_analyzer(object):
    '''This class is used to analyze the data of JAL.'''
    
    def __init__(self, files:list):
        '''Initialize the class with the files of the data you want to analyze.
        
        '''
        self.df = make_dataframe(files)
    
    def drop_codeshare(self):
        '''Drop the code share flights in the data.Jal_reader is 
        not able to distinguish the code share flights from the regular flights.'''
        pass

    def get_df(self):
        '''Return the dataframe which is created by make_dataframe function.'''
        return self.df


def make_dataframe(files):
    '''Create a dataframe from the list of files which dose not have header line.
    
    after calling this function, you'll get a dataframe which has the following columns.'
    date : date of the flight, format is 'YYYY/MM/DD'
    name : name of the flight, e.g. 'JAL1234'
    from : departure airport, e.g. '東京（成田）' , '札幌（千歳）' etc.
    to : arrival airport, e.g. '札幌（千歳）', '東京（成田）' etc.
    schedule_dep : scheduled departure time, format is 'HH:MM'
    schedule_arr : scheduled arrival time, format is 'HH:MM'
    actual_dep : actual departure time, format is 'HH:MM'
    actual_arr : actual arrival time, format is 'HH:MM'
    dep_info : information about departure, e.g. '出発済み搭乗口７' etc.
    arr_info : information about arrival, e.g. '到着済み' etc.
    info_other : other information, e.g. '出発遅れ' etc.
    info_detail : detail information, e.g. '使用機到着遅れのため出発が遅れました。' etc.
    act_dep_time_with_date : actual departure time with date, format is 'YYYY-MM-DD HH:MM'
    act_arr_time_with_date : actual arrival time with date, format is 'YYYY-MM-DD HH:MM'
    sch_dep_time_with_date : scheduled departure time with date, format is 'YYYY-MM-DD HH:MM'
    sch_arr_time_with_date : scheduled arrival time with date, format is 'YYYY-MM-DD HH:MM'
    dep_delay : delay time of departure in minutes
    arr_delay : delay time of arrival in minutes
    '''
    if len(files) == 0:
        return pd.DataFrame()
    df = pd.concat([pd.read_csv(f, header=None, na_filter=False) for f in files], ignore_index=True)
    df.columns = ['date', 'name', 'from', 'to', 'schedule_dep', 'schedule_arr', 'actual_dep', 'actual_arr', 'dep_info', 'arr_info', 'info_other', 'info_detail']
    df = _edit_date(df)
    df = _add_delay_column(df)
    return df

def _edit_date(df):
    # add date column
    df['date'] = df['date'].str.replace('年', '/').str.replace('月', '/').str.replace('日', '')
    df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d')
    return df

def _add_delay_column(df):
    # add delay column
    # delete the rows which have "-" value in actual_dep and actual_arr
    df = df
    df = df[~(df['schedule_dep'].astype(str).str.contains("--"))]
    df = df[~(df['schedule_dep'].astype(str).str.contains("ERROR"))]
    df = df[~(df['actual_dep'].astype(str).str.contains("--"))]
    df = df[~(df['actual_dep'].astype(str).str.contains("ERROR"))]
    df = df[~(df['actual_dep'].astype(str).str.contains("再就航"))]
    df = df[~(df['actual_arr'].astype(str).str.contains("--"))]
    df = df[~(df['actual_arr'].astype(str).str.contains("ERROR"))]
    df = df.drop(df[df['name'].isna()].index)
    # convert the type of actual_dep and actual_arr to datetime
    # jal page describes the time beyond 24:00 as "0:00" or "1:00" etc.

    # calculate delay time in minites
    df['dep_delay'] = df.apply(lambda row: time_deltaer(row['schedule_dep'], row['actual_dep']).total_seconds() / 60, axis=1)
    df['arr_delay'] = df.apply(lambda row: time_deltaer(row['schedule_arr'], row['actual_arr']).total_seconds() / 60, axis=1)

    return df

def time_deltaer(origin:str, actual:str) -> datetime.timedelta:
    '''Calculate the time difference between origin and actual.
    
    @param origin: scheduled time, format is 'HH:MM'
    @param actual: actual time, format is 'HH:MM'
    @return: timedelta object which is the time of delay.
    '''
    origin_datetime = datetime.datetime.strptime(origin, '%H:%M')
    actual_datetime = datetime.datetime.strptime(actual, '%H:%M')
    # assume that the acutual time is not 1hour earlier than the scheduled time.
    time_delta = actual_datetime - origin_datetime
    if time_delta.total_seconds() < -3600:
        actual_datetime += datetime.timedelta(days=1)
        time_delta = actual_datetime - origin_datetime
    elif time_delta.total_seconds() > 23 * 3600: 
        # in case departing earlier than scheduled time and
        # the scheduled time is beyond 24:00
        actual_datetime -= datetime.timedelta(days=1)
        time_delta = actual_datetime - origin_datetime
    return time_delta


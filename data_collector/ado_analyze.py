import datetime
import pandas as pd

class Ado_analyzer(object):
    '''This class is used to analyze the data of ANA.'''
    
    def __init__(self, files:list):
        '''Initialize the class with the files of the data you want to analyze.
        
        '''
        self.df = make_dataframe(files)
    
    def drop_codeshare(self):
        '''Include the code share flights in the data.
        Ado_reader is not able to distinguish the code share flights from the regular flights.'''
        pass
    
    def get_df(self):
        '''Return the dataframe which is created by make_dataframe function.'''
        return self.df

def make_dataframe(files):
    '''Create a dataframe from the list of files which dose not have header line.
    
    after calling this function, you'll get a dataframe which has the following columns.'
    date : date of the flight, format is 'YYYY/MM/DD'
    name : name of the flight, e.g. 'ADO1234'
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
    df.columns = ['date', 'name', 'from', 'to', 'schedule_dep', 'schedule_arr', 'actual_dep', 'actual_arr', 'dep_info', 'arr_info', 'info_other']
    df = _edit_date(df)
    df = _add_delay_column(df)
    return df

def _edit_date(df):
    # add date column
    df['date'] = df['date'].str.replace("\(.*?\)", "", regex=True)
    df['date'] = df['date'].str.replace('年', '/').str.replace('月', '/').str.replace('日', '')
    df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d')
    return df

def _add_delay_column(df):
    # add delay column
    # delete the rows which have "-" value in actual_dep and actual_arr
    df = df
    df = df[~(df['actual_dep'].astype(str).str.contains("-"))]
    df = df[~(df['actual_arr'].astype(str).str.contains("-"))]
    df = df.drop(df[df['name'].isna()].index)
    # convert the type of actual_dep and actual_arr to datetime

    # calculate delay time in minites
    df['dep_delay'] = df.apply((lambda row: time_deltaer(row['schedule_dep'], row['actual_dep']).total_seconds() / 60), axis=1)
    df['arr_delay'] = df.apply((lambda row: time_deltaer(row['schedule_arr'], row['actual_arr']).total_seconds() / 60), axis=1)

    return df

def time_deltaer(origin:str, actual:str) -> datetime.timedelta:
    '''Return timedelta object which is the time of delay.
    
    @param origin: scheduled time, format is 'HH:MM'
    @param actual: actual time, format is 'HH:MM'
    '''
    origin_time_hour, origin_time_minute = map(int, origin.split(":"))
    actual_time_hour, actual_time_minute = map(int, actual.split(":"))
    if origin_time_hour >= 24:
        origin_time_hour -= 24
        origin_datetime = datetime.datetime(2022, 1, 2, origin_time_hour, origin_time_minute)
    else:
        origin_datetime = datetime.datetime(2022, 1, 1, origin_time_hour, origin_time_minute)
    if actual_time_hour >= 24:
        actual_time_hour -= 24
        actual_datetime = datetime.datetime(2022, 1, 2, actual_time_hour, actual_time_minute)
    else:
        actual_datetime = datetime.datetime(2022, 1, 1, actual_time_hour, actual_time_minute)

    return actual_datetime - origin_datetime

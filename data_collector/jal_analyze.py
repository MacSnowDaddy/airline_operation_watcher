import pandas as pd

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
    df = pd.concat([pd.read_csv(f, header=None) for f in files], ignore_index=True)
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
    df = df[~(df['actual_dep'].astype(str).str.contains("--"))]
    df = df[~(df['actual_dep'].astype(str).str.contains("ERROR"))]
    df = df[~(df['actual_dep'].astype(str).str.contains("再就航"))]
    df = df[~(df['actual_arr'].astype(str).str.contains("--"))]
    df = df[~(df['actual_arr'].astype(str).str.contains("ERROR"))]
    df = df.drop(df[df['name'].isna()].index)
    # convert the type of actual_dep and actual_arr to datetime
    # if the time is grater than 24:00, it will be converted to the next day.
    def make_time_with_date(row):
        try:
            if int(row['actual_dep'].split(':')[0]) >= 24:
                row['act_dep_time_with_date'] = (row['date'] + pd.Timedelta(days=1)).strftime('%Y-%m-%d') + ' ' + str(int(row['actual_dep'].split(':')[0]) - 24) + ':' + row['actual_dep'].split(':')[1]
            else:
                row['act_dep_time_with_date'] = row['date'].strftime('%Y-%m-%d') + ' ' + row['actual_dep']
            if int(row['actual_arr'].split(':')[0]) >= 24:
                row['act_arr_time_with_date'] = (row['date'] + pd.Timedelta(days=1)).strftime('%Y-%m-%d') + ' ' + str(int(row['actual_arr'].split(':')[0]) - 24) + ':' + row['actual_arr'].split(':')[1]
            else:
                row['act_arr_time_with_date'] = row['date'].strftime('%Y-%m-%d') + ' ' + row['actual_arr']
            
            if int(row['schedule_dep'].split(':')[0]) >= 24:
                row['sch_dep_time_with_date'] = (row['date'] + pd.Timedelta(days=1)).strftime('%Y-%m-%d') + ' ' + str(int(row['schedule_dep'].split(':')[0]) - 24) + ':' + row['schedule_dep'].split(':')[1]
            else:
                row['sch_dep_time_with_date'] = row['date'].strftime('%Y-%m-%d') + ' ' + row['schedule_dep']
            
            if int(row['schedule_arr'].split(':')[0]) >= 24:
                row['sch_arr_time_with_date'] = (row['date'] + pd.Timedelta(days=1)).strftime('%Y-%m-%d') + ' ' + str(int(row['schedule_arr'].split(':')[0]) - 24) + ':' + row['schedule_arr'].split(':')[1]
            else:
                row['sch_arr_time_with_date'] = row['date'].strftime('%Y-%m-%d') + ' ' + row['schedule_arr']
        except:
            print(row)
            raise
        return row

    df = df.apply(make_time_with_date, axis=1)
    # calculate delay time in minites
    df['dep_delay'] = (pd.to_datetime(df['act_dep_time_with_date']) - pd.to_datetime(df['sch_dep_time_with_date'])).dt.total_seconds() / 60
    df['arr_delay'] = (pd.to_datetime(df['act_arr_time_with_date']) - pd.to_datetime(df['sch_arr_time_with_date'])).dt.total_seconds() / 60

    return df



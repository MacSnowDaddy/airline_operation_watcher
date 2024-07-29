# %%
import pandas as pd
import numpy as np


class Ana_analyzer(object):
    '''This class is used to analyze the data of ANA.'''
    
    def __init__(self, year, month, day):
        '''Initialize the class with the date of the data you want to analyze.
        
        @param year: year of the data you want to analyze. accept "*" as a wildcard.
        @param month: month of the data you want to analyze. accept "*" as a wildcard.
        @param day: day of the data you want to analyze. accept "*" as a wildcard.
        '''
        import os
        import glob
        pattern = find_analyze_target_dir()
        if type(year) == int:
            year = "{:04d}".format(year)
        else:
            year = "[0-9][0-9][0-9][0-9]"
        if type(month) == int:
            month = "{:02d}".format(month)
        else:
            month = "[0-9][0-9]"
        if type(day) == int:
            day = "{:02d}".format(day)
        else:
            day = "[0-9][0-9]"
        pattern += f'**/ana{year}{month}{day}.csv'
        files = glob.glob(pattern, recursive=True)
        self.df = make_dataframe(files)
    
    def drop_codeshare(self):
        '''Drop the code share flights in the data.'''
        self.df = self.df[~(self.df['info_detail'].str.contains('ADO運航', regex=True))]
    
    def get_df(self):
        '''Return the dataframe which is created by make_dataframe function.'''
        return self.df


def find_analyze_target_dir():
    '''just return dir string who has analyze_target files.
    
    this function is made to make test easier.
    '''
    import os
    return os.path.join(os.path.dirname(__file__), f'ana/analyze_target/')

def make_dataframe(files):
    '''Create a dataframe from the list of files which dose not have header line.

    @return: a dataframe which is created from the list of files.
        This function will return empty dataframe if the list of files is empty.
    after calling this function, you'll get a dataframe which has the following columns.
    date : date of the flight, format is 'YYYY/MM/DD'
    name : name of the flight, e.g. 'ANA1234'
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
    type_of_aircraft : type of aircraft, e.g. 'B73D' etc. see the file 'type_and_volume.csv' for the detail of each type of aircraft.
    act_dep_time_with_date : actual departure time with date, format is 'YYYY-MM-DD HH:MM'
    act_arr_time_with_date : actual arrival time with date, format is 'YYYY-MM-DD HH:MM'
    sch_dep_time_with_date : scheduled departure time with date, format is 'YYYY-MM-DD HH:MM'
    sch_arr_time_with_date : scheduled arrival time with date, format is 'YYYY-MM-DD HH:MM'
    dep_delay : delay time of departure in minutes
    arr_delay : delay time of arrival in minutes
    number_of_seat : number of seats of the aircraft
    '''
    if len(files) == 0:
        return pd.DataFrame()
    df = pd.concat([pd.read_csv(f, header=None, na_filter=False) for f in files], ignore_index=True)
    df.columns = ['date', 'name', 'from', 'to', 'schedule_dep', 'schedule_arr', 'actual_dep', 'actual_arr', 'dep_info', 'arr_info', 'info_other', 'info_detail', 'type_of_aircraft']
    df = edit_date(df)
    df = add_delay_column(df)
    # df = add_ac_type_column(df)
    return df


def edit_date(df):
    # add date column
    df['date'] = df['date'].str.replace('年', '/').str.replace('月', '/').str.replace('日', '')
    if(df['date'].str.contains('nan')).any():
        print(df[df['date'].str.contains('nan')])
        df.drop(df[df['date'].str.contains('nan')].index, inplace=True)
    df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d')
    return df



def add_delay_column(df):
    # add dlay column
    # delete the rows which have "-" value in actual_dep and actual_arr
    df = df[df['actual_dep'] != '-']
    df = df[df['actual_arr'] != '-']
    df = df.drop(df[df['name'].isna()].index)
    # convert the type of actual_dep and actual_arr to datetime
    # if the time is grater than 24:00, it will be converted to the next day.
    def make_time_with_date(row):
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
        return row

    df = df.apply(make_time_with_date, axis=1)
    # calculate delay time in minites
    df['dep_delay'] = (pd.to_datetime(df['act_dep_time_with_date']) - pd.to_datetime(df['sch_dep_time_with_date'])).dt.total_seconds() / 60
    df['arr_delay'] = (pd.to_datetime(df['act_arr_time_with_date']) - pd.to_datetime(df['sch_arr_time_with_date'])).dt.total_seconds() / 60

    return df



def add_ac_type_column(df):
    # put the volume of each type of aircraft
    import os
    df_type = pd.read_csv(find_type_and_volume_csv(), header=None)
    df_type.columns = ['type_of_aircraft', 'number_of_seat', 'category']

    df = pd.merge(df, df_type, on='type_of_aircraft', how='left')
    return df

def find_type_and_volume_csv():
    '''just return dir string who has type_and_volume.csv.
    
    this function is made to make test easier.
    '''
    import os
    return os.path.join(os.path.dirname(__file__), f'ana/type_and_volume.csv')


# def analyze_by_seat_cat(df):
#     import seaborn as sns
#     # volumeを[0, 100, 200, 300, 400, 500]に分割し、delayをそれぞれのvolumeに分けてヒストグラムを作成する
#     df['num_seat_bin'] = pd.cut(df['number_of_seat'], [0, 100, 200, 300, 400, 500])

#     # %%
#     desc = df.groupby('num_seat_bin')['dep_delay'].describe()
#     print(desc)

#     # %%
#     violin_plot = sns.violinplot(data=df[df['dep_delay'] < 200], x=df['num_seat_bin'], y=df['dep_delay'])
#     violin_plot.set_ylabel('departure delay [min]')
#     violin_plot.set_xlabel('number of seat')


# def analyze_by_date(df):
#     import seaborn as sns
#     print(df.groupby('date').describe()[['dep_delay']])
#     print(df.groupby('date').describe()[['arr_delay']])
#     df.groupby('date').describe()[['dep_delay']][('dep_delay', 'count')].mean()

#     sns.violinplot(data=df.sort_values(by="date"), x='date', y='dep_delay')


# def word_analyze(df, date):
#     import seaborn as sns
#     # info_detailに含まれる名詞と動詞の数をjanomeを使ってカウントする。
#     from janome.analyzer import Analyzer
#     from janome.tokenfilter import POSKeepFilter, TokenCountFilter, WordKeepFilter, WordStopFilter
#     from matplotlib import pyplot as plt

#     token_filters = [POSKeepFilter(['名詞', '動詞']),
#                     WordStopFilter(['-']),
#                     TokenCountFilter(att='base_form'),]
#     analyzer = Analyzer(token_filters=token_filters)

#     reason = ' '.join(df[df['date'] == date]['info_detail'])

#     pairs = analyzer.analyze(reason)
#     pairs_dict = dict(pairs)
#     print(sorted(pairs_dict.items(), key=lambda x: x[1], reverse=True))

#     from wordcloud import WordCloud

#     fpath = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
#     wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=fpath).generate_from_frequencies(pairs_dict)
#     wordcloud.to_file(file_name_of_wordcloud())
#     plt.imshow(wordcloud, interpolation='bilinear')
#     plt.axis('off')
#     plt.show()

# def file_name_of_wordcloud():
#     '''Return the file name of the wordcloud image. Code will replace the file if the file already exists.
    
#     This function is made to make test easier.'''
#     import os
#     return os.path.join(os.path.dirname(__file__), f'ana/wordcloud.png')



    # %%
    df_words_pairs = pd.DataFrame(data=pairs_dict.items(), columns=['word', 'count'])
    print(pairs_dict)
    df_words_pairs

    # %%
    from matplotlib import rcParams
    rcParams['font.family'] = 'Hiragino Mincho ProN'
    rcParams['font.size'] = 12
    sns.barplot(x='count', y='word', data=df_words_pairs.sort_values(by='count', ascending=False))



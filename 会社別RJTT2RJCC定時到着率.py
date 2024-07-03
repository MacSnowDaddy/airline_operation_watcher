import pandas as pd
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './data_collector/'))
import glob
import ana_analyze
import jal_analyze
import sky_analyze
import ado_analyze
import ap_dict
import types
import seaborn as sns
import matplotlib.pyplot as plt
import datetime


'''完成品としては、日毎時間毎の定時到着率をlinechartで表現する。'''

def make_df(airline:str, year:str, month:str, date:str='*') -> pd.DataFrame:
    pattern = os.path.join(os.path.dirname(__file__), f'data_collector/{airline}/analyze_target/')
    pattern += f'**/{airline}{year}{month}{date}.csv'
    files = glob.glob(pattern, recursive=True)

    return eval(f'{airline}_analyze.make_dataframe(files)')

def on_schedule_arrival_rate(df:pd.DataFrame) -> float:
    on_schedule_arr_count = df[df['arr_delay'] <= 14]
    all_flight_count = len(df)
    return len(on_schedule_arr_count) / all_flight_count

def print_on_schedule_arrival_rate(airline:str, df:pd.DataFrame, dep_ap:str='*', dest_ap:str='*'):
    '''
    @param airline: airline name, 'ana', 'jal' or 'sky'
    @param dep_ap: (optional)departure airport IATA code
    @param dest_ap: (optional)destination airport IATA code
    '''
    if dep_ap != "*":
        df = df[(df['from'] == ap_dict.decode(dep_ap,  airline))]
    if dest_ap != "*":
        df = df[(df['to']   == ap_dict.decode(dest_ap, airline))]
    print(f'{airline.upper()} {on_schedule_arrival_rate(df)*100:.1f}% ({len(df[df["arr_delay"] <= 14])}/{len(df)})')
    df['hour'] = df['schedule_arr'].str.split(':').str[0]
    group_hour = df.groupby('hour')['arr_delay'].describe()
    group_hour.index = group_hour.index.astype(int)
    group_hour = group_hour.sort_index()
    # print(df.groupby('hour')['arr_delay'].describe())
    # sns.lineplot(group_hour, x=group_hour.index, y='mean')
    # plt.fill_between(x=group_hour.index, y1=group_hour['std']+group_hour['mean'], y2=group_hour['mean']-group_hour['std'], alpha=0.2)
    # plt.show()
    return df

def daily_on_schedule_arrival_rate(df:pd.DataFrame) -> pd.DataFrame:
    return df.groupby('date').apply(on_schedule_arrival_rate)


def main(year, month, day, dep_ap:str = "HND", dest_ap:str = "CTS"):
    '''the result of this function is make a format of tweet.
    
    @param year: year of the data you want to analyze. accept "*" as a wildcard.
    @param month: month of the data you want to analyze. accept "*" as a wildcard.
    @param day: day of the data you want to analyze. accept "*" as a wildcard.'''
    # year, month, and day are passed as str type.
    # they are passed as int if they can be converted to int.
    # else, they are passed as str.
    try:
        year = int(year)
    except ValueError:
            year = year
    try:
        month = int(month)
    except ValueError:
            month = month
    try:
        day = int(day)
    except ValueError:
        day = day

    ana_analyzer = ana_analyze.Ana_analyzer(year=year, month=month, day=day)
    ana_analyzer.include_codeshare(False)
    ana_df = ana_analyzer.get_df()
    jal_analyzer = jal_analyze.Jal_analyzer(year=year, month=month, day=day)
    jal_analyzer.include_codeshare(False)
    jal_df = jal_analyzer.get_df()
    sky_analyzer = sky_analyze.Sky_analyzer(year=year, month=month, day=day)
    sky_analyzer.include_codeshare(False)
    sky_df = sky_analyzer.get_df()
    ado_analyzer = ado_analyze.Ado_analyzer(year=year, month=month, day=day)
    ado_analyzer.include_codeshare(False)
    ado_df = ado_analyzer.get_df()
    airline_list = ["ana", "jal", "sky", "ado"]
    print(f'{month}月{day}日 各社の定時到着*率（欠航は除く)\n' + ap_dict.decode(dep_ap, "sky") + dep_ap + '=>' + ap_dict.decode(dest_ap, "sky") + dest_ap)

    for airline in airline_list:
        print_on_schedule_arrival_rate(airline, eval(f'{airline}_df'), dep_ap, dest_ap)
    print("*定時到着:14分以内の遅れで到着")

if __name__ == "__main__":
    # read std args.
    # if std args is not passed, use yesterday as default.
    if len(sys.argv) == 4:
        year = sys.argv[1]
        month = sys.argv[2]
        day = sys.argv[3]
        dep_ap = "HND"
        dest_ap = "CTS"
    elif len(sys.argv) == 6:
        year = sys.argv[1]
        month = sys.argv[2]
        day = sys.argv[3]
        dep_ap = sys.argv[4]
        dest_ap = sys.argv[5]
    else:
        target_date:datetime.date = datetime.date.today() - datetime.timedelta(days=1)
        year = target_date.year
        month = target_date.month
        day = target_date.day
        dep_ap = "HND"
        dest_ap = "CTS"
    main(year, month, day, dep_ap, dest_ap)
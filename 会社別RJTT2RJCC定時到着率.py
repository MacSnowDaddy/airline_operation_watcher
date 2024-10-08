import pandas as pd
import os
import sys
import glob
from data_collector import ana_analyze
from data_collector import jal_analyze
from data_collector import sky_analyze
from data_collector import ado_analyze
from data_collector import ap_dict
from data_collector import conditional_file_finder
import types
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
    if len(df) == 0:
        print(f'{airline.upper()} {dep_ap}=>{dest_ap}のデータはありません')
        return
    if dep_ap != "*":
        df = df[(df['from'] == ap_dict.decode(dep_ap,  airline))]
    if dest_ap != "*":
        df = df[(df['to']   == ap_dict.decode(dest_ap, airline))]
    try:
        print(f'{airline.upper()} {on_schedule_arrival_rate(df)*100:.1f}% {len(df[df["arr_delay"] <= 14])}/{len(df)}')
    except ZeroDivisionError:
        print(f'{airline.upper()} {dep_ap}=>{dest_ap}のデータはありません')
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
    
    @param year: year of the data you want to analyze. accept regex.
    @param month: month of the data you want to analyze. accept regex.
    @param day: day of the data you want to analyze. accept regex.'''

    _conditional_file_finder = conditional_file_finder.ConditionalFileFinder()
    _condition = conditional_file_finder.FileFindCondition(year, month, day)

    #ana
    files = _conditional_file_finder.pick_files_from_with(glob.glob("**/ana/analyze_target/**", recursive=True), _condition)
    ana_analyzer = ana_analyze.Ana_analyzer(files)
    ana_analyzer.drop_codeshare()
    ana_df = ana_analyzer.get_df()
    #jal
    files = _conditional_file_finder.pick_files_from_with(glob.glob("**/jal/analyze_target/**", recursive=True), _condition)
    jal_analyzer = jal_analyze.Jal_analyzer(files)
    jal_analyzer.drop_codeshare()
    jal_df = jal_analyzer.get_df()
    #sky
    files = _conditional_file_finder.pick_files_from_with(glob.glob("**/sky/analyze_target/**", recursive=True), _condition)
    sky_analyzer = sky_analyze.Sky_analyzer(files)
    sky_analyzer.drop_codeshare()
    sky_df = sky_analyzer.get_df()
    #ado
    files = _conditional_file_finder.pick_files_from_with(glob.glob("**/ado/analyze_target/**", recursive=True), _condition)
    ado_analyzer = ado_analyze.Ado_analyzer(files)
    ado_analyzer.drop_codeshare()
    ado_df = ado_analyzer.get_df()
    airline_list = ["ana", "jal", "sky", "ado"]
    dep_ap_janapese = ap_dict.decode(dep_ap, "sky") if ap_dict.decode(dep_ap, "sky") else dep_ap
    dest_ap_janapese = ap_dict.decode(dest_ap, "sky") if ap_dict.decode(dest_ap, "sky") else dest_ap
    print(f'{month}月{day}日 各社の定時到着*率（欠航は除く)\n' + dep_ap_janapese + " #" +dep_ap + ' =>' + dest_ap_janapese + " #" + dest_ap)

    for airline in airline_list:
        print_on_schedule_arrival_rate(airline, eval(f'{airline}_df'), dep_ap, dest_ap)
    print("*定時到着:14分以内の遅れで到着")

if __name__ == "__main__":
    # read std args.
    # if std args is not passed, use yesterday as default.
    # if you specify dep_ap and dest_ap, you can get the ontime arrival rate of the specified route.
    # else you can get the ontime arrival rate of the route between HND and CTS and CTS and HND.
    if len(sys.argv) == 4:
        year = sys.argv[1]
        month = sys.argv[2]
        day = sys.argv[3]
        dep_ap = "HND"
        dest_ap = "CTS"
        main(year, month, day, dep_ap, dest_ap)
        dep_ap = "CTS"
        dest_ap = "HND"
        main(year, month, day, dep_ap, dest_ap)
    elif len(sys.argv) == 6:
        year = sys.argv[1]
        month = sys.argv[2]
        day = sys.argv[3]
        dep_ap = sys.argv[4]
        dest_ap = sys.argv[5]
        main(year, month, day, dep_ap, dest_ap)
    else:
        target_date:datetime.date = datetime.date.today() - datetime.timedelta(days=1)
        year = target_date.year
        month = target_date.month
        day = target_date.day
        dep_ap = "HND"
        dest_ap = "CTS"
        main(year, month, day, dep_ap, dest_ap)
        dep_ap = "CTS"
        dest_ap = "HND"
        main(year, month, day, dep_ap, dest_ap)
    print("#定時運航 #ANA #JAL #SKY #ADO")

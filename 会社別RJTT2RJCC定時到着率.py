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
    # df['hour'] = df['schedule_arr'].str.split(':').str[0]
    # print(df.groupby('hour')['arr_delay'].describe())
    # print(f'\t')
    return df

def daily_on_schedule_arrival_rate(df:pd.DataFrame) -> pd.DataFrame:
    return df.groupby('date').apply(on_schedule_arrival_rate)


def main(date:datetime.date, dep_ap:str = "HND", dest_ap:str = "CTS"):
    ana_analyzer = ana_analyze.Ana_analyzer(year=date.year, month=date.month, day=date.day)
    ana_analyzer.include_codeshare(False)
    ana_df = ana_analyzer.get_df()
    jal_analyzer = jal_analyze.Jal_analyzer(year=date.year, month=date.month, day=date.day)
    jal_analyzer.include_codeshare(False)
    jal_df = jal_analyzer.get_df()
    sky_analyzer = sky_analyze.Sky_analyzer(year=date.year, month=date.month, day=date.day)
    sky_analyzer.include_codeshare(False)
    sky_df = sky_analyzer.get_df()
    ado_analyzer = ado_analyze.Ado_analyzer(year=date.year, month=date.month, day=date.day)
    ado_analyzer.include_codeshare(False)
    ado_df = ado_analyzer.get_df()
    airline_list = ["ana", "jal", "sky", "ado"]
    print(date.strftime('%m月%d日 ') + ap_dict.decode(dep_ap) + dep_ap + '=>' + ap_dict.decode(dest_ap) + dest_ap)
    print('各社の定時到着*率（欠航は除く)')
    for airline in airline_list:
        print_on_schedule_arrival_rate(airline, eval(f'{airline}_df'), dep_ap, dest_ap)
    print("*定時到着:時刻表から14分以内の遅れで到着\n#エアライン #ANA #JAL #SKY #ADO #定時運航")

if __name__ == "__main__":
    # read std args.
    # if std args is not passed, use yesterday as default.
    if len(sys.argv) == 4:
        year = sys.argv[1]
        month = sys.argv[2]
        day = sys.argv[3]
        target_date = datetime.date(int(year), int(month), int(day))
        dep_ap = "HND"
        dest_ap = "CTS"
    elif len(sys.argv) == 6:
        year = sys.argv[1]
        month = sys.argv[2]
        day = sys.argv[3]
        target_date = datetime.date(int(year), int(month), int(day))
        dep_ap = sys.argv[4]
        dest_ap = sys.argv[5]
    else:
        target_date:datetime.date = datetime.date.today() - datetime.timedelta(days=1)
    main(target_date, dep_ap, dest_ap)
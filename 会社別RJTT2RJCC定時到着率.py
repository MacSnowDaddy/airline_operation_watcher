import pandas as pd
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './data_collector/'))
import glob
import ana_analyze
import jal_analyze
import sky_analyze
import ap_dict
import types
import seaborn as sns
import matplotlib.pyplot as plt
import datetime


'''完成品としては、日毎の定時到着率をlinechartで表現する。'''

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
    print(f'{airline} {dep_ap} -> {dest_ap} number of flight : ', len(df))
    print(f'{airline} {dep_ap} -> {dest_ap} number of on schedule arrival : ', len(df[df['arr_delay'] <= 14]))
    print(f'{airline} {dep_ap} -> {dest_ap} の定時到着率は', on_schedule_arrival_rate(df))
    return df

def daily_on_schedule_arrival_rate(df:pd.DataFrame) -> pd.DataFrame:
    return df.groupby('date').apply(on_schedule_arrival_rate)


def main():
    yesterday:datetime.date = datetime.date.today() - datetime.timedelta(days=1)
    ana_df = make_df('ana', yesterday.year, "{:02d}".format(yesterday.month), "{:02d}".format(yesterday.day))
    jal_df = make_df('jal', yesterday.year, "{:02d}".format(yesterday.month), "{:02d}".format(yesterday.day))
    sky_df = make_df('sky', yesterday.year, "{:02d}".format(yesterday.month), "{:02d}".format(yesterday.day))
    # ado_df = make_df('ado', yesterday.year, "{:02d}".format(yesterday.month), "{:02d}".format(yesterday.day))
    airline_list = ["ana", "jal", "sky"]
    print(yesterday)
    for airline in airline_list:
        print_on_schedule_arrival_rate(airline, eval(f'{airline}_df'), 'HND', 'CTS')
        # print_on_schedule_arrival_rate('ado', df, 'HND', 'CTS')

if __name__ == "__main__":
    main()
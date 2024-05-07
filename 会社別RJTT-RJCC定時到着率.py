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


'''完成品としては、日毎の定時到着率をlinechartで表現する。'''

def make_df(airline:str, yearmonth, analyzer:types.ModuleType) -> pd.DataFrame:
    files = glob.glob(os.path.join(
        os.path.dirname(__file__), 
        f'data_collector/{airline}/analyze_target/**/{airline}{yearmonth}*.csv')
        )

    return analyzer.make_dataframe(files)

def on_schedule_arrival_rate(df:pd.DataFrame) -> float:
    on_schedule_arr_count = df[df['arr_delay'] <= 14]
    all_flight_count = len(df)
    return len(on_schedule_arr_count) / all_flight_count

def print_on_schedule_arrival_rate(airline:str, df:pd.DataFrame):
    print(f'{airline} number of flight : ', len(df))
    print(f'{airline} number of on schedule arrival : ', len(df[df['arr_delay'] <= 14]))
    print(f'{airline}の定時到着率は', on_schedule_arrival_rate(df))

def daily_on_schedule_arrival_rate(df:pd.DataFrame) -> pd.DataFrame:
    return df.groupby('date').apply(on_schedule_arrival_rate)

ana_df = make_df('ana', '', ana_analyze)
sky_df = make_df('sky', '', sky_analyze)
jal_df = make_df('jal', '', jal_analyze)

ana_df_HND_CTS = ana_df[(ana_df['from'] == ap_dict.decode("HND", "ana")) 
                        & (ana_df['to'] == ap_dict.decode("CTS", "ana"))]
sky_df_HND_CTS = sky_df[(sky_df['from'] == ap_dict.decode("HND", "sky")) 
                        & (sky_df['to'] == ap_dict.decode("CTS", "sky"))]
jal_df_HND_CTS = jal_df[(jal_df['from'] == ap_dict.decode("HND", "jal")) 
                        & (jal_df['to'] == ap_dict.decode("CTS", "jal"))]

plt.plot(daily_on_schedule_arrival_rate(ana_df_HND_CTS), label='ana', color='blue')
plt.plot(daily_on_schedule_arrival_rate(sky_df_HND_CTS), label='sky', color='yellow')
plt.plot(daily_on_schedule_arrival_rate(jal_df_HND_CTS), label='jal', color='red')

plt.legend()
plt.show()

print(daily_on_schedule_arrival_rate(jal_df_HND_CTS))

print_on_schedule_arrival_rate('ana', ana_df)
print_on_schedule_arrival_rate('sky', sky_df)
print_on_schedule_arrival_rate('jal', jal_df)

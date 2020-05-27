import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def format_time_axis(axis):
    axis.xaxis.set_major_locator(hours)
    axis.xaxis.set_major_formatter(hours_fmt)
    axis.xaxis.set_minor_locator(minutes)
    axis.format_xdata = mdates.DateFormatter('%H:%M')


def interpret_sleep(data):
    # Add new columns
    data['sleep'] = [1] * len(data)

    # Check sensors values
    for i in range(0, len(data)):
        if data.loc[i, 'loudness_mean'] > 5 or data.loc[i, 'loudness_max'] > 10:
            data.loc[i, 'sleep'] = 0
        if data.loc[i, 'motion'] > 1:
            data.loc[i, 'sleep'] = 0

    # Filter out outliers
    for i in range(1, len(data) - 1):
        if data.loc[i, 'sleep'] == 0:
            if data.loc[i - 1, 'sleep'] == 1 and data.loc[i + 1, 'sleep'] == 1:
                data.loc[i, 'sleep'] = 1

    return data


def extract_sleep_start_end(data):
    start = []
    end = []
    is_sleeping = False
    for i in range(0, len(data)):
        if data.loc[i, 'sleep'] == 1 and not is_sleeping:
            start.append(data.loc[i, 'time'])
            is_sleeping = True
        elif data.loc[i, 'sleep'] == 0 and is_sleeping:
            end.append(data.loc[i, 'time'])
            is_sleeping = False

    if len(start) > len(end):
        end.append(data.loc[len(data) - 1, 'time'])

    return start, end


dat = pd.read_csv("C:\\Users\\pasca\\Desktop\\2020-05-27_0856_monitoring.csv", dtype=float,
                  skipinitialspace=True, parse_dates=[0], infer_datetime_format=True)
date = dat['time']

dat = interpret_sleep(dat)
sleep_start, sleep_end = extract_sleep_start_end(dat)

hours = mdates.HourLocator()
minutes = mdates.MinuteLocator([15, 30, 45])
hours_fmt = mdates.DateFormatter('%H:%M')

fig, axes = plt.subplots(nrows=4, figsize=(8, 10))

ax = axes[0]
ax.set_title('{}  -  {}'.format(date[0].strftime('%d.%m.%Y  %H:%M'), date[len(date) - 1].strftime('%d.%m.%Y  %H:%M')))
for j in range(0, len(sleep_start)):
    ax.axvspan(sleep_start[j], sleep_end[j], alpha=0.3, color='gray')
ax.plot(date, dat['temperature'], color='firebrick')
ax.set_ylabel('Temperature', color='firebrick')

ax2 = ax.twinx()
ax2.plot(date, dat['humidity'], color='royalblue')
ax2.set_ylabel('Humidity [%]', color='royalblue')
format_time_axis(ax)

ax = axes[1]
for j in range(0, len(sleep_start)):
    ax.axvspan(sleep_start[j], sleep_end[j], alpha=0.3, color='gray')
ax.plot(date, dat['light_mean'], color='orange')
ax.set_ylabel('Average light', color='orange')

ax2 = ax.twinx()
ax2.plot(date, dat['light_max'], color='orangered')
ax2.set_ylabel('Max light', color='orangered')
format_time_axis(ax)

ax = axes[2]
for j in range(0, len(sleep_start)):
    ax.axvspan(sleep_start[j], sleep_end[j], alpha=0.3, color='gray')
ax.plot(date, dat['loudness_mean'], color='limegreen')
ax.set_ylabel('Average loudness', color='limegreen')

ax2 = ax.twinx()
ax2.plot(date, dat['loudness_max'], color='darkgreen')
ax2.set_ylabel('Max loudness', color='darkgreen')
format_time_axis(ax)

ax = axes[3]
for j in range(0, len(sleep_start)):
    ax.axvspan(sleep_start[j], sleep_end[j], alpha=0.3, color='gray')
ax.plot(date, dat['motion'], color='purple')
ax.set_ylabel('Motion', color='purple')

ax2 = ax.twinx()
date_melato = date[dat['button'] == 1]
ax2.vlines(date_melato, [0] * len(date_melato), [1] * len(date_melato),
           color='deeppink', linestyles='dashed', linewidth=3)
ax2.set_ylabel('Melatonin', color='deeppink')
format_time_axis(ax)

plt.tight_layout()

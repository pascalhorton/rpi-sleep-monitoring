import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

threshold_avg_loudness = 20
threshold_max_loudness = 200
threshold_motion = 2


def main():
    if len(sys.argv) < 3:
        print('Usage: {} input_file plot_dir'.format(sys.argv[0]))
        sys.exit(1)
    create_plot(sys.argv[1], sys.argv[2])


def create_plot(input_file, plot_dir):
    print('Reading file {}'.format(input_file))
    dat = pd.read_csv(input_file, dtype=float, skipinitialspace=True, parse_dates=[0], infer_datetime_format=True)
    date = dat['time']

    smooth_data(dat)
    interpret_sleep(dat)
    sleep_start, sleep_end = extract_sleep_start_end(dat)

    fig, axes = plt.subplots(nrows=4, figsize=(8, 10))

    ax = axes[0]
    title = '{}  -  {}'.format(date[0].strftime('%d.%m.%Y  %H:%M'),
                               date[len(date) - 1].strftime('%d.%m.%Y  %H:%M'))
    ax.set_title(title)
    plot_sleep(ax, sleep_end, sleep_start)
    ax.plot(date, dat['temperature'], color='firebrick')
    ax.set_ylabel('Temperature [°C]', color='firebrick')

    ax2 = ax.twinx()
    ax2.plot(date, dat['humidity'], color='royalblue')
    ax2.set_ylabel('Humidity [%]', color='royalblue')
    format_time_axis(ax)

    ax = axes[1]
    plot_sleep(ax, sleep_end, sleep_start)
    ax.plot(date, dat['light_mean'], color='orange')
    ax.set_ylabel('Average light', color='orange')

    ax2 = ax.twinx()
    ax2.plot(date, dat['light_max'], color='orangered')
    ax2.set_ylabel('Max light', color='orangered')
    format_time_axis(ax)

    ax = axes[2]
    plot_sleep(ax, sleep_end, sleep_start)
    ax.plot(date, dat['loudness_mean'], color='limegreen')
    ax.set_ylabel('Average loudness', color='limegreen')

    ax2 = ax.twinx()
    ax2.plot(date, dat['loudness_max'], color='darkgreen')
    ax2.set_ylabel('Max loudness', color='darkgreen')
    format_time_axis(ax)

    ax = axes[3]
    plot_sleep(ax, sleep_end, sleep_start)
    ax.plot(date, dat['motion'], color='purple')
    ax.set_ylabel('Motion', color='purple')

    ax2 = ax.twinx()
    date_melato = date[dat['button'] == 1]
    ax2.vlines(date_melato, [0] * len(date_melato), [1] * len(date_melato),
               color='deeppink', linestyles='dashed', linewidth=3)
    ax2.set_ylabel('Melatonin', color='deeppink')
    format_time_axis(ax)

    plt.tight_layout()

    filename = date[0].strftime('%Y-%m-%d_%H%M') + '.png'
    fig_path = os.path.join(plot_dir, filename)
    print('Writing file to {}'.format(fig_path))
    plt.savefig(fig_path, dpi=150)


def plot_sleep(ax, sleep_end, sleep_start):
    for j in range(0, len(sleep_start)):
        ax.axvspan(sleep_start[j], sleep_end[j], alpha=0.3, color='gray')


def format_time_axis(axis):
    hours = mdates.HourLocator()
    minutes = mdates.MinuteLocator([15, 30, 45])
    hours_fmt = mdates.DateFormatter('%H:%M')
    axis.xaxis.set_major_locator(hours)
    axis.xaxis.set_major_formatter(hours_fmt)
    axis.xaxis.set_minor_locator(minutes)
    axis.format_xdata = mdates.DateFormatter('%H:%M')


def interpret_sleep(data):
    # Add new columns
    data['sleep'] = [1] * len(data)
    data.loc[0, 'sleep'] = 0

    # Check sensors values
    for i in range(0, len(data)):
        if data.loc[i, 'loudness_mean'] > threshold_avg_loudness \
                or data.loc[i, 'loudness_max'] > threshold_max_loudness:
            data.loc[i, 'sleep'] = 0
        if data.loc[i, 'motion'] > threshold_motion:
            data.loc[i, 'sleep'] = 0

    # Filter out outliers
    data['sleep'] = data.loc[:, 'sleep'].rolling(window=3, center=True).min()
    data['sleep'] = data.loc[:, 'sleep'].rolling(window=3, center=True).max()
    data['sleep'] = data.loc[:, 'sleep'].rolling(window=3, center=True).max()
    data['sleep'] = data.loc[:, 'sleep'].rolling(window=3, center=True).min()


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


def smooth_data(data):
    data['temperature'] = data.loc[:, 'temperature'].rolling(window=7, center=True).mean()
    data['humidity'] = data.loc[:, 'humidity'].rolling(window=7, center=True).mean()
    data['loudness_mean'] = data.loc[:, 'loudness_mean'].rolling(window=7, center=True).mean()
    data['loudness_max'] = data.loc[:, 'loudness_max'].rolling(window=7, center=True).mean()
    data['motion'] = data.loc[:, 'motion'].rolling(window=7, center=True).mean()


if __name__ == '__main__':
    main()

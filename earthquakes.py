from bs4 import BeautifulSoup

import urllib.request
import datetime
import collections

import matplotlib.pyplot as plt
import math
import argparse
import os

# store historic values
all_dates = []
all_seconds = []
all_latitudes = []
all_longitudes = []
all_coordinates = []
all_depths = []
all_magnitudes = []
all_time_diffs = []
big_magnitude = 6.0
earthquakes_after_big = []
time_diffs_grouped = {}

# Parse verbose argument
parser = argparse.ArgumentParser(description="Earthquakes Collector - CLCERT Randomness Beacon")
parser.add_argument("--only",
                    action="store", dest="unique_year", default=0, type=int)
parser.add_argument("--first",
                    action="store", dest="first_year", default=0, type=int)
parser.add_argument("--last",
                    action="store", dest="last_year", default=0, type=int)
options = parser.parse_args()

# set year limits
if options.unique_year != 0:
    first_year = last_year = options.unique_year
else:
    first_year = options.first_year
    last_year = options.last_year


# write data to files
def write_data(data, filename):
    try:
        with open(filename, 'a') as f:
            f.write(str(data) + '\n')
            f.close()
    except FileNotFoundError:
        os.makedirs(''.join([e + '/' for e in filename.split('/') if e][0:-1]))


# complete date for url in sismologia web page
def complete_date_for_url(number):
    return str(number) if len(str(number)) == 2 else '0' + str(number)


# main function that collect events
def collect_events():
    total_earthquakes = 0
    years = range(first_year, last_year + 1)  # set range of years
    months = range(1, 13)
    days = range(1, 32)
    collect_eq_after_big = False
    big_date = datetime.datetime(first_year, 1, 1)

    for year in years:
        for month in months:
            for day in days:
                url = 'http://sismologia.cl/events/listados/' + str(year) + '/' + complete_date_for_url(month) + '/' + str(year) + complete_date_for_url(month) + complete_date_for_url(day) + '.html'
                try:
                    web = urllib.request.urlopen(url)
                    soup = BeautifulSoup(web, "html.parser")
                    earthquakes_text = soup.findAll("tr", {'class': ['impar', 'par']})[1:]

                    for earthquake_text in earthquakes_text:
                        params = []
                        for parameter in earthquake_text.contents:
                            params.append(parameter.text)
                        
                        date_time = datetime.datetime.strptime(params[0], '%d/%m/%Y %H:%M:%S')  # date
                        latitude = "%s" % (params[2])  # latitude
                        longitude = "%s" % (params[3])  # longitude
                        depth = "%s" % (params[4])  # depth
                        magnitude = "%s" % (params[5].split(' ')[0]) # magnitude
                        
                        # clean data filtering by coordinate or magnitude
                        if magnitude == '' or magnitude == '0.0' or magnitude == 'Mw' or float(magnitude) < 3.0 or \
                                float(latitude) < -60 or float(latitude) > -12 or \
                                float(longitude) < -81 or float(longitude) > -60:
                            continue

                        total_earthquakes += 1
                        all_dates.append(date_time)
                        all_seconds.append(date_time.second)
                        all_coordinates.append((latitude, longitude))
                        all_latitudes.append(latitude)
                        all_longitudes.append(longitude)
                        all_depths.append(float(depth))
                        all_magnitudes.append(float(magnitude))

                        if float(magnitude) >= 6.5:
                            print(date_time)

                        # if float(magnitude) == big_magnitude and collect_eq_after_big == False:
                        #     collect_eq_after_big = True
                        #     big_date = date_time
                        #     print('date of ' + str(big_magnitude) + ': ' + big_date.isoformat())
                        # if collect_eq_after_big:
                        #     earthquakes_after_big.append((date_time, magnitude))
                        #     if (date_time - big_date).total_seconds() > 2592000:
                        #         collect_eq_after_big = False
                        #         print('eqs after big in next 30 days: ' + str(len(earthquakes_after_big)))
                        #         del earthquakes_after_big[:]

                except urllib.error.HTTPError:
                    continue

    # time diff
    all_dates.sort()
    prev = ''
    for date in all_dates:
        if prev == '':
            prev = date
            diff = 0
            all_time_diffs.append(diff)
        else:
            diff = date - prev
            prev = date
            all_time_diffs.append(diff.total_seconds()/60)

    return total_earthquakes


def plot_data():
    plt.hist(all_time_diffs, bins='auto')
    plt.show()


def calculate_cluster_diffs(diff):
    return int(diff // 1) * 1


def group_data(data, cluster_fn=lambda x: x):
    grouped_data = {}
    factor = (1/len(data) * 100)
    for value in data:
        cluster = cluster_fn(value)
        if cluster in grouped_data:
            grouped_data[cluster] += factor
        else:
            grouped_data[cluster] = factor
    return grouped_data


def save_grouped_data_with_pctg(dataname, column_label, grouped_data):
    if first_year == last_year:
        folder = 'reports/' + str(first_year) + '/'
    else:
        folder = 'reports/' + str(first_year) + '-' + str(last_year) + '/'
    filename = folder + dataname + '_' + str(first_year) + '_' + str(last_year) + '_percentage'
    write_data(column_label + ',' + '%', filename + '.csv')
    for k, v in collections.OrderedDict(sorted(grouped_data.items())).items():
        write_data(str(k) + ',' + '%.4f' % v, filename + '.csv')


def save_accumulated(dataname, grouped_data):
    if first_year == last_year:
        folder = 'reports/' + str(first_year) + '/'
    else:
        folder = 'reports/' + str(first_year) + '-' + str(last_year) + '/'
    filename = folder + dataname + '_' + str(first_year) + '_' + str(last_year) + '_factor'
    acc = 0
    write_data('{', filename + '.json')
    for k, v in collections.OrderedDict(sorted(grouped_data.items())).items():
        write_data("\"" + str(k) + "\"" + ':' + '%.4f' % (float(acc + v) / 100) + ",", filename + '.json')
        acc += v
    write_data('}', filename + '.json')


def calculate_most_frequent_event(values_dict):
    high_freq = 0
    most_freq = ''
    for value in values_dict:
        if values_dict[value] > high_freq:
            most_freq = value
            high_freq = values_dict[value]
    return most_freq, high_freq


def most_frequent(values_dict, title):
    most_freq = calculate_most_frequent_event(values_dict)
    return title + ' -> ' + str(most_freq[0]) + ': ' + '%.3f' % (most_freq[1]) + '% (' + entropy_bits(most_freq[1]) + ')'


def entropy_bits(percentage):
    prob = percentage / 100
    return '%.4f' % (math.log((1 / prob), 2))


def plot_magnitude_date(f, l, m):
    diff_and_magnitude = []
    first_day = datetime.datetime(f, 2, 1)
    last_day = datetime.datetime(l, 12, 31)
    for i in range(len(all_dates)):
        if first_day <= all_dates[i] <= last_day and float(all_magnitudes[i]) < m:
            diff = (all_dates[i] - first_day)
            diff_and_magnitude.append((diff.total_seconds() / 3600, all_magnitudes[i]))
            # diff_and_magnitude.append((all_dates[i], all_magnitudes[i]))
    diff_and_magnitude = sorted(diff_and_magnitude, key=lambda tup: tup[0])
    plt.scatter(*zip(*diff_and_magnitude))
    plt.show()


def plot_diff_date(f, l, max_diff):
    date_and_diff = []
    first_day = datetime.datetime(f, 2, 1)
    last_day = datetime.datetime(l, 12, 31)
    for i in range(len(all_dates)):
        if first_day <= all_dates[i] <= last_day and all_time_diffs[i] < max_diff:
            diff_with_first = (all_dates[i] - first_day)
            # date_and_diff.append((diff_with_first.total_seconds() / 3600, all_time_diffs[i]))
            date_and_diff.append((all_dates[i], all_time_diffs[i]))
    diff_and_magnitude = sorted(date_and_diff, key=lambda tup: tup[0])
    plt.scatter(*zip(*diff_and_magnitude))
    plt.show()


def plot_accumulated(data):
    acc_diff = []
    acc = 0
    for k, v in collections.OrderedDict(sorted(data.items())).items():
        acc_diff.append((k, (acc + v)))
        acc += v
    plt.scatter(*zip(*acc_diff))
    plt.show()


print('Collecting Earthquakes from ' + str(first_year) + ' to ' + str(last_year))
a = collect_events()
plot_diff_date(first_year, last_year, 30)
# plot_magnitude_date(first_year, last_year, 10)

# print('Grouping Data...')
# seconds_grouped = group_data(all_seconds)
# magnitude_grouped = group_data(all_magnitudes)
# depth_grouped = group_data(all_depths)
# coord_grouped = group_data(all_coordinates)
# lat_grouped = group_data(all_latitudes)
# long_grouped = group_data(all_longitudes)
# time_diffs_grouped = group_data(all_time_diffs, cluster_fn=calculate_cluster_diffs)
# # plot_accumulated(time_diffs_grouped)
#
# print('Creating Reports...')
# save_grouped_data_with_pctg('seconds', 'second mark', seconds_grouped)
# save_grouped_data_with_pctg('magnitudes', 'magnitude', magnitude_grouped)
# save_grouped_data_with_pctg('depths', 'depth (km)', depth_grouped)
# save_grouped_data_with_pctg('coordinates', 'coordinate', coord_grouped)
# save_grouped_data_with_pctg('latitudes', 'latitude', lat_grouped)
# save_grouped_data_with_pctg('longitudes', 'longitude', long_grouped)
# save_grouped_data_with_pctg('time_diff', 'minute-difference between earthquakes', time_diffs_grouped)
# save_accumulated('acc_time_diff', time_diffs_grouped)
#
# # create main report
# if first_year == last_year:
#     folder = 'reports/' + str(first_year) + '/'
# else:
#     folder = 'reports/' + str(first_year) + '-' + str(last_year) + '/'
# report_name = folder + 'report_' + str(first_year) + '_' + str(last_year)
# write_data('TOTAL_EARTHQUAKES: ' + str(a), report_name)
# write_data(most_frequent(seconds_grouped, 'SECONDS'), report_name)
# write_data(most_frequent(magnitude_grouped, 'MAGNITUDE'), report_name)
# write_data(most_frequent(depth_grouped, 'DEPTH'), report_name)
# write_data(most_frequent(coord_grouped, 'COORDINATES'), report_name)
# write_data(most_frequent(lat_grouped, 'LATITUDES'), report_name)
# write_data(most_frequent(long_grouped, 'LONGITUDES'), report_name)

# plot_data()

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
                        if magnitude == '' or magnitude == '0.0' or magnitude == 'Mw' or float(magnitude) < 3.0 or float(latitude) < -60 or float(latitude) > -12 or float(longitude) < -81 or float(longitude) > -60:
                            continue

                        total_earthquakes += 1
                        all_dates.append(date_time)
                        all_seconds.append(date_time.second)
                        all_coordinates.append((latitude, longitude))
                        all_latitudes.append(latitude)
                        all_longitudes.append(longitude)
                        all_depths.append(float(depth))
                        all_magnitudes.append(float(magnitude))

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


def cluster_time_diffs():
    factor = (1/len(all_time_diffs) * 100)
    for diff in all_time_diffs:
        cluster = calculate_cluster_diffs(diff)
        if cluster in time_diffs_grouped:
            time_diffs_grouped[cluster] += factor
        else:
            time_diffs_grouped[cluster] = factor


def group_data(data):
    grouped_data = {}
    factor = (1/len(data) * 100)
    for value in data:
        if value in grouped_data:
            grouped_data[value] += factor
        else:
            grouped_data[value] = factor
    return grouped_data


def group_magnitudes():
    factor = (1/len(all_magnitudes) * 100)
    for magnitude in all_magnitudes:
        if magnitude in magnitude_grouped:
            magnitude_grouped[magnitude] += factor
        else:
            magnitude_grouped[magnitude] = factor


def group_seconds():
    factor = (1/len(all_seconds) * 100)
    for second in all_seconds:
        if second in seconds_grouped:
            seconds_grouped[second] += factor
        else:
            seconds_grouped[second] = factor


def group_depths():
    factor = (1/len(all_depths) * 100)
    for depth in all_depths:
        if depth in depth_grouped:
            depth_grouped[depth] += factor
        else:
            depth_grouped[depth] = factor


def group_coordinates():
    factor = (1/len(all_coordinates) * 100)
    for coord in all_coordinates:
        if coord in coord_grouped:
            coord_grouped[coord] += factor
        else:
            coord_grouped[coord] = factor


def group_latitudes():
    factor = (1 / len(all_latitudes) * 100)
    for latitude in all_latitudes:
        if latitude in lat_grouped:
            lat_grouped[latitude] += factor
        else:
            lat_grouped[latitude] = factor


def group_longitudes():
    factor = (1 / len(all_longitudes) * 100)
    for longitude in all_longitudes:
        if longitude in long_grouped:
            long_grouped[longitude] += factor
        else:
            long_grouped[longitude] = factor


def save_clusters_diffs_pctg_data():
    if first_year == last_year:
        folder = 'reports/' + str(first_year) + '/'
    else:
        folder = 'reports/' + str(first_year) + '-' + str(last_year) + '/'
    filename = folder + 'time_diff_' + str(first_year) + '_' + str(last_year) + '_percentage'
    # for cluster in range(5000):
    #     if cluster in time_diffs_grouped:
    #       write_data(str(cluster) + ',' + '%.2f' % (time_diffs_grouped[cluster]), filename)
    for k, v in collections.OrderedDict(sorted(time_diffs_grouped.items())).items():
        write_data(str(k) + ',' + '%.2f' % v, filename + '.csv')


def save_grouped_data_with_pctg(dataname, grouped_data):
    if first_year == last_year:
        folder = 'reports/' + str(first_year) + '/'
    else:
        folder = 'reports/' + str(first_year) + '-' + str(last_year) + '/'
    filename = folder + dataname + '_' + str(first_year) + '_' + str(last_year) + '_percentage'
    for k, v in collections.OrderedDict(sorted(grouped_data.items())).items():
        write_data(str(k) + ',' + '%.4f' % v, filename + '.csv')


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


print('Collecting Earthquakes from ' + str(first_year) + ' to ' + str(last_year))
a = collect_events()

print('Grouping Data...')
seconds_grouped = group_data(all_seconds)
magnitude_grouped = group_data(all_magnitudes)
depth_grouped = group_data(all_depths)
coord_grouped = group_data(all_coordinates)
lat_grouped = group_data(all_latitudes)
long_grouped = group_data(all_longitudes)
cluster_time_diffs()

print('Creating Reports...')
save_grouped_data_with_pctg('seconds', seconds_grouped)
save_grouped_data_with_pctg('magnitudes', magnitude_grouped)
save_grouped_data_with_pctg('depths', depth_grouped)
save_grouped_data_with_pctg('coordinates', coord_grouped)
save_grouped_data_with_pctg('latitudes', lat_grouped)
save_grouped_data_with_pctg('longitudes', long_grouped)
save_clusters_diffs_pctg_data()

# create main report
if first_year == last_year:
    folder = 'reports/' + str(first_year) + '/'
else:
    folder = 'reports/' + str(first_year) + '-' + str(last_year) + '/'
report_name = folder + 'report_' + str(first_year) + '_' + str(last_year)
write_data('TOTAL_EARTHQUAKES: ' + str(a), report_name)
write_data(most_frequent(seconds_grouped, 'SECONDS'), report_name)
write_data(most_frequent(magnitude_grouped, 'MAGNITUDE'), report_name)
write_data(most_frequent(depth_grouped, 'DEPTH'), report_name)
write_data(most_frequent(coord_grouped, 'COORDINATES'), report_name)
write_data(most_frequent(lat_grouped, 'LATITUDES'), report_name)
write_data(most_frequent(long_grouped, 'LONGITUDES'), report_name)

plot_data()

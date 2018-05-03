from bs4 import BeautifulSoup

import urllib.request
import datetime
import time

import matplotlib.pyplot as plt
import numpy
import math

# store historic values
all_dates = []
all_latitudes = []
all_longitudes = []
all_coordinates = []
all_depths = []
all_magnitudes = []
all_time_diffs = []
diff_clusters = {}
magnitude_clusters = {}
depth_clusters = {}
coord_clusters = {}

# set year limits
first_year = 2018
last_year = 2018


# write data to files
def write_data(data, filename):
    with open(filename, 'a') as f:
        f.write(str(data) + '\n')
        f.close()


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
                        
                        date_time = datetime.datetime.strptime(params[0], '%d/%m/%Y %H:%M:%S')

                        latitude = "%s" % (params[2])  # latitude
                        longitude = "%s" % (params[3])  # longitude
                        depth = "%s" % (params[4])  # depth
                        magnitude = "%s" % (params[5].split(' ')[0]) # magnitude
                        
                        # clean data filtering by coordinate or magnitude
                        if magnitude == '' or magnitude == '0.0' or magnitude == 'Mw' or float(magnitude) < 3.0 or float(latitude) < -60 or float(latitude) > -12 or float(longitude) < -81 or float(longitude) > -60:
                            continue

                        total_earthquakes += 1
                        all_dates.append(date_time)
                        all_coordinates.append((latitude, longitude))
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
    plt.hist(all_magnitudes, bins='auto')
    plt.show()


def calculate_cluster_diffs(diff):
    return int(diff // 5) * 5


def calculate_cluster_depth(depth):
    return int(depth // 10) * 10


def calculate_cluster_coord(coord):
    lat = coord[0]
    lon = coord[1]
    lat_cl = float('%.1f' % (float(lat)))
    lon_cl = float('%.1f' % (float(lon)))
    return lat_cl, lon_cl


def cluster_time_diffs():
    factor = (1/len(all_time_diffs) * 100)
    for diff in all_time_diffs:
        cluster = calculate_cluster_diffs(diff)
        if cluster in diff_clusters:
            diff_clusters[cluster] += factor
        else:
            diff_clusters[cluster] = factor


def cluster_magnitudes():
    factor = (1/len(all_magnitudes) * 100)
    for magnitude in all_magnitudes:
        if magnitude in magnitude_clusters:
            magnitude_clusters[magnitude] += factor
        else:
            magnitude_clusters[magnitude] = factor


def cluster_depths():
    factor = (1/len(all_depths) * 100)
    for depth in all_depths:
        cluster = calculate_cluster_depth(depth)
        if cluster in depth_clusters:
            depth_clusters[cluster] += factor
        else:
            depth_clusters[cluster] = factor    


def cluster_coordinates():
    factor = (1/len(all_coordinates) * 100)
    for coord in all_coordinates:
        cluster = calculate_cluster_coord(coord)
        if cluster in coord_clusters:
            coord_clusters[cluster] += factor
        else:
            coord_clusters[cluster] = factor


def save_clusters_diffs_pctg_data():
    if first_year == last_year:
        folder = 'reports/' + str(first_year) + '/'
    else:
        folder = 'reports/' + str(first_year) + '-' + str(last_year) + '/'
    filename = folder + 'time_diff_' + str(first_year) + '_' + str(last_year) + '_percentage'
    for cluster in range(5000):
        if cluster in diff_clusters:
            # write_data(str(cluster) + ': ' + '%.2f' % (diff_clusters[cluster]) + '%', filename)
            write_data(str(cluster) + ',' + '%.2f' % (diff_clusters[cluster]), filename)


def save_clusters_magnitudes_pctg_data():
    if first_year == last_year:
        folder = 'reports/' + str(first_year) + '/'
    else:
        folder = 'reports/' + str(first_year) + '-' + str(last_year) + '/'
    filename = folder + 'magnitude_' + str(first_year) + '_' + str(last_year) + '_percentage'
    for magn in numpy.arange(0,9,0.1):
        if magn in magnitude_clusters:
            # write_data(str(magn) + ': ' + '%.2f' % (magnitude_clusters[magn]) + '%', filename)
            write_data(str(magn) + ',' + '%.2f' % (magnitude_clusters[magn]), filename)


def save_clusters_depths_pctg_data():
    if first_year == last_year:
        folder = 'reports/' + str(first_year) + '/'
    else:
        folder = 'reports/' + str(first_year) + '-' + str(last_year) + '/'
    filename = folder + 'depth_' + str(first_year) + '_' + str(last_year) + '_percentage'
    for depth in range(1000):
        if depth in depth_clusters:
            # write_data(str(depth) + ': ' + '%.2f' % (depth_clusters[depth]) + '%', filename)
            write_data(str(depth) + ',' + '%.2f' % (depth_clusters[depth]), filename)


def save_clusters_coordinates_pctg_data():
    if first_year == last_year:
        folder = 'reports/' + str(first_year) + '/'
    else:
        folder = 'reports/' + str(first_year) + '-' + str(last_year) + '/'
    filename = folder + 'coordinates_' + str(first_year) + '_' + str(last_year) + '_percentage'
    for coord in coord_clusters:
        # write_data(str(coord) + ': ' + '%.2f' % (coord_clusters[coord]) + '%', filename)
        write_data(str(coord) + ',' + '%.2f' % (coord_clusters[coord]), filename)


def save_clusters_data():
    save_clusters_coordinates_pctg_data()
    save_clusters_depths_pctg_data()
    save_clusters_diffs_pctg_data()
    save_clusters_magnitudes_pctg_data()


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
    return title + ' -> ' + str(most_freq[0]) + ': ' + '%.2f' % (most_freq[1]) + '% (' + entropy_bits(most_freq[1]) + ')'


def entropy_bits(percentage):
    prob = percentage / 100
    return '%.4f' % (math.log((1 / prob), 2))


def create_report(total_earthquakes):
    if first_year == last_year:
        folder = 'reports/' + str(first_year) + '/'
    else:
        folder = 'reports/' + str(first_year) + '-' + str(last_year) + '/'
    report_name = folder + 'report_' + str(first_year) + '_' + str(last_year)
    write_data('TOTAL_EARTHQUAKES: ' + str(total_earthquakes), report_name)
    write_data(most_frequent(diff_clusters, 'TIME_DIFF'), report_name)
    write_data(most_frequent(magnitude_clusters, 'MAGNITUDE'), report_name)
    write_data(most_frequent(depth_clusters, 'DEPTH'), report_name)
    write_data(most_frequent(coord_clusters, 'COORDINATES'), report_name)


a = collect_events()
cluster_time_diffs()
cluster_magnitudes()
cluster_depths()
cluster_coordinates()
# save_clusters_data()
# create_report(a)
plot_data()

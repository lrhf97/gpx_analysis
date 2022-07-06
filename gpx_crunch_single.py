from IPython.display import display
import gpxpy
import gpxpy.gpx

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import PercentFormatter

from geopy.distance import distance
from geopy.distance import geodesic
from geopy import distance
import math

import haversine as hs
import numpy as np

import datetime
from time import strftime
from time import gmtime

import folium
from folium.features import DivIcon

plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

name = 'Bull_Run_50M_2018'

with open('Routes/my_runs/'+name+'.gpx', 'r') as gpx_file:
    route = gpxpy.parse(gpx_file)

# making a dictionary that can be converted to Pandas Dataframe
route_info = []

for track in route.tracks:
    for segment in track.segments:
        for point in segment.points:
            route_info.append({
                'time': point.time,
                'latitude': point.latitude,
                'longitude': point.longitude,
                'elevation': point.elevation
            })

df = pd.DataFrame(route_info)


def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    distance = hs.haversine(
        point1=(lat1, lon1),
        point2=(lat2, lon2),
        unit=hs.Unit.MILES
    )
    return np.round(distance, 8)


distances = [np.nan]
# cap_mph = 10
# distance_cap = 1/(60/cap_mph*60)

for i in range(len(df)):
    if i == 0:
        continue
    else:
        unit_dist = haversine_distance(
            lat1=df.iloc[i - 1]['latitude'],
            lon1=df.iloc[i - 1]['longitude'],
            lat2=df.iloc[i]['latitude'],
            lon2=df.iloc[i]['longitude']
        )
        distances.append(unit_dist)

df['distance'] = distances
df['distance'] = df['distance'].interpolate().fillna(0)

df['elevation_change'] = df['elevation'].diff()
df['cum_elevation'] = df['elevation_change'].cumsum()
df['cum_distance'] = df['distance'].cumsum()
# df = df.fillna(0)

df['step_feet'] = df['distance'] * 5280

# assign points to particular mile


def make_mile_segments(row):
    return row['cum_distance']//1 + 1


df['mile_num'] = df.apply(make_mile_segments, axis=1)


grade_cap_high = 30
conversion_factor = 0.62137119
gradient_point = [np.nan]
for ind, row in df.iterrows():
    if ind == 0:
        continue
    grade = (row['elevation_change'] /
             ((row['distance']/conversion_factor*1000)+1))*100
    if abs(grade) > grade_cap_high:
        gradient_point.append(np.nan)
    else:
        gradient_point.append(np.round(grade, 1))

df['gradient_point'] = gradient_point
# df['gradient_point'] = df['gradient_point'].interpolate().fillna(0)

# bin the gradients
bin_labels_cut = ['bigDown', 'down', 'flat', 'up', 'bigUp']
bin_cuts = [-30, -15, -5, 5, 15, 30]
df['gradient_rating'] = pd.cut(df['gradient_point'],
                               bins=bin_cuts,
                               labels=bin_labels_cut)

# Alt bin grouping - gradients more precisely
bins_ex = pd.IntervalIndex.from_tuples([
    (-30, -10),
    (-10, -5),
    (-5, -3),
    (-3, -1),
    (-1, 0),
    (0, 1),
    (1, 3),
    (3, 5),
    (5, 7),
    (7, 10),
    (10, 12),
    (12, 15),
    (15, 20)
], closed='left')

# df['gradient_range'] = pd.cut(df['gradient_point'], bins=bins_ex)

# histogram support for

# mygradient_details=[]


# for gr_range in df['gradient_range'].unique():
#     subset = df[df['gradient_range']==gr_range]
#     # Statistics
#     total_distance = subset['distance'].sum()
#     pct_of_total_run = (subset['distance'].sum()/df['distance'].sum())*100
#     elevation_gain = subset[subset['elevation_change']>0]['elevation_change'].sum()
#     elevation_lost = subset[subset['elevation_change']<0]['elevation_change'].sum()

#     # Save Results
#     mygradient_details.append({
#         'gradient_range': gr_range,
#         'total_distance': np.round(total_distance, 2),
#         'pct_of_total_ride': np.round(pct_of_total_run, 2),
#         'elevation_gain': np.round(elevation_gain, 2),
#         'elevation_lost': np.round(np.abs(elevation_lost), 2)
#     })

# mygradient_details_df = pd.DataFrame(mygradient_details).sort_values(by='gradient_range').reset_index(drop=True)

# colors = [
#     '#0d46a0', '#2f3e9e', '#2195f2', '#4fc2f7',
#     '#a5d6a7', '#66bb6a', '#fff59d', '#ffee58',
#     '#ffca28', '#ffa000', '#ff6f00', '#f4511e', '#bf360c'
# ]
# custom_text = [f'''<b>{gr}%</b> - {dst}miles''' for gr, dst in zip(
#     mygradient_details_df['gradient_range'].astype('str'),
#     mygradient_details_df['total_distance']
# )]

# save point by point
df.to_csv('data/my_route_csv/'+name+'.csv', index=False)

# save gradient table for histogram
# mygradient_details_df.to_csv('data/my_route_csv/'+name+'_GT.csv', index=False)

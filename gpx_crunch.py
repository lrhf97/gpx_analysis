import gpxpy
import gpxpy.gpx

import glob

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
from IPython.display import display

# name = 'vhtrc-mmt-training-two-2021'

# make list of the files
files = glob.glob('Routes/*.gpx')
df_list=[]

# start the loop to crunch each file
for f in files:
    with open(f, 'r') as gpx_file:
        route = gpxpy.parse(gpx_file)
    
    # making a dictionary that can be converted to Pandas Dataframe
    route_info=[]

    for track in route.tracks:
        for segment in track.segments:
            for point in segment.points:
                route_info.append({
                    'time': point.time,
                    'latitude': point.latitude,
                    'longitude':point.longitude,
                    'elevation': point.elevation
                })
    df_list.append(f[7:-4])

    df = pd.DataFrame(route_info)

    # Get the distance between each point and total distance
    def haversine_distance(lat1, lon1, lat2, lon2) -> float:
        distance = hs.haversine(
            point1=(lat1,lon1),
            point2=(lat2,lon2),
            unit=hs.Unit.MILES
        )
        return np.round(distance,8)

    distances = [np.nan]
    cap_mph = 10
    distance_cap = 1/(60/cap_mph*60)

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
            # if unit_dist > distance_cap:
            #     distances.append(np.nan)
            # else:
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
        return row['cum_distance']//1 +1
    df['mile_num'] = df.apply(make_mile_segments, axis=1)

    # start the gradient calcs
    grade_cap_high = 30
    conversion_factor = 0.62137119
    gradient_point =[np.nan]
    for ind, row in df.iterrows():
        if ind == 0:
            continue
        grade = (row['elevation_change'] / ((row['distance']/conversion_factor*1000)+1))*100
        if abs(grade) > grade_cap_high :
            gradient_point.append(np.nan)
        else:
            gradient_point.append(np.round(grade,1))

    df['gradient_point'] = gradient_point
    df['gradient_point'] = df['gradient_point'].interpolate().fillna(0)

    # bin the gradients
    bin_labels_cut = ['bigDown', 'down', 'flat', 'up', 'bigUp']
    bin_cuts=[-30, -15, -5, 5, 15, 30]
    df['gradient_rating'] = pd.cut(df['gradient_point'],
                                bins=bin_cuts,
                                labels=bin_labels_cut)

    df.to_csv('data/route_csv/'+f[7:-4]+'.csv', index=False)
    
# df_list_dict = {'races':df_list}
dfdf_list = pd.DataFrame({'races':df_list}) 
dfdf_list.to_csv('data/df_list.csv', index=False)
df_list
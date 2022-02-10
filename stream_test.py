import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from streamlit_folium import folium_static
import folium
from folium.features import DivIcon

from IPython.display import display



df_list = pd.read_csv('data/df_list.csv')
col_list = ['race','cum_elevation', 'cum_distance']

grade_race_dict ={}
grade_labels_it = ['flat', 'up', 'down', 'bigUp', 'bigDown']
grade_labels3 = ['flat', 'up', 'down', 'bigUp', 'bigDown', 'Total_Distance']
all_elev_dict ={}
# col_list = ['cum_elevation', 'cum_distance']

race_total = pd.DataFrame([], columns=col_list)
for r in df_list['races']:
    rdf = pd.read_csv('data/route_csv/'+r+'.csv')
    race_info = rdf[['cum_elevation', 'cum_distance','latitude','longitude','mile_num']]
    race_info.insert(0,'race',r)
    race_total = pd.concat([race_total,race_info], ignore_index=True)

    # grade level df creation
    how_run_grade3 =[]
    # diff_grades = rdf['gradient_rating'].unique()
    for i in grade_labels_it:
        how_run_grade3.append(np.round(rdf[rdf['gradient_rating'] == i]['distance'].sum(),2))
    how_run_grade3.append(np.round(rdf['distance'].sum(),2))
    for i in how_run_grade3:
        grade_race_dict[r] = how_run_grade3

# make df of the gradient ratings
all_race_df = pd.DataFrame.from_dict(grade_race_dict,orient ='index',columns=grade_labels3)

# Streamlit formatting and layout

st.set_page_config(layout = "wide")
st.markdown("""# VHTRC Race Elevation Profiles...""")

space1,col3 = st.columns((1,30))


with col3: 
    
    default_races = ['twot-2013', 'vickis-death-march', 'vhtrc-waterfall-50k']
    races = race_total['race'].unique()
    selected_races = st.multiselect('Select race', races, default_races)
    df3 = race_total.query('race in @selected_races')


    fig = px.line(df3, x='cum_distance', y = 'cum_elevation',color ='race', title ='Elevation for Selected Races')
    st.plotly_chart(fig, use_container_width=True)

space4,col5 = st.columns((1,30))

with col5:
    st.subheader("Course and mile markers ")
    default_race = [selected_races[0]]
    # races = race_total['race'].unique()
    selected_races = st.multiselect('Select race', selected_races, default_race)[0]
    df4 = race_total.query('race in @selected_races')

    def find_neighbours(value, df, colname):
        exactmatch = df[df[colname] == value]
        if not exactmatch.empty:
            return exactmatch['cum_distancce']
        else:
            # lowerneighbour_ind = df[df[colname] < value][colname].idxmax()
            upperneighbour_ind = df[df[colname] > value]['cum_distance'].min()
            return upperneighbour_ind 

    def make_mile_segments(row):
        return row['cum_distance']//1 +1

    df4['mile_num'] = df4.apply(make_mile_segments, axis=1)

    # find the begining location of each mile
    def mile_marker_loc(df):
        mile_markers = []

        for i in range(1,len(df['mile_num'].unique())):
            mileM  = find_neighbours(i, df, 'cum_distance')
            jover = df.index[df['cum_distance'] == mileM].tolist()[0]
            mile_markers.append(jover)
        return mile_markers

    def number_DivIcon(color,number):
        """ Create a 'numbered' icon
        
        """
        icon = DivIcon(
                icon_size=(150,36),
                icon_anchor=(14,40),
    #             html='<div style="font-size: 18pt; align:center, color : black">' + '{:02d}'.format(num+1) + '</div>',
                html="""<span class="fa-stack " style="font-size: 12pt" >>
                        <!-- The icon that will wrap the number -->
                        <span class="fa fa-circle-o fa-stack-2x" style="color : {:s}"></span>
                        <!-- a strong element with the custom content, in this case a number -->
                        <strong class="fa-stack-1x">
                            {:02d}  
                        </strong>
                    </span>""".format(color,number)
            )
        return icon
        
    col_hex = ['#440154',
    '#481a6c',
    '#472f7d',
    '#414487',
    '#39568c',
    '#31688e',
    '#2a788e',
    '#23888e',
    '#1f988b',
    '#22a884',
    '#35b779',
    '#54c568',
    '#7ad151',
    '#a5db36',
    '#d2e21b']

    # Graph mile markers on map with mile time on click - folium
    lat_map = df4['latitude'].mean()
    lon_map = df4['longitude'].mean()
    route_map = folium.Map(
        location=[lat_map, lon_map],
        zoom_start=12,
        tiles='OpenStreetMap',
        width= 1000,
        height=800
    )
    coordinates = [tuple(x) for x in df4[['latitude','longitude']].to_numpy()]
    folium.PolyLine(coordinates, weight=6).add_to(route_map)

    # find mile markers
    locations_to_chart = mile_marker_loc(df4)
    # find mile times
    # mile_times = run_miles(df)
    num =0
    mile=1

    for i in locations_to_chart:
        mile_hex = mile//15+1
        loc = [df4['latitude'][i], df4['longitude'][i]]
        folium.Marker(
            location=loc,
            popup="Mile " + '{:02d}'.format(mile),
            icon=folium.Icon(color='white',icon_color='white'),
            markerColor=col_hex[mile_hex]
        ).add_to(route_map)

        # folium.Marker(
        #     location=loc,
        #     popup="Mile " + '{:02d}'.format(mile)+ " "+ mile_times[mile-1],
        #     icon= number_DivIcon(col_hex[mile_hex],mile)
        # ).add_to(route_map)
        # mile+=1

        folium.Marker(
            location=loc,
            popup="Mile " + '{:02d}'.format(mile),
            icon= number_DivIcon(col_hex[mile_hex],mile)
        ).add_to(route_map)
        mile+=1



    folium_static(route_map)
    ...

space4,col6 = st.columns((1,30))




with col6:
    st.subheader("Total amount of Gradient")
    st.write(all_race_df)
    
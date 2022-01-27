import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st


df_list = pd.read_csv('data/df_list.csv')
col_list = ['race','cum_elevation', 'cum_distance']

race_total = race_total = pd.DataFrame([], columns=col_list)
for r in df_list['races']:
    rdf = pd.read_csv('data/route_csv/'+r+'.csv')
    race_info = rdf[['cum_distance','cum_elevation']]
    race_info.insert(0,'race',r)
    race_total = race_total.append(race_info, ignore_index=True)

# streamlit multiselect parameters
default_races = ['twot-2013', 'vickis-death-march', 'vhtrc-waterfall-50k']
races = race_total['race'].unique()
selected_races = st.multiselect('Select race', races, default_races)
df3 = race_total.query('race in @selected_races')


fig = px.line(df3, x='cum_distance', y = 'cum_elevation',color ='race', title ='Elevation for Selected Races')
st.plotly_chart(fig)
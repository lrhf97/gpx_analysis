import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)

df_list = pd.read_csv('data/df_list.csv')
col_list = ['race','cum_elevation', 'cum_distance']

race_total = race_total = pd.DataFrame([], columns=col_list)
for r in df_list['races']:
    rdf = pd.read_csv('data/route_csv/'+r+'.csv')
    race_info = rdf[['cum_distance','cum_elevation']]
    race_info.insert(0,'race',r)
    race_total = race_total.append(race_info, ignore_index=True)

st.write(race_total['race'].unique())

fig = px.line(race_total,x='cum_distance', y = 'cum_elevation',color ='race', title ='Elevation for races')
st.plotly_chart(fig)
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st


df_list = pd.read_csv('data/df_list.csv')
col_list = ['race','cum_elevation', 'cum_distance']

all_race_dict ={}
grade_labels_it = ['flat', 'up', 'down', 'bigUp', 'bigDown']
grade_labels3 = ['flat', 'up', 'down', 'bigUp', 'bigDown', 'Total_Distance']
all_elev_dict ={}
col_list = ['cum_elevation', 'cum_distance']

race_total = race_total = pd.DataFrame([], columns=col_list)
for r in df_list['races']:
    rdf = pd.read_csv('data/route_csv/'+r+'.csv')
    race_info = rdf[['cum_distance','cum_elevation']]
    race_info.insert(0,'race',r)
    race_total = race_total.append(race_info, ignore_index=True)

    # grade level df creation
    how_run_grade3 =[]
    # diff_grades = rdf['gradient_rating'].unique()
    for i in grade_labels_it:
        how_run_grade3.append(np.round(rdf[rdf['gradient_rating'] == i]['distance'].sum(),2))
    how_run_grade3.append(np.round(rdf['distance'].sum(),2))
    for i in how_run_grade3:
        all_race_dict[r] = how_run_grade3

# make df of the gradient ratings
all_race_df = pd.DataFrame.from_dict(all_race_dict,orient ='index',columns=grade_labels3)

# streamlit multiselect parameters
# default_races = ['twot-2013', 'vickis-death-march', 'vhtrc-waterfall-50k']
# races = race_total['race'].unique()
# selected_races = st.multiselect('Select race', races, default_races)
# df3 = race_total.query('race in @selected_races')

# fig = px.line(df3, x='cum_distance', y = 'cum_elevation',color ='race', title ='Elevation for Selected Races')
# st.plotly_chart(fig)

# st.write(all_race_df)

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

    

space4,col6 = st.columns((1,30))


# with col5:
#     st.subheader("World sea temperature change ")
#     ...

with col6:
    st.subheader("Total amount of Gradient")
    st.write(all_race_df)
    
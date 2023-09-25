#importing the libraaries needed for data manipulation and plots/visualizations
import streamlit as st
import pandas as pd
import numpy as np

import folium
import altair as alt
import seaborn as sns
import plost

#to allow making of a date and time dispaly feature
import datetime
import time

#app settings
st.set_page_config(
    page_title="ccc site mapper",
    layout="wide",
    page_icon="icons/sitemarker.png")

#hide the menu feature
hide_menu_style = """
        <style>
        #MainMenu {visibility:hidden;}
        footer {visibility:hidden;}
        </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

#to remove the padding on top
st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)


#our data source
data_source = 'processed_data/cleaned_data.xlsx'
df = pd.read_excel(data_source)

#sidebar
with st.sidebar:
    st.markdown(''' ### KCCB-ACTS Supported Facility Mapper''')
    st.caption("all sites supported by KCCB-ACTS under CDC's agency")
    st.markdown(''' ---''')
    st.write(f'As at August 2023, KCCB-ACTS supports {df.shape[0]} sites in {df.county.nunique()} counties')
    st.markdown('''---
                created by [Wayne Omondi](https://www.linkedin.com/in/waynewillislink/)
                ''')
    
#tabs for the main view    
Map_tab, Viz_tab  = st.tabs(["Site Locations","Data Visualizations"])

#our map
with Map_tab:
   #st.header("map here")
   map = folium.Map(location=[ -1.286389, 36.817223], 
                    zoom_start=7, 
                    min_zoom=3, 
                    max_zoom=11)
   folium.TileLayer('cartodbpositron').add_to(map)
   #folium.Marker(location=[ -1.286389, 36.817223], icon="icons/sitemarker.png").add_to(map)
   st.write(map)


#our visualization and metrics dashboard
with Viz_tab:
   st.caption("metrics as at 2023Q4 end of August 2023")
   
   show_data_toggle = st.toggle('show data')
   if show_data_toggle:
      st.dataframe(df[['mfl_code', 'facility_name', 'region',
       'county', 'sub_county', 'owner', 'txnew2023Q1', 'txnew2023Q2',
       'txnew2023Q3', 'txnew2023Q4', '2023Q1', '2023Q2', '2023Q3', '2023Q4']],
                   hide_index=True, use_container_width=True, height=125
                  )    
      
   metric1, metric2, metric3, metric4 = st.columns(4)
   with metric1:
      st.metric(label="Current on Treatment",
                value=(df['2023Q4'].sum().astype(str)), delta=(df['2023Q3'].sum().astype(str)), delta_color="inverse")
   with metric2:
      st.metric(label="New on Treatment",
                value=(np.sum(df[['txnew2023Q1', 'txnew2023Q2','txnew2023Q3', 'txnew2023Q4']], axis=1).sum().astype(str)), 
                delta=(np.sum(df[['txnew2023Q1', 'txnew2023Q2','txnew2023Q3', 'txnew2023Q4']], axis=1).sum().astype(str)))   
   with metric3:
      st.metric(label="Net New",
                value=(np.sum(df[['txnew2023Q1', 'txnew2023Q2','txnew2023Q3', 'txnew2023Q4']], axis=1).sum().astype(str)), 
                delta=(np.sum(df[['txnew2023Q1', 'txnew2023Q2','txnew2023Q3', 'txnew2023Q4']], axis=1).sum().astype(str)))   
   with metric4:
      st.metric(label="TX New Total",
                value=(np.sum(df[['txnew2023Q1', 'txnew2023Q2','txnew2023Q3', 'txnew2023Q4']], axis=1).sum().astype(str)), 
                delta=(np.sum(df[['txnew2023Q1', 'txnew2023Q2','txnew2023Q3', 'txnew2023Q4']], axis=1).sum().astype(str)))   
   #data source for regional art bar chart
   regionaltx = df.groupby(by=['region'])['2023Q4'].sum().reset_index()
   
   st.caption("ART clients on care as of August 2023")
   bar = alt.Chart(regionaltx).mark_bar().encode(
      y="region:N",
      x=alt.X("2023Q4:Q").title("Current on Care"),
      color="region")

   text = bar.mark_text(
      align="left",
      baseline="middle",
      dx=3
   ).encode(text="2023Q4")

   bar + text
   
   
    
    

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
    st.caption("a mapping of all sites supported by KCCB-ACTS with additional visualizations on key indicator elements. "
              "the first tab - Site Locations - maps all the facility, grouping them into clusters based on promixity and zoom level. "
              "it also shows popup information for each facility on click. "
              "the second tab - Data Visualization - shows various data elements and metrics with various aggregations and pivotting used.  "
              "data used extracted from 3pm reporting platform. cleaning, feature engineering and aggregations done afterwards")
    st.markdown(''' ''')
    st.markdown(''' ---''')
    st.markdown('''---
                created by [Wayne Omondi](https://www.linkedin.com/in/waynewillislink/)
                ''')
    
#tabs for the main view    
Map_tab, Viz_tab  = st.tabs(["Site Locations","Data Visualizations"])

#our map
with Map_tab:
   st.write(f'As at August 2023, KCCB-ACTS supports the following {df.shape[0]} sites in {df.county.nunique()} different counties across Kenya')
   map = folium.Map(location=[ -1.286389, 36.817223], 
                    zoom_start=7, 
                    min_zoom=3, 
                    max_zoom=11)
   folium.TileLayer('cartodbpositron').add_to(map)
   #folium.Marker(location=[ -1.286389, 36.817223], icon="icons/sitemarker.png").add_to(map)
   st.write(map)


#our visualization and metrics dashboard
with Viz_tab:
   show_data_toggle = st.toggle(label='toggle data')
   if show_data_toggle:
      st.dataframe(df[['mfl_code', 'facility_name', 'region',
       'county', 'sub_county', 'owner', 'txnew2023Q1', 'txnew2023Q2',
       'txnew2023Q3', 'txnew2023Q4', '2023Q1', '2023Q2', '2023Q3', '2023Q4']],
                   hide_index=True, use_container_width=True, height=125
                  )    
   st.caption("metrics as at 2023 Quarter 4 **(end of August 2023)**")
   metric1, metric2, metric3, metric4 = st.columns(4)
   with metric1:
      st.metric(label="Current on Treatment",
                value=(df['2023Q4'].sum().astype(str)), delta=(df['2023Q3'].sum().astype(str)), delta_color="inverse"
                )
   with metric2:
      st.metric(label="New on Treatment",
                value=(np.sum(df[['txnew2023Q1', 'txnew2023Q2','txnew2023Q3', 'txnew2023Q4']], axis=1).sum().astype(str)), 
                delta=("2022Q4"),delta_color="off"
                )
   with metric3:
      st.metric(label="Treatment Net New",
                value=(df['2023Q4'] - df['2023Q3']).sum().astype(str),
                delta=(df['2023Q3'] - df['2023Q2']).sum().astype(str),
                )
   with metric4:
      st.metric(label="""Tx Current Growth""",
                value=((f"{(df['txnew2023Q4']).sum() - (df['txnew2023Q3']).sum()}")), 
                delta=((f"- previous: {(df['txnew2023Q3']).sum() - (df['txnew2023Q2']).sum()}")), delta_color="normal"
      )
   #data source for regional art bar chart
   
   viz1, viz2, viz3 = st.columns([2,3,2])
   
   #table showing tx new per quarter per region
   with viz1:
      st.write("New on Treatment")
      st.caption("number of adults and children newly enrolled on antiretroviral therapy in each quarter of operation. this measures the ongoing scale up and uptake of art program. ")
      viz1.dataframe((df.groupby(
         by=['region'])[['txnew2023Q1','txnew2023Q2','txnew2023Q3','txnew2023Q4']]
                  .sum()
                  .reset_index()), 
               column_config={"region":"Region",
                              "txnew2023Q1":"Q1",
                              "txnew2023Q2":"Q2",
                              "txnew2023Q3":"Q3",
                              "txnew2023Q4":"Q4"}, 
               hide_index=True, height=220)

   
   regionaltx = df.groupby(by=['region'])['2023Q4'].sum().reset_index()
   with viz2:
      st.write("ART clients on Treatment")
      st.caption("number of adults and children currently receiving antiretroviral theraphy end of the period. 'current' is a state defined by treatment status when last seen i.e., end of the reporting period.")
      bar = alt.Chart(regionaltx).mark_bar().encode(
         y=alt.Y("region:N").title("").axis(labels=False),
         x=alt.X("2023Q4:Q").title("Current on Care"),
         color=alt.Color("region").scale(scheme="purplered")
         ).properties(width=500, height=260)

      text = bar.mark_text(
         align="left",
         baseline="middle",
         dx=3
      ).encode(text="2023Q4")

      bar + text
      
   with viz3:
      st.write("KCCB-ACTS sites per county")
      st.caption("a tally of health facilities grouped by county with KCCB-ACTS as the implementing partner")
      sitescount = df.county.value_counts().reset_index()

      bar = alt.Chart(sitescount).mark_bar().encode(
         y=alt.Y("county:N").title("").axis(labels=False),
         x=alt.X("count:Q").title("Number of Sites").axis(labels=False),
         color=alt.Color("county").scale(scheme="purplered")
         ).properties(width=400, height=260)

      text = bar.mark_text(
         align="left",
         baseline="middle",
         dx=3
      ).encode(text="count")

      bar + text
   
   
    
    

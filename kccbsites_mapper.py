'''
making a streamlit app that loads in a dataset from an excel file, and uses that to display a map of the passed coordinates
coordinates will have popups when clicked. app will include a dashboard with some metric cards
app should also show present date and time; a sidebar with basic information on the app; 2 tabs to act as containers for
the map and dashboard features 
use st.container() to aid responsive of elements and utilize use_container_width=True
'''
#to do that we need to import a few libraries
#importing the streamlit library to build and host the app
import streamlit as st

#importing the libraries needed for data manipulation 
import pandas as pd
import numpy as np

#for read excel files
import openpyxl

#import libraries for the mapping
import folium
from streamlit_folium import st_folium

#import libraries for visualizations
import altair as alt
import seaborn as sns
import plost

#to allow making of a date and time dispaly feature
import datetime
import time

#app settings
st.set_page_config(
    page_title="facility mapper",
    layout="wide",
    page_icon="icons/txregime.png")

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

#load css for extra styling we cant do here
with open("extra_styling/style.css") as f:
   st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#loading our data sources
data_source = 'processed_data/cleaned_data.xlsx'
df = pd.read_excel(data_source)

tested_data = 'raw_data/tested_totals.xlsx'
tested_df = pd.read_excel(tested_data)

entry_point_data = "raw_data/entry_point_tests.xlsx"
entrypoint_tests = pd.read_excel(entry_point_data)

#sidebar
with st.sidebar:
    st.header('KCCB-ACTS Supported Sites Mapper `version 1.0` ')
    st.caption("a mapping of all sites supported by KCCB-ACTS with additional visualizations on key indicator elements. "
              "The first tab - Site Locations - maps all the facility, grouping them into clusters based on promixity and zoom level. "
              "It also shows popup information for each facility on click. "
              "The second tab - Data Visualization - shows various data elements and metrics with various aggregations and pivotting used.  ")
    st.caption("Data used was extracted from 3pm reporting platform: then cleaned and prepared with feature engineering and aggregations to get the desired datasets")
    st.divider()
    st.markdown('''Made by [Wayne Omondi](https://www.linkedin.com/in/waynewillislink/)
                ''')
    
#tabs for the main view    
Map_tab, Viz_tab  = st.tabs(["Site Locations","Data Visualizations"])

#our map
with Map_tab:
   st.write(f'As at August 2023, KCCB-ACTS supports the following {df.shape[0]} sites in {df.county.nunique()} different counties across Kenya')
   sites_map = folium.Map(location=[ -1.286389, 36.817223], 
                    zoom_start=7, 
                    min_zoom=3, 
                    max_zoom=11)
   
   folium.TileLayer('cartodbpositron').add_to(sites_map)
   
   '''
   for site in sites_map.iterrows():  
    folium.Marker(list([site['lat'],site['lon']]),popup=site['facility_name']).add_to(sites_map)
   ''' 
   #folium.Marker(location=[ -1.286389, 36.817223], icon="icons/sitemarker.png").add_to(sites_map)
   st_folium(sites_map, use_container_width=True)


#our visualization and metrics dashboard
with Viz_tab:
   show_data_toggle = st.toggle(label='toggle data')
   if show_data_toggle:
      st.caption("**tip**: _once 'on' you can expand dataframe on your right and interact with the columns by sorting in ascending or descending order_")
      st.dataframe(df[['mfl_code', 'facility_name', 'region',
       'county', 'sub_county', 'owner', 'txnew2023Q1', 'txnew2023Q2',
       'txnew2023Q3', 'txnew2023Q4', '2023Q1', '2023Q2', '2023Q3', '2023Q4']],
                   hide_index=True, use_container_width=True, height=125
                  )    
   with st.container():   
      st.caption("metrics **(August 2023)**")
      metric1, metric2, metric3, metric4 = st.columns(4)
      
      #streanlit extras to style our metric cards
      from streamlit_extras.metric_cards import style_metric_cards
      
      with metric1:
         st.metric(label="Current on Treatment",
                  value=(df['2023Q4'].sum().astype(str)),
                  delta=(f"- {(df['2023Q3'].sum().astype(str))}")
                  )
      with metric2:
         st.metric(label="Total Tested",
                  value=(np.sum(tested_df[['number_tested']], axis=1).sum().astype(str)), 
                  delta=("2022Q4"),delta_color="off"
                  )
      with metric3:
         st.metric(label="New on Treatment",
                  value=(df[['txnew2023Q4']]).sum().sum().astype(str),
                  delta=(f"-{(df['txnew2023Q3']).sum().astype(str)}"),
                  )
      with metric4:
         st.metric(label="""Tx Current Growth Q4""",
                  value=((f"{(df['2023Q4']).sum() - (df['2023Q3']).sum()}")), 
                  delta=((f"{(df['2023Q3']).sum() - (df['2023Q2']).sum()}")), delta_color="inverse"
         )
      
      #styling our metric cards
      style_metric_cards(background_color="#e4e4e4", 
                        border_left_color="fca311", 
                        border_color='#e4e4e4', box_shadow=True)
      
   #data source for regional art bar chart
   
   viz1, viz2, viz3 = st.columns([2,3,2])
   
   #table showing tx new per quarter per region
   with viz1:
      with st.container():
         st.subheader("New on Treatment", divider="grey")
         st.caption("number of adults and children newly enrolled on antiretroviral therapy in each quarter of operation. all individuals initiating ART during the period. ")
         viz1.dataframe((df.groupby(
            by=['region'])[['txnew2023Q1','txnew2023Q2','txnew2023Q3','txnew2023Q4']]
                     .sum()
                     .reset_index()), 
                  column_config={"region":"Region",
                                 "txnew2023Q1":"Q1",
                                 "txnew2023Q2":"Q2",
                                 "txnew2023Q3":"Q3",
                                 "txnew2023Q4":"Q4"}, 
                  hide_index=True, height=220, use_container_width=True)

   #new df from use
   regionaltx = df.groupby(by=['region'])['2023Q4'].sum().reset_index()
   
   with viz2:
      with st.container():
         st.subheader("ART clients on Treatment", divider="grey")
         st.caption("number of adults and children currently receiving antiretroviral theraphy end of the period. 'current' is a state defined by treatment status when last seen i.e., end of the reporting period.")
         txcurrbar = alt.Chart(regionaltx).mark_bar().encode(
            y=alt.Y("region:N", 
                  sort=alt.EncodingSortField(field="2023Q4", 
                                             order='descending'),
                  axis=alt.Axis(labelFontSize=10)).title(""),
            x=alt.X("2023Q4:Q").title("Current on Care"),
            color=alt.Color("region",legend=None).scale(scheme="category20c")
            ).properties(width=500, height=260)
         

         text = txcurrbar.mark_text(
            align="left",
            baseline="middle",
            dx=3
         ).encode(text="2023Q4")

         st.altair_chart(txcurrbar + text, use_container_width=True)
      
   with viz3:
      with st.container():
         st.subheader("Sites per county", divider="grey")
         st.caption("a tally of health facilities grouped by county with KCCB-ACTS as the implementing partner")
         sitescount = df.county.value_counts().reset_index()

         site_count_bar = alt.Chart(sitescount).mark_bar().encode(
            y=alt.Y("county:N",sort=alt.EncodingSortField(field='count',
                                                         order='ascending'),
                  axis=alt.Axis(labelFontSize=10)).title(""),
            x=alt.X("count:Q").title("Number of Sites").axis(labels=False),
            color=alt.Color("county",legend=None).scale(scheme="category20c")
            ).properties(height=270)

         text = site_count_bar.mark_text(
            align="left",
            baseline="middle",
            dx=3
         ).encode(text="count")

         st.altair_chart(site_count_bar + text, use_container_width=True)
      
   
   viznext1, viznext2 = st.columns(2)
   with viznext1:
      with st.container():
         st.subheader("Testing service delivery", divider="grey")
         st.caption("all clients from various testing service points who were elligible for HIV testing services, were tested and have known HIV results. ")
                 
         entry_point_tests = alt.Chart(entrypoint_tests).mark_bar().encode(
            x=alt.X("entry_point").title(""), 
            y=alt.Y("sum(number_tested)").title(""), 
            color=alt.Color("entry_point").scale(scheme="category20c").legend(None)
         )
         
         st.altair_chart(entry_point_tests, use_container_width=True)
      
   #create a new dataset merge tx new per county with tested per county    
   txnew_yield = (df.groupby(by=['county'])[['txnew2023Q4']].sum()).merge(tested_df,
                                                                 on=['county'],
                                                                 how='outer')
      
   #stacked area plot
   with viznext2:
      with st.container():
         st.subheader("New on ART", divider="grey")
         st.caption("visualization of how tests done resulted in new on ART clients for the month August 2023")
         
         #test_yield = alt.Chart(txnew_yield).mark_area().encode(y= alt.Y("sum(txnew2023Q4):Q, sum(tested_totals):Q"),x= alt.X("county:N"),color= alt.Color("county:N").scale(scheme="category20b"))

         #test_yield
   
    
    

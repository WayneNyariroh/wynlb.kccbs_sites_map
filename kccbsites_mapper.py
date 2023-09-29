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
from folium.plugins import MarkerCluster
from folium.plugins import FeatureGroupSubGroup

#import libraries for visualizations
import altair as alt

#to allow making of a date and time dispaly feature
import datetime
import time

pageicon = "icons/txregime.png"

#app settings
st.set_page_config(
    page_title="KCCB-ACTS: Facility Mapper FY2023",
    layout="wide",
    page_icon=pageicon,
    initial_sidebar_state="expanded")

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
df.rename(columns={"facility_name":"nameascii"}, inplace=True)

tested_data = 'raw_data/tested_totals.xlsx'
tested_df = pd.read_excel(tested_data)

entry_point_data = "raw_data/entry_point_tests.xlsx"
entrypoint_tests = pd.read_excel(entry_point_data)

#sidebar
with st.sidebar:
   cal_watch = datetime.datetime.now()
   st.button(f':clock1: {cal_watch.strftime("%d/%m/%Y  %H:%M")}', 
             disabled=True)
   st.subheader('KCCB-ACTS Supported Sites Mapper `version 1.0` ')
   st.caption("mapping of sites supported by ***KCCB-ACTS*** with additional visualizations. "
              "First tab - :orange[Site Locations] - maps all the facilities, grouping them into proximity clusters depending on zoom level. "
              "Second tab - :orange[Data Visualization] - shows various data elements and metrics with various aggregations and pivotting used.")
   st.divider()
   st.markdown('''Made by [Wayne Omondi](https://www.linkedin.com/in/waynewillislink/)
                ''')
    
#tabs for the main view    
Map_tab, Viz_tab, Code_tabs  = st.tabs(["Site Locations :earth_africa:",
                             "Data Visualizations :bar_chart:",
                             "Discards & Outtakes :disappointed:"])

#our map
with Map_tab:
   with st.container():
      #st.write(f'As at August 2023, KCCB-ACTS supports the following {df.shape[0]} sites in {df.county.nunique()} different counties across Kenya')
      st.caption("***click on the clusters to access the sites; click on the points to see site information***")
      sites_map = folium.Map(location=[ -1.286389, 36.817223], 
                             zoom_start=7, 
                             min_zoom=2, 
                             max_zoom=9)
      
      #folium.TileLayer('cartodbpositron').add_to(sites_map)
      
      
      sites_cluster = MarkerCluster().add_to(sites_map)  

      for site in df.iterrows():
         sites_coordinates = ([site[1]['lat'],site[1]['lon']])
         name = site[1]['nameascii']
         folium.Marker(sites_coordinates,
                       icon=folium.Icon(color='orange'),
                       popup=(site[1]['nameascii']+","+" located in"+" "+site[1]['sub_county']+" "+"sub county"+" "+"in"+" "+site[1]['county']+"."+" Serves "+str(site[1]['2023Q4'])+" clients on ART (close of aug 2023)"),
                             min_width=2500, 
                       tooltip="Click for Facility Information", name="nameascii").add_to(sites_cluster) 
         
       #implement a search feature on to the map with the SearchPlugin

      folium.TileLayer('cartodbpositron').add_to(sites_cluster)
         
      st_folium(sites_map, use_container_width=True)


#our visualization and metrics dashboard
with Viz_tab:
   show_data_toggle = st.toggle(label='toggle data')
   if show_data_toggle:
      st.caption("**tip**: _once 'on' you can expand dataframe on your right and interact with the columns by sorting in ascending or descending order_")
      st.dataframe(df[['mfl_code', 'nameascii', 'region','txnew2023Q1', 'txnew2023Q2','txnew2023Q3', 'txnew2023Q4', '2023Q1', '2023Q2', '2023Q3', '2023Q4']],
                   column_config={"mfl_code":"Mfl Code",
                                  "nameascii":"Facility Name",
                                  "region":"Assigned Region",
                                  "txnew2023Q1":"TX New Q1",
                                  "txnew2023Q2":"TX New Q2",
                                  "txnew2023Q3":"TX New Q3",
                                  "txnew2023Q4":"TX New Q4",
                                  "2023Q1":"TX Cur Q1",
                                  "2023Q2":"TX Cur Q2",
                                  "2023Q3":"TX Cur Q3",
                                  "2023Q4":"TX Cur Q4"
                                   },
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
                  delta=((f"{(df['2023Q3']).sum() - (df['2023Q2']).sum()} Q3 growth")), delta_color="inverse")
                  
      
      #styling our metric cards
      style_metric_cards(background_color="#EFF2F5", 
                        border_size_px=0.05,
                        border_radius_px=8,
                        border_left_color="#ED795F", 
                        border_color="#A7ADB2", box_shadow=True)
      
   #data source for regional art bar chart
   
   viz1, viz2, viz3 = st.columns([2,3,2])
   
   #table showing tx new per quarter per region
   with viz1:
      with st.container():
         st.subheader("New on Treatment", divider="grey")
         st.caption("number of adults and children newly enrolled on antiretroviral therapy in each quarter of operation. all individuals initiating ART during _FY23_ . ")
         viz1.dataframe((df.groupby(
            by=['region'])[['txnew2023Q1','txnew2023Q2','txnew2023Q3','txnew2023Q4']]
                     .sum().reset_index()), 
                  column_config={"region":"Region",
                                 "txnew2023Q1":"Q1",
                                 "txnew2023Q2":"Q2",
                                 "txnew2023Q3":"Q3",
                                 "txnew2023Q4":"Q4"}, 
                  hide_index=True, height=220, use_container_width=True)
      #st.caption("**tip:** click on columns to sort")

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
                  axis=alt.Axis(labelFontSize=11)).title(""),
            x=alt.X("2023Q4:Q").axis(tickCount=4).title(""),
            color=alt.Color("region",legend=None).scale(scheme="category20c")
            ).properties(height=270)
      

         text = txcurrbar.mark_text(
            align="left",
            baseline="middle",
            dx=3
         ).encode(text="2023Q4")

         st.altair_chart(txcurrbar + text, use_container_width=True)
      
   with viz3:
      with st.container():
         st.subheader("Sites per county", divider="grey")
         st.caption("a tally of health facilities with _KCCB-ACTS_ as the implementing partner grouped by county ")
         sitescount = df.county.value_counts().reset_index()

         site_count_bar = alt.Chart(sitescount).mark_bar().encode(
            y=alt.Y("county:N",sort=alt.EncodingSortField(field='count',
                                                         order='ascending'),
                  axis=alt.Axis(labelOverlap=False,
                                labelFontSize=11)).title(""),
            x=alt.X("count:Q").title("").axis(labels=False, tickCount=4),
            color=alt.Color("county",legend=None).scale(scheme="category20c")
            ).properties(height=270)

         text = site_count_bar.mark_text(
            align="left",
            baseline="middle",
            dx=3
         ).encode(text="count")

         st.altair_chart(site_count_bar + text, use_container_width=True)
      
   with st.container():
      st.dataframe(((df[['county','txnew2023Q1','txnew2023Q2',
               'txnew2023Q3','txnew2023Q4']].groupby(
                  by=['county'])[['txnew2023Q1',
                                    'txnew2023Q2','txnew2023Q3','txnew2023Q4']].sum()).transpose().reset_index().rename(columns={"index":"FY23 Quarter"}).set_index('FY23 Quarter')),
                  use_container_width=True)
      
   viznext1, viznext2 = st.columns([3,2])
   with viznext1:
      with st.container():
         st.subheader("Testing service delivery & Entry points", divider="grey")
         st.caption("all clients from various testing service points and testing strategies who were elligible for HIV testing services, were tested and have known HIV results **August 2023** ")
                 
         entry_point_tests = alt.Chart(entrypoint_tests).mark_bar().encode(
            x=alt.X("entry_point").title(""), 
            y=alt.Y("sum(number_tested)").title("").axis(tickCount=4), 
            color=alt.Color("entry_point").scale(scheme="category20c").legend(None)
         )
         
         text_tested = entry_point_tests.mark_text(
            align="center",
            baseline="middle",
            dx=5, dy=-6
         ).encode(text="sum(number_tested)")
         
         st.altair_chart(entry_point_tests + text_tested, use_container_width=True)
      
   #create a new dataset merge tx new per county with tested per county    
   pos_yield = (df.groupby(by=['county'])[['txnew2023Q4']].sum()).merge(tested_df, 
               on=['county'],
               how='outer').groupby(by=['region'])[['number_tested','number_positive']].sum()
                     
      
   #stacked area plot
   with viznext2:
      with st.container():
         st.subheader("Tested Positive", divider="grey")
         st.caption("Positivity yield for the month **August 2023** from the total tests done in each region")
         st.dataframe(pos_yield, column_config={"region":"Region",
                                                "number_tested":"Tests Done",
                                                "number_positive":"Postivive Results"}, width=350)
         
         #test_yield = alt.Chart(pos_yield).mark_area().encode(y= alt.Y("sum(number_tested):Q, sum(number_positive):Q"),x= alt.X("region:N"),color= alt.Color("region:N").scale(scheme="category20b"))

with Code_tabs:
   st.caption("***Some ideas, features and visualizations that didnt pan out, and missed a place in the two main tabs, but will be explored later.***")   
   st.caption("Attempted to code a stacked area chart for total tests against total positives identifed by layering the two plots above but it was mind numbing, though with use of some scaling, aggregations, melt and pivots it should be possible.")
   code_1, code_2 = st.columns([2,2])
   with code_1:
      with st.container():
         st.write("***input***")
         st.markdown('''            
            ```python
            alt.Chart(
               (sites_dataset.groupby(
                  by=['county'])[['txnew2023Q4']]
               .sum())
               .merge(tests_dataset, 
               on=['county'], how='outer')
               .set_index('county').reset_index())
               .mark_point().encode(
                  x= alt.X("county:N"),
                  y= alt.Y("number_tested:Q"))       
                                                                        
            alt.Chart(
               (sites_dataset.groupby(
                  by=['county'])[['txnew2023Q4']]
               .sum())
               .merge(
                  tests_dataset, 
                  on=['county'], how='outer')
               .set_index('county').reset_index())
               .mark_area().encode(
                  x= alt.X("county:N"), 
                  y= alt.Y("number_positive:Q"))

            (test_num + test_num.mark_line() & test_pos)
         ``` ''')
   with code_2:   
      with st.container():
         st.write("***output***")      
         test_num = alt.Chart((df.groupby(by=['county'])[['txnew2023Q4']].sum()).merge(tested_df,
                                                                        on=['county'],
                                                                        how='outer').set_index('county').reset_index()).mark_point().encode(
               x= alt.X("county:N").title(""),
               y= alt.Y("number_tested:Q").axis(tickCount=4)).properties(
            height=220)        
                                                                        
         test_pos = alt.Chart((df.groupby(by=['county'])[['txnew2023Q4']].sum()).merge(tested_df,
                                                                        on=['county'],
                                                                        how='outer').set_index('county').reset_index()).mark_area().encode(
               x= alt.X("county:N").title(""),
               y= alt.Y("number_positive:Q").axis(tickCount=4)).properties(
            height=220)

         st.altair_chart(test_num + test_num.mark_line() & test_pos, use_container_width=True)
      
   st.divider()
   with st.container():
      st.caption(" ***Ongoing work on implementing a facility search feature. Experimenting with turning the dataframe into a :green[GEOjSON] object to see if it works. Additional testing the :green[Geocoder()] plugin for the same functionality.*** ")
      st.markdown('''
               ```python        
               import SearchPlugin
               import MarkerCluster
               
               cluster = MarkerCluster().add_to(map)  
                  
               search = Search(
                  layer=cluster,
                  geom_type="Point",
                  search_label=name,
                  placeholder="Search for a Facility",
                  position="topright",
                  collapsed=False).add_to(map)                    
               ```        
                       ''')
    
    

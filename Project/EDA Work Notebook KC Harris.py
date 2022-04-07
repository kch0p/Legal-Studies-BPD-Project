#!/usr/bin/env python
# coding: utf-8

# In[36]:


# import libraries
# !pip install folium --upgrade

from numpy.random import *
import pandas as pd
from geopandas import *
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import folium
import json
import os
from branca.colormap import linear
import branca.colormap
import geopandas as gpd
from collections import defaultdict
import webbrowser

import folium.plugins # The Folium Javascript Map Library
from folium.plugins import HeatMap
from folium.plugins import HeatMapWithTime
from folium import Choropleth
from folium.map import *

# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = "all"


# # DATA PREPARATION

# In[37]:


berkeley_tracts2 = os.path.join('Census Tract Polygons 2010 (With Incom+Race+Numstops+Numschools Data).geojson')
geo_json_data2 = json.load(open(berkeley_tracts2))


stops_data = os.path.join('formatted_allstops.csv')
df = pd.read_csv(stops_data)


# In[38]:


df['Date of Stop'] = pd.to_datetime(df['Date of Stop'])
df_grouped_by_tract = df.groupby(['Census Tract']).size().to_frame(name = 'Count').sort_values("Count", ascending = False).reset_index()
df_grouped_by_tract.head()


# # CHOROPLETH with GEOJSON

# In[39]:


colormap = linear.PuBu_07.scale(
    df_grouped_by_tract.Count.min(),
    df_grouped_by_tract.Count.max())

colormap


# In[40]:


berk_coords = (37.8715, -122.2730)
berk_map = folium.Map(berk_coords, tiles='cartodbpositron', zoom_start=13.25)


folium.Choropleth(
    geo_data = geo_json_data2,
    name = 'Stops by Census Tract',
    data = df_grouped_by_tract,
    columns=['Census Tract', 'Count'],
    key_on='properties.name10',
    fill_color='PuBu',
    fill_opacity=0.9,
    nan_fill_color = 'White',
    nan_fill_opacity=.3,
    legend_name=f'Stops by Census Tract in Berkeley, CA',
    highlight=True
).add_to(berk_map)
    
    
folium.features.GeoJson(geo_json_data2,  
                        name='Tract Information',
                        style_function=lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
                        highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.10, 'weight': 0.1},
                        tooltip=folium.features.GeoJsonTooltip( fields=['name10','totalpop','numstops','medianincome','whitepop','aapop','na_aipop','aisianpop','hawaiian','mixed2','numschools'],
                                                                aliases = ['Tract Name','Total Population','Number of Stops','Median Income','Number White Residents','Number African American Residents','Number Native American/American Indian Residents','Number Asian American Residents','Number Hawaiian Residents','Number Mixed Residents','Number of Schools'],
                                                                labels=True,
                                                                sticky=False
                                                                            )
                       ).add_to(berk_map)


school_points = pd.read_csv('school points.csv')

feature_group = FeatureGroup(name='School Points')
# https://towardsdatascience.com/folium-map-how-to-create-a-table-style-pop-up-with-html-code-76903706b88a
for i in range(0,len(school_points)):
    institution_type = school_points['schooltype'].iloc[i]
    if institution_type == 'higher education':
        color = 'orange'
        icon='university'
    elif institution_type == 'middle school' or institution_type == 'elementary':
        color = 'lightblue'
        icon='book'
    else:
        color = 'darkblue'
        icon='building'
#         print('debug', color, icon)
        
    label = school_points['name'].iloc[i]

    feature_group.add_child(Marker([school_points['lat'].iloc[i],school_points['lon'].iloc[i]],
                                    popup=label, icon=folium.Icon(color=color, icon=icon,name='Schools', prefix='fa')))


berk_map.add_child(feature_group)

# https://towardsdatascience.com/how-to-step-up-your-folium-choropleth-map-skills-17cf6de7c6fe
folium.TileLayer('cartodbdark_matter',name="Dark Mode",control=True).add_to(berk_map)
folium.TileLayer('openstreetmap',name="Street Map",control=True).add_to(berk_map)

folium.LayerControl(collapsed=False).add_to(berk_map)

file_path = r"choropleth.html"
berk_map.save(file_path) # Save as html file
# print('debug','saved!')
berk_map


# # Heatmap with GEOJSON

# In[41]:


# ir_loc_nan_na = ir_BIG.dropna(subset = ['Latitude', 'Longitude'], inplace=True)

lat = df['LAT'].values 
lon = df['LONG'].values 

df_locs = np.vstack((lat, lon)).transpose().tolist() 


berk_coords = (37.8715, -122.2730)
berk_map = folium.Map(berk_coords, tiles='cartodbpositron', zoom_start=13.25)
heatmap = HeatMap(df_locs, name='Heatmap', radius = 13) 

# Add it to your Berkeley map.
heatmap.add_to(berk_map)

folium.Choropleth(
    geo_data = geo_json_data2,
    name='Tract Boundaries',
    data = df_grouped_by_tract,
    columns=['Census Tract', 'Count'],
    line_weight=.25,
    fill_opacity=0,
    opacity=0,
    highlight=True,
).add_to(berk_map)
    
    

# Convert points to GeoJson
folium.features.GeoJson(geo_json_data2,  
                        name='Tract Information',
                        style_function=lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
                        highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.10, 'weight': 0.1},
                        tooltip=folium.features.GeoJsonTooltip( fields=['name10','totalpop','numstops','medianincome','whitepop','aapop','na_aipop','aisianpop','hawaiian','mixed2','numschools'],
                                                                aliases = ['Tract Name','Total Population','Number of Stops','Median Income','Number White Residents','Number African American Residents','Number Native American/American Indian Residents','Number Asian American Residents','Number Hawaiian Residents','Number Mixed Residents','Number of Schools'],
                                                                labels=True,
                                                                sticky=False,
                                                                legend=False,
                                                                highlight=True
                                                                            )
                       ).add_to(berk_map)


steps=20
colormap = branca.colormap.linear.YlOrRd_09.scale(0, 1).to_step(steps)
gradient_map=defaultdict(dict)
for i in range(steps):
    gradient_map[1/steps*i] = colormap.rgb_hex_str(1/steps*i)
colormap.add_to(berk_map) #add color bar at the top of the map

# https://github.com/python-visualization/folium/pull/242
school_points = pd.read_csv('school points.csv')
feature_group = FeatureGroup(name='School Points')
for i in range(0,len(school_points)):
    institution_type = school_points['schooltype'].iloc[i]
    if institution_type == 'higher education':
        color = 'orange'
        icon='university'
    elif institution_type == 'middle school' or institution_type == 'elementary':
        color = 'lightblue'
        icon='book'
    else:
        color = 'darkblue'
        icon='building'
#         print('debug', color, icon)
        
    label = school_points['name'].iloc[i]

    feature_group.add_child(Marker([school_points['lat'].iloc[i],school_points['lon'].iloc[i]],
                                    popup=label, icon=folium.Icon(color=color, icon=icon,name='Schools', prefix='fa')))


berk_map.add_child(feature_group)
# berk_map.add_child(folium.map.LayerControl())     
# folium.LayerControl(collapsed=False).add_to(berk_map)


# Add dark and light mode. 
folium.TileLayer('cartodbdark_matter',name="Dark Mode",control=True).add_to(berk_map)
folium.TileLayer('openstreetmap',name="Street Map",control=True).add_to(berk_map)

folium.LayerControl(collapsed=False).add_to(berk_map)

file_path = r"heatmap.html"
berk_map.save(file_path) # Save as html file
# print('debug','saved!')
berk_map


# # CIRCLE MAP

# In[42]:


# lat = df['LAT'].values 
# lon = df['LONG'].values 

# df_locs = np.vstack((lat, lon)).transpose().tolist() 


berk_coords = (37.8715, -122.2730)
berk_map = folium.Map(berk_coords, tiles='cartodbpositron', zoom_start=13.25)
# https://medium.com/datasciencearth/map-visualization-with-folium-d1403771717#:~:text=process%20using%20CircleMaker()
locations = list(zip(df.LAT,df.LONG))

for i in range(len(locations)):
    folium.CircleMarker(location=locations[i],radius=1).add_to(berk_map)

    
    
folium.Choropleth(
    geo_data = geo_json_data2,
    name='Tract Boundaries',
    data = df_grouped_by_tract,
    columns=['Census Tract', 'Count'],
    line_weight=.25,
    fill_opacity=0,
    opacity=0,
    highlight=True,
).add_to(berk_map)
    
    

# Convert points to GeoJson
folium.features.GeoJson(geo_json_data2,  
                        name='Tract Information',
                        style_function=lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
                        highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.10, 'weight': 0.1},
                        tooltip=folium.features.GeoJsonTooltip( fields=['name10','totalpop','numstops','medianincome','whitepop','aapop','na_aipop','aisianpop','hawaiian','mixed2','numschools'],
                                                                aliases = ['Tract Name','Total Population','Number of Stops','Median Income','Number White Residents','Number African American Residents','Number Native American/American Indian Residents','Number Asian American Residents','Number Hawaiian Residents','Number Mixed Residents','Number of Schools'],
                                                                labels=True,
                                                                sticky=False,
                                                                legend=False,
                                                                highlight=True
                                                                            )
                       ).add_to(berk_map)


# https://github.com/python-visualization/folium/pull/242
school_points = pd.read_csv('school points.csv')
feature_group = FeatureGroup(name='School Points')
for i in range(0,len(school_points)):
    institution_type = school_points['schooltype'].iloc[i]
    if institution_type == 'higher education':
        color = 'orange'
        icon='university'
    elif institution_type == 'middle school' or institution_type == 'elementary':
        color = 'lightblue'
        icon='book'
    else:
        color = 'darkblue'
        icon='building'
#         print('debug', color, icon)
        
    label = school_points['name'].iloc[i]

    feature_group.add_child(Marker([school_points['lat'].iloc[i],school_points['lon'].iloc[i]],
                                    popup=label, icon=folium.Icon(color=color, icon=icon,name='Schools', prefix='fa')))


berk_map.add_child(feature_group)
# berk_map.add_child(folium.map.LayerControl())     
# folium.LayerControl(collapsed=False).add_to(berk_map)


# Add dark and light mode. 
folium.TileLayer('cartodbdark_matter',name="Dark Mode",control=True).add_to(berk_map)
folium.TileLayer('openstreetmap',name="Street Map",control=True).add_to(berk_map)

folium.LayerControl(collapsed=False).add_to(berk_map)

file_path = r"circlemap.html"
berk_map.save(file_path) # Save as html file
print('debug','saved!')
berk_map


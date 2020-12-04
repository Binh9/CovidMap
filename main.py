#!/usr/bin/env python3

"""
@author: Binh
"""

import json
import folium
import http.client
import pandas as pd
from pandas.io.json import json_normalize 

api = "api.covid19api.com"
query = '/summary'   # a summary of new and total cases per country updated daily

# Geodata
WORLD_COUNTRIES = 'https://raw.githubusercontent.com/Binh9/CovidMap/main/examples/data/world-countries.json'
COUNTRY_COORDINATES = pd.read_csv('https://raw.githubusercontent.com/Binh9/CovidMap/main/examples/data/countries-coordinates.csv')

# Access Data via API
conn = http.client.HTTPSConnection(api)
payload = ''
headers = {}

conn.request('GET', query, payload, headers)
res = conn.getresponse()

data = res.read().decode('UTF-8')

# Converting Data to JSON
summary = json.loads(data)

# Normalize data and clean it
countries = json_normalize(summary['Countries'])

# Convert to DataFrame and clean the columns
df = pd.DataFrame(countries)
clean_countries = df.drop(columns=['CountryCode', 'Date'], axis=1)

# clean_countries['Slug'] = clean_countries['Slug'].str.capitalize() 
# print(clean_countries.loc[clean_countries['Country'] == 'Viet Nam'])

# Base map
base_map = folium.Map(tiles='CartoDB dark_matter', min_zoom=1.5, max_bounds=True)

# Generate Choropleth Map Layer
folium.Choropleth(
        geo_data = WORLD_COUNTRIES,
        min_zoom = 2,
        name = "COVID-19",
        data = clean_countries,
        columns = ['Country', 'TotalConfirmed'],
        key_on = 'feature.properties.name',
        fill_color = 'YlOrRd',
        nan_fill_color = 'black',
        fill_opacity = 0.4,
        line_opacity = 0.2,
        legend_name = 'Total Confirmed COVID-19 Cases',
        ).add_to(base_map)

#folium.Choropleth(
#        geo_data = world_countries,
#        min_zoom = 2,
#        name = "COVID-19",
#        data = clean_countries,
#        columns = ['Country', 'TotalConfirmed'],
#        key_on = 'feature.properties.name',
#        fill_color = 'YlOrRd',
#        nan_fill_color = 'black',
#        fill_opacity = 0.4,
#        line_opacity = 0.2,
#        legend_name = 'New Recovered COVID-19 Cases',
#        ).add_to(base_map)

# Generate circular markers
# clean_countries.update(clean_countries['TotalConfirmed'].map('Total Confirmed: {}'.format))

# Merge the coordinates with covid info
merged_countries = pd.merge(clean_countries, COUNTRY_COORDINATES, on='Country')

# print(merged_countries)

def plotDot(point):
    lat = float(point.Latitude.replace('"', ''))
    log = float(point.Longitude.replace('"', ''))
    folium.CircleMarker(location = [lat, log],
                        radius = 5,
                        weight = 2,
                        popup = f'{point.Country}: {point.TotalConfirmed}',
                        color='red',
                        fill_color ='red').add_to(base_map) 
    
# #3186cc
    
merged_countries.apply(plotDot, axis=1)
base_map.fit_bounds(base_map.get_bounds())

# base_map.save('testing.html')


merged_countries = merged_countries.sort_values(by=['TotalConfirmed'], ascending=False)

def plotTopN(dtFrame, topN):
    slicedDt = dtFrame.head(topN)
    top_countries = slicedDt['Country'].values.tolist()
    print(top_countries)

plotTopN(merged_countries, 7)


    


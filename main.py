#!/usr/bin/env python3

"""
@author: Binh
"""

import json
import folium
import requests
import mimetypes
import http.client
import pandas as pd
from pandas.io.json import json_normalize 


api = "api.covid19api.com"

query = '/summary'   # a summary of new and total cases per country updated daily

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
base_map = folium.Map(tiles='CartoDB dark_matter', min_zoom=1.5)

# Obtain geodata 
folium_url = 'https://raw.githubusercontent.com/Binh9/CovidMap/main/examples/data'
world_countries = f'{folium_url}/world-countries.json'

# Generate Choropleth Map Layer
folium.Choropleth(
        geo_data = world_countries,
        min_zoom = 2,
        name = "COVID-19",
        data = clean_countries,
        columns = ['Country', 'TotalConfirmed'],
        key_on = 'feature.properties.name',
        fill_color = 'OrRd',
        nan_fill_color = 'black',
        fill_opacity = 0.55,
        line_opacity = 0.2,
        legend_name = 'Total Confirmed COVID-19 Cases',
        ).add_to(base_map)

# Generate circular markers
clean_countries.update(clean_countries['TotalConfirmed'].map('Total Confirmed: {}'.format))

# Get Countries Coordinates
country_coordinates = pd.read_csv('https://gist.githubusercontent.com/tadast/8827699/raw/f5cac3d42d16b78348610fc4ec301e9234f82821/countries_codes_and_coordinates.csv')

# Merge the coordinates with covid info
merged_countries = pd.merge(clean_countries, country_coordinates, on='Country')

def plotDot(point):
    folium.CircleMarker(location = [point.Latitude, point.Longtitude],
                        radius = 5,
                        weight = 2,
                        popup = [point.Country, point.TotalConfirmed],
                        fill_color = 'red').add_to(base_map) 
    
merged_countries.apply(plotDot, axis=1)
base_map.fit_bounds(base_map.get_bounds())

print(merged_countries)
base_map.save('map.html')

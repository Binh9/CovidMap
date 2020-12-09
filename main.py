"""
@author: Binh
"""

import json
import folium
import http.client
import pandas as pd
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize 

api = "api.covid19api.com"
query = '/summary'   # a summary of new and total cases per country updated daily

# Geodata
WORLD_COUNTRIES = 'https://raw.githubusercontent.com/Binh9/CovidMap/main/examples/data/world-countries.json'
COUNTRY_COORDINATES = pd.read_csv('https://raw.githubusercontent.com/Binh9/CovidMap/main/examples/data/countries-coordinates.csv')

TIME_COUNTRIES = 'https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv'
WORLD_AGGREGATED = 'https://raw.githubusercontent.com/datasets/covid-19/master/data/worldwide-aggregate.csv'

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

# Generates the pointers
def plotDot(point, stat, color, base_map):
    lat = float(point.Latitude.replace('"', ''))
    log = float(point.Longitude.replace('"', ''))
    folium.CircleMarker(location = [lat, log],
                        radius = 5,
                        weight = 2,
                        popup = f'{point.Country}: {point[stat]:,}',
                        color=color,
                        fill_color =color).add_to(base_map) 

# Generates the interactive global map with pointers
def generateMap(base_map, geo_data, data, stat, color_scheme, legend_name, color_pointer):
    # Generates the choropleth map layer and adds it on top of the base map
    folium.Choropleth(
        geo_data = geo_data,
        min_zoom = 2,
        name = "COVID-19",
        data = data,
        columns = ['Country', stat],
        key_on = 'feature.properties.name',
        fill_color = color_scheme,
        nan_fill_color = 'black',
        fill_opacity = 0.4,
        line_opacity = 0.2,
        legend_name = legend_name,
        ).add_to(base_map)

    # Merge the country coordinates with covid info
    merged_countries = pd.merge(clean_countries, COUNTRY_COORDINATES, on='Country')

    merged_countries.apply(lambda x: plotDot(x, stat, color_pointer, base_map), axis=1)
    base_map.fit_bounds(base_map.get_bounds())

    base_map.save(f'images/{stat}.html')

# Generate Choropleth Map Layer
# folium.Choropleth(
#         geo_data = WORLD_COUNTRIES,
#         min_zoom = 2,
#         name = "COVID-19",
#         data = clean_countries,
#         columns = ['Country', 'TotalConfirmed'],
#         key_on = 'feature.properties.name',
#         fill_color = 'YlOrRd',
#         nan_fill_color = 'black',
#         fill_opacity = 0.4,
#         line_opacity = 0.2,
#         legend_name = 'Total Confirmed COVID-19 Cases',
#         ).add_to(base_map)

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
# merged_countries = pd.merge(clean_countries, COUNTRY_COORDINATES, on='Country')

# print(merged_countries)

# def plotDot(point):
#     lat = float(point.Latitude.replace('"', ''))
#     log = float(point.Longitude.replace('"', ''))
#     folium.CircleMarker(location = [lat, log],
#                         radius = 5,
#                         weight = 2,
#                         popup = f'{point.Country}: {point.TotalConfirmed}',
#                         color='red',
#                         fill_color ='red').add_to(base_map)                         
    
# #3186cc
    
# merged_countries.apply(plotDot, axis=1)
# base_map.fit_bounds(base_map.get_bounds())

# base_map.save('testing.html')

generateMap(base_map, WORLD_COUNTRIES, clean_countries, 'TotalConfirmed', 'YlOrRd', 'Total Confirmed COVID-19 Cases', 'red')
# ------------

# merged_countries = merged_countries.sort_values(by=['TotalConfirmed'],
#                                                 ascending=False)

# time_covid = pd.read_csv(TIME_COUNTRIES)
# time_confirmed_covid = time_covid.pivot(index='Date',
#                                         columns='Country',
#                                         values='Deaths')

# world_aggregated_covid = pd.read_csv(WORLD_AGGREGATED)

# print(world_aggregated_covid['Confirmed'])


# # Translating to python datatime
# index = pd.date_range(start = time_confirmed_covid.index[0],
#                       end = time_confirmed_covid.index[-1],
#                       )
# index = [pd.to_datetime(date, format='%Y-%m-%d').date() for date in index]

# # Plot the time series of 
# def plotTopN(topN):
#     slicedDt = merged_countries.head(topN)
#     top_countries = slicedDt['Country'].values.tolist()
    
#     # Fixing the countries name that data works with
#     for i, country in enumerate(top_countries):
#         if country == "United States of America":
#             top_countries[i] = 'US'
#         elif country == "Russian Federation":
#             top_countries[i] = 'Russia'
#     print(top_countries)
    
#     top_time_confirmed_covid = time_confirmed_covid[top_countries]

#     top_time_confirmed_covid.reset_index()
    
#     # Reformat dataframe to use datetime as indices
#     reformatted_dt = pd.DataFrame(data = top_time_confirmed_covid.values,
#                                   index = index,
#                                   columns=top_countries)
    
#     plt.style.use('ggplot')
#     reformatted_dt.plot(figsize=(10, 6),
#                         title  = 'COVID-19 Deaths by Country')
#     plt.xlabel('Dates')
#     plt.ylabel('Total # of Deaths')
    

# #plotTopN(7)
    
# def plotWorld():
#     # Transform values to thousands for better readability
#     cases_in_thousands = [val / 1000 for val in world_aggregated_covid['Confirmed'].tolist()]
#     world_dt = pd.DataFrame(data = cases_in_thousands,
#                             index = index,
#                             columns = ['World Aggregated'])
    
# #   # Custom yticks    
# #    ytick_list = []
# #    interval = world_dt.iloc[-1]['World Aggregated'] / 6
# #    start = 0
# #    for i in range(7):
# #        ytick_list.append(start)
# #        start += interval
# #        
# #    print(ytick_list)
    
#     plt.style.use('ggplot')
#     world_dt.plot(figsize=(10, 6),
#                   title  = 'World COVID-19 Confirmed Cases',)
# #                  yticks = ytick_list)
#     plt.xlabel('Dates')
#     plt.ylabel('Total # of Confirmed Cases (in thousands)')
               
# plotWorld()
           
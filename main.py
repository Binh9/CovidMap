"""
@author: Binh
"""

import json
import folium
import http.client
import pandas as pd
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize 
import plotly.express as px

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


# Merge the coordinates with covid info
merged_countries = pd.merge(clean_countries, COUNTRY_COORDINATES, on='Country')
# merged_countries = merged_countries.sort_values(by=['TotalConfirmed'], ascending=False)

time_covid = pd.read_csv(TIME_COUNTRIES)
# time_confirmed_covid = time_covid.pivot(index='Date',
#                                         columns='Country',
#                                         values='Confirmed')

world_aggregated_covid = pd.read_csv(WORLD_AGGREGATED)
    
# Plots a line graph for top N countries based on the given stat (i.e. Confirmed/Death/Recovered)
def plotTopN(topN, df, time_df, stat, title):
    # Sort the given dataframe by the given data
    df = df.sort_values(by=[f'Total{stat}'], ascending=False)
    # Getting the top N countries based on ....
    slicedDt = df.head(topN)
    top_countries = slicedDt['Country'].values.tolist()
    
    # Fixing the countries name that data works with
    # More like a hack, since working with different data sets
    for i, country in enumerate(top_countries):
        if country == "United States of America":
            top_countries[i] = 'US'
        elif country == "Russian Federation":
            top_countries[i] = 'Russia'
    # print(top_countries)

    time_stat_covid = time_df.pivot(index = 'Date', columns = 'Country', values = stat)

    # Translating to python datatime
    index = pd.date_range(start = time_stat_covid.index[0],
                          end = time_stat_covid.index[-1])
    index = [pd.to_datetime(date, format='%Y-%m-%d').date() for date in index]
    
    top_time_stat_covid = time_stat_covid[top_countries]
    top_time_stat_covid.reset_index()
    
    # Reformat dataframe to use datetime as indices for top N countries
    reformatted_dt = pd.DataFrame(data = top_time_stat_covid.values,
                                  index = index,
                                  columns = top_countries)

    fig = px.line(reformatted_dt, x = index, y = top_countries, title = title, labels = {'x': 'Date', 'value': f'Total {stat} Cases', 'variable': 'Country'})
    return fig
    
def plotWorld(df):
    stats = ['Confirmed', 'Deaths', 'Recovered']

    # Translating to python datatime
    index = pd.date_range(start = df['Date'].tolist()[0],
                          end = df['Date'].tolist()[-1])
    index = [pd.to_datetime(date, format='%Y-%m-%d').date() for date in index]

    world_dt = pd.DataFrame(data = df[stats].values,
                            index = index,
                            columns = stats)

    fig = px.line(
        world_dt, 
        x = index, 
        y = stats, 
        title = 'World COVID-19 Situation Over Time', 
        labels = {'x': 'Date', 'value': 'World Aggregated Cases', 'variable': 'World'}
    )
    fig.layout['paper_bgcolor'] = 'rgb(71, 71, 71)'
    fig.layout['plot_bgcolor'] = 'rgb(71, 71, 71)'
    fig.layout['font'] = {'color': 'white'}
    return fig
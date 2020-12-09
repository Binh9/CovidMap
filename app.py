import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import json
import folium
import http.client
import matplotlib.pyplot as plt
from main import plotDot, generateMap
from pandas.io.json import json_normalize 
from dash.dependencies import Input, Output


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# -------------------------------------------------------------------------------------------------
# Data processing

# Geodata:
# countries boundaries data
WORLD_COUNTRIES = 'https://raw.githubusercontent.com/Binh9/CovidMap/main/examples/data/world-countries.json'
# countries location data
COUNTRY_COORDINATES = pd.read_csv('https://raw.githubusercontent.com/Binh9/CovidMap/main/examples/data/countries-coordinates.csv')
# countries COVID-19 data over time
TIME_COUNTRIES = 'https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv'
# world aggregated COVID-19 data over time
WORLD_AGGREGATED = 'https://raw.githubusercontent.com/datasets/covid-19/master/data/worldwide-aggregate.csv'

# API for getching general COVID-19 data
api_general = "api.covid19api.com"
query = '/summary'   # a summary of new and total cases per country updated daily

# Access live data via API
conn = http.client.HTTPSConnection(api_general)
payload = ''
headers = {}
conn.request('GET', query, payload, headers)
res = conn.getresponse()
data = res.read().decode('UTF-8')

# Converting Data to JSON
summary = json.loads(data)

# Normalize data for each country and clean it
countries = json_normalize(summary['Countries'])
# Normalize global data and cleant it
global_summary = json_normalize(summary['Global'])

# Convert to DataFrame and clean the columns
df = pd.DataFrame(countries)
clean_countries = df.drop(columns=['CountryCode', 'Date'], axis=1)
global_df = pd.DataFrame(global_summary)

# Stats interested in
stats_intr = global_df.columns.tolist()
print(global_df)

# Base map
# base_map = folium.Map(tiles='CartoDB dark_matter', min_zoom=1.5, max_bounds=True)



# -------------------------------------------------------------------------------------------------
# APP LAYOUT

addit_map_tab_css = {'background-color': '#171818'}
addit_map_tab_slct_css = {'background-color': '#171818', 'color': 'white'}

app.layout = html.Div(children = [
    html.Div(children = [
        html.H1(id = 'project-title', children = "COVID-19 DASHBOARD", style = {'margin' : '10px'})]),

    html.Div(children = [
        html.Div(children = [
            html.Div(children = [
                html.Div(children = 'Total Confirmed Cases'), 
                html.Div(id = 'total-confirmed', children = f'{global_df.TotalConfirmed[0]:,}')
            ], style = {'display': 'table-cell'}),
            html.Div(children = [
                html.Div(children = 'Total Deaths'), 
                html.Div(id = 'total-deaths', children = f'{global_df.TotalDeaths[0]:,}')
            ], style = {'display': 'table-cell'}),
            html.Div(children = [
                html.Div(children = 'Total Recovered Cases'), 
                html.Div(id = 'total-recovered', children = f'{global_df.TotalRecovered[0]:,}')
            ], style = {'display': 'table-cell'})
        ], style = {'display': 'table', 'width': '100%', 'margin': '0px'})
    ], style = {'display': 'block', 'border-style': 'outset', 'margin': '10px'}),

    html.Div(children = [
        html.Div(children = [
            html.Div(children = [
                dcc.Tabs(id = 'general-data-tabs', value = 'tc', parent_className = 'custom-general-tabs', children = [
                    dcc.Tab(
                        label = 'Total Confirmed',
                        value = 'tc',
                        className = 'custom-general-tab',
                        selected_className = 'custom-general-tab--selected'
                    ),
                    dcc.Tab(
                        label = 'Total Deaths', 
                        value = 'td',
                        className = 'custom-general-tab',
                        selected_className = 'custom-general-tab--selected'
                    ),
                    dcc.Tab(
                        label = 'Total Recovered', 
                        value = 'tr', 
                        className = 'custom-general-tab',
                        selected_className = 'custom-general-tab--selected'
                    ),
                ]),
                html.Div(id = 'general-tabs-content', style = {})
            ], style = {'border-style': 'outset', 'position': 'relative', 'float': 'left', 'width': '300px'}),
            html.Div(children = [
                dcc.Tabs(id = 'map-data-tabs', value = 'TotalConfirmed', parent_className = 'custom-map-tabs', children = [
                    dcc.Tab(
                        label = 'Total Confirmed',
                        value = 'TotalConfirmed',
                        className = 'custom-map-tab',
                        selected_className = 'custom-map-tab--selected',
                        style = addit_map_tab_css,
                        selected_style = addit_map_tab_slct_css,
                    ),
                    dcc.Tab(
                        label = 'New Confirmed',
                        value = 'NewConfirmed',
                        className = 'custom-map-tab',
                        selected_className = 'custom-map-tab--selected',
                        style = addit_map_tab_css,
                        selected_style = addit_map_tab_slct_css,
                    ),
                    dcc.Tab(
                        label = 'Total Deaths', 
                        value = 'TotalDeaths',
                        className = 'custom-map-tab',
                        selected_className = 'custom-map-tab--selected',
                        style = addit_map_tab_css,
                        selected_style = addit_map_tab_slct_css,
                    ),
                    dcc.Tab(
                        label = 'New Deaths', 
                        value = 'NewDeaths',
                        className = 'custom-map-tab',
                        selected_className = 'custom-map-tab--selected',
                        style = addit_map_tab_css,
                        selected_style = addit_map_tab_slct_css,
                    ),
                    dcc.Tab(
                        label = 'Total Recovered', 
                        value = 'TotalRecovered', 
                        className = 'custom-map-tab',
                        selected_className = 'custom-map-tab--selected',
                        style = addit_map_tab_css,
                        selected_style = addit_map_tab_slct_css,
                    ),
                    dcc.Tab(
                        label = 'New Recovered', 
                        value = 'NewRecovered', 
                        className = 'custom-map-tab',
                        selected_className = 'custom-map-tab--selected',
                        style = addit_map_tab_css,
                        selected_style = addit_map_tab_slct_css,
                    ),
                ]),
                #html.Div(id = 'map-tabs-content', style = {})
                html.Iframe(id = 'map', srcDoc = open('images/TotalConfirmed.html', 'r').read(), style = {'height': '100%'})
            ], style = {'width': '100%', 'display': 'flex', 'flex-direction': 'column'}),
        ], style = {'display': 'flex', 'height': '450px'}),
    ], style = {'border-style': 'outset', 'margin': '10px'}),

    html.Div(children = [
        'PLACEHOLDER FOR ADDITIONAL VISUALS',
        
    ]),
], style = {'textAlign': 'center', 'height': '1000px', 'border-style': 'outset'})

# -------------------------------------------------------------------------------------------------
# Dash Components
@app.callback(
    Output(component_id='general-tabs-content', component_property='children'),
    Input(component_id='general-data-tabs', component_property='value'))
def render_general_content(tab):
    # work with copy
    cc_countries = clean_countries.copy()
    countries_by_tc = []
    if tab == 'tc':
        cc_countries = cc_countries.sort_values(by=['TotalConfirmed'], ascending = False)
        for index, r in cc_countries.iterrows():
            countries_by_tc.append(html.Li(
                className = 'general-li-row',
                children = [
                    html.Span(children = [f'{r.TotalConfirmed:,}'], style = {'color': 'red', 'font-weight': 'bold'}),
                    html.Span(children = [f' {r.Country}'])
                ]))               
        return html.Ul(
            className = 'general-ul-info',
            children = countries_by_tc)
    elif tab == 'td':
        cc_countries = cc_countries.sort_values(by=['TotalDeaths'], ascending = False)
        for index, r in cc_countries.iterrows():
            countries_by_tc.append(html.Li(
                className = 'general-li-row',
                children = [
                    html.Span(children = [f'{r.TotalDeaths:,}'], style = {'color': 'whitesmoke', 'font-weight': 'bold'}),
                    html.Span(children = [f' {r.Country}'])
                ]))

        return html.Ul(
            className = 'general-ul-info',
            children = countries_by_tc)
    elif tab == 'tr':
        cc_countries = cc_countries.sort_values(by=['TotalRecovered'], ascending = False)
        for index, r in cc_countries.iterrows():
            countries_by_tc.append(html.Li(
                className = 'general-li-row',
                children = [
                    html.Span(children = [f'{r.TotalRecovered:,}'], style = {'color': 'lawngreen', 'font-weight': 'bold'}),
                    html.Span(children = [f' {r.Country}'])
                ]))

        return html.Ul(
            className = 'general-ul-info',
            children = countries_by_tc)

@app.callback(
    Output(component_id='map', component_property='srcDoc'),
    Input(component_id='map-data-tabs', component_property='value'))
def render_map_content(tab):
    # Directory where the map html would be located
    dir = 'images/'

    base_map = folium.Map(tiles='CartoDB dark_matter', min_zoom=1.5, max_bounds=True)

    if tab == 'TotalConfirmed':
        generateMap(base_map, WORLD_COUNTRIES, clean_countries, tab, 'YlOrRd', 'Total Confirmed COVID-19 Cases', 'red')
        # return open('images/TotalConfirmed.html', 'r').read()
    elif tab == 'TotalDeaths':
        generateMap(base_map, WORLD_COUNTRIES, clean_countries, tab, 'BuPu', 'Total COVID-19 Deaths', 'red')
        # return open('images/TotalDeaths.html', 'r').read()
    elif tab == 'TotalRecovered':
        generateMap(base_map, WORLD_COUNTRIES, clean_countries, tab, 'YlGn', 'Total Recovered COVID-19 Cases', '#3186cc')
        # return open('images/TotalRecovered.html', 'r').read()
    elif tab == 'NewConfirmed':
        generateMap(base_map, WORLD_COUNTRIES, clean_countries, tab, 'YlOrRd', 'New Confirmed COVID-19 Cases', 'red')
        # return open('images/NewConfirmed.html', 'r').read()
    elif tab == 'NewDeaths':
        generateMap(base_map, WORLD_COUNTRIES, clean_countries, tab, 'BuPu', 'New COVID-19 Deaths', 'red')
        # return open('images/NewDeaths.html', 'r').read()
    elif tab == 'NewRecovered':
        generateMap(base_map, WORLD_COUNTRIES, clean_countries, tab, 'YlGn', 'New Recovered COVID-19 Cases', '#3186cc')
        # return open('images/NewRecovered.html', 'r').read()

    return open(f'{dir}{tab}.html', 'r').read()


# -------------------------------------------------------------------------------------------------
# Running point
if __name__ == '__main__':
    app.run_server(debug = True)

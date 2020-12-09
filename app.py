import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import json
import folium
import http.client
import matplotlib.pyplot as plt
from graphingFunc import plotDot, generateMap, plotTopN, plotWorld
from pandas.io.json import json_normalize 
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

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

# Merge the coordinates with covid info
merged_countries = pd.merge(clean_countries, COUNTRY_COORDINATES, on='Country')

# Read covid data over time
time_covid = pd.read_csv(TIME_COUNTRIES)
world_aggregated_covid = pd.read_csv(WORLD_AGGREGATED)

# -------------------------------------------------------------------------------------------------
# APP LAYOUT

addit_map_tab_css = {'background-color': '#171818'}
addit_map_tab_slct_css = {'background-color': '#171818', 'color': 'white'}
addit_graph_tab_css = {'background-color': '#171818'}
addit_graph_tab_slct_css = {'background-color': '#171818', 'color': 'white'}

app.layout = html.Div(children = [
    html.Div(children = [
        html.H1(id = 'project-title', children = "COVID-19 DASHBOARD", style = {'margin' : '10px'})]),

    html.Div(children = [
        html.Div(children = [
            html.Div(children = [
                html.Div(children = [
                    html.Span(children = ['Total Confirmed Cases'])
                ]), 
                html.Div(children = [
                    html.Span(children = [f'{global_df.TotalConfirmed[0]:,}'], style = {'color': 'red'})
                ]), 
            ], style = {'display': 'table-cell'}),
            html.Div(children = [
                html.Div(children = [
                    html.Span(children = ['Total Deaths'])
                ]), 
                html.Div(children = [
                    html.Span(children = [f'{global_df.TotalDeaths[0]:,}'], style = {'color': 'ghostwhite'})
                ]),
            ], style = {'display': 'table-cell'}),
            html.Div(children = [
                html.Div(children = [
                    html.Span(children = ['Total Recovered Cases'])
                ]), 
                html.Div(children = [
                    html.Span(children = [f'{global_df.TotalRecovered[0]:,}'], style = {'color': 'forestgreen'})
                ]),
            ], style = {'display': 'table-cell'})
        ], style = {'display': 'table', 'width': '100%', 'margin': '0px'})
    ], style = {'display': 'block', 'border-style': 'outset', 'margin': '10px', 'font-size': '140%', 'font-weight': 'bold'}),

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
                html.Iframe(id = 'map', srcDoc = open('images/TotalConfirmed.html', 'r').read(), style = {'height': '100%'})
            ], style = {'width': '100%', 'display': 'flex', 'flex-direction': 'column'}),
        ], style = {'display': 'flex', 'height': '450px'}),
    ], style = {'border-style': 'outset', 'margin': '10px'}),

    html.Div(children = [
        html.Div(children = [
            html.Div(children = [
                dcc.Tabs(id = 'graph-tabs', value = 'tc', parent_className = 'custom-general-tabs', children = [
                    dcc.Tab(
                        label = 'Total Confirmed',
                        value = 'tc',
                        className = 'custom-general-tab',
                        selected_className = 'custom-general-tab--selected',
                        style = addit_graph_tab_css,
                        selected_style = addit_graph_tab_slct_css,
                    ),
                    dcc.Tab(
                        label = 'Total Deaths', 
                        value = 'td',
                        className = 'custom-general-tab',
                        selected_className = 'custom-general-tab--selected',
                        style = addit_graph_tab_css,
                        selected_style = addit_graph_tab_slct_css,
                    ),
                    dcc.Tab(
                        label = 'Total Recovered', 
                        value = 'tr', 
                        className = 'custom-general-tab',
                        selected_className = 'custom-general-tab--selected',
                        style = addit_graph_tab_css,
                        selected_style = addit_graph_tab_slct_css,
                    ),
                ]),
                dcc.Graph(id = 'graph-by-country', style = {'height': '500px'})
            ], style = {'border-style': 'outset', 'position': 'relative', 'float': 'left', 'width': '600px'}),
            html.Div(children = [
                dcc.Graph(id = 'graph-world-agg', figure = plotWorld(world_aggregated_covid))
            ], style = {'border-style': 'outset', 'position': 'relative', 'float': 'right', 'width': '600px'}),
        ], style = {'display': 'flex', 'justify-content': 'space-between'})
    ], style = {'border-style': 'outset', 'margin': '10px'}),
], style = {'textAlign': 'center', 'height': '1130px', 'border-style': 'outset'})

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

    # base_map
    base_map = folium.Map(tiles='CartoDB dark_matter', min_zoom=1.5, max_bounds=True)

    if tab == 'TotalConfirmed':
        generateMap(base_map, WORLD_COUNTRIES, merged_countries, tab, 'YlOrRd', 'Total Confirmed COVID-19 Cases', 'red')
    elif tab == 'TotalDeaths':
        generateMap(base_map, WORLD_COUNTRIES, merged_countries, tab, 'BuPu', 'Total COVID-19 Deaths', 'red')
    elif tab == 'TotalRecovered':
        generateMap(base_map, WORLD_COUNTRIES, merged_countries, tab, 'YlGn', 'Total Recovered COVID-19 Cases', '#3186cc')
    elif tab == 'NewConfirmed':
        generateMap(base_map, WORLD_COUNTRIES, merged_countries, tab, 'YlOrRd', 'New Confirmed COVID-19 Cases', 'red')
    elif tab == 'NewDeaths':
        generateMap(base_map, WORLD_COUNTRIES, merged_countries, tab, 'BuPu', 'New COVID-19 Deaths', 'red')
    elif tab == 'NewRecovered':
        generateMap(base_map, WORLD_COUNTRIES, merged_countries, tab, 'YlGn', 'New Recovered COVID-19 Cases', '#3186cc')

    return open(f'{dir}{tab}.html', 'r').read()

@app.callback(
    Output(component_id='graph-by-country', component_property='figure'),
    Input(component_id='graph-tabs', component_property='value'))
def render_graph(tab):
    # plot graphs for top 7 countries 
    TOP_N = 7
   
    if tab == 'tc':
        fig = plotTopN(TOP_N, merged_countries, time_covid, 'Confirmed', 'COVID-19 Confirmed Cases by Country')
    elif tab == 'td':
        fig = plotTopN(TOP_N, merged_countries, time_covid, 'Deaths', 'COVID-19 Deaths by Country')
    elif tab == 'tr':
        fig = plotTopN(TOP_N, merged_countries, time_covid, 'Recovered', 'COVID-19 Recovered Cases by Country')

    fig.layout['paper_bgcolor'] = 'rgb(71, 71, 71)'
    fig.layout['plot_bgcolor'] = 'rgb(71, 71, 71)'
    fig.layout['font'] = {'color': 'white'}
    return fig

# -------------------------------------------------------------------------------------------------
# Running point
if __name__ == '__main__':
    app.run_server(debug = True)
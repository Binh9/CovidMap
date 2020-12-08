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
base_map = folium.Map(tiles='CartoDB dark_matter', min_zoom=1.5, max_bounds=True)



# -------------------------------------------------------------------------------------------------
# APP LAYOUT
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
                html.Div(children = 'Total Death'), 
                html.Div(id = 'total-deaths', children = f'{global_df.TotalDeaths[0]:,}')
            ], style = {'display': 'table-cell'}),
            html.Div(children = [
                html.Div(children = 'Total Recovered Cases'), 
                html.Div(id = 'total-recovered', children = f'{global_df.TotalRecovered[0]:,}')
            ], style = {'display': 'table-cell'})
        ], style = {'display': 'table', 'width': '100%', 'margin': '0px'})
    ], style = {'display': 'block', 'border-style': 'outset', 'margin': '10px'}),

    html.Div(children = '''
        PLACEHOLDER FOR MAP
    ''', style = {'border-style': 'outset', 'margin': '10px'}),

    html.Div(children = '''
        PLACEHOLDER FOR ADDITIONAL VISUALS
    '''),
], style = {'textAlign': 'center', 'height': '100vh', 'border-style': 'outset'})

# -------------------------------------------------------------------------------------------------
# Dash Components
# @app.callback(
#     Output(component_id='...', component_property='...'),
#     Input(component_id='...', component_property='...')]
# )

def update_map(fromInput):
    return "DOSOMETHING"


# -------------------------------------------------------------------------------------------------
# Running point
if __name__ == '__main__':
    app.run_server(debug = True)

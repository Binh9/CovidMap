import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# -------------------------------------------------------------------------------------------------
# LALALA

# -------------------------------------------------------------------------------------------------
# APP LAYOUT
app.layout = html.Div(children = [
    html.H1(children = "DASH APP"),

    html.Div(children = '''
        Dash: A web application framework for Python
    '''),

    html.Div(children = '''
        PLACEHOLDER FOR GENERAL STAT
    '''),

    html.Div(children = '''
        PLACEHOLDER FOR MAP
    '''),

    html.Div(children = '''
        PLACEHOLDER FOR ADDITIONAL VISUALS
    '''),
])

# -------------------------------------------------------------------------------------------------
# Dash Components



# -------------------------------------------------------------------------------------------------
# Running point
if __name__ == '__main__':
    app.run_server(debug = True)

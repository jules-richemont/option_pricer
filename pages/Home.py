import dash
from dash import html

dash.register_page(__name__, name='Home', path='/')

layout = html.Div([
    "hllow world"
],
style={'marginTop': '200px'})

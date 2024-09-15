import dash
from dash import html

dash.register_page(__name__, name='Home', path='/')

# Page layout for 'Home'
layout = html.Div([
    html.Div([
        "hello world"
    ], style={
        'width': '100%',
        'height': '100%',
        'background-color': '#f0f0f0',  # Light gray background
    })
], style={
    'width': '100vw',  # Full width of the viewport
    'height': '100vh',  # Full height of the viewport
    'margin': '0',      # No margin
    'padding': '0',     # No padding
    'boxSizing': 'border-box',  # Include padding/border in the element's width/height
})


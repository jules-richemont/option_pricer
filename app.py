import dash
from dash import html, dcc

app = dash.Dash(__name__, use_pages=True)

# Header with black background and centered links using inline CSS
header = html.Div([
    html.Div([
        html.Div([
            dcc.Link(
                page['name'] + ' | ',
                href=page['path'],
                style={
                    'color': '#fff',  # White text for links
                    'fontSize': '18px',
                    'padding': '0 10px',
                    'textDecoration': 'none',
                }
            )
            for page in dash.page_registry.values()
        ], style={
            'display': 'flex',
            'justifyContent': 'center',  # Center the navigation links
            'alignItems': 'center',
        }),
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center',
        'padding': '20px 0',
    })
], style={
    'backgroundColor': '#000',  # Black background for the header
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'width': '100%',
    'position': 'fixed',
    'top': '0',
    'left': '0',
    'height': '7vh'
})

# Page layout
app.layout = html.Div([
    header,
    html.Br(),
    html.Div(
        dash.page_container,
        style={'paddingTop': '80px'}  # Adds space for the fixed header
    )
])

if __name__ == '__main__':
    app.run(debug=True, port=7777)

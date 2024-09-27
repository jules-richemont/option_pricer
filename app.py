import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import numpy as np

# Importing the various pricing models
from bs_pricer import BS_pricer
from binomial_pricer import Binomial_pricer
from heston_pricer import Heston_pricer
from sabr_pricer import SABR_pricer
from merton_pricer import Merton_pricer
from vg_pricer import VG_pricer
from dupire_pricer import Dupire_pricer

# Initialize the Dash app
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.CYBORG])

# Header for the app
header = html.Div([
    html.Div([
        html.Div([
            dcc.Link(
                page['name'] + ' | ',
                href=page['path'],
                style={
                    'color': '#fff',
                    'fontSize': '18px',
                    'padding': '0 10px',
                    'textDecoration': 'none',
                }
            )
            for page in dash.page_registry.values()
        ], style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'height': '100%',
        }),
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center',
        'padding': '0',
        'height': '100%',
    })
], style={
    'backgroundColor': '#1a1a1a',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'width': '100%',
    'position': 'fixed',
    'top': '0',
    'left': '0',
    'height': '7vh',
    'zIndex': '999',
    'margin': '0',
    'padding': '0'
})

# Set the HTML structure of the app
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            html, body {
                width: 100%;
                height: 100%;
                margin: 0;
                padding: 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout of the app
app.layout = html.Div([
    header,
    html.Div([
        # Dropdown for selecting pricing model
        dcc.Dropdown(
            id='model-dropdown',
            options=[
                {'label': 'Black-Scholes', 'value': 'BS'},
                {'label': 'Binomial', 'value': 'Binomial'},
                {'label': 'Heston', 'value': 'Heston'},
                {'label': 'SABR', 'value': 'SABR'},
                {'label': 'Merton', 'value': 'Merton'},
                {'label': 'Variance Gamma', 'value': 'VG'},
                {'label': 'Dupire (Local Volatility)', 'value': 'Dupire'},
            ],
            value='BS',  # Default model
            style={'width': '50%'}
        ),
        dcc.Input(id='S', type='number', placeholder='Spot Price', value=100),
        dcc.Input(id='K', type='number', placeholder='Strike Price', value=100),
        dcc.Input(id='T', type='number', placeholder='Maturity (in years)', value=1),
        dcc.Input(id='r', type='number', placeholder='Risk-free Rate', value=0.05),
        dcc.Input(id='sigma', type='number', placeholder='Volatility', value=0.2),
        html.Button('Calculate', id='calculate-btn'),
        html.Div(id='option-prices', style={'margin': '20px 0'}),
        html.Div([
            dcc.Graph(id='call-option-heatmap', style={'display': 'inline-block', 'width': '49%'}),
            dcc.Graph(id='put-option-heatmap', style={'display': 'inline-block', 'width': '49%'}),
        ]),
        html.Div([
            dcc.Graph(id='call-option-3d', style={'display': 'inline-block', 'width': '49%'}),
            dcc.Graph(id='put-option-3d', style={'display': 'inline-block', 'width': '49%'}),
        ])
    ], style={'marginTop': '7vh', 'padding': '0', 'flex': '1'})
], style={
    'display': 'flex',
    'flexDirection': 'column',
    'margin': 0,
    'padding': 0,
    'minHeight': '100vh',
})

# Callback for calculating option prices, generating heatmaps, and 3D plots
@app.callback(
    [Output('call-option-heatmap', 'figure'),
     Output('put-option-heatmap', 'figure'),
     Output('call-option-3d', 'figure'),
     Output('put-option-3d', 'figure'),
     Output('option-prices', 'children')],
    Input('calculate-btn', 'n_clicks'),
    State('model-dropdown', 'value'),  # Get selected model
    State('S', 'value'),
    State('K', 'value'),
    State('T', 'value'),
    State('r', 'value'),
    State('sigma', 'value')
)
def update_option_price_graph(n_clicks, selected_model, S, K, T, r, sigma):
    if not n_clicks:
        return {}, {}, {}, {}, ""

    # Range of spot prices and volatilities for the heatmap
    spot_prices = np.linspace(S * 0.5, S * 1.5, 50)
    volatilities = np.linspace(sigma * 0.5, sigma * 1.5, 50)

    # Initialize call and put prices array
    call_prices = np.zeros((len(spot_prices), len(volatilities)))
    put_prices = np.zeros((len(spot_prices), len(volatilities)))

    # Variables to hold the current option prices
    current_call_price, current_put_price = None, None

    # Loop through spot prices and volatilities to calculate option prices
    for i, s in enumerate(spot_prices):
        for j, v in enumerate(volatilities):
            # Dynamically choose the pricing model based on user input
            if selected_model == 'BS':
                pricer = BS_pricer(s, K, T, r, v)
                call_price, put_price = pricer.get_european_option()

            elif selected_model == 'Binomial':
                pricer = Binomial_pricer(s, K, T, r, v, steps=100)
                call_price, put_price = pricer.price_option()

            elif selected_model == 'Heston':
                pricer = Heston_pricer(S=s, K=K, T=T, r=r, kappa=1.0, theta=0.04, xi=0.1, rho=-0.5, v0=v, mu=0.1)
                call_price, put_price = pricer.get_european_option()

            elif selected_model == 'SABR':
                pricer = SABR_pricer(S=s, K=K, T=T, alpha=0.2, beta=0.5, rho=-0.3, nu=v)
                call_price, put_price = pricer.get_european_option()

            elif selected_model == 'Merton':
                pricer = Merton_pricer(S=s, K=K, T=T, r=r, sigma=v, lambda_j=0.1, mu_j=0.0, sigma_j=0.1)
                call_price, put_price = pricer.get_european_option()

            elif selected_model == 'VG':
                pricer = VG_pricer(S=s, K=K, T=T, r=r, sigma=v, theta=0.1, nu=0.2)
                call_price, put_price = pricer.get_european_option()

            elif selected_model == 'Dupire':
                pricer = Dupire_pricer(S=s, K=K, T=T, r=r, sigma=v)
                call_price, put_price = pricer.get_european_option()

            # Store the prices in the respective arrays
            call_prices[i, j] = call_price
            put_prices[i, j] = put_price

            # If the current spot price and volatility match the input values, store the current prices
            if s == S and v == sigma:
                current_call_price, current_put_price = call_price, put_price

    # Generate heatmap for call prices
    call_heatmap = go.Figure(data=go.Heatmap(
        z=call_prices,
        x=volatilities,
        y=spot_prices,
        colorscale='Viridis'
    ))
    call_heatmap.update_layout(
        title=f'Call Option Prices (Model: {selected_model})',
        xaxis_title='Volatility',
        yaxis_title='Spot Price'
    )

    # Generate heatmap for put prices
    put_heatmap = go.Figure(data=go.Heatmap(
        z=put_prices,
        x=volatilities,
        y=spot_prices,
        colorscale='Viridis'
    ))
    put_heatmap.update_layout(
        title=f'Put Option Prices (Model: {selected_model})',
        xaxis_title='Volatility',
        yaxis_title='Spot Price'
    )

    # Generate 3D plot for call prices
    call_3d = go.Figure(data=[go.Surface(
        z=call_prices,
        x=volatilities,
        y=spot_prices,
        colorscale='Viridis'
    )])
    call_3d.update_layout(
        title=f'Call Option Prices (3D) - {selected_model}',
        scene=dict(
            xaxis_title='Volatility',
            yaxis_title='Spot Price',
            zaxis_title='Call Price'
        )
    )

    # Generate 3D plot for put prices
    put_3d = go.Figure(data=[go.Surface(
        z=put_prices,
        x=volatilities,
        y=spot_prices,
        colorscale='Viridis'
    )])
    put_3d.update_layout(
        title=f'Put Option Prices (3D) - {selected_model}',
        scene=dict(
            xaxis_title='Volatility',
            yaxis_title='Spot Price',
            zaxis_title='Put Price'
        )
    )

    # Display current calculated call and put prices
    price_text = f"Call Price: {current_call_price:.2f}, Put Price: {current_put_price:.2f}"

    return call_heatmap, put_heatmap, call_3d, put_3d, price_text

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=7777)
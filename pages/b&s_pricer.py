import dash
from dash import html, dcc, Input, Output, callback
import numpy as np
from dash.exceptions import PreventUpdate
from scipy.stats import norm
import plotly.express as px


# Registering the page in the app
dash.register_page(__name__, name='B&S Pricer', path='/b&s_pricer')

# Layout for B&S Pricer page
parameters = html.Div([
    html.Div([
        html.Label('Current Asset Price:'),
        dcc.Input(
            id='spot-price-bs',
            type='number',
            step=0.01,
            value=100,
            style={'width': '14vw'}
        ),
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'padding': '10px'
    }),

    html.Div([
        html.Label('Strike Price:'),
        dcc.Input(
            id='strike-bs',
            type='number',
            step=0.01,
            value=70,
            style={
                'width': '14vw',
            }
        )
    ],style={
        'display': 'flex',
        'flexDirection': 'column',
        'padding': '10px'
    }),

    html.Div([
        html.Label('Time to Maturity (Years):'),
        dcc.Input(
            id='maturity-bs',
            type='number',
            step=0.01,
            value=2,
            style={
                'width': '14vw',
            }
        )
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'padding': '10px'
    }),

    html.Div([
        html.Label('Volatility:'),
        dcc.Input(
            id='volatility-bs',
            type='number',
            step=0.01,
            value=0.25,
            style={
                'width': '14vw',
            }
        )
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'padding': '10px'
    }),

    html.Div([
        html.Label('Risk Free Rate'),
        dcc.Input(
            id='rf-rate-bs',
            type='number',
            step=0.01,
            value=0.05,
            style={
                'width': '14vw',
            }
        )
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'padding': '10px'
    }),

    html.Br(),

    html.Div([
        html.Label('min Spot Price:'),
        dcc.Input(
            id='min-spot-price-bs',
            type='number',
            step=0.01,
            value=50,
            style={
                'width': '20w'
            }
        )
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'padding': '10px'
    }),

    html.Div([
        html.Label('max Spot Price:'),
        dcc.Input(
            id='max-spot-price-bs',
            type='number',
            step=0.01,
            value=150,
            style={
                'width': '20w'
            }
        )
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'padding': '10px'
    }),

    html.Div([
        html.Label('min Volatility:'),
        dcc.Slider(
            id='min-volatility-bs',
            min=0,
            max=1,
            step=0.01,
            value=0,
            marks={0: '0', 1: '1'},
            tooltip={"placement": "bottom", "always_visible": True},
        )
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'padding': '10px'
    }),

    html.Div([
        html.Label('max Volatility:'),
        dcc.Slider(
            id='max-volatility-bs',
            min=0,
            max=1,
            step=0.01,
            value = 1,
            marks={0: '0', 1: '1'},
            tooltip={"placement": "bottom", "always_visible": True},
        )
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'padding': '10px'
    })
])


results = html.Div([
    html.Div([
        dcc.Input(
            id='call-price-bs',
            type='number',
            value=None,
            disabled=True,
        ),
        dcc.Input(
            id='put-price-bs',
            type='number',
            value=None,
            disabled=True,
        )
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'gap': '50px',
        'width': '100%',
        'padding': '10px',
        'boxSizing': 'border-box'
    }),

    html.Div([
        dcc.Graph(
            id='call-heatmap',
            figure={},
            style={
                'width': '50vw'
            }
        ),
        dcc.Graph(
            id='put-heatmap',
            figure={},
            style={
                'width': '50vw'
            }
        )
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'width': '100%',
        'padding': '10px',
        'boxSizing': 'border-box'
    })
], style={
    'display': 'flex',
    'justifyContent': 'center',
    'alignItems': 'flex-start',
    'width': '100vw',
    'height': '100vw',

}
)

layout = html.Div([
    parameters,
    results
], style={
    'display': 'flex',
    'justifyContent': 'inline-block',
    'width': '100vw',
    'height': '100vh',
}
)


@callback(
    Output('call-price-bs', 'value'),
    Output('put-price-bs', 'value'),
    [
        Input('spot-price-bs', 'value'),
        Input('strike-bs', 'value'),
        Input('maturity-bs', 'value'),
        Input('volatility-bs', 'value'),
        Input('rf-rate-bs', 'value'),
    ]
)
def compute_option_price_with_bs(spot, strike, maturity, sigma, rf):

    d1 = (np.log(spot / strike) + (rf + 0.5 * sigma ** 2) * maturity) / (sigma * np.sqrt(maturity))
    d2 = d1 - sigma * np.sqrt(maturity)
    call_price = spot * norm.cdf(d1) - strike * norm.cdf(d2)
    put_price = strike * np.exp(-rf * maturity) * norm.cdf(-d2) - spot * norm.cdf(-d1)

    return call_price, put_price

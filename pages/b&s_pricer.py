import dash
from dash import html, dcc, Input, Output, State, callback
import numpy as np
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from scipy.stats import norm
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# Registering the page in the app
dash.register_page(__name__, name='B&S Pricer', path='/b&s_pricer')



# key_parameters
bs_key_parameters = [
    {'label': 'Spot Price', 'value': 'S'},
    {'label': 'Strike Price', 'value': 'K'},
    {'label': 'Time To Maturity', 'value': 'T'},
    {'label': 'Volatility', 'value': 'V'},
    {'label': 'Risk Free Rate', 'value': 'rf'},
]

# Layout for B&S Pricer page
parameters = html.Div([
    html.Div([
        dbc.Button(
            "B&S Settings",
            id='calculator-settings',
            n_clicks=0,
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("B&S Calculator Settings")),
                dbc.ModalBody([
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
                ])
            ],
            id='modal-calculator-bs',
            is_open=False
        )
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'marginTop': '5%'
    }
    ),

    html.H4(
        "Heatmaps Settings",
        style={
            'marginTop': '10%',
            'borderTop': '1px solid white',
            'borderBottom': '1px solid white',
        }
    ),

    dcc.Dropdown(
        id='xaxis-bs',
        options=bs_key_parameters,
        value=None,
    ),

    dcc.Dropdown(
        id='yaxis-bs',
        options=bs_key_parameters,
        value=None,
    ),


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
            value=0.01,
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
        'padding': '10px',
        'marginLeft': '0px'
    })
], style={
    'height': '100vh',
    'width': '20vw',
    'backgroundColor': '#2b2b2b',
})

results = html.Div([
    html.Div([
        html.Div(
            [
                html.Label(
                    'Call Value',
                    style={
                        'fontSize': '15px',
                        'fontWeight': 'normal',
                        'marginBottom': '5px'
                    }
                ),
                html.Div(
                    id='call-price-bs',
                    style={
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                    })
            ],
            style={
                'border': '3px solid #4CAF50',
                'borderRadius': '15px',
                'padding': '10px',
                'backgroundColor': '#4CAF50',
                'color': 'black',
                'width': '200px',
                'textAlign': 'center',
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'boxShadow': '2px 2px 10px rgba(0, 128, 0, 0.3)',  # Softer green shadow
            }
        ),

        html.Div(
            [
                html.Label(
                    'Put Value',
                    style={
                        'fontSize': '15px',
                        'fontWeight': 'normal',
                        'marginBottom': '5px'
                    }
                ),
                html.Div(
                    id='put-price-bs',
                    style={
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                    }
                )
            ],
            style={
                'border': '3px solid #FF6347',
                'borderRadius': '15px',
                'padding': '10px',
                'backgroundColor': '#FF6347',
                'color': 'black',
                'width': '200px',
                'textAlign': 'center',
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'boxShadow': '2px 2px 10px rgba(255, 99, 71, 0.5)',
            }
        ),
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'gap': '20%',
        'width': '100%',
        'height': '10%',
        'padding': '10px',
        'boxSizing': 'border-box'
    }),

    html.Div([
        dcc.Graph(
            id='call-heatmap',
            figure={},
            style={
                'width': '50%'
            }
        ),
        dcc.Graph(
            id='put-heatmap',
            figure={},
            style={
                'width': '50%'
            }
        )
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'width': '100%',
        'padding': '10px',
        'gap': '10px',
        'boxSizing': 'border-box'
    }),

    html.Div([
        dcc.Graph(
            id='3d-call-bs',
            figure={},
            style={
                'width': '50%'
            }
        ),
        dcc.Graph(
            id='3d-put-bs',
            figure={},
            style={
                'width': '50%'
            }
        )
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'width': '100%',
        'padding': '10px',
        'gap': '10px',
        'boxSizing': 'border-box'
    })
], style={
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'flex-start',
    'width': '100vw',
    'height': '100vh',
}
)

layout = html.Div([
    parameters,
    results
], style={
    'display': 'flex',
    'justifyContent': 'inline-block',
    'width': '100%',
    'height': '100%',
    'margin': '0',
    'padding': '0',
    'backgroundColor': '#3a3a3a',
}
)


def b_s_approximation(S, K, T, sigma, rf):

    d1 = (np.log(S / K) + (rf + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * norm.cdf(d1) - K * norm.cdf(d2)
    put_price = K * np.exp(-rf * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return call_price, put_price


@callback(
    Output('modal-calculator-bs', 'is_open'),
    Input('calculator-settings', 'n_clicks'),
    State('modal-calculator-bs', 'is_open'),
)
def toggle_calculator_settings(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output('call-price-bs', 'children'),
    Output('put-price-bs', 'children'),
    [
        Input('spot-price-bs', 'value'),
        Input('strike-bs', 'value'),
        Input('maturity-bs', 'value'),
        Input('volatility-bs', 'value'),
        Input('rf-rate-bs', 'value'),
    ]
)
def compute_option_price_with_bs(spot, strike, maturity, sigma, rf):

    if not spot or not strike or not maturity or not sigma or not rf:
        raise PreventUpdate

    call_price, put_price = b_s_approximation(spot, strike, maturity, sigma, rf)

    return '$ ' + str(call_price.round(3)), '$ ' + str(put_price.round(3))

@callback(
    Output('call-heatmap', 'figure'),
    Output('put-heatmap', 'figure'),
    Output('3d-call-bs', 'figure'),
    [
        Input('min-spot-price-bs', 'value'),
        Input('max-spot-price-bs', 'value'),
        Input('min-volatility-bs', 'value'),
        Input('max-volatility-bs', 'value'),
        Input('strike-bs', 'value'),
        Input('maturity-bs', 'value'),
        Input('rf-rate-bs', 'value'),
    ]
)
def fill_heatmap(S_min, S_max, vol_min, vol_max, K, T, rf):
    if not S_min or not S_max or not vol_min or not vol_max or not rf:
        raise PreventUpdate

    s_range = np.linspace(S_min, S_max, 11)
    vol_range = np.linspace(vol_min, vol_max, 11)

    df = pd.DataFrame([(S, vol) for S in s_range for vol in vol_range], columns=['S', 'vol'])
    df.sort_values(by=['S'], ascending=False, inplace=True)
    # Apply the b_s_approximation function to compute call and put prices
    df[['call_price', 'put_price']] = df.apply(lambda row: b_s_approximation(row['S'], K, T, row['vol'], rf), axis=1,
                                               result_type='expand')


    call_df = df.pivot(index='S', columns='vol', values='call_price')
    put_df = df.pivot(index='S', columns='vol', values='put_price')

    call_heatmap = px.imshow(
        call_df.round(3),
        x=call_df.index.tolist(),
        y=call_df.columns.tolist(),
        labels={'x': 'Spot Price', 'y': 'Volatility', 'color': 'Call Price'},
        color_continuous_scale='viridis',
        aspect='auto',
        text_auto=True,
    )

    put_heatmap = px.imshow(
        put_df.round(2),
        labels={'x': 'Spot Price', 'y': 'Volatility', 'color': 'Put Price'},
        x=put_df.index.tolist(),
        y=put_df.columns.tolist(),
        color_continuous_scale='viridis',
        aspect='auto',
        text_auto=True,
    )

    call_fig = go.Figure(data=[go.Mesh3d(
        x=call_df.index.tolist(),
        y=call_df.columns.tolist(),
        z=call_df.values,
        colorscale='Viridis',
        opacity=0.5,
        showscale=True,
    )])

    return call_heatmap, put_heatmap, call_fig
#
# @callback(
#     Output('3d-call-bs', 'figure'),
#     Output('3d-put-bs', 'figure'),
#     [
#         Input('min-spot-price-bs', 'value'),
#         Input('max-spot-price-bs', 'value'),
#         Input('min-volatility-bs', 'value'),
#         Input('max-volatility-bs', 'value'),
#         Input('strike-bs', 'value'),
#         Input('maturity-bs', 'value'),
#         Input('rf-rate-bs', 'value'),
#     ]
# )
# def get_3d_graph(s_min, s_max, vol_min, vol_max, K, mat, rf):
#     if not s_min or not s_max or not vol_min or not vol_max or not rf:
#         raise PreventUpdate
#
#     s_range = np.linspace(s_min, s_max, 11)
#     vol_range = np.linspace(vol_min, vol_max, 11)
#     mat_range = np.linspace(0.5, 1.5, 11)
#     df = pd.DataFrame([
#         (S, vol, T)
#         for S in s_range
#         for vol in vol_range
#         for T in mat_range
#     ], columns=['S', 'vol', 'T'])
#
#     df[['call_price', 'put_price']] = df.apply(lambda row: b_s_approximation(row['S'], K, row['T'], row['vol'], rf), axis=1,
#                                                result_type='expand')
#
#     call_fig = go.Figure(data=[go.Mesh3d(
#         x=df['S'],
#         y=df['T'],
#         z=df['call_price'],
#         intensity = df['vol'],
#         colorscale='Viridis',
#         opacity=0.5,
#         showscale=True,
#     )])
#
#
#     put_fig = go.Figure(data=[go.Mesh3d(
#         x=df['S'],
#         y=df['T'],
#         z=df['put_price'],
#         intensity=df['vol'],
#         colorscale='Plasma',
#         opacity=0.5,
#         showscale=True
#     )])
#
#
#     return call_fig, put_fig
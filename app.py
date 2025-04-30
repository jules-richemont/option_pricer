import dash
from dash import html, dcc, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from flask import Flask

# Importation des classes de pricers
from option_class.bs_pricer import BS_pricer
from option_class.binomial_pricer import Binomial_pricer
from option_class.sabr_pricer import SABR_pricer
from option_class.heston_pricer import Heston_pricer
from option_class.merton_pricer import Merton_pricer
from option_class.vg_pricer import VG_pricer
from option_class.dupire_pricer import Dupire_pricer

# Initialisation de l'application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

# Liste des modèles disponibles
models = [
    {'label': 'Binomial', 'value': 'BINOMIAL'},
    {'label': 'Black-Scholes', 'value': 'BS'},
    {'label': 'SABR', 'value': 'SABR'},
    {'label': 'Heston', 'value': 'HESTON'},
    {'label': 'Merton', 'value': 'MERTON'},
    {'label': 'Variance Gamma', 'value': 'VG'},
    {'label': 'Dupire (Local Volatility)', 'value': 'DUPIRE'}
]

# Paramètres nécessaires par modèle
model_parameters = {
    'BINOMIAL': ['S', 'K', 'T', 'r', 'sigma', 'steps'],
    'BS': ['S', 'K', 'T', 'r', 'sigma'],
    'SABR': ['S', 'K', 'T', 'alpha', 'beta', 'rho', 'nu'],
    'HESTON': ['S', 'K', 'T', 'r', 'kappa', 'theta', 'xi', 'rho', 'v0', 'mu'],
    'MERTON': ['S', 'K', 'T', 'r', 'sigma', 'lambda_j', 'mu_j', 'sigma_j'],
    'VG': ['S', 'K', 'T', 'r', 'sigma', 'theta', 'nu'],
    'DUPIRE': ['S', 'K', 'T', 'r']
}

# Traduction des paramètres pour affichage
parameter_names = {
    'S': 'Spot Price',
    'K': 'Strike Price',
    'T': 'Time to Maturity (Years)',
    'r': 'Risk-Free Interest Rate',
    'sigma': 'Volatility (σ)',
    'alpha': 'Alpha',
    'beta': 'Beta',
    'rho': 'Rho',
    'nu': 'Nu',
    'v0': 'Initial Variance (v0)',
    'kappa': 'Kappa',
    'theta': 'Theta',
    'xi': 'Vol of Vol (ξ)',
    'lambda_j': 'Lambda (λ_j)',
    'mu_j': 'Jump Mean (μ_j)',
    'sigma_j': 'Jump Volatility (σ_j)',
    'steps': 'Number of Steps',
    'mu': 'Mu'
}

# Valeurs par défaut des paramètres
default_values = {param: 100.0 for param in ['S', 'K']}
default_values.update({
    'T': 1.0, 'r': 0.05, 'sigma': 0.20, 'alpha': 0.20, 'beta': 0.50,
    'rho': 0.0, 'nu': 0.40, 'v0': 0.04, 'kappa': 2.0, 'theta': 0.04,
    'xi': 0.20, 'lambda_j': 0.10, 'mu_j': 0.0, 'sigma_j': 0.10,
    'steps': 100, 'mu': 0.0
})

# Incréments pour sliders et inputs
parameter_steps = {param: 0.01 for param in [
    'sigma', 'alpha', 'beta', 'rho', 'nu', 'v0', 'kappa', 'theta',
    'xi', 'lambda_j', 'mu_j', 'sigma_j', 'mu', 'r', 'T'
]}
parameter_steps.update({'S': 1, 'K': 1, 'steps': 1})

# Paramètres obligatoirement positifs
positive_params = [
    'sigma', 'alpha', 'nu', 'v0', 'kappa', 'theta', 'xi',
    'lambda_j', 'sigma_j', 'steps', 'T'
]

# Paramètres utilisés pour la génération des heatmaps
heatmap_params = {
    'BS': ['S', 'sigma'],
    'BINOMIAL': ['S', 'sigma'],
    'SABR': ['S', 'alpha'],
    'HESTON': ['S', 'theta'],
    'MERTON': ['S', 'sigma'],
    'VG': ['S', 'sigma'],
    'DUPIRE': ['S', 'T']
}
# Layout principal
app.layout = dbc.Container([
    dcc.Store(id='stored-params', data={}),
    
    html.H1("Option Pricer", style={'textAlign': 'center', 'marginTop': '20px'}),
    html.Hr(),

    dbc.Row([

        # Sidebar gauche (paramètres)
        dbc.Col([
            html.Div([
                html.H4("Credits", style={'textAlign': 'center'}),
                dbc.Button("Jules de Richemont", href='https://linkedin.com/in/jules-de-richemont/', target='_blank', color='primary', style={'margin': '5px'}),
                dbc.Button("Antoine Chambellan", href='https://www.linkedin.com/in/antoine-chambellan-63a49820b/', target='_blank', color='primary', style={'margin': '5px'}),
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),

            html.Hr(),
            html.H4("Model Parameters", style={'textAlign': 'center'}),

            html.Label("Select Model:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='model-dropdown',
                options=models,
                value='BS',
                clearable=False,
                style={'color': '#3A3A3A'}
            ),
            html.Br(),

            html.Div(id='parameter-inputs'),
            html.Hr(),

            html.H4("Heatmap Parameters", style={'textAlign': 'center'}),

            html.Label('Spot Price Range:', style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='spot-slider',
                min=0,
                max=200,
                step=1,
                value=[80, 120],
                marks={i: f'{i}' for i in range(0, 201, 20)},
                tooltip={'always_visible': True}
            ),
            html.Br(),

            html.Label('Volatility Range:', style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='vol-slider',
                min=0.0,
                max=1.0,
                step=0.1,
                value=[0.0, 1.0],
                marks={i / 10: f'{i / 10:.1f}' for i in range(0, 11)},
                tooltip={'always_visible': True}
            ),
        ], width=3, style={
            'height': '100vh',
            'overflowY': 'scroll',
            'paddingLeft': '20px',
            'paddingRight': '20px',
            'backgroundColor': '#303030',
            'marginLeft': '20px',
            'marginRight': '20px'
        }),

        # Contenu principal (résultats + graphes)
        dbc.Col([
            html.Div([
                html.Div([
                    html.Label('Call Price', style={'fontSize': '15px', 'fontWeight': 'normal'}),
                    html.Div(id='call-price', style={'fontSize': '18px', 'fontWeight': 'bold'})
                ], style={
                    'border': '3px solid #4CAF50',
                    'borderRadius': '15px',
                    'padding': '10px',
                    'backgroundColor': '#4CAF50',
                    'color': 'black',
                    'width': '250px',
                    'textAlign': 'center',
                    'display': 'inline-block',
                    'marginRight': '50px'
                }),

                html.Div([
                    html.Label('Put Price', style={'fontSize': '15px', 'fontWeight': 'normal'}),
                    html.Div(id='put-price', style={'fontSize': '18px', 'fontWeight': 'bold'})
                ], style={
                    'border': '3px solid #FF6347',
                    'borderRadius': '15px',
                    'padding': '10px',
                    'backgroundColor': '#FF6347',
                    'color': 'black',
                    'width': '250px',
                    'textAlign': 'center',
                    'display': 'inline-block'
                }),
            ], style={'textAlign': 'center', 'marginTop': '20px'}),

            html.Hr(),

            # Tabs pour afficher Heatmap et Surface 3D
            dcc.Tabs(id='tabs', value='tab-1', children=[
                dcc.Tab(label='Heatmap', value='tab-1', children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='heatmap-call', style={'height': '60vh'}), width=6),
                        dbc.Col(dcc.Graph(id='heatmap-put', style={'height': '60vh'}), width=6)
                    ])
                ]),
                dcc.Tab(label='3D Surface', value='tab-2', children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='surface-call', style={'height': '60vh'}), width=6),
                        dbc.Col(dcc.Graph(id='surface-put', style={'height': '60vh'}), width=6)
                    ])
                ])
            ], colors={'primary': '#303030', 'background': '#303030'}),
        ], width=8, style={
            'paddingLeft': '20px',
            'paddingRight': '20px',
            'marginLeft': '20px',
            'marginRight': '20px'
        })
    ], style={'height': '100vh'})
], fluid=True, style={'padding': '0', 'margin': '0'})

#Callback pour mettre à jour les paramètres en fonction du modèle sélectionné
@app.callback(
    Output('parameter-inputs', 'children'),
    Input('model-dropdown', 'value')
)
def update_parameters(model):
    params = model_parameters[model]
    inputs = []
    for param in params:
        step = parameter_steps.get(param, 1)
        min_value = 0 if param in positive_params else None
        inputs.append(html.Div([
            html.Label(parameter_names.get(param, param), style={'fontWeight': 'bold'}),
            dcc.Input(
                id={'type': 'parameter-input', 'index': param},
                type='number',
                value=default_values.get(param, 0),
                step=step,
                min=min_value,
                style={'width': '100%'}
            ),
            html.Br()
        ]))
    return inputs

#Callback pour mettre à jour le slider de spot price lorsque le spot price change
@app.callback(
    [Output('spot-slider', 'value'),
     Output('spot-slider', 'min'),
     Output('spot-slider', 'max'),
     Output('spot-slider', 'marks')],
    Input({'type': 'parameter-input', 'index': 'S'}, 'value')
)
def update_spot_slider(spot_price):
    range_width = 50
    min_spot = max(0, spot_price - range_width)
    max_spot = spot_price + range_width
    marks = {i: f'{i}' for i in range(int(min_spot), int(max_spot) + 1, 10)}
    return [min_spot, max_spot], min_spot, max_spot, marks

#Callback pour calculer les prix des options et générer les graphiques
@app.callback(
    [Output('call-price', 'children'),
     Output('put-price', 'children'),
     Output('heatmap-call', 'figure'),
     Output('heatmap-put', 'figure'),
     Output('surface-call', 'figure'),
     Output('surface-put', 'figure')],
    [Input('model-dropdown', 'value'),
     Input({'type': 'parameter-input', 'index': ALL}, 'value'),
     Input('spot-slider', 'value'),
     Input('vol-slider', 'value')],
    [State({'type': 'parameter-input', 'index': ALL}, 'id')]
)
def update_output(model, param_values, spot_range, vol_range, param_ids):
    params = {param_id['index']: value for param_id, value in zip(param_ids, param_values)}
    required_params = model_parameters[model]

    # Vérification que tous les paramètres nécessaires sont présents
    if any(param not in params or params[param] in [None, ''] for param in required_params):
        return "N/A", "N/A", {}, {}, {}, {}

    # Création de l'instance du pricer
    try:
        num_simulations = 10000
        pricer = create_pricer(model, params, num_simulations)
        call_price, put_price = pricer.get_european_option()
        call_price_str = f"${call_price:.3f}"
        put_price_str = f"${put_price:.3f}"

    except Exception as e:
        return f"Error: {e}", f"Error: {e}", {}, {}, {}, {}

    # Génération des grilles pour heatmaps/surfaces
    min_spot, max_spot = spot_range
    S_values = np.linspace(min_spot, max_spot, 11)
    min_vol, max_vol = vol_range

    x_param, y_param = heatmap_params[model]
    x_label = parameter_names[x_param]
    y_label = parameter_names[y_param]

    if y_param in ['sigma', 'alpha', 'v0', 'theta']:
        y_min, y_max = min_vol, max_vol
    else:
        y_min, y_max = default_values.get(y_param, 0), default_values.get(y_param, 1)

    Y_values = np.linspace(y_min, y_max, 11)
    X_grid, Y_grid = np.meshgrid(S_values, Y_values)

    call_prices, put_prices = np.zeros_like(X_grid), np.zeros_like(X_grid)

    # Boucle de calcul
    for i in range(X_grid.shape[0]):
        for j in range(X_grid.shape[1]):
            params_loop = params.copy()
            params_loop[x_param] = X_grid[i, j]
            params_loop[y_param] = Y_grid[i, j]

            try:
                pricer_loop = create_pricer(model, params_loop, num_simulations)
                call, put = pricer_loop.get_european_option()
                call_prices[i, j] = call
                put_prices[i, j] = put
            except:
                call_prices[i, j] = np.nan
                put_prices[i, j] = np.nan

    # Génération des figures
    heatmap_call = create_heatmap(S_values, Y_values, call_prices, x_label, y_label, 'Call Price')
    heatmap_put = create_heatmap(S_values, Y_values, put_prices, x_label, y_label, 'Put Price')
    surface_call = create_surface(S_values, Y_values, call_prices, x_label, y_label, 'Call Price')
    surface_put = create_surface(S_values, Y_values, put_prices, x_label, y_label, 'Put Price')

    return call_price_str, put_price_str, heatmap_call, heatmap_put, surface_call, surface_put

def create_pricer(model, params, num_simulations=10000):
    if model == 'HESTON':
        return Heston_pricer(**params, num_simulations=num_simulations)
    elif model == 'MERTON':
        return Merton_pricer(**params, num_simulations=num_simulations)
    elif model == 'DUPIRE':
        local_vol_surface = lambda S, T: 0.2 * np.ones_like(S)  # Placeholder
        return Dupire_pricer(**params, local_vol_surface=local_vol_surface, num_simulations=num_simulations)
    elif model == 'BS':
        if params['sigma'] <= 0:
            raise ValueError("Volatility sigma must be positive")
        return BS_pricer(**params)
    elif model == 'BINOMIAL':
        return Binomial_pricer(**params)
    elif model == 'SABR':
        return SABR_pricer(**params)
    elif model == 'VG':
        return VG_pricer(**params)
    else:
        raise ValueError("Unknown model")

def create_heatmap(x_values, y_values, z_values, x_label, y_label, title):
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_values,
        y=y_values,
        colorscale='RdYlGn',
        text=np.round(z_values, 3),
        texttemplate="%{text}",
        hovertemplate=f'{x_label}: %{{x}}<br>{y_label}: %{{y}}<br>Price: %{{z:.3f}}<extra></extra>'
    ))
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(50,50,50,1)',
        font_color='white',
        xaxis=dict(gridcolor='gray'),
        yaxis=dict(gridcolor='gray')
    )
    return fig

def create_surface(x_values, y_values, z_values, x_label, y_label, title):
    fig = go.Figure(data=[go.Surface(
        z=z_values,
        x=x_values,
        y=y_values,
        colorscale='RdYlGn'
    )])
    fig.update_layout(
        title=f'Surface 3D {title}',
        scene=dict(
            xaxis_title=x_label,
            yaxis_title=y_label,
            zaxis_title=title,
            xaxis=dict(backgroundcolor='rgb(50,50,50)', gridcolor='gray'),
            yaxis=dict(backgroundcolor='rgb(50,50,50)', gridcolor='gray'),
            zaxis=dict(backgroundcolor='rgb(50,50,50)', gridcolor='gray'),
            bgcolor='rgb(50,50,50)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    return fig

# Lancement de l'application
if __name__ == '__main__':
    app.run(debug=True)
import dash
from dash import html, dcc, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import os
from flask import Flask

# Importation des classes de pricers
from option_class.bs_pricer import BS_pricer
from option_class.binomial_pricer import Binomial_pricer
from option_class.sabr_pricer import SABR_pricer
from option_class.heston_pricer import Heston_pricer
from option_class.merton_pricer import Merton_pricer
from option_class.vg_pricer import VG_pricer
from option_class.dupire_pricer import Dupire_pricer

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
    {'label': 'Dupire (Local Volatility)', 'value': 'DUPIRE'},
]

# Dictionnaire des paramètres pour chaque modèle
model_parameters = {
    'BINOMIAL': ['S', 'K', 'T', 'r', 'sigma', 'steps'],
    'BS': ['S', 'K', 'T', 'r', 'sigma'],
    'SABR': ['S', 'K', 'T', 'alpha', 'beta', 'rho', 'nu'],
    'HESTON': ['S', 'K', 'T', 'r', 'kappa', 'theta', 'xi', 'rho', 'v0', 'mu'],
    'MERTON': ['S', 'K', 'T', 'r', 'sigma', 'lambda_j', 'mu_j', 'sigma_j'],
    'VG': ['S', 'K', 'T', 'r', 'sigma', 'theta', 'nu'],
    'DUPIRE': ['S', 'K', 'T', 'r'],  # Removed 'sigma' and 'local_vol_surface'
}

# Noms des paramètres pour l'affichage
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
    'mu': 'Mu',
}

# Valeurs par défaut pour chaque paramètre
default_values = {
    'S': 100.00,
    'K': 100.00,
    'T': 1.00,
    'r': 0.05,
    'sigma': 0.20,
    'alpha': 0.20,
    'beta': 0.50,
    'rho': 0.00,
    'nu': 0.40,
    'v0': 0.04,
    'kappa': 2.00,
    'theta': 0.04,
    'xi': 0.20,
    'lambda_j': 0.10,
    'mu_j': 0.00,
    'sigma_j': 0.10,
    'steps': 100,
    'mu': 0.0,
}

# Increments for parameters
parameter_steps = {
    'S': 1,
    'K': 1,
    'steps': 1,
    'sigma': 0.01,
    'alpha': 0.01,
    'beta': 0.01,
    'rho': 0.01,
    'nu': 0.01,
    'v0': 0.01,
    'kappa': 0.01,
    'theta': 0.01,
    'xi': 0.01,
    'lambda_j': 0.01,
    'mu_j': 0.01,
    'sigma_j': 0.01,
    'mu': 0.01,
    'r': 0.01,
    'T': 0.01,
}

# Parameters that must be positive
positive_params = ['sigma', 'alpha', 'nu', 'v0', 'kappa', 'theta', 'xi', 'lambda_j', 'sigma_j', 'steps', 'T']

# Paramètres pour les axes de la heatmap par modèle
heatmap_params = {
    'BS': ['S', 'sigma'],
    'BINOMIAL': ['S', 'sigma'],
    'SABR': ['S', 'alpha'],
    'HESTON': ['S', 'theta'],
    'MERTON': ['S', 'sigma'],
    'VG': ['S', 'sigma'],
    'DUPIRE': ['S', 'T'],  # For Dupire, using S and T
}

# Mise en page de l'application
app.layout = dbc.Container([
    dcc.Store(id='stored-params', data={}),
    html.H1("Option Pricer", style={'textAlign': 'center', 'marginTop': '20px'}),
    html.Hr(),
    dbc.Row([
        # Colonne pour le menu des paramètres
        dbc.Col([
            # Section des crédits en haut
            html.Div([
                html.H4("Credits", style={'textAlign': 'center'}),
                dbc.Button("Jules de Richemont", id='btn-jules', href='https://linkedin.com/in/jules-de-richemont/', target='_blank', color='primary', style={'margin': '5px'}),
                dbc.Button("Antoine Chambellan", id='btn-antoine', href='https://www.linkedin.com/in/antoine-chambellan-63a49820b/', target='_blank', color='primary', style={'margin': '5px'}),
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),
            html.Hr(),  # Separator
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
                tooltip={'always_visible': True},
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
                tooltip={'always_visible': True},
            ),
        ], width=3, style={
            'height': '100vh',
            'overflowY': 'scroll',
            'paddingLeft': '20px',
            'paddingRight': '20px',
            'backgroundColor': '#303030',
            'marginLeft': '20px',
            'marginRight': '20px',
        }),
        # Colonne pour les graphiques et les résultats
        dbc.Col([
            html.Div([
                html.Div([
                    html.Label('Call Price', style={'fontSize': '15px', 'fontWeight': 'normal'}),
                    html.Div(id='call-price', style={'fontSize': '18px', 'fontWeight': 'bold'}),
                ], style={
                    'border': '3px solid #4CAF50',
                    'borderRadius': '15px',
                    'padding': '10px',
                    'backgroundColor': '#4CAF50',
                    'color': 'black',
                    'width': '250px',
                    'textAlign': 'center',
                    'display': 'inline-block',
                    'marginRight': '50px',
                }),
                html.Div([
                    html.Label('Put Price', style={'fontSize': '15px', 'fontWeight': 'normal'}),
                    html.Div(id='put-price', style={'fontSize': '18px', 'fontWeight': 'bold'}),
                ], style={
                    'border': '3px solid #FF6347',
                    'borderRadius': '15px',
                    'padding': '10px',
                    'backgroundColor': '#FF6347',
                    'color': 'black',
                    'width': '250px',
                    'textAlign': 'center',
                    'display': 'inline-block',
                }),
            ], style={'textAlign': 'center', 'marginTop': '20px'}),
            html.Hr(),
            dcc.Tabs(id='tabs', value='tab-1', children=[
                dcc.Tab(label='Heatmap', value='tab-1', children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='heatmap-call', style={'height': '60vh'}), width=6),
                        dbc.Col(dcc.Graph(id='heatmap-put', style={'height': '60vh'}), width=6),
                    ])
                ], style={'backgroundColor': '#303030'}),
                dcc.Tab(label='3D Surface', value='tab-2', children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='surface-call', style={'height': '60vh'}), width=6),
                        dbc.Col(dcc.Graph(id='surface-put', style={'height': '60vh'}), width=6),
                    ])
                ], style={'backgroundColor': '#303030'}),
            ], colors={'primary': '#303030', 'background': '#303030'}),
        ], width=8, style={
            'paddingLeft': '20px',
            'paddingRight': '20px',
            'marginLeft': '20px',
            'marginRight': '20px',
        }),
    ], style={'height': '100vh'}),
], fluid=True, style={'padding': '0', 'margin': '0'})

# Callback pour mettre à jour les paramètres en fonction du modèle sélectionné
@app.callback(
    Output('parameter-inputs', 'children'),
    Input('model-dropdown', 'value'),
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
            html.Br(),
        ]))
    return inputs

# Callback pour mettre à jour le slider de spot price lorsque le spot price change
@app.callback(
    [Output('spot-slider', 'value'),
     Output('spot-slider', 'min'),
     Output('spot-slider', 'max'),
     Output('spot-slider', 'marks')],
    Input({'type': 'parameter-input', 'index': 'S'}, 'value'),
)
def update_spot_slider(spot_price):
    # Définir la plage autour du spot price
    range_width = 50  # Demi-largeur de la plage
    min_spot = max(0, spot_price - range_width)
    max_spot = spot_price + range_width
    marks = {int(i): f'{int(i)}' for i in range(int(min_spot), int(max_spot)+1, 10)}
    return [min_spot, max_spot], min_spot, max_spot, marks

# Callback pour calculer les prix des options et générer les graphiques
@app.callback(
    [
        Output('call-price', 'children'),
        Output('put-price', 'children'),
        Output('heatmap-call', 'figure'),
        Output('heatmap-put', 'figure'),
        Output('surface-call', 'figure'),
        Output('surface-put', 'figure'),
    ],
    [
        Input('model-dropdown', 'value'),
        Input({'type': 'parameter-input', 'index': ALL}, 'value'),
        Input('spot-slider', 'value'),
        Input('vol-slider', 'value'),
    ],
    [State({'type': 'parameter-input', 'index': ALL}, 'id')]
)
def update_output(model, param_values, spot_range, vol_range, param_ids):
    params = {param_id['index']: value for param_id, value in zip(param_ids, param_values)}
    required_params = model_parameters[model]
    # Vérification que tous les paramètres requis sont présents
    if any(param not in params or params[param] in [None, ''] for param in required_params):
        return "N/A", "N/A", {}, {}, {}, {}
    # Création de l'instance du pricer
    try:
        adjusted_params = params.copy()
        num_simulations = 10000  # Nombre de simulations Monte Carlo
        if model == 'HESTON':
            pricer = Heston_pricer(
                S=adjusted_params['S'],
                K=adjusted_params['K'],
                T=adjusted_params['T'],
                r=adjusted_params['r'],
                kappa=adjusted_params['kappa'],
                theta=adjusted_params['theta'],
                xi=adjusted_params['xi'],
                rho=adjusted_params['rho'],
                v0=adjusted_params['v0'],
                mu=adjusted_params['mu'],
                num_simulations=num_simulations
            )
        elif model == 'MERTON':
            pricer = Merton_pricer(
                S=adjusted_params['S'],
                K=adjusted_params['K'],
                T=adjusted_params['T'],
                r=adjusted_params['r'],
                sigma=adjusted_params['sigma'],
                lambda_j=adjusted_params['lambda_j'],
                mu_j=adjusted_params['mu_j'],
                sigma_j=adjusted_params['sigma_j'],
                num_simulations=num_simulations
            )
        elif model == 'DUPIRE':
            # For Dupire model, we need to define a local volatility surface
            # Here, we'll use a placeholder function for demonstration
            local_vol_surface = lambda S, T: 0.2 * np.ones_like(S)  # Modifié pour gérer les tableaux
            pricer = Dupire_pricer(
                S=adjusted_params['S'],
                K=adjusted_params['K'],
                T=adjusted_params['T'],
                r=adjusted_params['r'],
                local_vol_surface=local_vol_surface,
                num_simulations=num_simulations
            )
        elif model == 'BS':
            # Ensure sigma is positive
            if adjusted_params['sigma'] <= 0:
                return "Error: Volatility sigma must be positive", "Error: Volatility sigma must be positive", {}, {}, {}, {}
            pricer = BS_pricer(**adjusted_params)
        elif model == 'BINOMIAL':
            pricer = Binomial_pricer(**adjusted_params)
        elif model == 'SABR':
            pricer = SABR_pricer(**adjusted_params)
        elif model == 'VG':
            pricer = VG_pricer(**adjusted_params)
        else:
            return "Unknown model", "Unknown model", {}, {}, {}, {}
        call_price, put_price = pricer.get_european_option()
        call_price_str = f"${call_price:.3f}"
        put_price_str = f"${put_price:.3f}"
    except Exception as e:
        return f"Error: {e}", f"Error: {e}", {}, {}, {}, {}
    # Génération des graphiques
    min_spot, max_spot = spot_range
    S_values = np.linspace(min_spot, max_spot, 11)
    min_vol, max_vol = vol_range
    x_param = heatmap_params[model][0]
    y_param = heatmap_params[model][1]
    x_label = parameter_names[x_param]
    y_label = parameter_names[y_param]
    if y_param in ['sigma', 'alpha', 'v0', 'theta']:
        y_min = min_vol
        y_max = max_vol
    else:
        y_min = default_values.get(y_param, 0)
        y_max = default_values.get(y_param, 1)
    Y_values = np.linspace(y_min, y_max, 11)
    X_grid, Y_grid = np.meshgrid(S_values, Y_values)
    call_prices = np.zeros_like(X_grid)
    put_prices = np.zeros_like(X_grid)
    for i in range(X_grid.shape[0]):
        for j in range(X_grid.shape[1]):
            params_loop = adjusted_params.copy()
            params_loop[x_param] = X_grid[i, j]
            params_loop[y_param] = Y_grid[i, j]
            try:
                if model == 'HESTON':
                    pricer_loop = Heston_pricer(
                        S=params_loop['S'],
                        K=params_loop['K'],
                        T=params_loop['T'],
                        r=params_loop['r'],
                        kappa=params_loop['kappa'],
                        theta=params_loop['theta'],
                        xi=params_loop['xi'],
                        rho=params_loop['rho'],
                        v0=params_loop['v0'],
                        mu=params_loop['mu'],
                        num_simulations=num_simulations
                    )
                elif model == 'MERTON':
                    pricer_loop = Merton_pricer(
                        S=params_loop['S'],
                        K=params_loop['K'],
                        T=params_loop['T'],
                        r=params_loop['r'],
                        sigma=params_loop['sigma'],
                        lambda_j=params_loop['lambda_j'],
                        mu_j=params_loop['mu_j'],
                        sigma_j=params_loop['sigma_j'],
                        num_simulations=num_simulations
                    )
                elif model == 'DUPIRE':
                    pricer_loop = Dupire_pricer(
                        S=params_loop['S'],
                        K=params_loop['K'],
                        T=params_loop['T'],
                        r=params_loop['r'],
                        local_vol_surface=local_vol_surface,
                        num_simulations=num_simulations
                    )
                elif model == 'BS':
                    # Ensure sigma is positive
                    if params_loop['sigma'] <= 0:
                        call_prices[i, j] = np.nan
                        put_prices[i, j] = np.nan
                        continue
                    pricer_loop = BS_pricer(**params_loop)
                elif model == 'BINOMIAL':
                    pricer_loop = Binomial_pricer(**params_loop)
                elif model == 'SABR':
                    pricer_loop = SABR_pricer(**params_loop)
                elif model == 'VG':
                    pricer_loop = VG_pricer(**params_loop)
                else:
                    continue
                call, put = pricer_loop.get_european_option()
                call_prices[i, j] = call
                put_prices[i, j] = put
            except:
                call_prices[i, j] = np.nan
                put_prices[i, j] = np.nan
    # Création des figures
    heatmap_call = go.Figure(data=go.Heatmap(
        z=call_prices,
        x=S_values,
        y=Y_values,
        colorscale='RdYlGn',
        text=np.round(call_prices, 3),
        texttemplate="%{text}",
        hovertemplate=f'{x_label}: %{{x}}<br>{y_label}: %{{y}}<br>Call Price: %{{z:.3f}}<extra></extra>',
    ))
    heatmap_call.update_layout(
        title='Call Price',
        xaxis_title=x_label,
        yaxis_title=y_label,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(50,50,50,1)',
        font_color='white',
        xaxis=dict(gridcolor='gray'),
        yaxis=dict(gridcolor='gray'),
    )
    heatmap_put = go.Figure(data=go.Heatmap(
        z=put_prices,
        x=S_values,
        y=Y_values,
        colorscale='RdYlGn',
        text=np.round(put_prices, 3),
        texttemplate="%{text}",
        hovertemplate=f'{x_label}: %{{x}}<br>{y_label}: %{{y}}<br>Put Price: %{{z:.3f}}<extra></extra>',
    ))
    heatmap_put.update_layout(
        title='Put Price',
        xaxis_title=x_label,
        yaxis_title=y_label,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(50,50,50,1)',
        font_color='white',
        xaxis=dict(gridcolor='gray'),
        yaxis=dict(gridcolor='gray'),
    )
    surface_call = go.Figure(data=[go.Surface(
        z=call_prices,
        x=S_values,
        y=Y_values,
        colorscale='RdYlGn',
    )])
    surface_call.update_layout(
        title='Surface 3D Call',
        scene=dict(
            xaxis_title=x_label,
            yaxis_title=y_label,
            zaxis_title='Call Price',
            xaxis=dict(backgroundcolor='rgb(50,50,50)', gridcolor='gray'),
            yaxis=dict(backgroundcolor='rgb(50,50,50)', gridcolor='gray'),
            zaxis=dict(backgroundcolor='rgb(50,50,50)', gridcolor='gray'),
            bgcolor='rgb(50,50,50)',
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
    )
    surface_put = go.Figure(data=[go.Surface(
        z=put_prices,
        x=S_values,
        y=Y_values,
        colorscale='RdYlGn',
    )])
    surface_put.update_layout(
        title='Surface 3D Put',
        scene=dict(
            xaxis_title=x_label,
            yaxis_title=y_label,
            zaxis_title='Put Price',
            xaxis=dict(backgroundcolor='rgb(50,50,50)', gridcolor='gray'),
            yaxis=dict(backgroundcolor='rgb(50,50,50)', gridcolor='gray'),
            zaxis=dict(backgroundcolor='rgb(50,50,50)', gridcolor='gray'),
            bgcolor='rgb(50,50,50)',
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
    )
    return call_price_str, put_price_str, heatmap_call, heatmap_put, surface_call, surface_put

if __name__ == '__main__':
    app.run_server(debug=True)
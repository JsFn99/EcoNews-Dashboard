# components/auth.py
from dash import html, dcc
from config.settings import Config

config = Config()


def create_login_form():
    """Create login form"""
    return html.Div([
        html.Div([
            html.H2("Connexion", style={
                'textAlign': 'center',
                'color': config.COLORS['primary'],
                'marginBottom': '30px'
            }),

            html.Div([
                html.Label("Nom d'utilisateur:", style={'marginBottom': '5px', 'display': 'block'}),
                dcc.Input(
                    id='login-username',
                    type='text',
                    placeholder="Entrez votre nom d'utilisateur",
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'marginBottom': '15px',
                        'border': f'1px solid {config.COLORS["border"]}',
                        'borderRadius': '5px'
                    }
                )
            ]),

            html.Div([
                html.Label("Mot de passe:", style={'marginBottom': '5px', 'display': 'block'}),
                dcc.Input(
                    id='login-password',
                    type='password',
                    placeholder="Entrez votre mot de passe",
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'marginBottom': '15px',
                        'border': f'1px solid {config.COLORS["border"]}',
                        'borderRadius': '5px'
                    }
                )
            ]),

            html.Button(
                "Se connecter",
                id='login-button',
                n_clicks=0,
                style={
                    'width': '100%',
                    'padding': '12px',
                    'backgroundColor': config.COLORS['primary'],
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'fontSize': '16px',
                    'marginBottom': '15px'
                }
            ),

            html.Div(id='login-message', style={'textAlign': 'center', 'marginTop': '10px'}),

            html.Hr(),

            html.Div([
                html.P("Pas encore de compte?", style={'textAlign': 'center', 'margin': '10px 0'}),
                html.Button(
                    "Créer un compte",
                    id={'type': 'show-form', 'form': 'register'},
                    n_clicks=0,
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'backgroundColor': 'transparent',
                        'color': config.COLORS['primary'],
                        'border': f'1px solid {config.COLORS["primary"]}',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                )
            ])
        ], style={
            'maxWidth': '400px',
            'margin': '50px auto',
            'padding': '30px',
            'border': f'1px solid {config.COLORS["border"]}',
            'borderRadius': '10px',
            'backgroundColor': 'white',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
        })
    ])


def create_register_form():
    """Create registration form"""
    return html.Div([
        html.Div([
            html.H2("Créer un compte", style={
                'textAlign': 'center',
                'color': config.COLORS['primary'],
                'marginBottom': '30px'
            }),

            html.Div([
                html.Label("Nom d'utilisateur:", style={'marginBottom': '5px', 'display': 'block'}),
                dcc.Input(
                    id='register-username',
                    type='text',
                    placeholder="Choisissez un nom d'utilisateur",
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'marginBottom': '15px',
                        'border': f'1px solid {config.COLORS["border"]}',
                        'borderRadius': '5px'
                    }
                )
            ]),

            html.Div([
                html.Label("Email:", style={'marginBottom': '5px', 'display': 'block'}),
                dcc.Input(
                    id='register-email',
                    type='email',
                    placeholder="Entrez votre email",
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'marginBottom': '15px',
                        'border': f'1px solid {config.COLORS["border"]}',
                        'borderRadius': '5px'
                    }
                )
            ]),

            html.Div([
                html.Label("Mot de passe:", style={'marginBottom': '5px', 'display': 'block'}),
                dcc.Input(
                    id='register-password',
                    type='password',
                    placeholder="Choisissez un mot de passe",
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'marginBottom': '15px',
                        'border': f'1px solid {config.COLORS["border"]}',
                        'borderRadius': '5px'
                    }
                )
            ]),

            html.Div([
                html.Label("Confirmer le mot de passe:", style={'marginBottom': '5px', 'display': 'block'}),
                dcc.Input(
                    id='register-confirm-password',
                    type='password',
                    placeholder="Confirmez votre mot de passe",
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'marginBottom': '15px',
                        'border': f'1px solid {config.COLORS["border"]}',
                        'borderRadius': '5px'
                    }
                )
            ]),

            html.Button(
                "Créer le compte",
                id='register-button',
                n_clicks=0,
                style={
                    'width': '100%',
                    'padding': '12px',
                    'backgroundColor': config.COLORS['primary'],
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'fontSize': '16px',
                    'marginBottom': '15px'
                }
            ),

            html.Div(id='register-message', style={'textAlign': 'center', 'marginTop': '10px'}),

            html.Hr(),

            html.Div([
                html.P("Déjà un compte?", style={'textAlign': 'center', 'margin': '10px 0'}),
                html.Button(
                    "Se connecter",
                    id={'type': 'show-form', 'form': 'login'},
                    n_clicks=0,
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'backgroundColor': 'transparent',
                        'color': config.COLORS['primary'],
                        'border': f'1px solid {config.COLORS["primary"]}',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                )
            ])
        ], style={
            'maxWidth': '400px',
            'margin': '50px auto',
            'padding': '30px',
            'border': f'1px solid {config.COLORS["border"]}',
            'borderRadius': '10px',
            'backgroundColor': 'white',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
        })
    ])

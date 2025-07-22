# components/header.py
from dash import html, dcc
from flask_login import current_user
from styles.styles import (
    navbar_style, toggle_button_style, logo_style, sidebar_style,
    sidebar_link_style, sidebar_dropdown_header_style, sidebar_dropdown_content_style,
    sidebar_dropdown_link_style, COLORS
)


def create_navbar():
    """Create the main navigation bar"""
    return html.Div([
        html.Div([
            html.Button(
                html.I(className='fas fa-bars'),
                id='sidebar-toggle',
                style=toggle_button_style,
                n_clicks=0
            ),
            html.H1("Observatoire Économique Intelligent",
                    style={'color': COLORS['light'], 'fontWeight': '700', 'margin': '0 0 0 20px', 'fontSize': '26px'}),
        ], style={'display': 'flex', 'alignItems': 'center'}),

        html.Div([
            # User menu
            html.Div(id='user-menu-container'),

            html.Img(
                src='static/logo.jpg',
                alt='Logo',
                style=logo_style
            ),
        ], style={'display': 'flex', 'alignItems': 'center', 'gap': '15px'})
    ], style=navbar_style)


def create_user_menu(user=None):
    """Create user menu based on authentication status"""
    if user:
        return html.Div([
            html.Div([
                html.I(className='fas fa-user', style={'marginRight': '8px'}),
                html.Span(user.username),
                html.I(className='fas fa-chevron-down', style={'marginLeft': '8px'})
            ],
                id='user-menu-button',
                style={
                    'color': COLORS['light'],
                    'cursor': 'pointer',
                    'padding': '8px 15px',
                    'borderRadius': '5px',
                    'backgroundColor': 'rgba(255,255,255,0.1)',
                    'display': 'flex',
                    'alignItems': 'center'
                }),

            html.Div([
                html.Div([
                    html.I(className='fas fa-user', style={'marginRight': '8px'}),
                    'Mon Profil'
                ], style={'padding': '10px 15px', 'cursor': 'pointer', 'borderBottom': '1px solid #eee'}),

                html.Div([
                    html.I(className='fas fa-star', style={'marginRight': '8px'}),
                    'Mes Favoris'
                ], style={'padding': '10px 15px', 'cursor': 'pointer', 'borderBottom': '1px solid #eee'}),

                html.Div([
                    html.I(className='fas fa-sign-out-alt', style={'marginRight': '8px'}),
                    'Déconnexion'
                ],
                    id='logout-button',
                    style={'padding': '10px 15px', 'cursor': 'pointer', 'color': 'red'})
            ],
                id='user-dropdown',
                style={
                    'display': 'none',
                    'position': 'absolute',
                    'top': '100%',
                    'right': '0',
                    'background': 'white',
                    'border': '1px solid #ddd',
                    'borderRadius': '5px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                    'minWidth': '150px',
                    'zIndex': '1000'
                })
        ], style={'position': 'relative'}, className='user-menu')
    else:
        return html.Div([
            dcc.Link([
                html.I(className='fas fa-sign-in-alt', style={'marginRight': '8px'}),
                'Connexion'
            ],
                href='/auth',
                style={
                    'color': COLORS['light'],
                    'textDecoration': 'none',
                    'padding': '8px 15px',
                    'borderRadius': '5px',
                    'backgroundColor': 'rgba(255,255,255,0.1)',
                    'display': 'flex',
                    'alignItems': 'center'
                })
        ])


def create_sidebar():
    """Create the sidebar navigation"""
    return html.Div([
        # Home link
        dcc.Link([
            html.I(className='fas fa-home', style={'marginRight': '10px', 'width': '20px'}),
            'Accueil'
        ], href='/', style=sidebar_link_style, className='sidebar-link'),

        # Bourse section (dropdown)
        html.Div([
            html.Div([
                html.Div([
                    html.I(className='fas fa-chart-line', style={'marginRight': '10px', 'width': '20px'}),
                    'Bourse de Casablanca'
                ], style={'display': 'flex', 'alignItems': 'center'}),
                html.I(id='bourse-chevron', className='fas fa-chevron-down',
                       style={'transition': 'transform 0.3s ease'})
            ], style=sidebar_dropdown_header_style, id='bourse-dropdown-header', n_clicks=0),

            html.Div([
                dcc.Link([
                    html.I(className='fas fa-chart-bar', style={'marginRight': '10px', 'width': '20px'}),
                    'Données Techniques'
                ], href='/bourse', style=sidebar_dropdown_link_style, className='sidebar-link'),
                dcc.Link([
                    html.I(className='fas fa-newspaper', style={'marginRight': '10px', 'width': '20px'}),
                    'Sentiment du Marché'
                ], href='/News', style=sidebar_dropdown_link_style, className='sidebar-link'),
            ], id='bourse-dropdown-content', style=sidebar_dropdown_content_style),
        ]),

        # Other links
        dcc.Link([
            html.I(className='fas fa-briefcase', style={'marginRight': '10px', 'width': '20px'}),
            'Économie'
        ], href='/eco', style=sidebar_link_style, className='sidebar-link'),

        dcc.Link([
            html.I(className='fas fa-file-alt', style={'marginRight': '10px', 'width': '20px'}),
            'Zoom'
        ], href='/zoom', style=sidebar_link_style, className='sidebar-link'),

        dcc.Link([
            html.I(className='fas fa-star', style={'marginRight': '10px', 'width': '20px'}),
            'Mes Articles Favoris'
        ], href='/my_articles', style=sidebar_link_style, className='sidebar-link'),
    ], id='sidebar', style=sidebar_style)

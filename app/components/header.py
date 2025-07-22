# components/header.py
from dash import html, dcc
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
        
        html.Img(
            src='static/logo.jpg',
            alt='Logo',
            style=logo_style
        ),
    ], style=navbar_style)

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
                html.I(id='bourse-chevron', className='fas fa-chevron-down', style={'transition': 'transform 0.3s ease'})
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
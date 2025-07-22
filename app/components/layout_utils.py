# components/layout_utils.py
from dash import html
from styles.styles import COLORS

def create_overlay():
    """Create overlay for mobile sidebar"""
    return html.Div(
        id='sidebar-overlay',
        style={
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0, 0, 0, 0.5)',
            'zIndex': '998',
            'display': 'none'
        },
        n_clicks=0
    )

def create_footer():
    """Create application footer"""
    return html.Footer([
        html.Div([
            html.P([
                "© 2024 Observatoire Économique Intelligent - ",
                html.A("BMCE Bank", href="#", style={'color': COLORS['primary']}),
                " | Tous droits réservés"
            ], style={
                'margin': '0',
                'textAlign': 'center',
                'color': '#666',
                'fontSize': '14px'
            })
        ], style={
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'borderTop': '1px solid #dee2e6'
        })
    ],
    id='footer',
    style={
        'marginTop': 'auto',
        'transition': 'margin-left 0.3s ease'
    })

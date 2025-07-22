# components/layout_utils.py
from dash import html
from styles.styles import footer_style

def create_overlay():
    """Create the overlay for mobile sidebar"""
    return html.Div(id='sidebar-overlay', style={
        'position': 'fixed',
        'top': '0',
        'left': '0',
        'right': '0',
        'bottom': '0',
        'backgroundColor': 'rgba(0, 0, 0, 0.5)',
        'zIndex': '998',
        'display': 'none',
    })

def create_footer():
    """Create the footer component"""
    return html.Footer([
        html.P([
            "Développé par ",
            html.Strong("FNINE Jasser"),
            " • © 2025 Observatoire Économique Intelligent"
        ], style={'margin': '0'})
    ], style=footer_style, id='footer')
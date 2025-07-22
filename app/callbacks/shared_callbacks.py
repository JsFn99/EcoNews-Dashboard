# callbacks/shared_callbacks.py
import dash
from dash import Input, Output, State, callback


def register_callbacks(app):
    """Register all shared callbacks"""

    # Callback for sidebar toggle
    @app.callback(
        [Output('sidebar', 'className'),
         Output('page-content', 'className'),
         Output('footer', 'className'),
         Output('sidebar-overlay', 'style'),
         Output('sidebar-state', 'data')],
        [Input('sidebar-toggle', 'n_clicks'),
         Input('sidebar-overlay', 'n_clicks')],
        [State('sidebar-state', 'data')]
    )
    def toggle_sidebar(toggle_clicks, overlay_clicks, sidebar_state):
        ctx = dash.callback_context
        if not ctx.triggered:
            return '', '', '', {'display': 'none'}, {'open': False}

        if ctx.triggered[0]['prop_id'] in ['sidebar-toggle.n_clicks', 'sidebar-overlay.n_clicks']:
            is_open = not sidebar_state['open']
            sidebar_class = 'sidebar-open' if is_open else ''
            content_class = 'content-shifted' if is_open else ''
            footer_class = 'footer-shifted' if is_open else ''
            overlay_style = {'display': 'block'} if is_open else {'display': 'none'}

            return sidebar_class, content_class, footer_class, overlay_style, {'open': is_open}

        return '', '', '', {'display': 'none'}, {'open': False}

    # Callback for bourse dropdown
    @app.callback(
        [Output('bourse-dropdown-content', 'className'),
         Output('bourse-chevron', 'className'),
         Output('bourse-dropdown-state', 'data')],
        [Input('bourse-dropdown-header', 'n_clicks')],
        [State('bourse-dropdown-state', 'data')]
    )
    def toggle_bourse_dropdown(n_clicks, dropdown_state):
        if n_clicks is None or n_clicks == 0:
            return '', 'fas fa-chevron-down', {'open': False}

        is_open = not dropdown_state['open']
        dropdown_class = 'dropdown-open' if is_open else ''
        chevron_class = 'fas fa-chevron-down chevron-rotated' if is_open else 'fas fa-chevron-down'

        return dropdown_class, chevron_class, {'open': is_open}

    # Page routing callback
    @app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
    def display_page(pathname):
        # Import pages here to avoid circular imports
        from pages import bourse, eco, home, my_articles, news, zoom

        if pathname == '/bourse':
            # Check if layout is a function or object
            return bourse.layout() if callable(bourse.layout) else bourse.layout
        elif pathname == '/News':
            # Check if layout is a function or object
            return news.layout() if callable(news.layout) else news.layout
        elif pathname == '/zoom':
            # Check if layout is a function or object
            return zoom.layout() if callable(zoom.layout) else zoom.layout
        elif pathname == '/eco':
            # Check if layout is a function or object
            return eco.layout() if callable(eco.layout) else eco.layout
        elif pathname == '/my_articles':
            # Check if layout is a function or object
            return my_articles.layout() if callable(my_articles.layout) else my_articles.layout
        else:  # Default to home page
            # Check if layout is a function or object
            return home.layout() if callable(home.layout) else home.layout

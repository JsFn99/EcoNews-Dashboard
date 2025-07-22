# callbacks/shared_callbacks.py
import dash
from dash import Input, Output, State, callback
from flask_login import current_user, logout_user
from components.header import create_user_menu
from models.user import UserManager


def register_callbacks(app):
    """Register all shared callbacks"""

    user_manager = UserManager()

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

    # User menu callback
    @app.callback(
        Output('user-menu-container', 'children'),
        [Input('url', 'pathname')]
    )
    def update_user_menu(pathname):
        if current_user.is_authenticated:
            return create_user_menu(current_user)
        else:
            return create_user_menu(None)

    # User dropdown toggle callback
    @app.callback(
        Output('user-dropdown', 'style'),
        [Input('user-menu-button', 'n_clicks')],
        [State('user-dropdown', 'style')],
        prevent_initial_call=True
    )
    def toggle_user_dropdown(n_clicks, current_style):
        if n_clicks:
            if current_style.get('display') == 'block':
                current_style['display'] = 'none'
            else:
                current_style['display'] = 'block'
        return current_style

    # Logout callback
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        [Input('logout-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def handle_logout(n_clicks):
        if n_clicks:
            logout_user()
            return '/auth'
        return dash.no_update

    # Page routing callback with authentication check
    @app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
    def display_page(pathname):
        # Import pages here to avoid circular imports
        from pages import bourse, eco, home, my_articles, news, zoom, auth

        # Public pages (no authentication required)
        public_pages = ['/auth']

        # Check if user needs to be authenticated
        if pathname not in public_pages and not current_user.is_authenticated:
            return auth.layout() if callable(auth.layout) else auth.layout

        if pathname == '/auth':
            # If already authenticated, redirect to home
            if current_user.is_authenticated:
                return home.layout() if callable(home.layout) else home.layout
            return auth.layout() if callable(auth.layout) else auth.layout
        elif pathname == '/bourse':
            return bourse.layout() if callable(bourse.layout) else bourse.layout
        elif pathname == '/News':
            return news.layout() if callable(news.layout) else news.layout
        elif pathname == '/zoom':
            return zoom.layout() if callable(zoom.layout) else zoom.layout
        elif pathname == '/eco':
            return eco.layout() if callable(eco.layout) else eco.layout
        elif pathname == '/my_articles':
            return my_articles.layout() if callable(my_articles.layout) else my_articles.layout
        else:  # Default to home page
            return home.layout() if callable(home.layout) else home.layout

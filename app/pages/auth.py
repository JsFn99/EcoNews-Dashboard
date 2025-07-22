# pages/auth.py
from dash import html, dcc
from components.auth import create_login_form, create_register_form


def layout():
    return html.Div([
        dcc.Store(id='auth-mode', data='login'),  # 'login' or 'register'
        html.Div(id='auth-content', children=create_login_form())
    ])


def register_callbacks(app):
    from dash import Input, Output, State, callback_context, ALL
    from flask_login import login_user, current_user
    from models.user import UserManager
    import dash

    user_manager = UserManager()

    # Combined callback for both login and register form switching
    @app.callback(
        [Output('auth-content', 'children'),
         Output('auth-mode', 'data')],
        [Input({'type': 'show-form', 'form': ALL}, 'n_clicks')],
        [State('auth-mode', 'data')],
        prevent_initial_call=True
    )
    def toggle_auth_mode(n_clicks_list, current_mode):
        ctx = callback_context
        if not ctx.triggered:
            return create_login_form(), 'login'

        # Check if any button was clicked
        if any(n_clicks_list):
            button_id = ctx.triggered[0]['prop_id']
            if 'register' in button_id:
                return create_register_form(), 'register'
            elif 'login' in button_id:
                return create_login_form(), 'login'

        return create_login_form(), 'login'

    @app.callback(
        [Output('login-message', 'children'),
         Output('url', 'pathname', allow_duplicate=True)],
        [Input('login-button', 'n_clicks')],
        [State('login-username', 'value'),
         State('login-password', 'value')],
        prevent_initial_call=True
    )
    def handle_login(n_clicks, username, password):
        if n_clicks == 0 or not username or not password:
            return "", dash.no_update

        try:
            user = user_manager.authenticate_user(username, password)
            if user:
                login_user(user)
                return html.Div("Connexion réussie!", style={'color': 'green'}), '/'
            else:
                return html.Div("Nom d'utilisateur ou mot de passe incorrect", style={'color': 'red'}), dash.no_update
        except Exception as e:
            print(f"Login error: {e}")
            return html.Div("Erreur lors de la connexion", style={'color': 'red'}), dash.no_update

    @app.callback(
        Output('register-message', 'children'),
        [Input('register-button', 'n_clicks')],
        [State('register-username', 'value'),
         State('register-email', 'value'),
         State('register-password', 'value'),
         State('register-confirm-password', 'value')],
        prevent_initial_call=True
    )
    def handle_register(n_clicks, username, email, password, confirm_password):
        if n_clicks == 0:
            return ""

        if not all([username, email, password, confirm_password]):
            return html.Div("Tous les champs sont requis", style={'color': 'red'})

        if password != confirm_password:
            return html.Div("Les mots de passe ne correspondent pas", style={'color': 'red'})

        if len(password) < 6:
            return html.Div("Le mot de passe doit contenir au moins 6 caractères", style={'color': 'red'})

        try:
            user = user_manager.create_user(username, email, password)
            if user:
                return html.Div("Compte créé avec succès! Vous pouvez maintenant vous connecter.",
                                style={'color': 'green'})
            else:
                return html.Div("Nom d'utilisateur ou email déjà utilisé", style={'color': 'red'})
        except Exception as e:
            print(f"Registration error: {e}")
            return html.Div("Erreur lors de la création du compte", style={'color': 'red'})

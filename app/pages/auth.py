# pages/auth.py
from components.auth import create_login_form, create_register_form
from dash import dcc, html


def layout():
    return html.Div([
        # Add custom CSS for modern styling
        html.Link(
            rel='stylesheet',
            href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
        ),
        html.Link(
            rel='stylesheet',
            href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
        ),

        dcc.Store(id='auth-mode', data='login'),

        # Main container
        html.Div([
            # Centered auth card
            html.Div([
                # Header section with logo and branding
                html.Div([
                    html.Div([
                        html.Img(
                            src='/static/bmce.ico',
                            style={
                                'width': '80px',
                                'height': '80px',
                                'marginBottom': '24px',
                                'borderRadius': '16px',
                                'boxShadow': '0 8px 32px rgba(86, 121, 216, 0.15)'
                            }
                        ),
                        html.H1(
                            'EcoNews Dashboard',
                            style={
                                'color': '#2F3F6A',
                                'fontFamily': 'Inter, sans-serif',
                                'fontWeight': '700',
                                'fontSize': '32px',
                                'marginBottom': '8px',
                                'textAlign': 'center',
                                'letterSpacing': '-0.5px'
                            }
                        ),
                        html.P(
                            'Votre plateforme pour les actualités economiques et financières',
                            style={
                                'color': '#64748b',
                                'fontFamily': 'Inter, sans-serif',
                                'fontSize': '16px',
                                'textAlign': 'center',
                                'lineHeight': '1.6',
                                'marginBottom': '40px',
                                'fontWeight': '400'
                            }
                        )
                    ], style={
                        'textAlign': 'center',
                        'marginBottom': '32px'
                    })
                ], style={
                    'paddingBottom': '2px',
                    'borderBottom': '1px solid #e2e8f0'
                }),

                # Auth forms container
                html.Div([
                    html.Div(id='auth-content', children=create_login_form())
                ], style={
                    'paddingTop': '32px'
                })

            ], style={
                'backgroundColor': '#ffffff',
                'borderRadius': '24px',
                'padding': '48px',
                'boxShadow': '0 20px 60px rgba(0, 0, 0, 0.08), 0 8px 32px rgba(0, 0, 0, 0.04)',
                'border': '1px solid #e2e8f0',
                'width': '100%',
                'maxWidth': '480px',
                'margin': '0 auto'
            })

        ], style={
            'minHeight': '100vh',
            'background': 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'padding': '24px',
            'fontFamily': 'Inter, sans-serif'
        })

    ], style={
        'margin': '0',
        'padding': '0'
    })


def register_callbacks(app):
    import dash
    from dash import ALL, Input, Output, State, callback_context
    from flask_login import current_user, login_user
    from models.user import UserManager

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
                return html.Div([
                    html.I(className="fas fa-check-circle", style={'marginRight': '12px', 'fontSize': '16px'}),
                    "Connexion réussie! Redirection en cours..."
                ], style={
                    'color': '#059669',
                    'backgroundColor': '#ecfdf5',
                    'padding': '16px 20px',
                    'borderRadius': '12px',
                    'border': '1px solid #a7f3d0',
                    'fontFamily': 'Inter, sans-serif',
                    'fontSize': '14px',
                    'fontWeight': '500',
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginTop': '16px',
                    'boxShadow': '0 4px 12px rgba(5, 150, 105, 0.1)'
                }), '/'
            else:
                return html.Div([
                    html.I(className="fas fa-exclamation-circle", style={'marginRight': '12px', 'fontSize': '16px'}),
                    "Nom d'utilisateur ou mot de passe incorrect"
                ], style={
                    'color': '#dc2626',
                    'backgroundColor': '#fef2f2',
                    'padding': '16px 20px',
                    'borderRadius': '12px',
                    'border': '1px solid #fecaca',
                    'fontFamily': 'Inter, sans-serif',
                    'fontSize': '14px',
                    'fontWeight': '500',
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginTop': '16px',
                    'boxShadow': '0 4px 12px rgba(220, 38, 38, 0.1)'
                }), dash.no_update
        except Exception as e:
            print(f"Login error: {e}")
            return html.Div([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '12px', 'fontSize': '16px'}),
                "Erreur lors de la connexion. Veuillez réessayer."
            ], style={
                'color': '#d97706',
                'backgroundColor': '#fffbeb',
                'padding': '16px 20px',
                'borderRadius': '12px',
                'border': '1px solid #fed7aa',
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '14px',
                'fontWeight': '500',
                'display': 'flex',
                'alignItems': 'center',
                'marginTop': '16px',
                'boxShadow': '0 4px 12px rgba(217, 119, 6, 0.1)'
            }), dash.no_update

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
            return html.Div([
                html.I(className="fas fa-exclamation-circle", style={'marginRight': '12px', 'fontSize': '16px'}),
                "Tous les champs sont requis"
            ], style={
                'color': '#dc2626',
                'backgroundColor': '#fef2f2',
                'padding': '16px 20px',
                'borderRadius': '12px',
                'border': '1px solid #fecaca',
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '14px',
                'fontWeight': '500',
                'display': 'flex',
                'alignItems': 'center',
                'marginTop': '16px',
                'boxShadow': '0 4px 12px rgba(220, 38, 38, 0.1)'
            })

        if password != confirm_password:
            return html.Div([
                html.I(className="fas fa-exclamation-circle", style={'marginRight': '12px', 'fontSize': '16px'}),
                "Les mots de passe ne correspondent pas"
            ], style={
                'color': '#dc2626',
                'backgroundColor': '#fef2f2',
                'padding': '16px 20px',
                'borderRadius': '12px',
                'border': '1px solid #fecaca',
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '14px',
                'fontWeight': '500',
                'display': 'flex',
                'alignItems': 'center',
                'marginTop': '16px',
                'boxShadow': '0 4px 12px rgba(220, 38, 38, 0.1)'
            })

        if len(password) < 6:
            return html.Div([
                html.I(className="fas fa-exclamation-circle", style={'marginRight': '12px', 'fontSize': '16px'}),
                "Le mot de passe doit contenir au moins 6 caractères"
            ], style={
                'color': '#dc2626',
                'backgroundColor': '#fef2f2',
                'padding': '16px 20px',
                'borderRadius': '12px',
                'border': '1px solid #fecaca',
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '14px',
                'fontWeight': '500',
                'display': 'flex',
                'alignItems': 'center',
                'marginTop': '16px',
                'boxShadow': '0 4px 12px rgba(220, 38, 38, 0.1)'
            })

        try:
            user = user_manager.create_user(username, email, password)
            if user:
                return html.Div([
                    html.I(className="fas fa-check-circle", style={'marginRight': '12px', 'fontSize': '16px'}),
                    "Compte créé avec succès! Vous pouvez maintenant vous connecter."
                ], style={
                    'color': '#059669',
                    'backgroundColor': '#ecfdf5',
                    'padding': '16px 20px',
                    'borderRadius': '12px',
                    'border': '1px solid #a7f3d0',
                    'fontFamily': 'Inter, sans-serif',
                    'fontSize': '14px',
                    'fontWeight': '500',
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginTop': '16px',
                    'boxShadow': '0 4px 12px rgba(5, 150, 105, 0.1)'
                })
            else:
                return html.Div([
                    html.I(className="fas fa-exclamation-circle", style={'marginRight': '12px', 'fontSize': '16px'}),
                    "Nom d'utilisateur ou email déjà utilisé"
                ], style={
                    'color': '#dc2626',
                    'backgroundColor': '#fef2f2',
                    'padding': '16px 20px',
                    'borderRadius': '12px',
                    'border': '1px solid #fecaca',
                    'fontFamily': 'Inter, sans-serif',
                    'fontSize': '14px',
                    'fontWeight': '500',
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginTop': '16px',
                    'boxShadow': '0 4px 12px rgba(220, 38, 38, 0.1)'
                })
        except Exception as e:
            print(f"Registration error: {e}")
            return html.Div([
                html.I(className="fas fa-exclamation-triangle", style={'marginRight': '12px', 'fontSize': '16px'}),
                "Erreur lors de la création du compte. Veuillez réessayer."
            ], style={
                'color': '#d97706',
                'backgroundColor': '#fffbeb',
                'padding': '16px 20px',
                'borderRadius': '12px',
                'border': '1px solid #fed7aa',
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '14px',
                'fontWeight': '500',
                'display': 'flex',
                'alignItems': 'center',
                'marginTop': '16px',
                'boxShadow': '0 4px 12px rgba(217, 119, 6, 0.1)'
            })

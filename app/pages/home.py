# pages/home.py
import pandas as pd
from dash import dcc, html
from flask_login import current_user
from components.media_banner import create_media_banner
from components.news_components import create_news_items_with_favorites
from services.eco_service import EcoService
from config.settings import Config
from models.user import UserManager

# Initialize services
eco_service = EcoService()
config = Config()
user_manager = UserManager()


def layout():
    # Load data
    news_df = eco_service.load_news_data()
    sentiment_fig = eco_service.create_sentiment_chart(news_df)
    theme_fig = eco_service.create_theme_chart(news_df)
    news_items = create_news_items_with_favorites(news_df) if news_df is not None else []

    # Welcome message for authenticated users
    welcome_message = ""
    if current_user.is_authenticated:
        welcome_message = html.Div([
            html.H2(f'Bienvenue, {current_user.username}!',
                    style={
                        'textAlign': 'center',
                        'color': config.COLORS['primary'],
                        'marginBottom': '10px',
                        'fontSize': '1.8rem',
                        'fontWeight': '500'
                    })
        ], style={'marginBottom': '20px'})

    return html.Div([
        # Welcome message
        welcome_message,

        # En-tête principal
        html.Div([
            html.H1('Dernières Actualités Économiques Marocaines et Mondiales',
                    style={
                        'textAlign': 'center',
                        'color': config.COLORS['primary_blue'],
                        'marginBottom': '20px',
                        'fontSize': '2.5rem',
                        'fontWeight': '600',
                        'fontFamily': 'Inter'
                    })
        ]),

        # Rolling Media Banner
        create_media_banner(),

        # Search Field
        html.Div([
            dcc.Input(
                id='search-input',
                type='text',
                placeholder='Rechercher dans les articles...',
                style={
                    'width': '100%',
                    'maxWidth': '600px',
                    'padding': '12px 20px',
                    'fontSize': '16px',
                    'border': f'2px solid {config.COLORS["border"]}',
                    'borderRadius': '25px',
                    'outline': 'none',
                    'boxShadow': '0 2px 8px rgba(59, 130, 246, 0.1)',
                    'transition': 'all 0.3s ease',
                    'fontFamily': '"Segoe UI", sans-serif'
                }
            )
        ], style={
            'textAlign': 'center',
            'marginBottom': '30px',
            'paddingTop': '10px'
        }),

        # Section Actualités
        html.Div([
            html.Div([
                # Chronologie des actualités avec cartes modernes
                html.Div([
                    # En-tête avec contrôles de filtrage
                    html.Div([
                        html.H3('Chronologie des Actualités',
                                style={
                                    'color': config.COLORS['primary'],
                                    'marginBottom': '20px',
                                    'fontSize': '1.5rem',
                                    'fontWeight': '600',
                                    'display': 'inline-block',
                                    'marginRight': '30px'
                                }),

                        # Contrôles de filtrage
                        html.Div([
                            html.Div([
                                dcc.Dropdown(
                                    id='sentiment-filter-dropdown',
                                    options=[
                                        {'label': 'Tous les sentiments', 'value': 'Tous'},
                                        {'label': 'Positif', 'value': 'Positif'},
                                        {'label': 'Négatif', 'value': 'Négatif'},
                                        {'label': 'Neutre', 'value': 'Neutre'}
                                    ],
                                    value='Tous',
                                    style={'width': '180px', 'display': 'inline-block'}
                                )
                            ], style={'display': 'inline-block', 'marginRight': '20px'}),

                            html.Div([
                                dcc.Dropdown(
                                    id='theme-filter-dropdown',
                                    options=[{'label': 'Tous les thèmes', 'value': 'Tous'}] +
                                            [{'label': theme, 'value': theme} for theme in
                                             sorted(news_df['theme'].dropna().unique())] if news_df is not None else [],
                                    value='Tous',
                                    style={'width': '400px', 'display': 'inline-block'}
                                )
                            ], style={'display': 'inline-block'})
                        ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
                    ], style={'marginBottom': '25px', 'display': 'flex', 'alignItems': 'center',
                              'justifyContent': 'space-between'}),

                    # Container pour les actualités
                    html.Div(
                        id='news-container',
                        children=news_items,
                        style={
                            'maxHeight': '900px',
                            'overflowY': 'auto',
                            'border': f'1px solid {config.COLORS["border"]}',
                            'borderRadius': '12px',
                            'padding': '20px',
                            'background': config.COLORS['background']
                        }
                    )
                ], style=config.enhanced_card_style),

                # Cartes de résumé des sentiments des actualités
                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Graph(figure=sentiment_fig, style={'height': '350px'})
                        ], style={**config.enhanced_card_style, 'height': '350px'})
                    ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),

                    html.Div([
                        html.Div([
                            dcc.Graph(figure=theme_fig, style={'height': '350px'})
                        ], style={**config.enhanced_card_style, 'height': '350px'})
                    ], style={'width': '48%', 'display': 'inline-block'})
                ], style={'marginBottom': '40px'}),

            ])
        ], style={'marginBottom': '60px'}),

    ], style={
        'padding': '20px',
        'backgroundColor': config.COLORS['background'],
        'minHeight': '100vh',
        'fontFamily': '"Segoe UI", "Helvetica Neue", Arial, sans-serif'
    })


def register_callbacks(app):
    """Register home page callbacks"""
    from dash import Input, Output, State
    from flask_login import current_user

    # Add favorite article callback
    @app.callback(
        Output('favorite-message', 'children'),
        [Input('add-favorite-button', 'n_clicks')],
        [State('article-id', 'data'),
         State('article-title', 'data'),
         State('article-url', 'data')],
        prevent_initial_call=True
    )
    def add_to_favorites(n_clicks, article_id, article_title, article_url):
        if n_clicks and current_user.is_authenticated:
            success = user_manager.add_favorite(
                current_user.id,
                article_id,
                article_title,
                article_url
            )
            if success:
                return html.Div("Article ajouté aux favoris!", style={'color': 'green'})
            else:
                return html.Div("Article déjà dans les favoris", style={'color': 'orange'})
        return ""

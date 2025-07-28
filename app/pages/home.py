# pages/home.py
import pandas as pd
from dash import dcc, html
from flask_login import current_user
from components.media_banner import create_media_banner
from components.news_components import create_news_items_with_favorites
from services.eco_service import EcoService
from config.settings import Config
from models.user import UserManager
from datetime import date, timedelta

# Initialize services
eco_service = EcoService()
config = Config()
user_manager = UserManager()

def layout():
    # Load initial data
    news_df = eco_service.load_news_data()

    # Default date range (last week)
    today = date.today()
    week_ago = today - timedelta(days=7)
    if not news_df.empty:
        default_filtered_df = news_df[news_df['published'] >= pd.to_datetime(week_ago)]
    else:
        default_filtered_df = pd.DataFrame()

    # Create initial components
    sentiment_fig = eco_service.create_sentiment_chart(default_filtered_df)
    theme_fig = eco_service.create_theme_chart(default_filtered_df)
    news_items = create_news_items_with_favorites(default_filtered_df)
    date_options = eco_service.get_date_range_options()
    theme_options = [{'label': 'Tous les thèmes', 'value': 'Tous'}] + \
                    [{'label': theme, 'value': theme} for theme in sorted(news_df['theme'].dropna().unique())] if not news_df.empty else []

    # Welcome message for authenticated users
    welcome_message = html.Div()
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
        welcome_message,
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
        create_media_banner(),
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
        ], style={'textAlign': 'center', 'marginBottom': '30px', 'paddingTop': '10px'}),
        html.Div([
            html.Div([
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
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Label('Sentiment:', style={'fontSize': '14px', 'fontWeight': '600', 'color': config.COLORS['text'], 'marginBottom': '5px', 'display': 'block'}),
                                dcc.Dropdown(
                                    id='sentiment-filter-dropdown',
                                    options=[
                                        {'label': 'Tous les sentiments', 'value': 'Tous'},
                                        {'label': 'Positif', 'value': 'Positif'},
                                        {'label': 'Négatif', 'value': 'Négatif'},
                                        {'label': 'Neutre', 'value': 'Neutre'}
                                    ],
                                    value='Tous',
                                    style={'width': '200px'}
                                )
                            ], style={'display': 'inline-block', 'marginRight': '20px', 'verticalAlign': 'top'}),
                            html.Div([
                                html.Label('Thème:', style={'fontSize': '14px', 'fontWeight': '600', 'color': config.COLORS['text'], 'marginBottom': '5px', 'display': 'block'}),
                                dcc.Dropdown(
                                    id='theme-filter-dropdown',
                                    options=theme_options,
                                    value='Tous',
                                    style={'width': '400px'}
                                )
                            ], style={'display': 'inline-block', 'marginRight': '20px', 'verticalAlign': 'top'})
                        ], style={'marginBottom': '15px'}),
                        html.Div([
                            html.Div([
                                html.Label('Période:', style={'fontSize': '14px', 'fontWeight': '600', 'color': config.COLORS['text'], 'marginBottom': '5px', 'display': 'block'}),
                                dcc.Dropdown(
                                    id='date-period-dropdown',
                                    options=date_options,
                                    value='week',
                                    style={'width': '200px'}
                                )
                            ], style={'display': 'inline-block', 'marginRight': '20px', 'verticalAlign': 'top'}),
                            html.Div([
                                html.Div([
                                    html.Label('Du:', style={'fontSize': '14px', 'fontWeight': '600', 'color': config.COLORS['text'], 'marginBottom': '5px', 'display': 'block'}),
                                    dcc.DatePickerSingle(id='start-date-picker', date=week_ago, display_format='DD/MM/YYYY', style={'width': '140px'})
                                ], style={'display': 'inline-block', 'marginRight': '15px', 'verticalAlign': 'top'}),
                                html.Div([
                                    html.Label('Au:', style={'fontSize': '14px', 'fontWeight': '600', 'color': config.COLORS['text'], 'marginBottom': '5px', 'display': 'block'}),
                                    dcc.DatePickerSingle(id='end-date-picker', date=today, display_format='DD/MM/YYYY', style={'width': '140px'})
                                ], style={'display': 'inline-block', 'verticalAlign': 'top'})
                            ], id='custom-date-container', style={'display': 'none', 'marginTop': '10px'})
                        ])
                    ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
                ], style={'marginBottom': '25px', 'display': 'flex', 'alignItems': 'flex-start', 'justifyContent': 'space-between', 'flexWrap': 'wrap'}),
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
            ], style={
                'background': config.COLORS['card_bg'], 'padding': '30px', 'border-radius': '16px',
                'box-shadow': '0 8px 24px rgba(59, 130, 246, 0.12)', 'border': f'1px solid {config.COLORS["border"]}',
                'margin-bottom': '24px', 'transition': 'transform 0.2s ease, box-shadow 0.2s ease'
            }),
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(id='sentiment-chart', figure=sentiment_fig, style={'height': '350px'}, config={'responsive': True, 'displayModeBar': False})
                    ], style={'background': config.COLORS['card_bg'], 'padding': '30px', 'border-radius': '16px', 'box-shadow': '0 8px 24px rgba(59, 130, 246, 0.12)', 'border': f'1px solid {config.COLORS["border"]}', 'margin-bottom': '24px', 'transition': 'transform 0.2s ease, box-shadow 0.2s ease', 'height': '420px'})
                ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),
                html.Div([
                    html.Div([
                        dcc.Graph(id='theme-chart', figure=theme_fig, style={'height': '350px'}, config={'responsive': True, 'displayModeBar': False})
                    ], style={'background': config.COLORS['card_bg'], 'padding': '30px', 'border-radius': '16px', 'box-shadow': '0 8px 24px rgba(59, 130, 246, 0.12)', 'border': f'1px solid {config.COLORS["border"]}', 'margin-bottom': '24px', 'transition': 'transform 0.2s ease, box-shadow 0.2s ease', 'height': '420px'})
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'marginBottom': '40px'}),
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

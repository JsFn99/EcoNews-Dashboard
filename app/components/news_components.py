# components/news_components.py

import pandas as pd
from dash import html
from services.stock_service import stock_service
from config.settings import Config

config = Config()


def create_news_items_with_favorites(df):
    """Create economic news items with favorite functionality (for home page)"""
    if df is None or df.empty:
        return [
            html.Div([
                html.P("Aucune actualité disponible pour le moment.",
                       style={
                           'text-align': 'center',
                           'color': config.COLORS['text_light'],
                           'font-size': '16px',
                           'margin': '40px 0'
                       })
            ])
        ]

    items = []

    for i, (idx, row) in enumerate(df.iterrows()):
        sentiment_color = {
            'Positif': config.COLORS['success'],
            'Négatif': config.COLORS['danger'],
            'Neutre': config.COLORS['neutral']
        }.get(row['sentiment'], config.COLORS['neutral'])

        # Check if this article is favorited (using economic news favorites)
        from services.favorites_service import FavoritesService
        favorites_service = FavoritesService()
        favorited = favorites_service.is_favorited(row['title'], row['published'].strftime('%Y-%m-%d %H:%M:%S'))

        # Create unique identifier using title + published date
        unique_id = f"{row['title']}_{row['published'].strftime('%Y-%m-%d %H:%M:%S').replace('-', '').replace(':', '').replace(' ', '_')}"

        items.append(
            html.Div([
                # En-tête avec badges thème et sentiment + bouton favori
                html.Div([
                    html.Div([
                        html.Span(row.get('theme', 'Économie'), style={  # Use theme or default
                            'background': config.COLORS['primary'],
                            'color': 'white',
                            'padding': '8px 16px',
                            'border-radius': '20px',
                            'font-size': '12px',
                            'font-weight': '600',
                            'display': 'inline-block'
                        }),
                        html.Span(row['sentiment'], style={
                            'background': sentiment_color,
                            'color': 'white',
                            'padding': '8px 16px',
                            'border-radius': '20px',
                            'font-size': '12px',
                            'margin-left': '12px',
                            'font-weight': '500',
                            'display': 'inline-block'
                        })
                    ], style={'display': 'inline-block'}),

                    # Favorite button
                    html.Button(
                        '❤️' if favorited else '🤍',
                        id={'type': 'favorite-btn', 'index': unique_id},
                        style={
                            'background': 'none',
                            'border': 'none',
                            'fontSize': '20px',
                            'cursor': 'pointer',
                            'float': 'right',
                            'padding': '5px 10px',
                            'borderRadius': '50%',
                            'transition': 'transform 0.2s ease'
                        },
                        title='Ajouter aux favoris' if not favorited else 'Retirer des favoris'
                    )
                ], style={'margin-bottom': '15px', 'display': 'flex', 'justify-content': 'space-between',
                          'align-items': 'center'}),

                # Store article data as hidden div
                html.Div(
                    id={'type': 'article-data', 'index': unique_id},
                    children=str({
                        'source': row.get('source', ''),
                        'theme': row.get('theme', 'Économie'),
                        'title': row['title'],
                        'summary': row.get('summary', ''),
                        'mini_resume': row.get('mini_resume', row.get('summary', '')),
                        'sentiment': row['sentiment'],
                        'published': row['published'].strftime('%Y-%m-%d %H:%M:%S'),
                        'link': row.get('link', '')
                    }),
                    style={'display': 'none'}
                ),

                # Titre de l'article
                html.H4(row['title'], style={
                    'margin': '0 0 12px 0',
                    'font-size': '18px',
                    'color': config.COLORS['primary'],
                    'line-height': '1.4',
                    'font-weight': '600'
                }),

                # Résumé de l'article
                html.P(row.get('mini_resume', row.get('summary', '')), style={
                    'margin': '0 0 12px 0',
                    'font-size': '14px',
                    'color': config.COLORS['text'],
                    'line-height': '1.6'
                }),

                # Lien vers l'article complet
                html.A("Lire l'article complet",
                       href=row.get('link', '#'),
                       target="_blank",
                       style={
                           'color': config.COLORS['secondary'],
                           'font-size': '13px',
                           'text-decoration': 'none',
                           'font-weight': '500',
                           'border': f'1px solid {config.COLORS["secondary"]}',
                           'padding': '6px 12px',
                           'border-radius': '6px',
                           'display': 'inline-block',
                           'transition': 'all 0.2s'
                       }) if pd.notna(row.get('link')) else html.Span(),

                html.Br() if pd.notna(row.get('link')) else html.Span(),
                html.Br() if pd.notna(row.get('link')) else html.Span(),

                # Date de publication
                html.P(f" Publié le {row['published'].strftime('%d/%m/%Y')}", style={
                    'margin': '12px 0 0 0',
                    'font-size': '12px',
                    'color': config.COLORS['text_light'],
                    'font-style': 'italic'
                })
            ], style={
                'background': config.COLORS['card_bg'],
                'padding': '24px',
                'border-radius': '12px',
                'box-shadow': '0 4px 12px rgba(59, 130, 246, 0.08)',
                'margin-bottom': '20px',
                'border-left': f'5px solid {sentiment_color}',
                'border': f'1px solid {config.COLORS["border"]}',
                'transition': 'transform 0.2s ease, box-shadow 0.2s ease'
            })
        )
    return items


def create_stock_news_items_with_favorites(df):
    """Create stock news items with favorite functionality (for news page)"""
    if df is None or df.empty:
        return [
            html.Div([
                html.P("Aucune actualité disponible pour le moment.",
                       style={
                           'text-align': 'center',
                           'color': config.COLORS['text_light'],
                           'font-size': '16px',
                           'margin': '40px 0'
                       })
            ])
        ]

    items = []

    for i, (idx, row) in enumerate(df.iterrows()):
        sentiment_color = {
            'Haussier': config.COLORS['success'],
            'Baissier': config.COLORS['danger'],
            'Neutre': config.COLORS['neutral']
        }.get(row['sentiment'], config.COLORS['neutral'])

        # Check if this article is favorited (using stock favorites)
        favorited = stock_service.is_stock_favorited(row['title'], row['published'].strftime('%Y-%m-%d %H:%M:%S'))

        # Create unique identifier using title + published date
        unique_id = f"{row['title']}_{row['published'].strftime('%Y-%m-%d %H:%M:%S').replace('-', '').replace(':', '').replace(' ', '_')}"

        items.append(
            html.Div([
                # En-tête avec badges stock et sentiment + bouton favori
                html.Div([
                    html.Div([
                        html.Span(row['stock'], style={
                            'background': config.COLORS['primary'],
                            'color': 'white',
                            'padding': '6px 12px',
                            'border-radius': '15px',
                            'font-size': '12px',
                            'font-weight': '600',
                            'display': 'inline-block'
                        }),
                        html.Span(row['sentiment'], style={
                            'background': sentiment_color,
                            'color': 'white',
                            'padding': '6px 12px',
                            'border-radius': '15px',
                            'font-size': '12px',
                            'margin-left': '10px',
                            'font-weight': '500',
                            'display': 'inline-block'
                        })
                    ], style={'display': 'inline-block'}),

                    # Favorite button
                    html.Button(
                        '❤️' if favorited else '🤍',
                        id={'type': 'stock-favorite-btn', 'index': unique_id},
                        style={
                            'background': 'none',
                            'border': 'none',
                            'fontSize': '18px',
                            'cursor': 'pointer',
                            'float': 'right',
                            'padding': '5px 10px',
                            'borderRadius': '50%',
                            'transition': 'transform 0.2s ease'
                        },
                        title='Ajouter aux favoris' if not favorited else 'Retirer des favoris'
                    )
                ], style={'margin-bottom': '12px', 'display': 'flex', 'justify-content': 'space-between',
                          'align-items': 'center'}),

                # Store article data as hidden div
                html.Div(
                    id={'type': 'stock-article-data', 'index': unique_id},
                    children=str({
                        'stock': row['stock'],
                        'source': row.get('source', ''),
                        'title': row['title'],
                        'mini_resume': row.get('mini_resume', row.get('summary', '')),
                        'sentiment': row['sentiment'],
                        'published': row['published'].strftime('%Y-%m-%d %H:%M:%S'),
                        'link': row.get('link', '')
                    }),
                    style={'display': 'none'}
                ),

                # Titre de l'article
                html.H4(row['title'], style={
                    'margin': '0 0 10px 0',
                    'font-size': '16px',
                    'color': config.COLORS['primary'],
                    'line-height': '1.4',
                    'font-weight': '600'
                }),

                # Source
                html.P(f"Source: {row.get('source', 'N/A')}", style={
                    'margin': '0 0 10px 0',
                    'font-size': '13px',
                    'color': config.COLORS['neutral'],
                    'font-style': 'italic'
                }),

                # Résumé de l'article
                html.P(row.get('mini_resume', row.get('summary', '')), style={
                    'margin': '0 0 12px 0',
                    'font-size': '14px',
                    'color': config.COLORS['text'],
                    'line-height': '1.6'
                }),

                # Lien vers l'article complet
                html.A("Lire l'article complet",
                       href=row.get('link', '#'),
                       target="_blank",
                       style={
                           'color': config.COLORS['secondary'],
                           'font-size': '13px',
                           'text-decoration': 'none',
                           'font-weight': '500',
                           'border': f'1px solid {config.COLORS["secondary"]}',
                           'padding': '6px 12px',
                           'border-radius': '6px',
                           'display': 'inline-block',
                           'transition': 'all 0.2s'
                       }) if pd.notna(row.get('link')) else html.Span(),

                html.Br() if pd.notna(row.get('link')) else html.Span(),

                # Date de publication
                html.P(row['published'].strftime('%d/%m/%Y %H:%M'), style={
                    'margin': '8px 0 0 0',
                    'font-size': '12px',
                    'color': config.COLORS['neutral']
                })
            ], style={
                'background': 'white',
                'padding': '20px',
                'border-radius': '10px',
                'box-shadow': '0 2px 8px rgba(0,0,0,0.06)',
                'margin-bottom': '15px',
                'border-left': f'4px solid {sentiment_color}',
                'border': f'1px solid {config.COLORS["border"]}',
                'transition': 'transform 0.2s ease'
            })
        )
    return items

# pages/news.py

from dash import dcc, html
from services.stock_service import get_analyzed_stocks_list
from styles.styles import COLORS


def layout():
    return html.Div([
        # Header Section
        html.Div([
            html.H1('Analyse des Actualités Boursières Marocaines',
                    style={
                        'textAlign': 'center',
                        'color': COLORS['secondary'],
                        'marginBottom': '40px',
                        'fontSize': '2.5rem',
                        'fontWeight': '600',
                        'fontFamily': 'Inter'
                    })
        ]),

        # News Timeline Section - Top Priority
        html.Div([
            html.H2('Actualités Récentes Relatives aux Actions',
                    style={
                        'margin': '0 0 20px 0',
                        'color': COLORS['primary'],
                        'font-weight': '600',
                        'font-size': '24px',
                        'border-bottom': f'2px solid {COLORS["accent"]}',
                        'padding-bottom': '10px'
                    }),

            # Stock filter dropdown
            dcc.Dropdown(
                id='news-stock-filter',
                options=[],
                value='all',
                placeholder="Sélectionner une action...",
                clearable=False,  # Prevent clearing the selection
                style={
                    'width': '100%',
                    'margin-bottom': '20px',
                    'font-size': '14px'
                }
            ),

            # News timeline container
            html.Div(id='news-timeline-page', style={
                'height': '500px',
                'overflow-y': 'auto',
                'padding-right': '10px'
            })
        ], style={
            'background': 'white',
            'padding': '25px',
            'border-radius': '12px',
            'box-shadow': '0 4px 12px rgba(0,0,0,0.08)',
            'border': f'1px solid {COLORS["border"]}',
            'margin-bottom': '30px'
        }),

        # Second row - Sentiment Overview and Analyzed Stocks
        html.Div([
            # Sentiment Overview
            html.Div([
                html.Div([
                    html.H3("Aperçu du Sentiment",
                            style={
                                'margin': '0 0 20px 0',
                                'color': COLORS['primary'],
                                'font-weight': '600',
                                'font-size': '18px'
                            }),
                    html.Div(id='news-sentiment-cards', style={
                        'display': 'flex',
                        'flex-direction': 'column',
                        'gap': '12px'
                    })
                ], style={
                    'background': 'white',
                    'padding': '25px',
                    'border-radius': '12px',
                    'box-shadow': '0 4px 12px rgba(0,0,0,0.08)',
                    'border': f'1px solid {COLORS["border"]}',
                    'height': '90%'
                })
            ], style={'width': '30%'}),

            # Analyzed Stocks
            html.Div([
                html.Div([
                    html.H3("Actions Analysées",
                            style={
                                'margin': '0 0 20px 0',
                                'color': COLORS['primary'],
                                'font-weight': '600',
                                'font-size': '18px'
                            }),
                    html.Div(id='analyzed-stocks-list')
                ], style={
                    'background': 'white',
                    'padding': '25px',
                    'border-radius': '12px',
                    'box-shadow': '0 4px 12px rgba(0,0,0,0.08)',
                    'border': f'1px solid {COLORS["border"]}',
                    'height': '90%'
                })
            ], style={'width': '40%'}),

            # Risk Indicators
            html.Div([
                html.Div([
                    html.H3("Indicateurs de Risque",
                            style={
                                'margin': '0 0 20px 0',
                                'color': COLORS['primary'],
                                'font-weight': '600',
                                'font-size': '18px'
                            }),
                    html.Div(id='news-risk-indicators')
                ], style={
                    'background': 'white',
                    'padding': '25px',
                    'border-radius': '12px',
                    'box-shadow': '0 4px 12px rgba(0,0,0,0.08)',
                    'border': f'1px solid {COLORS["border"]}',
                    'height': '90%'
                })
            ], style={'width': '28%'})
        ], style={'display': 'flex', 'gap': '2%', 'margin-bottom': '30px'}),

        # Third row - Sentiment Distribution Chart
        html.Div([
            html.Div([
                html.H3("Distribution du Sentiment par Action",
                        style={
                            'margin': '0 0 20px 0',
                            'color': COLORS['primary'],
                            'font-weight': '600',
                            'font-size': '20px'
                        }),
                dcc.Graph(id='news-sentiment-chart', style={'height': '400px'})
            ], style={
                'background': 'white',
                'padding': '25px',
                'border-radius': '12px',
                'box-shadow': '0 4px 12px rgba(0,0,0,0.08)',
                'border': f'1px solid {COLORS["border"]}'
            })
        ])
    ], style={'padding': '20px'})

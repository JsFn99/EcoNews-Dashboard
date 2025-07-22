# callbacks/stock_callbacks.py

import pandas as pd
import plotly.graph_objects as go
from dash import ALL, Input, Output, State, callback_context, html
from services.stock_service import stock_service
from components.news_components import create_stock_news_items_with_favorites
from config.settings import Config

config = Config()

def register_callbacks(app):
    """Register stock-related callbacks"""

    # Callback to populate stock filter dropdown and set default value
    @app.callback(
        [Output('news-stock-filter', 'options'),
         Output('news-stock-filter', 'value')],
        Input('news-stock-filter', 'id')
    )
    def populate_stock_filter(_):
        stocks = stock_service.get_analyzed_stocks_list()
        options = [{'label': 'Toutes les Actions', 'value': 'all'}]
        options.extend([{'label': stock, 'value': stock} for stock in stocks])

        # Return both options and the default value
        return options, 'all'

    # Update the news timeline callback to use the correct function
    @app.callback(
        Output('news-timeline-page', 'children'),
        Input('news-stock-filter', 'value')
    )
    def update_news_timeline(selected_stock):
        # Handle case when selected_stock is None (initial load)
        if selected_stock is None:
            selected_stock = 'all'

        data = stock_service.get_articles_data(selected_stock)

        if data.empty:
            return [html.Div([
                html.P("Aucune actualité disponible pour cette sélection.",
                       style={
                           'text-align': 'center',
                           'color': config.COLORS['text_light'],
                           'font-size': '14px',
                           'margin': '40px 0'
                       })
            ])]

        # Sort by published date and get recent articles
        data = data.sort_values('published', ascending=False).head(20)
        return create_stock_news_items_with_favorites(data)

    # Callback for updating sentiment cards
    @app.callback(
        Output('news-sentiment-cards', 'children'),
        Input('news-stock-filter', 'value')
    )
    def update_sentiment_cards(selected_stock):
        # Handle case when selected_stock is None (initial load)
        if selected_stock is None:
            selected_stock = 'all'

        sentiment_averages = stock_service.get_sentiment_averages(selected_stock)

        cards = []
        sentiments = ['Haussier', 'Neutre', 'Baissier']
        colors = [config.COLORS['success'], config.COLORS['neutral'], config.COLORS['danger']]
        icons = ['↗', '→', '↘']

        for i, sentiment in enumerate(sentiments):
            avg_pct = sentiment_averages.get(sentiment, 0)
            cards.append(
                html.Div([
                    html.Div([
                        html.Div(icons[i], style={
                            'font-size': '28px',
                            'color': colors[i],
                            'font-weight': 'bold'
                        }),
                        html.Div([
                            html.H4(f"{avg_pct:.1f}%", style={
                                'margin': '0',
                                'color': colors[i],
                                'font-size': '22px',
                                'font-weight': '700'
                            }),
                            html.P(sentiment, style={
                                'margin': '2px 0 0 0',
                                'font-size': '13px',
                                'color': config.COLORS['text'],
                                'font-weight': '500'
                            })
                        ])
                    ], style={
                        'display': 'flex',
                        'align-items': 'center',
                        'gap': '15px'
                    })
                ], style={
                    'background': 'white',
                    'padding': '18px',
                    'border-radius': '10px',
                    'box-shadow': '0 2px 8px rgba(0,0,0,0.06)',
                    'border-left': f'4px solid {colors[i]}',
                    'border': f'1px solid {config.COLORS["border"]}'
                })
            )
        return cards

    # Callback for analyzed stocks list
    @app.callback(
        Output('analyzed-stocks-list', 'children'),
        Input('news-stock-filter', 'id')
    )
    def update_analyzed_stocks(_):
        stocks = stock_service.get_analyzed_stocks_list()
        return html.Div([
            html.Span(stock, style={
                'background': config.COLORS['accent'],
                'color': 'white',
                'padding': '8px 15px',
                'border-radius': '25px',
                'font-size': '14px',
                'margin': '6px',
                'display': 'inline-block',
                'font-weight': '400'
            }) for stock in stocks
        ], style={'line-height': '2'})

    # Callback for risk indicators
    @app.callback(
        Output('news-risk-indicators', 'children'),
        Input('news-stock-filter', 'value')
    )
    def update_risk_indicators(selected_stock):
        # Handle case when selected_stock is None (initial load)
        if selected_stock is None:
            selected_stock = 'all'

        risk_metrics = stock_service.calculate_risk_metrics(selected_stock)

        cards = []

        # Main indicators
        main_indicators = [
            {
                'title': 'Volatilité Sentiment Moy.',
                'value': f"{risk_metrics['avg_volatility']:.2f}",
                'color': config.COLORS['warning'] if risk_metrics['avg_volatility'] > 0.5 else config.COLORS['success']
            },
            {
                'title': 'Indice Polarisation Moy.',
                'value': f"{risk_metrics['avg_polarization']:.2f}",
                'color': config.COLORS['danger'] if risk_metrics['avg_polarization'] > 0.7 else config.COLORS['success']
            }
        ]

        for indicator in main_indicators:
            cards.append(
                html.Div([
                    html.H4(indicator['value'], style={
                        'margin': '0 0 5px 0',
                        'color': indicator['color'],
                        'font-size': '24px',
                        'font-weight': '700'
                    }),
                    html.P(indicator['title'], style={
                        'margin': '0',
                        'font-size': '11px',
                        'color': config.COLORS['text'],
                        'font-weight': '500'
                    })
                ], style={
                    'background': 'white',
                    'padding': '15px',
                    'border-radius': '8px',
                    'box-shadow': '0 2px 8px rgba(0,0,0,0.06)',
                    'margin-bottom': '12px',
                    'text-align': 'center',
                    'border': f'1px solid {config.COLORS["border"]}',
                    'border-left': f'4px solid {indicator["color"]}'
                })
            )

        # High risk stocks
        high_risk_stocks = risk_metrics['high_risk_stocks']
        if high_risk_stocks:
            high_risk_list = html.Div([
                html.H5(f"Actions à Haut Risque ({len(high_risk_stocks)})", style={
                    'margin': '0 0 10px 0',
                    'color': config.COLORS['danger'],
                    'font-size': '13px',
                    'font-weight': '600'
                }),
                html.Div([
                    html.Span(stock, style={
                        'background': config.COLORS['danger'],
                        'color': 'white',
                        'padding': '4px 8px',
                        'border-radius': '15px',
                        'font-size': '10px',
                        'margin': '3px',
                        'display': 'inline-block',
                        'font-weight': '500'
                    }) for stock in high_risk_stocks[:8]
                ])
            ], style={
                'background': 'white',
                'padding': '15px',
                'border-radius': '8px',
                'box-shadow': '0 2px 8px rgba(0,0,0,0.06)',
                'border': f'1px solid {config.COLORS["border"]}',
                'border-left': f'4px solid {config.COLORS["danger"]}'
            })
            cards.append(high_risk_list)

        return cards

    # Callback for sentiment chart
    @app.callback(
        Output('news-sentiment-chart', 'figure'),
        Input('news-stock-filter', 'value')
    )
    def update_sentiment_chart(selected_stock):
        # Handle case when selected_stock is None (initial load)
        if selected_stock is None:
            selected_stock = 'all'

        data = stock_service.get_sentiment_data(selected_stock)

        if data.empty:
            return go.Figure()

        fig = go.Figure()
        sentiments = ['Haussier', 'Neutre', 'Baissier']
        colors = [config.COLORS['success'], config.COLORS['neutral'], config.COLORS['danger']]

        for i, sentiment in enumerate(sentiments):
            fig.add_trace(go.Bar(
                name=sentiment,
                x=data['stock'],
                y=data[sentiment],
                marker_color=colors[i],
                marker_line=dict(width=0),
                text=data[sentiment].round(1).astype(str) + '%',
                textposition='inside',
                textfont=dict(size=11, color='white', family='Inter'),
                hovertemplate=f'<b>{sentiment}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>'
            ))

        fig.update_layout(
            barmode='stack',
            xaxis_title="Actions",
            yaxis_title="Distribution du Sentiment (%)",
            margin=dict(l=60, r=40, t=40, b=80),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Inter', size=12, color=config.COLORS['text']),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12)
            ),
            xaxis=dict(
                tickangle=45,
                tickfont=dict(size=11, color=config.COLORS['text']),
                gridcolor='rgba(0,0,0,0)',
                linecolor=config.COLORS['border']
            ),
            yaxis=dict(
                gridcolor='rgba(0,0,0,0.05)',
                linecolor=config.COLORS['border'],
                tickfont=dict(color=config.COLORS['text'])
            )
        )

        return fig

    # Callback for stock favorite button functionality
    @app.callback(
        Output({'type': 'stock-favorite-btn', 'index': ALL}, 'children'),
        Input({'type': 'stock-favorite-btn', 'index': ALL}, 'n_clicks'),
        State({'type': 'stock-article-data', 'index': ALL}, 'children'),
        prevent_initial_call=True
    )
    def handle_stock_favorite_click(n_clicks, article_data_list):
        if not callback_context.triggered:
            return ['🤍'] * len(n_clicks)

        # Find which button was clicked
        button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        clicked_unique_id = eval(button_id)['index']

        # Find the corresponding article data
        clicked_article_data = None
        for data_str in article_data_list:
            try:
                data = eval(data_str)
                # Match by unique_id
                if f"{data['title']}_{data['published'].replace('-', '').replace(':', '').replace(' ', '_')}" == clicked_unique_id:
                    clicked_article_data = data
                    break
            except:
                continue

        if clicked_article_data is None:
            return ['🤍'] * len(n_clicks)

        # Check current favorite status
        favorited = stock_service.is_stock_favorited(clicked_article_data['title'], clicked_article_data['published'])

        if favorited:
            # Remove from favorites
            stock_service.remove_from_stock_favorites(clicked_article_data['title'], clicked_article_data['published'])
        else:
            # Add to favorites
            stock_service.save_to_stock_favorites(clicked_article_data)

        # Return updated button states for all buttons
        result = []
        for data_str in article_data_list:
            try:
                data = eval(data_str)
                result.append('❤️' if stock_service.is_stock_favorited(data['title'], data['published']) else '🤍')
            except:
                result.append('🤍')

        return result

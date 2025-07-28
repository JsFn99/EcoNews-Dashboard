# callbacks/eco_callbacks.py

import pandas as pd
from dash import ALL, Input, Output, State, callback, callback_context
from services.favorites_service import FavoritesService
from components.news_components import create_news_items_with_favorites
from services.eco_service import EcoService
from datetime import timedelta

favorites_service = FavoritesService()
eco_service = EcoService()
news_df = eco_service.load_news_data()

@callback(
    Output({'type': 'favorite-btn', 'index': ALL}, 'children'),
    Input({'type': 'favorite-btn', 'index': ALL}, 'n_clicks'),
    State({'type': 'article-data', 'index': ALL}, 'children'),
    prevent_initial_call=True
)
def handle_favorite_click(n_clicks, article_data_list):
    if not callback_context.triggered:
        return ['🤍'] * len(n_clicks)

    button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    clicked_unique_id = eval(button_id)['index']

    clicked_article_data = None
    for data_str in article_data_list:
        data = eval(data_str)
        if f"{data['title']}_{data['published'].replace('-', '').replace(':', '').replace(' ', '_')}" == clicked_unique_id:
            clicked_article_data = data
            break

    if clicked_article_data is None:
        return ['🤍'] * len(n_clicks)

    favorited = favorites_service.is_favorited(clicked_article_data['title'], clicked_article_data['published'])

    if favorited:
        favorites_service.remove_from_favorites(clicked_article_data['title'], clicked_article_data['published'])
    else:
        favorites_service.save_to_favorites(clicked_article_data)

    result = []
    for data_str in article_data_list:
        data = eval(data_str)
        result.append('❤️' if favorites_service.is_favorited(data['title'], data['published']) else '🤍')

    return result

@callback(
    Output('custom-date-container', 'style'),
    Input('date-period-dropdown', 'value')
)
def toggle_custom_date_inputs(period_value):
    if period_value == 'custom':
        return {'display': 'block', 'marginTop': '10px'}
    else:
        return {'display': 'none'}

@callback(
    [
        Output('news-container', 'children'),
        Output('sentiment-chart', 'figure'),
        Output('theme-chart', 'figure')
    ],
    [
        Input('sentiment-filter-dropdown', 'value'),
        Input('theme-filter-dropdown', 'value'),
        Input('search-input', 'value'),
        Input('date-period-dropdown', 'value'),
        Input('start-date-picker', 'date'),
        Input('end-date-picker', 'date')
    ]
)
def update_news_display(sentiment_filter, theme_filter, search_query, date_period, start_date, end_date):
    global news_df
    if news_df.empty:
        return [], eco_service.create_sentiment_chart(news_df), eco_service.create_theme_chart(news_df)

    filtered_df = news_df.copy()

    if date_period and date_period != 'all':
        start_range, end_range = eco_service.calculate_date_range(date_period, start_date, end_date)
        if start_range and end_range:
            start_datetime = pd.to_datetime(start_range)
            end_datetime = pd.to_datetime(end_range) + timedelta(hours=23, minutes=59, seconds=59)
            filtered_df = filtered_df[(filtered_df['published'] >= start_datetime) & (filtered_df['published'] <= end_datetime)]

    if sentiment_filter and sentiment_filter != 'Tous':
        filtered_df = filtered_df[filtered_df['sentiment'] == sentiment_filter]

    if theme_filter and theme_filter != 'Tous':
        filtered_df = filtered_df[filtered_df['theme'] == theme_filter]

    if search_query and search_query.strip():
        search_term = search_query.strip().lower()
        mask = (
            filtered_df['title'].str.lower().str.contains(search_term, na=False) |
            filtered_df['mini_resume'].str.lower().str.contains(search_term, na=False)
        )
        filtered_df = filtered_df[mask]

    filtered_df = filtered_df.sort_values('published', ascending=False)

    sentiment_fig = eco_service.create_sentiment_chart(filtered_df)
    theme_fig = eco_service.create_theme_chart(filtered_df)
    news_items = create_news_items_with_favorites(filtered_df)

    return news_items, sentiment_fig, theme_fig

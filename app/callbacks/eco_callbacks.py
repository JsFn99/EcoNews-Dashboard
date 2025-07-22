# callbacks/eco_callbacks.py

import pandas as pd
from dash import ALL, Input, Output, State, callback, callback_context
from services.favorites_service import FavoritesService
from components.news_components import create_news_items_with_favorites
from services.eco_service import EcoService

favorites_service = FavoritesService()
eco_service = EcoService()


@callback(
    Output({'type': 'favorite-btn', 'index': ALL}, 'children'),
    Input({'type': 'favorite-btn', 'index': ALL}, 'n_clicks'),
    State({'type': 'article-data', 'index': ALL}, 'children'),
    prevent_initial_call=True
)
def handle_favorite_click(n_clicks, article_data_list):
    """Handle favorite button clicks"""
    if not callback_context.triggered:
        return ['🤍'] * len(n_clicks)

    # Find which button was clicked
    button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    clicked_unique_id = eval(button_id)['index']

    # Find the corresponding article data
    clicked_article_data = None

    for i, data_str in enumerate(article_data_list):
        data = eval(data_str)
        # Use the SAME logic as the original working code
        if f"{data['title']}_{data['published'].replace('-', '').replace(':', '').replace(' ', '_')}" == clicked_unique_id:
            clicked_article_data = data
            break

    if clicked_article_data is None:
        return ['🤍'] * len(n_clicks)

    # Check current favorite status
    favorited = favorites_service.is_favorited(clicked_article_data['title'], clicked_article_data['published'])

    if favorited:
        # Remove from favorites
        favorites_service.remove_from_favorites(clicked_article_data['title'], clicked_article_data['published'])
    else:
        # Add to favorites
        favorites_service.save_to_favorites(clicked_article_data)

    # Return updated button states for all buttons
    result = []
    for data_str in article_data_list:
        data = eval(data_str)
        result.append('❤️' if favorites_service.is_favorited(data['title'], data['published']) else '🤍')

    return result


@callback(
    Output('news-container', 'children'),
    [Input('sentiment-filter-dropdown', 'value'),
     Input('theme-filter-dropdown', 'value'),
     Input('search-input', 'value')]
)
def update_news_display(sentiment_filter, theme_filter, search_query):
    """Update news display based on filters"""
    news_df = eco_service.load_news_data()

    if news_df is None or news_df.empty:
        return create_news_items_with_favorites(news_df)

    # Filter data according to selected criteria
    filtered_df = news_df.copy()

    # Filter by sentiment if selected
    if sentiment_filter and sentiment_filter != 'Tous':
        filtered_df = filtered_df[filtered_df['sentiment'] == sentiment_filter]

    # Filter by theme if selected
    if theme_filter and theme_filter != 'Tous':
        filtered_df = filtered_df[filtered_df['theme'] == theme_filter]

    # Filter by search if query is provided
    if search_query and search_query.strip():
        search_term = search_query.strip().lower()
        # Search in both title and mini_resume
        mask = (
                filtered_df['title'].str.lower().str.contains(search_term, na=False) |
                filtered_df['mini_resume'].str.lower().str.contains(search_term, na=False)
        )
        filtered_df = filtered_df[mask]

    # Sort by date (most recent first)
    filtered_df = filtered_df.sort_values('published', ascending=False)

    # Recreate news items with favorites for filtered data
    return create_news_items_with_favorites(filtered_df)

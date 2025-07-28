# services/favorites_service.py

import os
import pandas as pd

class FavoritesService:
    def __init__(self, favorites_file='my_eco_news.csv'):
        self.favorites_file = favorites_file
        
    def load_favorites(self):
        """Load favorites from CSV file"""
        if os.path.exists(self.favorites_file):
            try:
                return pd.read_csv(self.favorites_file)
            except pd.errors.EmptyDataError:
                return pd.DataFrame(columns=['source', 'theme', 'title', 'summary', 'mini_resume', 'sentiment', 'published', 'link'])
        else:
            return pd.DataFrame(columns=['source', 'theme', 'title', 'summary', 'mini_resume', 'sentiment', 'published', 'link'])

    def save_to_favorites(self, article_data):
        """Save article to favorites"""
        favorites_df = self.load_favorites()
        
        # Check if article already exists
        if not ((favorites_df['title'] == article_data['title']) & 
                (favorites_df['published'] == article_data['published'])).any():
            # Add new favorite
            new_row = pd.DataFrame([article_data])
            favorites_df = pd.concat([favorites_df, new_row], ignore_index=True)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.favorites_file), exist_ok=True)
            favorites_df.to_csv(self.favorites_file, index=False)

    def remove_from_favorites(self, title, published):
        """Remove article from favorites"""
        favorites_df = self.load_favorites()
        favorites_df = favorites_df[~((favorites_df['title'] == title) & 
                                    (favorites_df['published'] == published))]
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.favorites_file), exist_ok=True)
        favorites_df.to_csv(self.favorites_file, index=False)

    def is_favorited(self, title, published):
        """Check if article is favorited"""
        favorites_df = self.load_favorites()
        return ((favorites_df['title'] == title) & 
                (favorites_df['published'] == published)).any()
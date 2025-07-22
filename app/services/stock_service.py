# services/stock_service.py

import os
import pandas as pd
from config.settings import Config
from styles.styles import COLORS

class StockService:
    def __init__(self):
        self.config = Config()
        self.articles_df = None
        self.sentiment_df = None
        self.stock_favorites_file = '/Users/mac/Sentiment Analysis Press/app/my_stock_news.csv'
        self.load_data()
    
    def load_data(self):
        """Load stock data from CSV files"""
        try:
            self.articles_df = pd.read_csv(self.config.config['paths']['stock_sentiment_news'])
            self.sentiment_df = pd.read_csv(self.config.config['paths']['stock_sentiment_kpi'])
            
            # Data preprocessing
            self.articles_df['published'] = pd.to_datetime(self.articles_df['published'])
        except Exception as e:
            print(f"Error loading stock data: {e}")
            self.articles_df = pd.DataFrame()
            self.sentiment_df = pd.DataFrame()
    
    def get_analyzed_stocks_list(self):
        """Get list of analyzed stocks"""
        if self.sentiment_df is not None and not self.sentiment_df.empty:
            return self.sentiment_df['stock'].unique().tolist()
        return []
    
    def get_articles_data(self, stock_filter='all'):
        """Get filtered articles data"""
        if self.articles_df is None or self.articles_df.empty:
            return pd.DataFrame()
        
        if stock_filter == 'all':
            return self.articles_df
        else:
            return self.articles_df[self.articles_df['stock'] == stock_filter]
    
    def get_sentiment_data(self, stock_filter='all'):
        """Get filtered sentiment data"""
        if self.sentiment_df is None or self.sentiment_df.empty:
            return pd.DataFrame()
        
        if stock_filter == 'all':
            return self.sentiment_df
        else:
            return self.sentiment_df[self.sentiment_df['stock'] == stock_filter]
    
    def load_stock_favorites(self):
        """Load stock favorites from CSV"""
        if os.path.exists(self.stock_favorites_file):
            try:
                return pd.read_csv(self.stock_favorites_file)
            except:
                return pd.DataFrame(columns=['stock', 'source', 'title', 'mini_resume', 'sentiment', 'published', 'link'])
        else:
            return pd.DataFrame(columns=['stock', 'source', 'title', 'mini_resume', 'sentiment', 'published', 'link'])
    
    def save_to_stock_favorites(self, article_data):
        """Save article to stock favorites"""
        favorites_df = self.load_stock_favorites()
        
        # Check if article already exists
        if not ((favorites_df['title'] == article_data['title']) & 
                (favorites_df['published'] == article_data['published'])).any():
            # Add new favorite
            new_row = pd.DataFrame([article_data])
            favorites_df = pd.concat([favorites_df, new_row], ignore_index=True)
            
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.stock_favorites_file), exist_ok=True)
            favorites_df.to_csv(self.stock_favorites_file, index=False)
    
    def remove_from_stock_favorites(self, title, published):
        """Remove article from stock favorites"""
        favorites_df = self.load_stock_favorites()
        favorites_df = favorites_df[~((favorites_df['title'] == title) & 
                                    (favorites_df['published'] == published))]
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.stock_favorites_file), exist_ok=True)
        favorites_df.to_csv(self.stock_favorites_file, index=False)
    
    def is_stock_favorited(self, title, published):
        """Check if article is favorited"""
        favorites_df = self.load_stock_favorites()
        return ((favorites_df['title'] == title) & 
                (favorites_df['published'] == published)).any()
    
    def calculate_risk_metrics(self, stock_filter='all'):
        """Calculate risk metrics for given stock filter"""
        data = self.get_sentiment_data(stock_filter)
        
        if data.empty:
            return {
                'avg_volatility': 0,
                'avg_polarization': 0,
                'high_risk_stocks': []
            }
        
        avg_volatility = data['sentiment_volatility'].mean()
        avg_polarization = data['polarization_index'].mean()
        high_risk_stocks_data = data[data['Baissier'] >= 50]
        
        return {
            'avg_volatility': avg_volatility,
            'avg_polarization': avg_polarization,
            'high_risk_stocks': high_risk_stocks_data['stock'].tolist()
        }
    
    def get_sentiment_averages(self, stock_filter='all'):
        """Get sentiment averages for given stock filter"""
        data = self.get_sentiment_data(stock_filter)
        
        if data.empty:
            return {'Haussier': 0, 'Neutre': 0, 'Baissier': 0}
        
        return {
            'Haussier': data['Haussier'].mean(),
            'Neutre': data['Neutre'].mean(),
            'Baissier': data['Baissier'].mean()
        }

# Global instance
stock_service = StockService()

# Convenience functions for backward compatibility
def get_analyzed_stocks_list():
    return stock_service.get_analyzed_stocks_list()

def load_stock_favorites():
    return stock_service.load_stock_favorites()

def save_to_stock_favorites(article_data):
    return stock_service.save_to_stock_favorites(article_data)

def remove_from_stock_favorites(title, published):
    return stock_service.remove_from_stock_favorites(title, published)

def is_stock_favorited(title, published):
    return stock_service.is_stock_favorited(title, published)
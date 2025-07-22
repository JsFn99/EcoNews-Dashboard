import yaml
import os

class Config:
    def __init__(self, config_file='config/config.yaml'):
        self.config_file = config_file
        self.config = self._load_config()
        self.COLORS = self._setup_colors()
        self.enhanced_card_style = self._setup_card_style()
        
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _setup_colors(self):
        """Setup color scheme"""
        return {
            'primary': '#1e3a8a',
            'primary_blue': '#2c5aa0',
            'secondary': '#3b82f6',
            'tertiary': '#60a5fa',
            'light_blue': '#dbeafe',
            'success': '#10b981',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'neutral': '#6b7280',
            'text': '#1f2937',
            'text_light': '#6b7280',
            'background': '#f8fafc',
            'card_bg': '#ffffff',
            'border': '#e2e8f0',
            'accent': '#8b5cf6'
        }
    
    def _setup_card_style(self):
        """Setup enhanced card style"""
        return {
            'background': self.COLORS['card_bg'],
            'padding': '30px',
            'border-radius': '16px',
            'box-shadow': '0 8px 32px rgba(59, 130, 246, 0.12)',
            'border': f'1px solid {self.COLORS["border"]}',
            'margin-bottom': '25px',
            'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
            'position': 'relative'
        }
    
    def get_database_path(self):
        """Get database file path"""
        return self.config.get('paths', {}).get('database', '/Users/mac/Sentiment Analysis Press/app/economic_news.db')
    
    def get_news_csv_path(self):
        """Get news CSV file path"""
        return self.config.get('paths', {}).get('economic_news', '/Users/mac/Sentiment Analysis Press/app/economic_news.csv')
    
    def get_favorites_path(self):
        """Get favorites CSV file path"""
        return self.config.get('paths', {}).get('favorites', '/Users/mac/Sentiment Analysis Press/app/my_eco_news.csv')
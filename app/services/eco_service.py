# services/eco_service.py

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from config.settings import Config

class EcoService:
    def __init__(self):
        self.config = Config()
        
    def load_news_data(self):
        """Load economic news data"""
        try:
            # Load economic news data
            news_df = pd.read_csv(self.config.config['paths']['economic_news'])
            
            # Process news data
            news_df['published'] = pd.to_datetime(news_df['published'])
            
            # Filter to last week's articles
            current_date = datetime.now()
            start_of_week = current_date - timedelta(days=7)
            news_df = news_df[news_df['published'] >= start_of_week]
            news_df = news_df.sort_values('published', ascending=False)
            
            return news_df
            
        except Exception as e:
            print(f"Error loading news data: {e}")
            return None
    
    def create_sentiment_chart(self, news_df):
        """Create sentiment distribution chart"""
        if news_df is None or news_df.empty:
            return self._create_error_figure("Données de Sentiment - Échec du Chargement")
        
        sentiment_counts = news_df['sentiment'].value_counts()
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title='Répartition des Sentiments dans les Actualités',
            color_discrete_map={
                'Positif': self.config.COLORS['success'],
                'Négatif': self.config.COLORS['danger'],
                'Neutre': self.config.COLORS['neutral']
            }
        )
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=self.config.COLORS['text'], family="'Segoe UI', sans-serif"),
            title_font=dict(size=18, color=self.config.COLORS['primary'])
        )
        return fig
    
    def create_theme_chart(self, news_df):
        """Create theme distribution chart"""
        if news_df is None or news_df.empty:
            return self._create_error_figure("Données de Thème - Échec du Chargement")
        
        theme_counts = news_df['theme'].value_counts().head(10)
        fig = px.bar(
            x=theme_counts.values,
            y=theme_counts.index,
            orientation='h',
            title='Top 10 des Thèmes d\'Actualités',
            labels={'x': 'Nombre d\'Articles', 'y': 'Thème'},
            color=theme_counts.values,
            color_continuous_scale=[self.config.COLORS['light_blue'], self.config.COLORS['primary']]
        )
        fig.update_layout(
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=self.config.COLORS['text'], family="'Segoe UI', sans-serif"),
            title_font=dict(size=18, color=self.config.COLORS['primary']),
            showlegend=False
        )
        return fig
    
    def _create_error_figure(self, title, error_msg=None):
        """Create error figure when data loading fails"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"{title}<br><br>Erreur: {error_msg if error_msg else 'Fichier non trouvé ou échec du chargement des données'}", 
            xref="paper", yref="paper", 
            x=0.5, y=0.5, 
            showarrow=False,
            font=dict(size=16, color=self.config.COLORS['danger']),
            align="center"
        )
        fig.update_layout(
            title=title,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=self.config.COLORS['text'], family="'Segoe UI', sans-serif")
        )
        return fig
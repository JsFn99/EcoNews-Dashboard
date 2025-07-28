# services/eco_service.py

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from config.settings import Config

class EcoService:
    def __init__(self):
        self.config = Config()

    def load_news_data(self):
        """Load all economic news data without date filtering."""
        try:
            news_df = pd.read_csv(self.config.config['paths']['economic_news'])
            news_df['published'] = pd.to_datetime(news_df['published'])
            news_df = news_df.sort_values('published', ascending=False)
            return news_df
        except Exception as e:
            print(f"Error loading news data: {e}")
            return pd.DataFrame() # Return empty DataFrame on error

    def create_sentiment_chart(self, news_df):
        """Create sentiment distribution chart with updated styling."""
        if news_df is None or news_df.empty:
            return self._create_error_figure("Données de Sentiment non disponibles")

        sentiment_counts = news_df['sentiment'].value_counts()
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title='Répartition des Sentiments',
            color=sentiment_counts.index,
            color_discrete_map={
                'Positif': self.config.COLORS['success'],
                'Négatif': self.config.COLORS['danger'],
                'Neutre': self.config.COLORS['neutral']
            }
        )
        fig.update_layout(
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=self.config.COLORS['text'], family="'Segoe UI', sans-serif"),
            title_font=dict(size=16, color=self.config.COLORS['primary']),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig

    def create_theme_chart(self, news_df):
        """Create theme distribution chart with updated styling."""
        if news_df is None or news_df.empty:
            return self._create_error_figure("Données de Thème non disponibles")

        theme_counts = news_df['theme'].value_counts().head(10)
        fig = px.bar(
            x=theme_counts.values,
            y=theme_counts.index,
            orientation='h',
            title='Top 10 des Thèmes',
            labels={'x': 'Articles', 'y': 'Thème'},
            color=theme_counts.values,
            color_continuous_scale=[self.config.COLORS['light_blue'], self.config.COLORS['primary']]
        )
        fig.update_layout(
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=self.config.COLORS['text'], family="'Segoe UI', sans-serif"),
            title_font=dict(size=16, color=self.config.COLORS['primary']),
            showlegend=False,
            margin=dict(l=20, r=20, t=50, b=20),
            autosize=True,
            yaxis=dict(tickmode='linear', automargin=True),
            xaxis=dict(automargin=True)
        )
        fig.update_traces(
            textposition='outside',
            texttemplate='%{x}',
            hovertemplate='<b>%{y}</b><br>Articles: %{x}<extra></extra>'
        )
        return fig

    @staticmethod
    def get_date_range_options():
        """Get predefined date range options for dropdown."""
        return [
            {'label': 'Toutes les dates', 'value': 'all'},
            {'label': "Aujourd'hui", 'value': 'today'},
            {'label': '3 derniers jours', 'value': '3days'},
            {'label': 'Cette semaine', 'value': 'week'},
            {'label': '2 dernières semaines', 'value': '2weeks'},
            {'label': 'Ce mois', 'value': 'month'},
            {'label': '3 derniers mois', 'value': '3months'},
            {'label': 'Période personnalisée', 'value': 'custom'}
        ]

    @staticmethod
    def calculate_date_range(period_value, start_date=None, end_date=None):
        """Calculate date range based on selection."""
        today = date.today()
        if period_value == 'all':
            return None, None
        elif period_value == 'today':
            return today, today
        elif period_value == '3days':
            return today - timedelta(days=3), today
        elif period_value == 'week':
            return today - timedelta(days=7), today
        elif period_value == '2weeks':
            return today - timedelta(days=14), today
        elif period_value == 'month':
            return today - timedelta(days=30), today
        elif period_value == '3months':
            return today - timedelta(days=90), today
        elif period_value == 'custom' and start_date and end_date:
            return pd.to_datetime(start_date).date(), pd.to_datetime(end_date).date()
        return None, None

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
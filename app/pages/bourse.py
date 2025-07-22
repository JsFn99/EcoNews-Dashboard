# pages/bourse.py
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yaml
from dash import Input, Output, callback, dcc, html
from plotly.subplots import make_subplots
from styles.styles import card_style

# Palette de couleurs unifiée autour du bleu
UNIFIED_COLORS = {
    'primary_blue': '#2c5aa0',
    'secondary_blue': '#4472c4',
    'light_blue': '#8fa8d3',
    'very_light_blue': '#e8f0ff',
    'accent_blue': '#1f4788',
    'success_blue': '#4a90e2',
    'warning_blue': '#6bb6ff',
    'danger_blue': '#5a7db8',
    'danger': '#ef4444',
    'text_dark': '#2c3e50',
    'text_light': '#5a6c7d',
    'background': '#fafbfc',
    'white': '#ffffff',
    'border': '#e1e8ed'
}

# Style unifié pour les cartes
UNIFIED_CARD_STYLE = {
    'backgroundColor': UNIFIED_COLORS['white'],
    'padding': '25px',
    'borderRadius': '12px',
    'boxShadow': '0 2px 8px rgba(44, 90, 160, 0.1)',
    'border': f'1px solid {UNIFIED_COLORS["border"]}',
    'marginBottom': '20px',
}

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

def load_and_prepare_data():
    """Charge et prépare les données des fichiers CSV"""
    
    # Chargement des données des actions
    try:
        stocks_df = pd.read_csv(config['paths']['stocks'])
        
        # Nettoyage des données numériques (suppression des espaces et virgules)
        numeric_columns = ['Cours de référence', 'Dernier cours', 'Quantité échangée', 
                          'Volume', 'Variation en %', '+ haut jour', '+ bas jour', 'Capitalisation', 'Nombre de transactions']
        
        for col in numeric_columns:
            if col in stocks_df.columns:
                # Suppression des espaces, remplacement des virgules par des points
                stocks_df[col] = stocks_df[col].astype(str).str.replace(' ', '').str.replace(',', '.')
                # Suppression du symbole % pour la variation
                if 'Variation' in col:
                    stocks_df[col] = stocks_df[col].str.replace('%', '')
                # Conversion en numérique
                stocks_df[col] = pd.to_numeric(stocks_df[col], errors='coerce')
        
        # Filtrage des actions avec des données valides
        stocks_df = stocks_df.dropna(subset=['Dernier cours', 'Variation en %'])
        
    except FileNotFoundError:
        # Données exemple si le fichier n'existe pas
        stocks_df = pd.DataFrame({
            'Instrument': ['ATTIJARIWAFA BANK', 'BCP', 'ITISSALAT AL-MAGHRIB', 'LAFARGEHOLCIM MAROC', 'MANAGEM'],
            'Dernier cours': [671.50, 290.00, 107.05, 1915.00, 5150.00],
            'Variation en %': [-0.68, 0.00, -0.83, 0.26, -1.51],
            'Volume': [39557358.70, 19514542.70, 11474371.00, 7409715.00, 6329439.00],
            'Capitalisation': [144467073388.50, 58960617170.00, 94107156147.00, 44870824600.00, 61103081400.00],
            'Nombre de transactions': [105, 54, 191, 42, 16]
        })
    
    # Chargement des données de dividendes
    try:
        dividends_df = pd.read_csv(config['paths']['dividends'])
        dividends_df['Montant'] = dividends_df['Montant'].astype(str).str.replace(',', '.').astype(float)
        dividends_df['Date de détachement'] = pd.to_datetime(dividends_df['Date de détachement'], format='%d/%m/%Y')
    except FileNotFoundError:
        # Données exemple
        dividends_df = pd.DataFrame({
            'Émetteur': ['ATTIJARIWAFA BANK', 'LAFARGEHOLCIM MAROC', 'WAFA ASSURANCE'],
            'Montant': [19.0, 70.0, 140.0],
            'Date de détachement': pd.to_datetime(['2025-05-27', '2025-06-13', '2025-06-17']),
            'Type Dividende': ['Ordinaire', 'Ordinaire', 'Ordinaire']
        })
    
    return stocks_df, dividends_df

def create_stock_performance_chart(stocks_df):
    """Crée un graphique de performance des actions avec couleurs unifiées"""
    perf_data = stocks_df.copy()
    perf_data = perf_data.sort_values(by='Instrument').reset_index(drop=True)
    
    fig = go.Figure()
    
    # Séparer les actions positives et négatives
    positive = perf_data[perf_data['Variation en %'] >= 0]
    negative = perf_data[perf_data['Variation en %'] < 0]
    
    # Ajouter les barres positives
    if not positive.empty:
        fig.add_trace(go.Bar(
            x=positive['Instrument'],
            y=positive['Variation en %'],
            name='Positif',
            marker_color=UNIFIED_COLORS['success_blue'],
            marker_line=dict(width=0),
            text=positive['Variation en %'].round(2).astype(str) + '%',
            textposition='outside',
            textfont=dict(size=11, color=UNIFIED_COLORS['success_blue'], family='Inter'),
            hovertemplate='<b>%{x}</b><br>Variation: %{y:.2f}%<extra></extra>'
        ))
    
    # Ajouter les barres négatives
    if not negative.empty:
        fig.add_trace(go.Bar(
            x=negative['Instrument'],
            y=negative['Variation en %'],
            name='Négatif',
            marker_color=UNIFIED_COLORS['danger'],
            marker_line=dict(width=0),
            text=negative['Variation en %'].round(2).astype(str) + '%',
            textposition='outside',
            textfont=dict(size=11, color=UNIFIED_COLORS['danger'], family='Inter'),
            hovertemplate='<b>%{x}</b><br>Variation: %{y:.2f}%<extra></extra>'
        ))
    
    fig.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis_title="Variation (%)",
        margin=dict(l=60, r=40, t=40, b=140),
        plot_bgcolor=UNIFIED_COLORS['white'],
        paper_bgcolor=UNIFIED_COLORS['white'],
        font=dict(family='Inter', size=12, color=UNIFIED_COLORS['text_dark']),
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=11, color=UNIFIED_COLORS['text_light']),
            gridcolor='rgba(0,0,0,0)',
            linecolor=UNIFIED_COLORS['border']
        ),
        yaxis=dict(
            zeroline=True,
            zerolinecolor=UNIFIED_COLORS['border'],
            zerolinewidth=2,
            gridcolor='rgba(44, 90, 160, 0.05)',
            linecolor=UNIFIED_COLORS['border'],
            tickfont=dict(color=UNIFIED_COLORS['text_light'])
        ),
        hovermode='x unified',
        height=500
    )
    
    return fig

def create_volume_chart(stocks_df):
    """Crée un graphique des volumes d'échange avec couleurs unifiées"""
    top_volume = stocks_df.nlargest(15, 'Volume')
    
    fig = px.bar(
        top_volume.sort_values('Volume', ascending=True),
        x='Volume',
        y='Instrument',
        orientation='h',
        labels={'Volume': 'Volume (MAD)', 'Instrument': 'Action'},
        color='Volume',
        color_continuous_scale=[UNIFIED_COLORS['very_light_blue'], UNIFIED_COLORS['primary_blue']]
    )
    
    fig.update_layout(
        height=450,
        showlegend=False,
        font=dict(size=11, color=UNIFIED_COLORS['text_dark']),
        plot_bgcolor=UNIFIED_COLORS['white'],
        paper_bgcolor=UNIFIED_COLORS['white'],
        margin=dict(l=150, r=40, t=20, b=40),
        xaxis=dict(gridcolor='rgba(44, 90, 160, 0.1)'),
        yaxis=dict(tickfont=dict(size=10))
    )
    
    # Format des nombres
    fig.update_traces(texttemplate='%{x:,.0f}', textposition='outside')
    
    return fig

def create_dividends_chart(dividends_df):
    """Crée un graphique des dividendes avec couleurs unifiées"""
    top_dividends = dividends_df.nlargest(10, 'Montant')
    
    fig = px.bar(
        top_dividends.sort_values('Montant', ascending=True),
        x='Montant',
        y='Émetteur',
        orientation='h',
        labels={'Montant': 'Montant du Dividende (MAD)', 'Émetteur': 'Société'},
        color='Type Dividende',
        color_discrete_map={
            'Ordinaire': UNIFIED_COLORS['secondary_blue'], 
            'Exceptionnel': UNIFIED_COLORS['warning_blue']
        }
    )
    
    fig.update_layout(
        height=350,
        font=dict(size=11, color=UNIFIED_COLORS['text_dark']),
        plot_bgcolor=UNIFIED_COLORS['white'],
        paper_bgcolor=UNIFIED_COLORS['white'],
        margin=dict(l=120, r=40, t=20, b=40),
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(color=UNIFIED_COLORS['text_dark'])
        ),
        xaxis=dict(gridcolor='rgba(44, 90, 160, 0.1)')
    )
    
    return fig

def create_market_summary_cards(stocks_df):
    """Crée des cartes de résumé du marché"""
    # Conversion sécurisée des valeurs numériques
    total_volume = pd.to_numeric(stocks_df['Volume'], errors='coerce').fillna(0).sum()
    total_transactions = pd.to_numeric(stocks_df['Nombre de transactions'], errors='coerce').fillna(0).sum()
    avg_variation = pd.to_numeric(stocks_df['Variation en %'], errors='coerce').fillna(0).mean()
    positive_stocks = len(stocks_df[pd.to_numeric(stocks_df['Variation en %'], errors='coerce') > 0])
    negative_stocks = len(stocks_df[pd.to_numeric(stocks_df['Variation en %'], errors='coerce') < 0])
    
    return {
        'total_volume': float(total_volume),
        'total_transactions': int(total_transactions),
        'avg_variation': float(avg_variation),
        'positive_stocks': int(positive_stocks),
        'negative_stocks': int(negative_stocks)
    }

def create_layout_content(stocks_df, dividends_df):
    """Crée le contenu du layout avec les données fournies"""
    
    # Création des graphiques
    stock_perf_fig = create_stock_performance_chart(stocks_df)
    volume_fig = create_volume_chart(stocks_df)
    dividends_fig = create_dividends_chart(dividends_df)
    
    # Statistiques du marché
    market_stats = create_market_summary_cards(stocks_df)
    
    return html.Div([
        # En-tête avec style amélioré
        html.Div([
            html.H1('Aperçu des Données Boursières - Bourse de Casablanca', 
                    style={
                        'textAlign': 'center', 
                        'color': UNIFIED_COLORS['primary_blue'], 
                        'marginBottom': '40px',
                        'fontSize': '2.5rem',
                        'fontWeight': '600',
                        'fontFamily': 'Inter'
                    })
        ]),
        
        # Section des indicateurs clés
        html.Div([
            html.H2('Indicateurs Clés du Marché', 
                    style={
                        'color': UNIFIED_COLORS['text_dark'], 
                        'marginBottom': '20px',
                        'fontSize': '1.5rem',
                        'fontWeight': '500'
                    }),
            
            # Cartes de résumé avec nouveau style
            html.Div([
                html.Div([
                    html.Div([
                        html.H3(f"{market_stats['total_volume']:,.0f} MAD", 
                               style={'color': UNIFIED_COLORS['primary_blue'], 'margin': '0', 'fontSize': '1.8rem'}),
                        html.P('Volume Total des Échanges', 
                              style={'margin': '5px 0', 'color': UNIFIED_COLORS['text_light'], 'fontSize': '0.9rem'})
                    ], style={'textAlign': 'center'})
                ], style={**UNIFIED_CARD_STYLE, 'width': '18%', 'display': 'inline-block', 'margin': '1%'}),
                
                html.Div([
                    html.Div([
                        html.H3(f"{market_stats['total_transactions']:,.0f}", 
                               style={'color': UNIFIED_COLORS['secondary_blue'], 'margin': '0', 'fontSize': '1.8rem'}),
                        html.P('Nombre de Transactions', 
                              style={'margin': '5px 0', 'color': UNIFIED_COLORS['text_light'], 'fontSize': '0.9rem'})
                    ], style={'textAlign': 'center'})
                ], style={**UNIFIED_CARD_STYLE, 'width': '12%', 'display': 'inline-block', 'margin': '1%'}),
                
                html.Div([
                    html.Div([
                        html.H3(f"{market_stats['avg_variation']:.2f}%", 
                               style={'color': UNIFIED_COLORS['warning_blue'], 'margin': '0', 'fontSize': '1.8rem'}),
                        html.P('Variation Moyenne', 
                              style={'margin': '5px 0', 'color': UNIFIED_COLORS['text_light'], 'fontSize': '0.9rem'})
                    ], style={'textAlign': 'center'})
                ], style={**UNIFIED_CARD_STYLE, 'width': '12%', 'display': 'inline-block', 'margin': '1%'}),
                
                html.Div([
                    html.Div([
                        html.H3(f"{market_stats['positive_stocks']}", 
                               style={'color': UNIFIED_COLORS['success_blue'], 'margin': '0', 'fontSize': '1.8rem'}),
                        html.P('Actions en Hausse', 
                              style={'margin': '5px 0', 'color': UNIFIED_COLORS['text_light'], 'fontSize': '0.9rem'})
                    ], style={'textAlign': 'center'})
                ], style={**UNIFIED_CARD_STYLE, 'width': '12%', 'display': 'inline-block', 'margin': '1%'}),
                
                html.Div([
                    html.Div([
                        html.H3(f"{market_stats['negative_stocks']}", 
                               style={'color': UNIFIED_COLORS['danger_blue'], 'margin': '0', 'fontSize': '1.8rem'}),
                        html.P('Actions en Baisse', 
                              style={'margin': '5px 0', 'color': UNIFIED_COLORS['text_light'], 'fontSize': '0.9rem'})
                    ], style={'textAlign': 'center'})
                ], style={**UNIFIED_CARD_STYLE, 'width': '12%', 'display': 'inline-block', 'margin': '1%'})
            ])
        ], style={'marginBottom': '40px'}),
        
        # Section Performance des Actions
        html.Div([
            html.H2('Performance des Actions', 
                    style={
                        'color': UNIFIED_COLORS['text_dark'], 
                        'marginBottom': '20px',
                        'fontSize': '1.5rem',
                        'fontWeight': '500'
                    }),
            html.Div([
                dcc.Graph(figure=stock_perf_fig)
            ], style=UNIFIED_CARD_STYLE)
        ], style={'marginBottom': '40px'}),
        
        # Sections Volumes/Dividendes et Crédit côte à côte
        html.Div([
        # Section Analyse des Volumes et Dividendes
        html.Div([
            html.H2('Analyse des Volumes et Dividendes', 
                    style={
                        'color': UNIFIED_COLORS['text_dark'], 
                        'marginBottom': '20px',
                        'fontSize': '1.5rem',
                        'fontWeight': '500'
                    }),
            
            html.Div([  # Flex container for the two graphs
                html.Div([
                    html.H3('Volume des Échanges', 
                            style={'color': UNIFIED_COLORS['primary_blue'], 'marginBottom': '15px'}),
                    dcc.Graph(figure=volume_fig)
                ], style={**UNIFIED_CARD_STYLE, 'width': '48%', 'marginRight': '4%'}),
                
                html.Div([
                    html.H3('Dividendes Versés', 
                            style={'color': UNIFIED_COLORS['primary_blue'], 'marginBottom': '15px'}),
                    dcc.Graph(figure=dividends_fig)
                ], style={**UNIFIED_CARD_STYLE, 'width': '48%'})
            ], style={'display': 'flex', 'justifyContent': 'space-between'})
            ], style={'width': '100%'}),
        ], style={'marginBottom': '40px'})
    ])

# SOLUTION: Dynamic Layout with Interval Component
layout = html.Div([
    # Container for dynamic content
    html.Div(id='bourse-content'),
    
    # Interval component for auto-refresh
    dcc.Interval(
        id='bourse-interval',
        interval=10*1000,  # Update every 10 seconds
        n_intervals=0
    )
], style={
    'backgroundColor': UNIFIED_COLORS['background'], 
    'padding': '30px',
    'fontFamily': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
})

# Callback to refresh data and update layout
@callback(
    Output('bourse-content', 'children'),
    [Input('bourse-interval', 'n_intervals')]
)
def update_bourse_data(n_intervals):
    """Charge les données dynamiquement et met à jour le layout"""
    # Load fresh data from CSV files
    stocks_df, dividends_df = load_and_prepare_data()
    
    # Create layout with fresh data
    return create_layout_content(stocks_df, dividends_df)
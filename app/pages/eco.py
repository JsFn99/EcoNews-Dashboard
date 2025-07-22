# pages/eco.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yaml
from dash import dash_table, dcc, html
from plotly.subplots import make_subplots
from styles.styles import card_style

# Schéma de couleurs centré sur le bleu
COLORS = {
    'primary': '#1e3a8a',        # Bleu foncé principal
    'primary_blue': '#2c5aa0',
    'secondary': '#3b82f6',      # Bleu secondaire 
    'tertiary': '#60a5fa',       # Bleu clair
    'light_blue': '#dbeafe',     # Bleu très clair
    'success': '#10b981',        # Vert pour positif (inchangé)
    'danger': '#ef4444',         # Rouge pour négatif (inchangé)
    'warning': '#f59e0b',        # Orange/jaune pour attention
    'neutral': '#6b7280',        # Gris neutre
    'text': '#1f2937',           # Texte principal
    'text_light': '#6b7280',     # Texte secondaire
    'background': '#f8fafc',     # Arrière-plan
    'card_bg': '#ffffff',        # Arrière-plan des cartes
    'border': '#e2e8f0',        # Bordures
    'accent': '#8b5cf6'          # Accent violet-bleu
}

# Variables d'initialisation
data_loaded = False
credit_fig = None
monthly_change_fig = None
inflation_fig = None
sentiment_fig = None
theme_fig = None
growth_fig = None

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)


# Chargement des données
try:
    # Charger les données de crédit
    credit_df = pd.read_csv(config['paths']['credit_data'])
    
    # Charger les données d'inflation depuis le CSV fourni
    inflation_df = pd.read_csv(config['paths']['inflation'])
    
    # Traitement des données d'inflation amélioré
    # Créer une colonne de date complète pour un meilleur affichage
    inflation_df['Date'] = inflation_df['Annee'].astype(str) + '-' + inflation_df['Trimestres']
    inflation_df['Date_num'] = inflation_df['Annee'] + (inflation_df['Trimestres'].str.replace('T', '').astype(int) - 1) * 0.25
    
    # Créer les visualisations avec le nouveau schéma de couleurs
    
    # 1. Graphique en barres des crédits par secteur
    credit_fig = px.bar(
        credit_df, 
        x='sector', 
        y='amount_mmdh',
        color='april_annual_growth',
        title='Crédit par Secteur (Mai 2025)',
        labels={
            'amount_mmdh': 'Montant (Millions MAD)', 
            'sector': 'Secteur', 
            'april_annual_growth': 'Croissance Annuelle %'
        },
        color_continuous_scale=['#ef4444', '#f59e0b', '#10b981']  # Rouge -> Orange -> Vert
    )
    credit_fig.update_layout(
        height=500, 
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text'], family="'Segoe UI', sans-serif"),
        title_font=dict(size=20, color=COLORS['primary'])
    )
    credit_fig.update_xaxes(tickangle=45, title_font=dict(color=COLORS['primary']))
    credit_fig.update_yaxes(title_font=dict(color=COLORS['primary']))
    
    # 2. Analyse des changements mensuels
    monthly_change_fig = px.scatter(
        credit_df,
        x='monthly_change_pct',
        y='april_annual_growth',
        size='amount_mmdh',
        color='sector',
        title='Évolution Mensuelle vs Croissance Annuelle par Secteur',
        labels={
            'monthly_change_pct': 'Variation Mensuelle %', 
            'april_annual_growth': 'Croissance Annuelle %'
        },
        hover_data=['amount_mmdh'],
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    monthly_change_fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text'], family="'Segoe UI', sans-serif"),
        title_font=dict(size=20, color=COLORS['primary'])
    )
    
    # 3. Graphique d'inflation amélioré avec plus de détails
    inflation_fig = go.Figure()
    
    # Ligne principale
    inflation_fig.add_trace(go.Scatter(
        x=inflation_df['Date_num'],
        y=inflation_df['Inflation_pct'],
        mode='lines+markers',
        name='Taux d\'Inflation',
        line=dict(color=COLORS['secondary'], width=3),
        marker=dict(size=8, color=COLORS['primary']),
        hovertemplate='<b>%{text}</b><br>Inflation: %{y}%<extra></extra>',
        text=inflation_df['Date']
    ))
    
    # Zone de remplissage pour visualiser les périodes
    inflation_fig.add_trace(go.Scatter(
        x=inflation_df['Date_num'],
        y=inflation_df['Inflation_pct'],
        fill='tozeroy',
        fillcolor=f'rgba(59, 130, 246, 0.1)',
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Ligne de référence à 0%
    inflation_fig.add_hline(y=0, line_dash="dash", line_color=COLORS['neutral'], 
                           annotation_text="Référence 0%", annotation_position="bottom right")
    
    inflation_fig.update_layout(
        title='Évolution du Taux d\'Inflation au Maroc (2013-2024)',
        xaxis_title='Année',
        yaxis_title='Taux d\'Inflation (%)',
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text'], family="'Segoe UI', sans-serif"),
        title_font=dict(size=20, color=COLORS['primary']),
        hovermode='x unified'
    )
    
    # Personnaliser les axes
    inflation_fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor=COLORS['border'],
        title_font=dict(color=COLORS['primary'])
    )
    inflation_fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor=COLORS['border'],
        title_font=dict(color=COLORS['primary'])
    )
    
    # 6. Analyse combinée des tendances de croissance
    growth_fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Croissance Annuelle du Crédit par Secteur', 'Montants par Secteur'),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]],
        vertical_spacing=0.15
    )
    
    # Ajouter les taux de croissance
    growth_fig.add_trace(
        go.Bar(
            x=credit_df['sector'], 
            y=credit_df['april_annual_growth'], 
            name='Croissance Mai %',
            marker_color=COLORS['secondary']
        ),
        row=1, col=1
    )
    
    # Ajouter les montants
    growth_fig.add_trace(
        go.Bar(
            x=credit_df['sector'], 
            y=credit_df['amount_mmdh'], 
            name='Montant (Millions MAD)',
            marker_color=COLORS['tertiary']
        ),
        row=2, col=1
    )
    
    growth_fig.update_layout(
        height=700, 
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text'], family="'Segoe UI', sans-serif"),
        title_font=dict(size=20, color=COLORS['primary'])
    )
    growth_fig.update_xaxes(tickangle=45)
    
    # Marquer le chargement des données comme réussi
    data_loaded = True
    
except Exception as e:
    print(f"Erreur lors du chargement des données: {e}")
    # Données de secours si les fichiers ne peuvent pas être chargés
    data_loaded = False
    
    # Créer des graphiques de secours simples
    def create_error_figure(title, error_msg=None):
        fig = go.Figure()
        fig.add_annotation(
            text=f"{title}<br><br>Erreur: {error_msg if error_msg else 'Fichier non trouvé ou échec du chargement des données'}", 
            xref="paper", yref="paper", 
            x=0.5, y=0.5, 
            showarrow=False,
            font=dict(size=16, color=COLORS['danger']),
            align="center"
        )
        fig.update_layout(
            title=title,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text'], family="'Segoe UI', sans-serif")
        )
        return fig
    
    credit_fig = create_error_figure("Données de Crédit - Échec du Chargement", str(e))
    monthly_change_fig = create_error_figure("Données de Variation Mensuelle - Échec du Chargement", str(e))
    inflation_fig = create_error_figure("Données d'Inflation - Échec du Chargement", str(e))
    theme_fig = create_error_figure("Données de Thème - Échec du Chargement", str(e))
    growth_fig = create_error_figure("Données de Croissance - Échec du Chargement", str(e))


# Style de carte amélioré
enhanced_card_style = {
    'background': COLORS['card_bg'],
    'padding': '30px',
    'border-radius': '16px',
    'box-shadow': '0 8px 24px rgba(59, 130, 246, 0.12)',
    'border': f'1px solid {COLORS["border"]}',
    'margin-bottom': '24px',
    'transition': 'transform 0.2s ease, box-shadow 0.2s ease'
}

# Mise en page
layout = html.Div([
    # En-tête principal
    html.Div([
        html.H1('Analyse des Données Économiques Marocaines', 
                style={
                    'textAlign': 'center', 
                    'color': COLORS['primary_blue'], 
                    'marginBottom': '40px',
                    'fontSize': '2.5rem',
                    'fontWeight': '600',
                    'fontFamily': 'Inter'
                })
    ]),
    
    # Section Données Économiques
    html.Div([
        # Analyse du crédit
        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=credit_fig)
                ], style=enhanced_card_style)
            ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),
            
            html.Div([
                html.Div([
                    dcc.Graph(figure=monthly_change_fig)
                ], style=enhanced_card_style)
            ], style={'width': '48%', 'display': 'inline-block'})
        ]),
        
        # Tendance de l'inflation
        html.Div([
            html.Div([
                dcc.Graph(figure=inflation_fig)
            ], style=enhanced_card_style)
        ]),
        
        # Analyse combinée de la croissance
        html.Div([
            html.Div([
                html.H3('Analyse Complète de la Croissance', style={
                    'color': COLORS['primary'],
                    'marginBottom': '20px',
                    'fontSize': '1.3rem'
                }),
                dcc.Graph(figure=growth_fig)
            ], style=enhanced_card_style)
        ])
    ])
], style={
    'padding': '20px',
    'backgroundColor': COLORS['background'],
    'minHeight': '100vh',
    'fontFamily': '"Segoe UI", "Helvetica Neue", Arial, sans-serif'
})
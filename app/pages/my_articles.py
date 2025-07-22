# pages/my_articles.py

import os
from datetime import datetime

import pandas as pd
import yaml
from dash import ALL, Input, Output, State, callback, dcc, html, no_update

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Schéma de couleurs centré sur le bleu
COLORS = {
    'primary': '#1e3a8a',
    'secondary': '#3b82f6',
    'success': '#10b981',
    'danger': '#ef4444',
    'neutral': '#6b7280',
    'text': '#1f2937',
    'text_light': '#6b7280',
    'background': '#f8fafc',
    'card_bg': '#ffffff',
    'border': '#e2e8f0'
}

# File paths
eco_news_file = config['paths'].get('eco_news', '/Users/mac/Sentiment Analysis Press/app/my_eco_news.csv')
stock_news_file = config['paths'].get('stock_news', '/Users/mac/Sentiment Analysis Press/app/my_stock_news.csv')

# Function to load CSV files
def load_csv_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['published'] = pd.to_datetime(df['published'])
            return df.sort_values('published', ascending=False)
        except:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

# Function to delete article from CSV
def delete_article_from_csv(article_title, file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Remove the article with matching title
            df = df[df['title'] != article_title]
            # Save back to CSV
            df.to_csv(file_path, index=False)
            return True
        except Exception as e:
            print(f"Error deleting article: {e}")
            return False
    return False

# Function to create article items
def create_article_items(df, section_type):
    if df.empty:
        return [html.Div([
            html.P("Aucun article pour le moment.",
                   style={
                       'text-align': 'center',
                       'color': COLORS['text_light'],
                       'font-size': '16px',
                       'margin': '40px 0'
                   })
        ])]
    
    items = []
    for index, row in df.iterrows():
        sentiment_color = {
            'Positif': COLORS['success'],
            'Haussier': COLORS['success'],
            'Négatif': COLORS['danger'],
            'Baissier': COLORS['danger'],
            'Neutre': COLORS['neutral']
        }.get(row['sentiment'], COLORS['neutral'])
        
        # Create badges based on section type
        if section_type == 'stock':
            first_badge = row.get('stock', row.get('theme', 'N/A'))
        else:
            first_badge = row.get('theme', row.get('source', 'N/A'))
        
        items.append(
            html.Div([
                # Header with badges and delete button
                html.Div([
                    html.Div([
                        html.Span(first_badge, style={
                            'background': COLORS['primary'],
                            'color': 'white',
                            'padding': '8px 16px',
                            'border-radius': '20px',
                            'font-size': '12px',
                            'font-weight': '600',
                            'display': 'inline-block'
                        }),
                        html.Span(row['sentiment'], style={
                            'background': sentiment_color,
                            'color': 'white',
                            'padding': '8px 16px',
                            'border-radius': '20px',
                            'font-size': '12px',
                            'margin-left': '12px',
                            'font-weight': '500',
                            'display': 'inline-block'
                        }),
                        html.Span(row.get('source', ''), style={
                            'background': COLORS['neutral'],
                            'color': 'white',
                            'padding': '8px 16px',
                            'border-radius': '20px',
                            'font-size': '12px',
                            'margin-left': '12px',
                            'font-weight': '500',
                            'display': 'inline-block'
                        }) if row.get('source') and section_type == 'stock' else html.Span()
                    ], style={'flex': '1'}),
                    
                    # Delete button
                    html.Button([
                        html.I(className="fas fa-trash-alt", style={'margin-right': '5px'}),
                        "Supprimer"
                    ], 
                    id={'type': 'delete-btn', 'index': f"{section_type}-{index}"},
                    style={
                        'background': COLORS['danger'],
                        'color': 'white',
                        'border': 'none',
                        'padding': '8px 12px',
                        'border-radius': '6px',
                        'font-size': '12px',
                        'cursor': 'pointer',
                        'transition': 'all 0.2s',
                        'font-weight': '500'
                    },
                    n_clicks=0
                    )
                ], style={
                    'display': 'flex',
                    'justify-content': 'space-between',
                    'align-items': 'flex-start',
                    'margin-bottom': '15px'
                }),
                
                # Titre
                html.H4(row['title'], style={
                    'margin': '0 0 12px 0',
                    'font-size': '18px',
                    'color': COLORS['primary'],
                    'line-height': '1.4',
                    'font-weight': '600'
                }),
                
                # Résumé
                html.P(row['mini_resume'], style={
                    'margin': '0 0 12px 0',
                    'font-size': '14px',
                    'color': COLORS['text'],
                    'line-height': '1.6'
                }),
                
                # Lien
                html.A("Lire l'article complet",
                       href=row.get('link', '#'),
                       target="_blank",
                       style={
                           'color': COLORS['secondary'],
                           'font-size': '13px',
                           'text-decoration': 'none',
                           'font-weight': '500',
                           'border': f'1px solid {COLORS["secondary"]}',
                           'padding': '6px 12px',
                           'border-radius': '6px',
                           'display': 'inline-block',
                           'transition': 'all 0.2s'
                       }) if pd.notna(row.get('link')) else html.Span(),
                
                html.Br() if pd.notna(row.get('link')) else html.Span(),
                html.Br() if pd.notna(row.get('link')) else html.Span(),
                
                # Date
                html.P(f"Publié le {row['published'].strftime('%d/%m/%Y')}", style={
                    'margin': '12px 0 0 0',
                    'font-size': '12px',
                    'color': COLORS['text_light'],
                    'font-style': 'italic'
                }),
                
                # Hidden div to store article title and section for deletion
                html.Div([
                    html.Span(row['title'], id={'type': 'article-title', 'index': f"{section_type}-{index}"}),
                    html.Span(section_type, id={'type': 'article-section', 'index': f"{section_type}-{index}"})
                ], style={'display': 'none'})
                
            ], style={
                'background': COLORS['card_bg'],
                'padding': '24px',
                'border-radius': '12px',
                'box-shadow': '0 4px 12px rgba(59, 130, 246, 0.08)',
                'margin-bottom': '20px',
                'border-left': f'5px solid {sentiment_color}',
                'border': f'1px solid {COLORS["border"]}'
            })
        )
    return items

# Layout with two sections
layout = html.Div([
    # Header
    html.Div([
        html.H1('Mes Articles', 
                style={
                    'textAlign': 'center', 
                    'color': COLORS['primary'], 
                    'marginBottom': '40px',
                    'fontSize': '2.5rem',
                    'fontWeight': '600'
                })
    ]),
    
    # Economic News Section
    html.Div([
        html.H2('Actualités Économiques', 
                style={
                    'color': COLORS['primary'],
                    'marginBottom': '20px',
                    'fontSize': '1.8rem',
                    'fontWeight': '600',
                    'borderBottom': f'2px solid {COLORS["primary"]}',
                    'paddingBottom': '10px'
                }),
        html.Div(
            id='eco-articles-container',
            children=[],
            style={
                'maxHeight': '600px', 
                'overflowY': 'auto',
                'border': f'1px solid {COLORS["border"]}',
                'borderRadius': '12px',
                'padding': '20px',
                'background': COLORS['background']
            }
        )
    ], style={
        'background': COLORS['card_bg'],
        'padding': '30px',
        'border-radius': '16px',
        'box-shadow': '0 8px 24px rgba(59, 130, 246, 0.12)',
        'border': f'1px solid {COLORS["border"]}',
        'marginBottom': '30px'
    }),
    
    # Stock News Section
    html.Div([
        html.H2('Actualités Boursières', 
                style={
                    'color': COLORS['primary'],
                    'marginBottom': '20px',
                    'fontSize': '1.8rem',
                    'fontWeight': '600',
                    'borderBottom': f'2px solid {COLORS["primary"]}',
                    'paddingBottom': '10px'
                }),
        html.Div(
            id='stock-articles-container',
            children=[],
            style={
                'maxHeight': '600px', 
                'overflowY': 'auto',
                'border': f'1px solid {COLORS["border"]}',
                'borderRadius': '12px',
                'padding': '20px',
                'background': COLORS['background']
            }
        )
    ], style={
        'background': COLORS['card_bg'],
        'padding': '30px',
        'border-radius': '16px',
        'box-shadow': '0 8px 24px rgba(59, 130, 246, 0.12)',
        'border': f'1px solid {COLORS["border"]}'
    }),
    
    # Store for the article to delete
    dcc.Store(id='article-to-delete', data=None),
    
    # Confirmation dialog
    dcc.ConfirmDialog(
        id='confirm-delete-dialog',
        message='Êtes-vous sûr de vouloir supprimer cet article ?',
    ),
    
    # Interval component for auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    )
    
], style={
    'padding': '20px',
    'backgroundColor': COLORS['background'],
    'minHeight': '100vh',
    'fontFamily': '"Segoe UI", "Helvetica Neue", Arial, sans-serif'
})

# Callback to load economic articles
@callback(
    Output('eco-articles-container', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def load_eco_articles(n_intervals):
    """Load economic articles dynamically"""
    eco_df = load_csv_data(eco_news_file)
    return create_article_items(eco_df, 'eco')

# Callback to load stock articles
@callback(
    Output('stock-articles-container', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def load_stock_articles(n_intervals):
    """Load stock articles dynamically"""
    stock_df = load_csv_data(stock_news_file)
    return create_article_items(stock_df, 'stock')

# Callback to handle delete button clicks
@callback(
    [Output('confirm-delete-dialog', 'displayed'),
     Output('article-to-delete', 'data')],
    [Input({'type': 'delete-btn', 'index': ALL}, 'n_clicks')],
    [State({'type': 'article-title', 'index': ALL}, 'children'),
     State({'type': 'article-section', 'index': ALL}, 'children')]
)
def show_confirm_dialog(n_clicks_list, article_titles, article_sections):
    if not any(n_clicks_list):
        return no_update, no_update
    
    # Find which button was clicked
    for i, n_clicks in enumerate(n_clicks_list):
        if n_clicks and n_clicks > 0:
            return True, {
                'title': article_titles[i],
                'section': article_sections[i]
            }
    
    return no_update, no_update

# Callback to handle article deletion
@callback(
    [Output('eco-articles-container', 'children', allow_duplicate=True),
     Output('stock-articles-container', 'children', allow_duplicate=True),
     Output('article-to-delete', 'data', allow_duplicate=True)],
    [Input('confirm-delete-dialog', 'submit_n_clicks')],
    [State('article-to-delete', 'data')],
    prevent_initial_call=True
)
def delete_article(submit_n_clicks, article_data):
    if submit_n_clicks and article_data:
        article_title = article_data['title']
        section = article_data['section']
        
        # Determine which file to delete from
        if section == 'eco':
            file_path = eco_news_file
        else:
            file_path = stock_news_file
        
        # Delete from CSV
        success = delete_article_from_csv(article_title, file_path)
        
        if success:
            # Reload both sections
            new_eco_df = load_csv_data(eco_news_file)
            new_stock_df = load_csv_data(stock_news_file)
            
            new_eco_items = create_article_items(new_eco_df, 'eco')
            new_stock_items = create_article_items(new_stock_df, 'stock')
            
            return new_eco_items, new_stock_items, None
        
    return no_update, no_update, no_update
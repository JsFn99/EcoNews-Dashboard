# pages/my_articles.py

import json
import os
from datetime import datetime

import pandas as pd
import requests
import yaml
from dash import (ALL, Input, Output, State, callback, callback_context, dcc,
                  html, no_update)

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Schéma de couleurs centré sur le bleu
COLORS = {
    'primary': '#1e3a8a',
    'secondary': '#3b82f6',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'neutral': '#6b7280',
    'text': '#1f2937',
    'text_light': '#6b7280',
    'background': '#f8fafc',
    'card_bg': '#ffffff',
    'border': '#e2e8f0'
}

# File paths
eco_news_file = config['paths'].get('eco_news', 'my_eco_news.csv')
stock_news_file = config['paths'].get('stock_news', 'my_stock_news.csv')

# FastAPI server URL
FASTAPI_SERVER_URL = "http://localhost:8000"  # Update this to match your FastAPI server

# Function to load CSV files
def load_csv_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['published'] = pd.to_datetime(df['published'])
            # Ensure treated column exists
            if 'treated' not in df.columns:
                df['treated'] = False
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

# Function to update treated status in CSV
def update_treated_status(article_titles, file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Update treated status for selected articles
            df.loc[df['title'].isin(article_titles), 'treated'] = True
            # Save back to CSV
            df.to_csv(file_path, index=False)
            return True
        except Exception as e:
            print(f"Error updating treated status: {e}")
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
        
        # Determine treated status
        is_treated = row.get('treated', False)
        treated_style = {
            'background': COLORS['success'] if is_treated else COLORS['warning'],
            'color': 'white',
            'padding': '6px 12px',
            'border-radius': '15px',
            'font-size': '11px',
            'margin-left': '12px',
            'font-weight': '600',
            'display': 'inline-block'
        }
        
        items.append(
            html.Div([
                # Header with badges, select checkbox, and delete button
                html.Div([
                    html.Div([
                        # Selection checkbox
                        dcc.Checklist(
                            id={'type': 'article-select', 'index': f"{section_type}-{index}"},
                            options=[{'label': 'Sélectionner', 'value': 'selected'}],
                            value=[],
                            style={
                                'margin-right': '15px',
                                'display': 'inline-block'
                            }
                        ),
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
                        }) if row.get('source') and section_type == 'stock' else html.Span(),
                        # Treated status badge
                        html.Span([
                            html.I(className="fas fa-check-circle" if is_treated else "fas fa-clock", 
                                   style={'margin-right': '5px'}),
                            "Traité" if is_treated else "Non traité"
                        ], style=treated_style)
                    ], style={'flex': '1', 'display': 'flex', 'align-items': 'center'}),
                    
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
                
                # Hidden div to store article data
                html.Div([
                    html.Span(row['title'], id={'type': 'article-title', 'index': f"{section_type}-{index}"}),
                    html.Span(row['mini_resume'], id={'type': 'article-resume', 'index': f"{section_type}-{index}"}),
                    html.Span(section_type, id={'type': 'article-section', 'index': f"{section_type}-{index}"})
                ], style={'display': 'none'})
                
            ], style={
                'background': COLORS['card_bg'],
                'padding': '24px',
                'border-radius': '12px',
                'box-shadow': '0 4px 12px rgba(59, 130, 246, 0.08)',
                'margin-bottom': '20px',
                'border-left': f'5px solid {sentiment_color}',
                'border': f'1px solid {COLORS["border"]}',
                'opacity': '0.7' if is_treated else '1.0'  # Slightly fade treated articles
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
                    'marginBottom': '20px',
                    'fontSize': '2.5rem',
                    'fontWeight': '600'
                }),
        
        # PDF Generation Section
        html.Div([
            html.Div([
                html.Button([
                    html.I(className="fas fa-file-pdf", style={'margin-right': '8px'}),
                    "Générer PDF avec articles sélectionnés"
                ], 
                id='generate-pdf-btn',
                style={
                    'background': COLORS['success'],
                    'color': 'white',
                    'border': 'none',
                    'padding': '12px 24px',
                    'border-radius': '8px',
                    'font-size': '14px',
                    'cursor': 'pointer',
                    'transition': 'all 0.2s',
                    'font-weight': '600',
                    'margin-right': '15px'
                },
                n_clicks=0
                ),
                html.Button([
                    html.I(className="fas fa-check-square", style={'margin-right': '8px'}),
                    "Tout sélectionner"
                ], 
                id='select-all-btn',
                style={
                    'background': COLORS['secondary'],
                    'color': 'white',
                    'border': 'none',
                    'padding': '12px 24px',
                    'border-radius': '8px',
                    'font-size': '14px',
                    'cursor': 'pointer',
                    'transition': 'all 0.2s',
                    'font-weight': '600',
                    'margin-right': '15px'
                },
                n_clicks=0
                ),
                html.Button([
                    html.I(className="fas fa-square", style={'margin-right': '8px'}),
                    "Tout désélectionner"
                ], 
                id='deselect-all-btn',
                style={
                    'background': COLORS['neutral'],
                    'color': 'white',
                    'border': 'none',
                    'padding': '12px 24px',
                    'border-radius': '8px',
                    'font-size': '14px',
                    'cursor': 'pointer',
                    'transition': 'all 0.2s',
                    'font-weight': '600',
                    'margin-right': '15px'
                },
                n_clicks=0
                ),
                html.Button([
                    html.I(className="fas fa-filter", style={'margin-right': '8px'}),
                    "Afficher non traités uniquement"
                ], 
                id='filter-untreated-btn',
                style={
                    'background': COLORS['warning'],
                    'color': 'white',
                    'border': 'none',
                    'padding': '12px 24px',
                    'border-radius': '8px',
                    'font-size': '14px',
                    'cursor': 'pointer',
                    'transition': 'all 0.2s',
                    'font-weight': '600'
                },
                n_clicks=0
                )
            ], style={'text-align': 'center', 'margin-bottom': '20px'}),
            
            # Status message
            html.Div(id='pdf-status', style={
                'text-align': 'center',
                'margin-bottom': '20px',
                'font-weight': '500'
            })
        ], style={
            'background': COLORS['card_bg'],
            'padding': '20px',
            'border-radius': '12px',
            'box-shadow': '0 4px 12px rgba(59, 130, 246, 0.08)',
            'border': f'1px solid {COLORS["border"]}',
            'margin-bottom': '30px'
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
    
    # Store for selected articles
    dcc.Store(id='selected-articles', data=[]),
    
    # Store for filter state
    dcc.Store(id='filter-untreated', data=False),
    
    # Confirmation dialog
    dcc.ConfirmDialog(
        id='confirm-delete-dialog',
        message='Êtes-vous sûr de vouloir supprimer cet article ?',
    ),
    
    # Interval component for auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Update every 1 minute
        n_intervals=0
    )
    
], style={
    'padding': '20px',
    'backgroundColor': COLORS['background'],
    'minHeight': '100vh',
    'fontFamily': '"Segoe UI", "Helvetica Neue", Arial, sans-serif'
})

# Callback to handle filter button
@callback(
    [Output('filter-untreated', 'data'),
     Output('filter-untreated-btn', 'children'),
     Output('filter-untreated-btn', 'style')],
    [Input('filter-untreated-btn', 'n_clicks')],
    [State('filter-untreated', 'data')]
)
def toggle_filter(n_clicks, current_filter):
    if not n_clicks:
        return False, [
            html.I(className="fas fa-filter", style={'margin-right': '8px'}),
            "Afficher non traités uniquement"
        ], {
            'background': COLORS['warning'],
            'color': 'white',
            'border': 'none',
            'padding': '12px 24px',
            'border-radius': '8px',
            'font-size': '14px',
            'cursor': 'pointer',
            'transition': 'all 0.2s',
            'font-weight': '600'
        }
    
    new_filter = not current_filter
    
    if new_filter:
        return True, [
            html.I(className="fas fa-eye", style={'margin-right': '8px'}),
            "Afficher tous les articles"
        ], {
            'background': COLORS['primary'],
            'color': 'white',
            'border': 'none',
            'padding': '12px 24px',
            'border-radius': '8px',
            'font-size': '14px',
            'cursor': 'pointer',
            'transition': 'all 0.2s',
            'font-weight': '600'
        }
    else:
        return False, [
            html.I(className="fas fa-filter", style={'margin-right': '8px'}),
            "Afficher non traités uniquement"
        ], {
            'background': COLORS['warning'],
            'color': 'white',
            'border': 'none',
            'padding': '12px 24px',
            'border-radius': '8px',
            'font-size': '14px',
            'cursor': 'pointer',
            'transition': 'all 0.2s',
            'font-weight': '600'
        }

# Callback to load economic articles
@callback(
    Output('eco-articles-container', 'children'),
    [Input('interval-component', 'n_intervals'),
     Input('filter-untreated', 'data')]
)
def load_eco_articles(n_intervals, filter_untreated):
    """Load economic articles dynamically"""
    eco_df = load_csv_data(eco_news_file)
    
    # Apply filter if needed
    if filter_untreated and not eco_df.empty:
        eco_df = eco_df[eco_df['treated'] == False]
    
    return create_article_items(eco_df, 'eco')

# Callback to load stock articles
@callback(
    Output('stock-articles-container', 'children'),
    [Input('interval-component', 'n_intervals'),
     Input('filter-untreated', 'data')]
)
def load_stock_articles(n_intervals, filter_untreated):
    """Load stock articles dynamically"""
    stock_df = load_csv_data(stock_news_file)
    
    # Apply filter if needed
    if filter_untreated and not stock_df.empty:
        stock_df = stock_df[stock_df['treated'] == False]
    
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
    [State('article-to-delete', 'data'),
     State('filter-untreated', 'data')],
    prevent_initial_call=True
)
def delete_article(submit_n_clicks, article_data, filter_untreated):
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
            # Reload both sections with current filter
            new_eco_df = load_csv_data(eco_news_file)
            new_stock_df = load_csv_data(stock_news_file)
            
            # Apply filter if needed
            if filter_untreated:
                if not new_eco_df.empty:
                    new_eco_df = new_eco_df[new_eco_df['treated'] == False]
                if not new_stock_df.empty:
                    new_stock_df = new_stock_df[new_stock_df['treated'] == False]
            
            new_eco_items = create_article_items(new_eco_df, 'eco')
            new_stock_items = create_article_items(new_stock_df, 'stock')
            
            return new_eco_items, new_stock_items, None
        
    return no_update, no_update, no_update

# Callback to handle select all button
@callback(
    Output({'type': 'article-select', 'index': ALL}, 'value'),
    [Input('select-all-btn', 'n_clicks'),
     Input('deselect-all-btn', 'n_clicks')],
    [State({'type': 'article-select', 'index': ALL}, 'value')]
)
def handle_select_all(select_all_clicks, deselect_all_clicks, current_values):
    if not select_all_clicks and not deselect_all_clicks:
        return [[] for _ in current_values]
    
    ctx = callback_context
    if not ctx.triggered:
        return [[] for _ in current_values]
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'select-all-btn':
        return [['selected'] for _ in current_values]
    elif button_id == 'deselect-all-btn':
        return [[] for _ in current_values]
    
    return [[] for _ in current_values]

# Callback to handle PDF generation
@callback(
    [Output('pdf-status', 'children'),
     Output('eco-articles-container', 'children', allow_duplicate=True),
     Output('stock-articles-container', 'children', allow_duplicate=True)],
    [Input('generate-pdf-btn', 'n_clicks')],
    [State({'type': 'article-select', 'index': ALL}, 'value'),
     State({'type': 'article-title', 'index': ALL}, 'children'),
     State({'type': 'article-resume', 'index': ALL}, 'children'),
     State({'type': 'article-section', 'index': ALL}, 'children'),
     State('filter-untreated', 'data')],
    prevent_initial_call=True
)
def generate_pdf(n_clicks, selected_values, article_titles, article_resumes, article_sections, filter_untreated):
    if not n_clicks:
        return "", no_update, no_update
    
    # Filter selected articles
    selected_articles = []
    selected_eco_titles = []
    selected_stock_titles = []
    
    for i, selected in enumerate(selected_values):
        if selected and 'selected' in selected:
            selected_articles.append({
                'title': article_titles[i],
                'mini_resume': article_resumes[i]
            })
            
            # Track which articles are selected for each section
            section = article_sections[i]
            if section == 'eco':
                selected_eco_titles.append(article_titles[i])
            else:
                selected_stock_titles.append(article_titles[i])
    
    if not selected_articles:
        return html.Div([
            html.I(className="fas fa-exclamation-triangle", style={'margin-right': '8px'}),
            "Aucun article sélectionné. Veuillez sélectionner au moins un article."
        ], style={'color': COLORS['danger']}), no_update, no_update
    
    try:
        # Send request to FastAPI server
        response = requests.post(
            f"{FASTAPI_SERVER_URL}/generate-pdf",
            json={"articles": selected_articles},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            filename = result.get('filename', '')
            articles_count = result.get('articles_count', 0)
            
            # Update treated status for selected articles
            if selected_eco_titles:
                update_treated_status(selected_eco_titles, eco_news_file)
            if selected_stock_titles:
                update_treated_status(selected_stock_titles, stock_news_file)
            
            # Reload articles to reflect updated treated status
            new_eco_df = load_csv_data(eco_news_file)
            new_stock_df = load_csv_data(stock_news_file)
            
            # Apply filter if needed
            if filter_untreated:
                if not new_eco_df.empty:
                    new_eco_df = new_eco_df[new_eco_df['treated'] == False]
                if not new_stock_df.empty:
                    new_stock_df = new_stock_df[new_stock_df['treated'] == False]
            
            new_eco_items = create_article_items(new_eco_df, 'eco')
            new_stock_items = create_article_items(new_stock_df, 'stock')
            
            status_message = html.Div([
                html.I(className="fas fa-check-circle", style={'margin-right': '8px'}),
                f"PDF généré avec succès ! {articles_count} articles traités. ",
                html.A(
                    "Télécharger PDF",
                    href=f"{FASTAPI_SERVER_URL}/download-pdf/{filename}",
                    target="_blank",
                    style={
                        'color': COLORS['secondary'],
                        'text-decoration': 'none',
                        'font-weight': '600'
                    }
                )
            ], style={'color': COLORS['success']})
            
            return status_message, new_eco_items, new_stock_items
        else:
            error_message = html.Div([
                html.I(className="fas fa-exclamation-circle", style={'margin-right': '8px'}),
                f"Erreur lors de la génération du PDF: {response.status_code}"
            ], style={'color': COLORS['danger']})
            
            return error_message, no_update, no_update
            
    except requests.RequestException as e:
        error_message = html.Div([
            html.I(className="fas fa-exclamation-circle", style={'margin-right': '8px'}),
            f"Erreur de connexion au serveur: {str(e)}"
        ], style={'color': COLORS['danger']})
        
        return error_message, no_update, no_update
    except Exception as e:
        error_message = html.Div([
            html.I(className="fas fa-exclamation-circle", style={'margin-right': '8px'}),
            f"Erreur inattendue: {str(e)}"
        ], style={'color': COLORS['danger']})
        
        return error_message, no_update, no_update
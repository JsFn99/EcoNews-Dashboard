# pages/zoom.py
import os
import time

import pandas as pd
import plotly.express as px
import yaml
from dash import Input, Output, State, callback, dcc, html
from styles.styles import card_style

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    
# Load the relevant data from the Excel file (starting from row 24, which is index 23)
file_path = config['paths']['ipc']
try:
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    # Force use of openpyxl engine to avoid xlrd compatibility issues
    df = pd.read_excel(
        file_path,
        sheet_name=0,
        skiprows=23,
        usecols="B:E",
        engine='openpyxl'
    )
    # Rename columns for clarity
    df.columns = ['Mois', 'Alimentation', 'Produits Non Alimentaires', 'Indice Général']
    # Clean up: remove any rows where 'Mois' is NaN (in case of trailing empty rows)
    df = df.dropna(subset=['Mois'])
    
    # Remove rows that contain source information or other non-date text
    # Filter out rows where 'Mois' contains text like "Source", "Enquête", etc.
    df = df[~df['Mois'].astype(str).str.contains('Source|Enquête|Note|Haut Commissariat|HCP', case=False, na=False)]
    
    # Remove rows where numeric columns are NaN (likely header/footer rows)
    df = df.dropna(subset=['Alimentation', 'Produits Non Alimentaires', 'Indice Général'])
    
    # Convert 'Mois' to datetime if it's not already, and sort chronologically
    if not pd.api.types.is_datetime64_any_dtype(df['Mois']):
        # First, try to filter out any remaining non-date entries
        def is_valid_date_string(x):
            """Check if a string could be a valid date"""
            try:
                str_x = str(x).strip()
                # Check if it looks like a date (contains numbers and common date separators)
                if any(char.isdigit() for char in str_x) and len(str_x) > 3:
                    # Try basic date conversion
                    pd.to_datetime(str_x, errors='raise')
                    return True
                return False
            except:
                return False
        
        # Filter to keep only rows with valid date strings
        valid_date_mask = df['Mois'].apply(is_valid_date_string)
        df = df[valid_date_mask]
        
        # Now try to convert to datetime with better error handling
        try:
            df['Mois'] = pd.to_datetime(df['Mois'], errors='coerce')
        except:
            # If direct conversion fails, try common date formats
            try:
                df['Mois'] = pd.to_datetime(df['Mois'], format='%Y-%m', errors='coerce')
            except:
                try:
                    df['Mois'] = pd.to_datetime(df['Mois'], format='%m/%Y', errors='coerce')
                except:
                    try:
                        df['Mois'] = pd.to_datetime(df['Mois'], format='%Y-%m-%d', errors='coerce')
                    except:
                        # Last resort: try to parse each format individually
                        df['Mois'] = pd.to_datetime(df['Mois'], errors='coerce')
        
        # Remove any rows where date conversion failed (NaT values)
        df = df.dropna(subset=['Mois'])
    
    # Sort by date in ascending order (oldest to newest)
    df = df.sort_values('Mois').reset_index(drop=True)
    
    # Melt the dataframe for multi-line plotting
    df_melted = df.melt(id_vars='Mois', var_name='Catégorie', value_name='Indice')
    # Create the line chart with professional styling
    fig = px.line(
        df_melted,
        x='Mois',
        y='Indice',
        color='Catégorie',
        title="Évolution de l'Indice des Prix à la Consommation"
    )
    
    # Enhanced chart styling
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12, color="#2d3436"),
        title=dict(
            font=dict(size=18, color="#2d3436", family="Inter, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            gridcolor='rgba(128,128,128,0.2)',
            showgrid=True,
            zeroline=False,
            # Ensure x-axis shows dates in chronological order
            type='date'
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.2)',
            showgrid=True,
            zeroline=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig.update_traces(line=dict(width=3))
    print("Data loaded successfully!")
except FileNotFoundError as e:
    print(f"File error: {e}")
    # Create empty figure as fallback
    fig = px.line(title="Fichier de données non trouvé")
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install openpyxl: pip install openpyxl")
    # Create empty figure as fallback
    fig = px.line(title="Dépendance manquante - Installer openpyxl")
except Exception as e:
    print(f"Error loading data: {e}")
    # Create empty figure as fallback
    fig = px.line(title="Erreur lors du chargement des données")

# Enhanced styling definitions
enhanced_card_style = {
    'backgroundColor': '#ffffff',
    'padding': '2rem',
    'borderRadius': '12px',
    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    'border': '1px solid #e5e7eb',
    'marginBottom': '2rem',
    'transition': 'all 0.3s ease'
}

button_style_primary = {
    'backgroundColor': '#3b82f6',
    'color': 'white',
    'border': 'none',
    'padding': '12px 24px',
    'fontSize': '14px',
    'fontWeight': '600',
    'borderRadius': '8px',
    'cursor': 'pointer',
    'marginBottom': '1.5rem',
    'fontFamily': 'Inter, sans-serif',
    'transition': 'all 0.2s ease',
    'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    'minWidth': '180px'
}

button_style_success = {
    'backgroundColor': '#10b981',
    'color': 'white',
    'border': 'none',
    'padding': '12px 24px',
    'fontSize': '14px',
    'fontWeight': '600',
    'borderRadius': '8px',
    'cursor': 'pointer',
    'marginBottom': '1.5rem',
    'fontFamily': 'Inter, sans-serif',
    'transition': 'all 0.2s ease',
    'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    'minWidth': '180px'
}

# Page layout with enhanced styling
layout = html.Div([

    
    # Main container with proper spacing
    html.Div([
        # Custom CSS styles
        html.Link(
            rel='stylesheet',
            href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
        ),
        
        # Header section
        html.Div([
            html.H1("Tableau de Bord Économique", style={
                'fontSize': '2.25rem',
                'fontWeight': '800',
                'color': '#1f2937',
                'fontFamily': 'Inter, sans-serif',
                'marginBottom': '1.5rem',
                'textAlign': 'center'
            })
        ]),
        
        # IPC Chart section
        html.Div([
            html.Div([
                html.H2("Indice des Prix à la Consommation", style={
                    'fontSize': '1.5rem',
                    'fontWeight': '700',
                    'color': '#1f2937',
                    'fontFamily': 'Inter, sans-serif',
                    'margin': '0'
                }),
                html.P("Évolution mensuelle des indices par catégorie - Maroc", style={
                    'fontSize': '0.875rem',
                    'color': '#6b7280',
                    'marginTop': '0.25rem',
                    'fontFamily': 'Inter, sans-serif'
                })
            ], style={
                'marginBottom': '1.5rem',
                'paddingBottom': '0.75rem',
                'borderBottom': '2px solid #f3f4f6'
            }),
            dcc.Graph(
                figure=fig,
                style={'height': '500px'},
                config={'displayModeBar': False}
            )
        ], style=enhanced_card_style),
        
        # News Generation sections in a grid
        html.Div([
            # Morning News section
            html.Div([
                html.Div([
                    html.H2("Morning News", style={
                        'fontSize': '1.5rem',
                        'fontWeight': '700',
                        'color': '#1f2937',
                        'fontFamily': 'Inter, sans-serif',
                        'margin': '0'
                    }),
                    html.P("Générez votre rapport matinal personnalisé", style={
                        'fontSize': '0.875rem',
                        'color': '#6b7280',
                        'marginTop': '0.25rem',
                        'fontFamily': 'Inter, sans-serif'
                    })
                ], style={
                    'marginBottom': '1.5rem',
                    'paddingBottom': '0.75rem',
                    'borderBottom': '2px solid #f3f4f6'
                }),
                
                html.Button(
                    [
                        html.Span("", style={'marginRight': '8px'}),
                        "Générer Morning News"
                    ], 
                    id="btn-morning-news", 
                    n_clicks=0,
                    style=button_style_primary
                ),
                html.Div(id="morning-news-content"),
                dcc.Download(id="download-morning-news"),
                dcc.Store(id="morning-news-store")
            ], style={**enhanced_card_style, 'marginRight': '1rem'}, className="col-6"),
            
            # Eco News section
            html.Div([
                html.Div([
                    html.H2("Éco News", style={
                        'fontSize': '1.5rem',
                        'fontWeight': '700',
                        'color': '#1f2937',
                        'fontFamily': 'Inter, sans-serif',
                        'margin': '0'
                    }),
                    html.P("Générez votre rapport économique détaillé", style={
                        'fontSize': '0.875rem',
                        'color': '#6b7280',
                        'marginTop': '0.25rem',
                        'fontFamily': 'Inter, sans-serif'
                    })
                ], style={
                    'marginBottom': '1.5rem',
                    'paddingBottom': '0.75rem',
                    'borderBottom': '2px solid #f3f4f6'
                }),
                
                html.Button(
                    [
                        html.Span("", style={'marginRight': '8px'}),
                        "Générer Éco News"
                    ], 
                    id="btn-eco-news", 
                    n_clicks=0,
                    style=button_style_success
                ),
                html.Div(id="eco-news-content"),
                dcc.Download(id="download-eco-news"),
                dcc.Store(id="eco-news-store")
            ], style={**enhanced_card_style, 'marginLeft': '1rem'}, className="col-6")
        ], style={
            'display': 'flex',
            'gap': '0',
            'marginBottom': '2rem'
        }),
        
        # Interval component for loading simulation
        dcc.Interval(
            id='loading-interval',
            interval=100,  # Update every 100ms
            n_intervals=0,
            disabled=True
        )
    ], style={
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': '2rem 1rem',
        'paddingTop': '2rem',  # Add top padding to separate from navbar
        'minHeight': 'calc(100vh - 200px)'  # Ensure proper spacing from footer
    })
])

# Enhanced Morning News callback
@callback(
    [Output("morning-news-content", "children"),
     Output("loading-interval", "disabled"),
     Output("morning-news-store", "data"),
     Output("download-morning-news", "data")],
    [Input("btn-morning-news", "n_clicks"),
     Input("loading-interval", "n_intervals")],
    [State("morning-news-store", "data")]
)
def generate_morning_news(n_clicks, n_intervals, store_data):
    if n_clicks == 0:
        return "", True, {}, None
    
    # Initialize store data if needed
    if not store_data:
        store_data = {"start_time": None, "loading": False}
    
    # Start loading process
    if n_clicks > 0 and not store_data.get("loading"):
        store_data = {"start_time": time.time(), "loading": True}
        loading_content = html.Div([
            html.Div(className="spinner", style={
                'border': '4px solid #f3f4f6',
                'borderTop': '4px solid #3b82f6',
                'borderRadius': '50%',
                'width': '40px',
                'height': '40px',
                'animation': 'spin 1s linear infinite',
                'margin': '0 auto 16px auto'
            }),
            html.H4("Génération en cours...", style={
                'color': '#374151',
                'fontSize': '1.125rem',
                'fontWeight': '600',
                'marginBottom': '0.5rem',
                'fontFamily': 'Inter, sans-serif'
            }),
            html.P("Collecte et analyse des dernières actualités", style={
                'color': '#6b7280',
                'fontSize': '0.875rem',
                'fontFamily': 'Inter, sans-serif'
            })
                    ], style={
                'padding': '2rem',
                'textAlign': 'center',
                'background': 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0'
            })
        return loading_content, False, store_data, None
    
    # Check if loading is complete (5 seconds)
    if store_data.get("loading") and store_data.get("start_time"):
        elapsed_time = time.time() - store_data["start_time"]
        if elapsed_time >= 5:
            pdf_file_path = "/Users/mac/Sentiment Analysis Press/morning_news_final.pdf"
            
            success_content = html.Div([
                html.Div("", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                html.H4("Morning News généré avec succès!", style={
                    'color': '#065f46',
                    'fontSize': '1.125rem',
                    'fontWeight': '600',
                    'marginBottom': '0.5rem',
                    'fontFamily': 'Inter, sans-serif'
                }),
                html.P("Le fichier PDF a été téléchargé automatiquement", style={
                    'color': '#047857',
                    'fontSize': '0.875rem',
                    'fontFamily': 'Inter, sans-serif'
                })
            ], style={
                'padding': '1rem 1.5rem',
                'backgroundColor': '#ecfdf5',
                'border': '1px solid #a7f3d0',
                'borderRadius': '8px',
                'color': '#065f46',
                'fontWeight': '500',
                'textAlign': 'center',
                'fontFamily': 'Inter, sans-serif'
            })
            
            download_data = dcc.send_file(pdf_file_path)
            return success_content, True, {"loading": False}, download_data
        
        # Still loading with enhanced progress bar
        progress = (elapsed_time / 5) * 100
        loading_content = html.Div([
            html.Div(className="spinner", style={
                'border': '4px solid #f3f4f6',
                'borderTop': '4px solid #3b82f6',
                'borderRadius': '50%',
                'width': '40px',
                'height': '40px',
                'animation': 'spin 1s linear infinite',
                'margin': '0 auto 16px auto'
            }),
            html.H4("Génération en cours...", style={
                'color': '#374151',
                'fontSize': '1.125rem',
                'fontWeight': '600',
                'marginBottom': '0.5rem',
                'fontFamily': 'Inter, sans-serif'
            }),
            html.P(f"Progression: {progress:.0f}%", style={
                'color': '#6b7280',
                'fontSize': '0.875rem',
                'fontFamily': 'Inter, sans-serif',
                'marginBottom': '1rem'
            }),
            html.Div([
                html.Div(style={
                    'width': f'{progress}%',
                    'height': '8px',
                    'background': 'linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%)',
                    'borderRadius': '10px',
                    'transition': 'width 0.3s ease'
                })
            ], style={
                'width': '100%',
                'backgroundColor': '#f3f4f6',
                'borderRadius': '10px',
                'margin': '16px 0',
                'overflow': 'hidden'
            })
        ], style={
            'padding': '2rem',
            'textAlign': 'center',
            'background': 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
            'borderRadius': '12px',
            'border': '1px solid #e2e8f0'
        })
        return loading_content, False, store_data, None
    
    return "", True, {}, None

# Enhanced Eco News callback
@callback(
    [Output("eco-news-content", "children"),
     Output("eco-news-store", "data"),
     Output("download-eco-news", "data")],
    [Input("btn-eco-news", "n_clicks"),
     Input("loading-interval", "n_intervals")],
    [State("eco-news-store", "data")]
)
def generate_eco_news(n_clicks, n_intervals, store_data):
    if n_clicks == 0:
        return "", {}, None
    
    # Initialize store data if needed
    if not store_data:
        store_data = {"start_time": None, "loading": False}
    
    # Start loading process
    if n_clicks > 0 and not store_data.get("loading"):
        store_data = {"start_time": time.time(), "loading": True}
        loading_content = html.Div([
            html.Div(style={
                'border': '4px solid #f3f4f6',
                'borderTop': '4px solid #10b981',
                'borderRadius': '50%',
                'width': '40px',
                'height': '40px',
                'animation': 'spin 1s linear infinite',
                'margin': '0 auto 16px auto'
            }),
            html.H4("Génération en cours...", style={
                'color': '#374151',
                'fontSize': '1.125rem',
                'fontWeight': '600',
                'marginBottom': '0.5rem',
                'fontFamily': 'Inter, sans-serif'
            }),
            html.P("Analyse des données économiques", style={
                'color': '#6b7280',
                'fontSize': '0.875rem',
                'fontFamily': 'Inter, sans-serif'
            })
        ], style={
            'padding': '2rem',
            'textAlign': 'center',
            'background': 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
            'borderRadius': '12px',
            'border': '1px solid #e2e8f0'
        })
        return loading_content, store_data, None
    
    # Check if loading is complete (5 seconds)
    if store_data.get("loading") and store_data.get("start_time"):
        elapsed_time = time.time() - store_data["start_time"]
        if elapsed_time >= 5:
            pdf_file_path = "/Users/mac/Sentiment Analysis Press/eco_news_report.pdf"
            
            success_content = html.Div([
                html.Div("", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                html.H4("Éco News généré avec succès!", style={
                    'color': '#065f46',
                    'fontSize': '1.125rem',
                    'fontWeight': '600',
                    'marginBottom': '0.5rem',
                    'fontFamily': 'Inter, sans-serif'
                }),
                html.P("Le fichier PDF a été téléchargé automatiquement", style={
                    'color': '#047857',
                    'fontSize': '0.875rem',
                    'fontFamily': 'Inter, sans-serif'
                })
            ], style={
                'padding': '1rem 1.5rem',
                'backgroundColor': '#ecfdf5',
                'border': '1px solid #a7f3d0',
                'borderRadius': '8px',
                'color': '#065f46',
                'fontWeight': '500',
                'textAlign': 'center',
                'fontFamily': 'Inter, sans-serif'
            })
            
            download_data = dcc.send_file(pdf_file_path)
            return success_content, {"loading": False}, download_data
        
        # Still loading with enhanced progress bar
        progress = (elapsed_time / 5) * 100
        loading_content = html.Div([
            html.Div(style={
                'border': '4px solid #f3f4f6',
                'borderTop': '4px solid #10b981',
                'borderRadius': '50%',
                'width': '40px',
                'height': '40px',
                'animation': 'spin 1s linear infinite',
                'margin': '0 auto 16px auto'
            }),
            html.H4("Génération en cours...", style={
                'color': '#374151',
                'fontSize': '1.125rem',
                'fontWeight': '600',
                'marginBottom': '0.5rem',
                'fontFamily': 'Inter, sans-serif'
            }),
            html.P(f"Progression: {progress:.0f}%", style={
                'color': '#6b7280',
                'fontSize': '0.875rem',
                'fontFamily': 'Inter, sans-serif',
                'marginBottom': '1rem'
            }),
            html.Div([
                html.Div(style={
                    'width': f'{progress}%',
                    'height': '8px',
                    'background': 'linear-gradient(90deg, #10b981 0%, #047857 100%)',
                    'borderRadius': '10px',
                    'transition': 'width 0.3s ease'
                })
            ], style={
                'width': '100%',
                'backgroundColor': '#f3f4f6',
                'borderRadius': '10px',
                'margin': '16px 0',
                'overflow': 'hidden'
            })
        ], className="loading-container")
        return loading_content, store_data, None
    
    return "", {}, None
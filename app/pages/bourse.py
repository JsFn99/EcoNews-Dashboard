# pages/bourse.py
import io
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yaml
from dash import Input, Output, callback, dash_table, dcc, html
from plotly.subplots import make_subplots

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

# Load config with error handling
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    print("Warning: config.yaml not found, using default configuration")
    config = {}

def debug_number_conversion():
    """Debug function to test number conversion"""
    test_values = ['37,84', '1 390,00', '1390,00', '37.84', '1390.00']
    
    for val in test_values:
        print(f"Testing '{val}':")
        
        # Step by step conversion
        step1 = str(val).strip()
        print(f"  After strip: '{step1}'")
        
        step2 = step1.replace(' ', '')
        print(f"  After remove spaces: '{step2}'")
        
        step3 = step2.replace(',', '.')
        print(f"  After comma to dot: '{step3}'")
        
        try:
            final = float(step3)
            print(f"  Final number: {final}")
        except:
            print(f"  ERROR converting to float")
        
        print("---")

# Call this function to debug
# debug_number_conversion()

def parse_date(date_str):
    """Parse date string in various formats"""
    try:
        # Try common formats
        for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except ValueError:
                continue
        # If none work, let pandas try to infer
        return pd.to_datetime(date_str, dayfirst=True)
    except:
        return pd.NaT

def load_and_process_data():
    """Charge et traite les données des fichiers CSV historiques"""
    
    try:
        # Load historical stock data
        historical_data = pd.read_csv('/Users/mac/Sentiment Analysis Press/stocks/Historical_Stock_Data.csv')
        
        # Clean and parse dates
        historical_data['Date'] = historical_data['Date'].apply(parse_date)
        historical_data = historical_data.dropna(subset=['Date'])
        historical_data = historical_data.sort_values(['Date', 'Valeur'])
        
        print(f"Loaded {len(historical_data)} historical records")
        
    except FileNotFoundError:
        print("Warning: Historical_Stock_Data.csv not found, creating sample data")
        # Create sample historical data
        dates = pd.date_range(start='2024-01-01', end='2024-07-25', freq='D')
        stocks = ['ADDOHA', 'AFMA', 'ATTIJARIWAFA BANK', 'BCP', 'ITISSALAT AL-MAGHRIB']
        
        historical_data = []
        for date in dates:
            for stock in stocks:
                base_price = np.random.uniform(100, 500)
                historical_data.append({
                    'Date': date,
                    'Valeur': stock,
                    'VMC': np.random.uniform(1000000, 50000000),
                    'QE': np.random.uniform(1000, 100000),
                    'CCA': base_price * (1 + np.random.normal(0, 0.02)),
                    'CCV': base_price
                })
        
        historical_data = pd.DataFrame(historical_data)
    
    try:
        # Load current indices data
        indices_data = pd.read_csv('/Users/mac/Sentiment Analysis Press/stock_indices_data_28_07_2025.csv')
        
        # Parse the date if it exists
        if 'Date' in indices_data.columns:
            indices_data['Date'] = indices_data['Date'].apply(parse_date)
        else:
            indices_data['Date'] = pd.Timestamp.now().date()
            
        print(f"Loaded {len(indices_data)} current indices records")
        
    except FileNotFoundError:
        print("Warning: stock_data_25_07_2025.csv not found, creating sample data")
        indices_data = pd.DataFrame({
            'Date': [pd.Timestamp.now().date()] * 6,
            'Indice': ['MASI', 'MASI 20', 'MASI ESG', 'MASI Mid and Small Cap', 
                      'MASI AGROALIMENTAIRE / PRODUCTION', 'MASI ASSURANCES'],
            'CCA': [19342.41, 1589.20, 1332.79, 1845.82, 37593.45, 6349.56],
            'CCV': [19266.33, 1583.50, 1329.27, 1823.32, 37593.45, 6349.56]
        })
    
    # Clean numeric columns for historical data
    def clean_numeric_columns(df, columns):
        for col in columns:
            if col in df.columns:
                # Handle European number format (space as thousands separator, comma as decimal)
                df[col] = df[col].astype(str)
                
                # Remove any leading/trailing whitespace
                df[col] = df[col].str.strip()
                
                # Handle empty strings and NaN
                df[col] = df[col].replace('', '0')
                df[col] = df[col].replace('nan', '0')
                df[col] = df[col].replace('NaN', '0')
                
                # Convert European format: "1 390,84" -> "1390.84"
                # First remove spaces (thousands separator)
                df[col] = df[col].str.replace(' ', '')
                
                # Then replace comma with dot (decimal separator)  
                df[col] = df[col].str.replace(',', '.')
                
                # Convert to numeric, coerce errors to NaN, then fill NaN with 0
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        return df
    
    # Clean historical data
    historical_data = clean_numeric_columns(historical_data, ['VMC', 'QE', 'CCA', 'CCV'])
    
    # Clean indices data
    indices_data = clean_numeric_columns(indices_data, ['CCA', 'CCV'])
    
    return historical_data, indices_data

def calculate_performance_metrics(df, period='daily'):
    """Calculate performance metrics for the selected period"""
    
    if df.empty:
        return df
    
    # Ensure Date column is datetime
    df = df.copy()
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    
    # Group by stock/indice name for calculations
    name_col = 'Valeur' if 'Valeur' in df.columns else 'Indice'
    
    result_data = []
    
    for name in df[name_col].unique():
        stock_data = df[df[name_col] == name].sort_values('Date')
        
        if len(stock_data) == 0:
            continue
            
        # Get the most recent data point
        latest = stock_data.iloc[-1].copy()
        
        # Calculate daily performance (most recent vs previous day)
        if len(stock_data) >= 2:
            previous = stock_data.iloc[-2]
            daily_perf = ((latest['CCA'] / previous['CCA']) - 1) * 100 if previous['CCA'] != 0 else 0
        else:
            daily_perf = ((latest['CCA'] / latest['CCV']) - 1) * 100 if latest['CCV'] != 0 else 0
        
        latest['Performance_Quotidienne'] = daily_perf
        
        # Calculate period-specific performance
        if period == 'weekly':
            # Performance over last 7 days
            week_ago = latest['Date'] - timedelta(days=7)
            week_data = stock_data[stock_data['Date'] >= week_ago].sort_values('Date')
            if len(week_data) >= 2:
                oldest_in_period = week_data.iloc[0]
                period_perf = ((latest['CCA'] / oldest_in_period['CCA']) - 1) * 100 if oldest_in_period['CCA'] != 0 else 0
                print(f"Weekly calc for {name}: {latest['CCA']} vs {oldest_in_period['CCA']} = {period_perf:.2f}%")
            else:
                period_perf = daily_perf
                
        elif period == 'monthly':
            # Performance over last 30 days
            month_ago = latest['Date'] - timedelta(days=30)
            month_data = stock_data[stock_data['Date'] >= month_ago].sort_values('Date')
            if len(month_data) >= 2:
                oldest_in_period = month_data.iloc[0]
                period_perf = ((latest['CCA'] / oldest_in_period['CCA']) - 1) * 100 if oldest_in_period['CCA'] != 0 else 0
                print(f"Monthly calc for {name}: {latest['CCA']} vs {oldest_in_period['CCA']} = {period_perf:.2f}%")
            else:
                period_perf = daily_perf
        else:  # daily
            period_perf = daily_perf
        
        latest['Performance_Periode'] = period_perf
        
        # Calculate YTD performance (from January 1st of current year)
        current_year = latest['Date'].year
        year_start = pd.Timestamp(f'{current_year}-01-01')
        ytd_data = stock_data[stock_data['Date'] >= year_start]
        
        if len(ytd_data) >= 2:
            year_start_price = ytd_data.iloc[0]['CCA']
            ytd_perf = ((latest['CCA'] / year_start_price) - 1) * 100 if year_start_price != 0 else 0
        else:
            ytd_perf = 0
            
        latest['Performance_YTD'] = ytd_perf
        
        # Calculate YoY performance (same date last year)
        last_year_date = latest['Date'] - timedelta(days=365)
        yoy_data = stock_data[stock_data['Date'] <= last_year_date]
        
        if len(yoy_data) > 0:
            last_year_price = yoy_data.iloc[-1]['CCA']  # Closest date to last year
            yoy_perf = ((latest['CCA'] / last_year_price) - 1) * 100 if last_year_price != 0 else 0
        else:
            yoy_perf = 0
            
        latest['Performance_YoY'] = yoy_perf
        
        # Calculate additional metrics for stocks
        if 'VMC' in latest.index:
            # Volume and liquidity metrics
            period_data = stock_data.tail(min(30, len(stock_data)))  # Last 30 days or available data
            
            latest['Volume_MC_Global'] = period_data['VMC'].sum()
            latest['Quantite_Echangee_Global'] = period_data['QE'].sum()
            latest['Volume_Moyen_Quotidien'] = period_data['VMC'].mean()
            
            # Price metrics
            latest['Cours_Moyen_Pondere'] = (
                period_data['VMC'].sum() / period_data['QE'].sum() 
                if period_data['QE'].sum() != 0 else latest['CCA']
            )
            latest['Maximum_Cloture'] = period_data['CCA'].max()
            latest['Minimum_Cloture'] = period_data['CCA'].min()
        else:
            # For indices, set basic metrics
            latest['Maximum_Cloture'] = latest['CCA']
            latest['Minimum_Cloture'] = latest['CCA']
        
        result_data.append(latest)
    
    if result_data:
        result_df = pd.DataFrame(result_data)
        return result_df.reset_index(drop=True)
    else:
        return pd.DataFrame()

# Load and process data
historical_data, indices_data = load_and_process_data()

# Create processed datasets for different data types
def get_processed_data(data_type, period='daily'):
    """Get processed data based on type and period"""
    
    if data_type == 'stocks':
        # Use historical stock data
        df = historical_data.copy()
        return calculate_performance_metrics(df, period)
        
    elif data_type == 'indices_general':
        # Filter for general indices
        general_indices = ['MASI', 'MASI 20', 'MASI ESG', 'MASI Mid and Small Cap', 
                          'FTSE CSE Morocco 15 Index', 'FTSE CSE Morocco All-Liquid']
        df = indices_data[indices_data['Indice'].isin(general_indices)].copy()
        return calculate_performance_metrics(df, period)
        
    elif data_type == 'indices_sectorial':
        # Filter for sectorial indices
        general_indices = ['MASI', 'MASI 20', 'MASI ESG', 'MASI Mid and Small Cap', 
                          'FTSE CSE Morocco 15 Index', 'FTSE CSE Morocco All-Liquid']
        df = indices_data[~indices_data['Indice'].isin(general_indices)].copy()
        return calculate_performance_metrics(df, period)
    
    return pd.DataFrame()

# Functions for creating tab content (keeping the same structure but using processed data)
def create_overview_tab(df, data_type, period='daily'):
    if df.empty:
        return html.Div([
            html.H3("Vue d'ensemble", style={'color': '#2c3e50'}),
            html.P("Aucune donnée disponible pour la sélection actuelle.", 
                   style={'textAlign': 'center', 'fontSize': 18, 'color': '#7f8c8d'})
        ])
    
    if data_type == 'stocks':
        columns_to_show = ['Valeur', 'CCA', 'CCV', 'Performance_Quotidienne', 'Performance_Periode', 'VMC', 'QE']
        column_names = ['Valeur', 'Cours Actuel', 'Cours Veille', 'Perf. Quotidienne (%)', f'Perf. {period.title()} (%)', 'Volume MC', 'Quantité Échangée']
    else:
        columns_to_show = ['Indice', 'CCA', 'CCV', 'Performance_Quotidienne', 'Performance_Periode']
        column_names = ['Indice', 'Cours Actuel', 'Cours Veille', 'Perf. Quotidienne (%)', f'Perf. {period.title()} (%)']
    
    # Check which columns actually exist
    existing_columns = [col for col in columns_to_show if col in df.columns]
    existing_names = [column_names[i] for i, col in enumerate(columns_to_show) if col in df.columns]
    
    # Formatage des données pour l'affichage
    display_df = df[existing_columns].copy()
    display_df.columns = existing_names
    
    # Formatage des nombres
    for col in display_df.columns:
        if 'Perf' in col:
            display_df[col] = display_df[col].round(2)
        elif col in ['Cours Actuel', 'Cours Veille', 'Volume MC']:
            display_df[col] = display_df[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) and x != 0 else "N/A")
    
    return html.Div([
        html.H3("Vue d'ensemble", style={'color': '#2c3e50'}),
        
        # Statistiques résumées
        html.Div([
            html.Div([
                html.H4(f"{len(df)}", style={'margin': 0, 'color': '#3498db'}),
                html.P("Total éléments", style={'margin': 0})
            ], className='stat-box', style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
                                           'borderRadius': 10, 'margin': 10, 'flex': 1}),
            
            html.Div([
                html.H4(f"{df['Performance_Periode'].mean():.2f}%", style={'margin': 0, 'color': '#27ae60'}),
                html.P(f"Perf. moy. {period}", style={'margin': 0})
            ], className='stat-box', style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
                                           'borderRadius': 10, 'margin': 10, 'flex': 1}),
            
            html.Div([
                html.H4(f"{len(df[df['Performance_Periode'] > 0])}", style={'margin': 0, 'color': '#27ae60'}),
                html.P("En hausse", style={'margin': 0})
            ], className='stat-box', style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
                                           'borderRadius': 10, 'margin': 10, 'flex': 1}),
            
            html.Div([
                html.H4(f"{len(df[df['Performance_Periode'] < 0])}", style={'margin': 0, 'color': '#e74c3c'}),
                html.P("En baisse", style={'margin': 0})
            ], className='stat-box', style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
                                           'borderRadius': 10, 'margin': 10, 'flex': 1})
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': 30}),
        
        # Tableau des données
        dash_table.DataTable(
            data=display_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in display_df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '10px'},
            style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8f9fa'
                }
            ],
            sort_action="native",
            filter_action="native",
            page_size=20
        )
    ])

def create_performance_tab(df, data_type, period='daily'):
    if df.empty:
        return html.Div([
            html.H3("Analyse des Performances", style={'color': '#2c3e50'}),
            html.P("Aucune donnée disponible pour l'analyse des performances.", 
                   style={'textAlign': 'center', 'fontSize': 18, 'color': '#7f8c8d'})
        ])
    
    # Graphique des performances
    fig = go.Figure()
    
    name_col = 'Valeur' if data_type == 'stocks' else 'Indice'
    
    # Limit to top 20 for better readability
    df_plot = df.head(20)
    
    fig.add_trace(go.Bar(
        x=df_plot[name_col],
        y=df_plot['Performance_Periode'],
        name=f'Performance {period.title()}',
        marker_color=['#27ae60' if x >= 0 else '#e74c3c' for x in df_plot['Performance_Periode']]
    ))
    
    fig.update_layout(
        title=f"Performances {period.title()} (Top 20)",
        xaxis_title="Valeurs" if data_type == 'stocks' else "Indices",
        yaxis_title="Performance (%)",
        showlegend=False,
        height=500,
        xaxis_tickangle=-45
    )
    
    # Graphique YTD vs YoY (if data exists)
    fig2 = go.Figure()
    
    if 'Performance_YTD' in df.columns and 'Performance_YoY' in df.columns:
        fig2.add_trace(go.Scatter(
            x=df['Performance_YTD'],
            y=df['Performance_YoY'],
            mode='markers',
            text=df[name_col],
            marker=dict(size=10, color=df['Performance_Periode'], colorscale='RdYlGn', showscale=True)
        ))
        
        fig2.update_layout(
            title="Performance YTD vs YoY",
            xaxis_title="Performance YTD (%)",
            yaxis_title="Performance YoY (%)",
            height=500
        )
    
    performance_columns = [name_col, 'Performance_Quotidienne', 'Performance_Periode']
    performance_names = ["Valeur" if data_type == 'stocks' else "Indice", "Perf. Quotidienne (%)", f"Perf. {period.title()} (%)"]
    
    # Add other performance columns if they exist
    if 'Performance_YTD' in df.columns:
        performance_columns.append('Performance_YTD')
        performance_names.append("Perf. YTD (%)")
    if 'Performance_YoY' in df.columns:
        performance_columns.append('Performance_YoY')
        performance_names.append("Perf. YoY (%)")
    
    return html.Div([
        html.H3("Analyse des Performances", style={'color': '#2c3e50'}),
        
        dcc.Graph(figure=fig),
        dcc.Graph(figure=fig2) if 'Performance_YTD' in df.columns else html.Div(),
        
        # Tableau des performances
        html.H4("Détail des Performances", style={'marginTop': 30}),
        dash_table.DataTable(
            data=df[performance_columns].round(2).to_dict('records'),
            columns=[{"name": performance_names[i], "id": col} 
                    for i, col in enumerate(performance_columns)],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '10px'},
            style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
            sort_action="native",
            filter_action="native",
            page_size=15
        )
    ])

def create_liquidity_tab(df, data_type, period='daily'):
    if data_type != 'stocks':
        return html.Div([
            html.H3("Analyse de Liquidité", style={'color': '#2c3e50'}),
            html.P("Les indicateurs de liquidité ne sont disponibles que pour les valeurs cotées.", 
                   style={'textAlign': 'center', 'fontSize': 18, 'color': '#7f8c8d'})
        ])
    
    if df.empty or 'VMC' not in df.columns:
        return html.Div([
            html.H3("Analyse de Liquidité", style={'color': '#2c3e50'}),
            html.P("Données de liquidité non disponibles.", 
                   style={'textAlign': 'center', 'fontSize': 18, 'color': '#7f8c8d'})
        ])
    
    # Graphiques de liquidité
    df_top20 = df.nlargest(20, 'VMC')
    fig1 = px.bar(df_top20, x='Valeur', y='VMC', title="Volume de Marché (Top 20)")
    fig1.update_layout(height=400, xaxis_tickangle=-45)
    
    fig2 = px.scatter(df.head(50), x='VMC', y='QE', text='Valeur', 
                     title="Volume vs Quantité Échangée (Top 50)")
    fig2.update_traces(textposition="top center")
    fig2.update_layout(height=500)
    
    return html.Div([
        html.H3("Analyse de Liquidité", style={'color': '#2c3e50'}),
        
        # Statistiques de liquidité
        html.Div([
            html.Div([
                html.H4(f"{df['VMC'].sum():,.0f}", style={'margin': 0, 'color': '#3498db'}),
                html.P("Volume Total MC", style={'margin': 0})
            ], style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
                     'borderRadius': 10, 'margin': 10, 'flex': 1}),
            
            html.Div([
                html.H4(f"{df['QE'].sum():,.0f}", style={'margin': 0, 'color': '#9b59b6'}),
                html.P("Quantité Totale Échangée", style={'margin': 0})
            ], style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
                     'borderRadius': 10, 'margin': 10, 'flex': 1}),
            
            html.Div([
                html.H4(f"{df['VMC'].mean():,.0f}", style={'margin': 0, 'color': '#f39c12'}),
                html.P("Volume Moyen MC", style={'margin': 0})
            ], style={'textAlign': 'center', 'padding': 20, 'backgroundColor': '#ecf0f1', 
                     'borderRadius': 10, 'margin': 10, 'flex': 1})
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': 30}),
        
        dcc.Graph(figure=fig1),
        dcc.Graph(figure=fig2)
    ])

def create_comparison_tab(df, data_type, period='daily'):
    if df.empty:
        return html.Div([
            html.H3("Comparaison Multi-Actifs", style={'color': '#2c3e50'}),
            html.P("Aucune donnée disponible pour la comparaison.", 
                   style={'textAlign': 'center', 'fontSize': 18, 'color': '#7f8c8d'})
        ])
    
    # Graphique de comparaison multi-actifs
    fig = go.Figure()
    
    name_col = 'Valeur' if data_type == 'stocks' else 'Indice'
    
    # Sélection des top performers pour la comparaison
    top_performers = df.nlargest(10, 'Performance_Periode')
    bottom_performers = df.nsmallest(10, 'Performance_Periode')
    
    fig.add_trace(go.Bar(
        x=top_performers[name_col],
        y=top_performers['Performance_Periode'],
        name='Top Performers',
        marker_color='#27ae60'
    ))
    
    fig.add_trace(go.Bar(
        x=bottom_performers[name_col],
        y=bottom_performers['Performance_Periode'],
        name='Bottom Performers',
        marker_color='#e74c3c'
    ))
    
    fig.update_layout(
        title=f"Comparaison des Performances {period.title()} - Top vs Bottom",
        xaxis_title="Valeurs" if data_type == 'stocks' else "Indices",
        yaxis_title="Performance (%)",
        height=600,
        xaxis_tickangle=-45
    )
    
    # Création du graphique de comparaison personnalisée avec les 5 premiers éléments
    selected_items = list(df[name_col].head(5))
    custom_fig = create_custom_comparison_figure(df, selected_items, data_type)
    
    return html.Div([
        html.H3("Comparaison Multi-Actifs", style={'color': '#2c3e50'}),
        
        dcc.Graph(figure=fig),
        
        # Sélecteur pour comparaison personnalisée
        html.Div([
            html.Label("Sélectionner les éléments à comparer:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='comparison-selector',
                options=[{'label': row[name_col], 'value': row[name_col]} 
                        for _, row in df.iterrows()],
                multi=True,
                value=selected_items,
                style={'marginTop': 10, 'marginBottom': 20}
            ),
            
            dcc.Graph(id='custom-comparison-chart', figure=custom_fig)
        ])
    ])

def create_custom_comparison_figure(df, selected_items, data_type):
    """Fonction utilitaire pour créer le graphique de comparaison personnalisée"""
    if not selected_items or df.empty:
        return go.Figure()
    
    name_col = 'Valeur' if data_type == 'stocks' else 'Indice'
    filtered_df = df[df[name_col].isin(selected_items)]
    
    if filtered_df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    # Performance quotidienne
    fig.add_trace(go.Bar(
        x=filtered_df[name_col],
        y=filtered_df['Performance_Periode'],
        name=f'Performance {data_type}',
        yaxis='y1'
    ))
    
    # Performance YTD (if available)
    if 'Performance_YTD' in filtered_df.columns:
        fig.add_trace(go.Scatter(
            x=filtered_df[name_col],
            y=filtered_df['Performance_YTD'],
            mode='lines+markers',
            name='Performance YTD',
            yaxis='y2',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            yaxis2=dict(title="Performance YTD (%)", side="right", overlaying="y")
        )
    
    fig.update_layout(
        title="Comparaison Personnalisée",
        xaxis_title="Sélection",
        yaxis=dict(title="Performance Période (%)", side="left"),
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig

# Layout de l'application
layout = html.Div([
    html.H1("Dashboard Bourse de Casablanca", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    # Contrôles
    html.Div([
        html.Div([
            html.Label("Type de données:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='data-type-dropdown',
                options=[
                    {'label': 'Valeurs Cotées', 'value': 'stocks'},
                    {'label': 'Indices Généraux', 'value': 'indices_general'},
                    {'label': 'Indices Sectoriels', 'value': 'indices_sectorial'}
                ],
                value='stocks',
                style={'marginTop': 5}
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': 20}),
        
        html.Div([
            html.Label("Filtre par secteur/indice:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='sector-filter',
                multi=True,
                style={'marginTop': 5}
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': 20}),
        
        html.Div([
            html.Label("Période:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='period-dropdown',
                options=[
                    {'label': 'Journalière', 'value': 'daily'},
                    {'label': 'Hebdomadaire', 'value': 'weekly'},
                    {'label': 'Mensuelle', 'value': 'monthly'}
                ],
                value='daily',
                style={'marginTop': 5}
            )
        ], style={'width': '30%', 'display': 'inline-block'})
    ], style={'marginBottom': 30, 'padding': 20, 'backgroundColor': '#f8f9fa', 'borderRadius': 10}),
    
    # Boutons d'export
    html.Div([
        html.Button('Exporter vers Excel', id='export-btn', 
                   style={'backgroundColor': '#27ae60', 'color': 'white', 'border': 'none', 
                         'padding': '10px 20px', 'borderRadius': 5, 'cursor': 'pointer'})
    ], style={'textAlign': 'center', 'marginBottom': 20}),
    
    # Onglets
    dcc.Tabs(id="tabs", value='tab-overview', children=[
        dcc.Tab(label='Vue d\'ensemble', value='tab-overview'),
        dcc.Tab(label='Performances', value='tab-performance'),
        dcc.Tab(label='Liquidité', value='tab-liquidity'),
        dcc.Tab(label='Comparaison', value='tab-comparison')
    ]),
    
    # Contenu des onglets
    html.Div(id='tab-content'),
    
    # Download component pour l'export
    dcc.Download(id="download-data")
])

# Callbacks
@callback(
    Output('sector-filter', 'options'),
    Input('data-type-dropdown', 'value')
)
def update_sector_filter(data_type):
    """Update sector filter options based on data type"""
    if data_type == 'stocks':
        # Get unique stock names from historical data
        unique_stocks = historical_data['Valeur'].unique() if not historical_data.empty else []
        return [{'label': stock, 'value': stock} for stock in sorted(unique_stocks)]
        
    elif data_type == 'indices_general':
        general_indices = ['MASI', 'MASI 20', 'MASI ESG', 'MASI Mid and Small Cap', 
                          'FTSE CSE Morocco 15 Index', 'FTSE CSE Morocco All-Liquid']
        available_indices = indices_data[indices_data['Indice'].isin(general_indices)]['Indice'].unique() if not indices_data.empty else []
        return [{'label': idx, 'value': idx} for idx in sorted(available_indices)]
        
    elif data_type == 'indices_sectorial':
        general_indices = ['MASI', 'MASI 20', 'MASI ESG', 'MASI Mid and Small Cap', 
                          'FTSE CSE Morocco 15 Index', 'FTSE CSE Morocco All-Liquid']
        available_indices = indices_data[~indices_data['Indice'].isin(general_indices)]['Indice'].unique() if not indices_data.empty else []
        return [{'label': idx, 'value': idx} for idx in sorted(available_indices)]
    
    return []

@callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'value'),
     Input('data-type-dropdown', 'value'),
     Input('sector-filter', 'value'),
     Input('period-dropdown', 'value')]
)
def update_tab_content(active_tab, data_type, selected_sectors, period):
    """Update tab content based on selections"""
    
    # Get processed data for the selected type and period
    df = get_processed_data(data_type, period)
    
    # Apply sector/stock filter if selected
    if selected_sectors and not df.empty:
        name_col = 'Valeur' if data_type == 'stocks' else 'Indice'
        if name_col in df.columns:
            df = df[df[name_col].isin(selected_sectors)]
    
    # Return appropriate tab content
    if active_tab == 'tab-overview':
        return create_overview_tab(df, data_type)
    elif active_tab == 'tab-performance':
        return create_performance_tab(df, data_type)
    elif active_tab == 'tab-liquidity':
        return create_liquidity_tab(df, data_type)
    elif active_tab == 'tab-comparison':
        return create_comparison_tab(df, data_type)
    
    return html.Div("Sélectionnez un onglet")

@callback(
    Output('custom-comparison-chart', 'figure'),
    [Input('comparison-selector', 'value'),
     Input('data-type-dropdown', 'value'),
     Input('sector-filter', 'value'),
     Input('period-dropdown', 'value')]
)
def update_custom_comparison(selected_items, data_type, selected_sectors, period):
    """Update custom comparison chart"""
    if not selected_items:
        return go.Figure()
    
    # Get processed data
    df = get_processed_data(data_type, period)
    
    # Apply sector filter if selected
    if selected_sectors and not df.empty:
        name_col = 'Valeur' if data_type == 'stocks' else 'Indice'
        if name_col in df.columns:
            df = df[df[name_col].isin(selected_sectors)]
    
    return create_custom_comparison_figure(df, selected_items, data_type)

@callback(
    Output("download-data", "data"),
    [Input("export-btn", "n_clicks"),
     Input('data-type-dropdown', 'value'),
     Input('period-dropdown', 'value')],
    prevent_initial_call=True,
)
def export_to_excel(n_clicks, data_type, period):
    """Export data to Excel"""
    if n_clicks:
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Export stock data
            stock_df = get_processed_data('stocks', period)
            if not stock_df.empty:
                export_columns = ['Valeur', 'Date', 'CCA', 'CCV', 'Performance_Quotidienne', 
                                'Performance_YTD', 'Performance_YoY', 'VMC', 'QE']
                # Only include columns that exist
                existing_cols = [col for col in export_columns if col in stock_df.columns]
                stock_df[existing_cols].to_excel(writer, sheet_name='Valeurs_Cotees', index=False)
            
            # Export indices data
            indices_general_df = get_processed_data('indices_general', period)
            if not indices_general_df.empty:
                export_columns = ['Indice', 'Date', 'CCA', 'CCV', 'Performance_Quotidienne',
                                'Performance_YTD', 'Performance_YoY']
                existing_cols = [col for col in export_columns if col in indices_general_df.columns]
                indices_general_df[existing_cols].to_excel(writer, sheet_name='Indices_Generaux', index=False)
            
            indices_sectorial_df = get_processed_data('indices_sectorial', period)
            if not indices_sectorial_df.empty:
                export_columns = ['Indice', 'Date', 'CCA', 'CCV', 'Performance_Quotidienne',
                                'Performance_YTD', 'Performance_YoY']
                existing_cols = [col for col in export_columns if col in indices_sectorial_df.columns]
                indices_sectorial_df[existing_cols].to_excel(writer, sheet_name='Indices_Sectoriels', index=False)
        
        output.seek(0)
        
        return dcc.send_bytes(
            output.getvalue(),
            f"bourse_casablanca_data_{period}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
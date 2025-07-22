# styles/styles.py

COLORS = {
    'primary': '#1a365d',
    'secondary': '#2c5aa0',
    'accent': '#3182ce',
    'success': '#38a169',
    'danger': '#e53e3e',
    'warning': '#dd6b20',
    'neutral': '#718096',
    'light': '#f7fafc',
    'background': '#ffffff',
    'text': '#2d3748',
    'border': '#e2e8f0',
    'text_secondary': '#605E5C'
}

# Link styles (imported from original styles module)
link_style = {
    'color': COLORS['accent'],
    'textDecoration': 'none',
    'fontWeight': '500',
    'transition': 'color 0.3s ease',
}

nav_style = {
    'backgroundColor': COLORS['primary'],
    'padding': '10px 20px',
    'display': 'flex',
    'alignItems': 'center',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
}

page_style = {
    'padding': '20px',
    'backgroundColor': COLORS['background'],
    'minHeight': '100vh',
    'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
}

# Sidebar styles
sidebar_style = {
    'position': 'fixed',
    'top': '80px',
    'left': '-250px',  # Hidden by default
    'bottom': '0',
    'width': '260px',
    'backgroundColor': COLORS['primary'],
    'padding': '20px 0',
    'boxShadow': '2px 0 10px rgba(0,0,0,0.1)',
    'zIndex': '999',
    'overflowY': 'auto',
    'transition': 'left 0.3s ease',
}

# Sidebar link styles
sidebar_link_style = {
    'display': 'flex',
    'alignItems': 'center',
    'color': COLORS['light'],
    'textDecoration': 'none',
    'padding': '15px 25px',
    'fontSize': '16px',
    'fontWeight': '500',
    'borderBottom': f'1px solid {COLORS["secondary"]}',
    'transition': 'all 0.3s ease',
}

# Sidebar dropdown styles
sidebar_dropdown_header_style = {
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'space-between',
    'color': COLORS['light'],
    'padding': '15px 25px',
    'fontSize': '16px',
    'fontWeight': '500',
    'borderBottom': f'1px solid {COLORS["secondary"]}',
    'cursor': 'pointer',
    'transition': 'all 0.3s ease',
    'backgroundColor': 'rgba(255, 255, 255, 0.05)',
}

sidebar_dropdown_content_style = {
    'maxHeight': '0',
    'overflow': 'hidden',
    'transition': 'max-height 0.3s ease',
    'backgroundColor': 'rgba(255, 255, 255, 0.05)',
}

sidebar_dropdown_link_style = {
    **sidebar_link_style,
    'paddingLeft': '45px',
    'fontSize': '14px',
    'fontWeight': '400',
    'borderBottom': f'1px solid rgba(255, 255, 255, 0.1)',
}

# Updated navbar style
navbar_style = {
    **nav_style,
    'position': 'fixed',
    'top': '0',
    'left': '0',
    'right': '0',
    'zIndex': '1000',
    'height': '80px',
    'justifyContent': 'space-between',
    'alignItems': 'center',
    'paddingLeft': '40px',
    'paddingRight': '40px',
}

# Toggle button style
toggle_button_style = {
    'backgroundColor': 'transparent',
    'border': 'none',
    'color': COLORS['light'],
    'fontSize': '24px',
    'cursor': 'pointer',
    'padding': '10px',
    'borderRadius': '4px',
    'transition': 'background-color 0.3s ease',
}

# Logo style
logo_style = {
    'height': '50px',
    'width': 'auto',
    'borderRadius': '5px',
}

# Content style
content_style = {
    'marginTop': '80px',
    'padding': '20px',
    'minHeight': 'calc(100vh - 80px)',
    'backgroundColor': COLORS['background'],
    'transition': 'margin-left 0.3s ease',
}

# Footer style
footer_style = {
    'backgroundColor': COLORS['secondary'],
    'color': COLORS['light'],
    'textAlign': 'center',
    'padding': '20px 40px',
    'marginTop': '50px',
    'borderTop': f'3px solid {COLORS["accent"]}',
    'fontSize': '14px',
    'fontWeight': '400',
    'transition': 'margin-left 0.3s ease',
}

page_style = {
    'padding': '40px',
    'fontFamily': 'Arial, sans-serif',
    'backgroundColor': '#f4f6f9',
    'minHeight': '100vh'
}

card_style = {
    'backgroundColor': 'white',
    'borderRadius': '8px',
    'padding': '30px',
    'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
    'maxWidth': '1000px',
    'margin': 'auto'
}

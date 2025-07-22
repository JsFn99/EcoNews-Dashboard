# app/main.py
import dash
from dash import dcc, html
from flask_login import LoginManager, current_user
from components.header import create_navbar, create_sidebar
from components.layout_utils import create_overlay, create_footer
from styles.styles import content_style
from callbacks import eco_callbacks, shared_callbacks, stock_callbacks
from models.user import UserManager
import pages

app = dash.Dash(__name__, suppress_callback_exceptions=True, title='Observatoire Économique Intelligent')
server = app.server

# Configure Flask-Login
server.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production!
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/auth'

# Initialize user manager
user_manager = UserManager()


@login_manager.user_loader
def load_user(user_id):
    return user_manager.get_user_by_id(int(user_id))


# Register pages
pages.register_pages(app)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='sidebar-state', data={'open': False}),
    dcc.Store(id='bourse-dropdown-state', data={'open': False}),
    dcc.Store(id='user-session', data={}),  # Store user session data

    # Components
    create_navbar(),
    create_sidebar(),
    create_overlay(),

    # Main content area
    html.Div(id='page-content', style=content_style),

    # Footer
    create_footer()
])

# Add external CSS and JavaScript
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link rel="icon" type="image/x-icon" href="static/bmce.ico">
        <link rel="icon" type="image/png" href="static/bmce.png">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        {%css%}
        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            .sidebar-link:hover {
                background-color: rgba(255, 255, 255, 0.15) !important;
                padding-left: 30px !important;
            }

            .sidebar-open {
                left: 0 !important;
            }

            .content-shifted {
                margin-left: 250px !important;
            }

            .footer-shifted {
                margin-left: 250px !important;
            }

            .dropdown-open {
                max-height: 200px !important;
            }

            .chevron-rotated {
                transform: rotate(180deg) !important;
            }

            #sidebar-toggle:hover {
                background-color: rgba(255, 255, 255, 0.1) !important;
            }

            .user-menu {
                position: relative;
                display: inline-block;
            }

            .user-dropdown {
                position: absolute;
                top: 100%;
                right: 0;
                background: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                min-width: 150px;
                z-index: 1000;
            }

            /* Responsive design */
            @media (max-width: 768px) {
                .content-shifted {
                    margin-left: 0 !important;
                }

                .footer-shifted {
                    margin-left: 0 !important;
                }
            }

            /* Scrollbar styling */
            #sidebar::-webkit-scrollbar {
                width: 6px;
            }

            #sidebar::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
            }

            #sidebar::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
            }

            #sidebar::-webkit-scrollbar-thumb:hover {
                background: rgba(255, 255, 255, 0.5);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)

# pages/__init__.py
from . import bourse, eco, home, my_articles, news, zoom

def register_pages(app):
    """Register all pages and their callbacks"""
    # Import and register shared callbacks here to avoid circular imports
    from callbacks.shared_callbacks import register_callbacks
    register_callbacks(app)

    # Import and register stock callbacks
    from callbacks.stock_callbacks import register_callbacks as register_stock_callbacks
    register_stock_callbacks(app)

    # Register page-specific callbacks if they exist
    if hasattr(bourse, 'register_callbacks'):
        bourse.register_callbacks(app)
    if hasattr(eco, 'register_callbacks'):
        eco.register_callbacks(app)
    if hasattr(home, 'register_callbacks'):
        home.register_callbacks(app)
    if hasattr(my_articles, 'register_callbacks'):
        my_articles.register_callbacks(app)
    if hasattr(news, 'register_callbacks'):
        news.register_callbacks(app)
    if hasattr(zoom, 'register_callbacks'):
        zoom.register_callbacks(app)

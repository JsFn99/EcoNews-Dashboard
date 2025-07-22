# components/media_banner.py

from dash import html

# Media logos data
MEDIA_LOGOS = [
    {"name": "Le Matin", "url": "https://s1.lematin.ma/cdn/images/kit-media/logo-lematin-vert.png"},
    {"name": "Challenge", "url": "https://www.challenge.ma/wp-content/uploads/2023/10/logo112.png?v=1750455236"},
    {"name": "Maroc Diplomatique", "url": "https://maroc-diplomatique.net/wp-content/uploads/2019/10/logo-1.png"},
    {"name": "Médias24", "url": "https://static.medias24.com/content/themes/medias24/dist/logo/logo.light.png?x58899"},
    {"name": "Le Desk", "url": "https://maroc.mom-gmr.org/uploads/tx_lfrogmom/media/39-1120_import.png"},
    {"name": "TelQuel", "url": "https://maroc.mom-gmr.org/uploads/tx_lfrogmom/media/37-1120_import.png"},
    {"name": "Le Site Info", "url": "https://morocco.mom-gmr.org/uploads/tx_lfrogmom/media/42-1120_import.png"},
    {"name": "HCP", "url": "https://lh6.googleusercontent.com/proxy/4_FWiSb-JWOFnOfj57FW7X13S2ZvjqmL7FJaSRpvhNxS5qux4mozIUzo8JPUKDiViSXH7_ZkyK1P"},
    {"name": "Bank Al Maghrib", "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Bank_Al-Maghrib_Logo.png/1200px-Bank_Al-Maghrib_Logo.png"}
]

def create_media_banner():
    """Create the rolling media banner with CSS animation"""
    animation_css = """
    <style>
    @keyframes scroll {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    
    .media-scroll {
        animation: scroll 30s linear infinite;
    }
    
    .media-logo:hover {
        transform: scale(1.1) !important;
        filter: grayscale(0) !important;
        opacity: 1 !important;
    }
    </style>
    """
    
    # Create multiple sets of logos for seamless scrolling
    logos_html = ""
    for _ in range(6):  # 6 sets for continuous scroll
        for logo in MEDIA_LOGOS:
            logos_html += f'<img src="{logo["url"]}" alt="{logo["name"]}" title="{logo["name"]}" class="media-logo" style="height: 50px; margin: 0 30px; border-radius: 8px; transition: transform 0.3s ease, filter 0.3s ease, opacity 0.3s ease; filter: grayscale(0.3); opacity: 0.8; cursor: pointer;" />'
    
    # Complete HTML for the banner
    banner_html = f"""
    {animation_css}
    <div style="width: 100%; height: 120px; overflow: hidden; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border: 1px solid #e2e8f0; border-radius: 12px; margin: 30px 0 40px 0; position: relative; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);">
        <div style="position: absolute; top: 5px; left: 15px; background: rgba(30, 58, 138, 0.9); color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; z-index: 10;">
            Sources Média
        </div>
        <div class="media-scroll" style="display: flex; align-items: center; height: 100%; white-space: nowrap;">
            {logos_html}
        </div>
        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, rgba(248, 250, 252, 0.8) 0%, rgba(248, 250, 252, 0) 15%, rgba(248, 250, 252, 0) 85%, rgba(248, 250, 252, 0.8) 100%); pointer-events: none;"></div>
    </div>
    """
    
    return html.Div([
        html.Iframe(
            srcDoc=banner_html,
            style={
                'width': '100%',
                'height': '160px',  
                'margin': '20px 0',
                'border': 'none',
                'overflow': 'hidden',
                'display': 'block'
            }
        )
    ])

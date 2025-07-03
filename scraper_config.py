# Configuration pour VPS
import os

# Détection environnement VPS
IS_VPS = os.path.exists('/usr/bin/chromium-browser')

# Configuration Chrome pour VPS
def get_chrome_options(options):
    """Ajouter les options spécifiques au VPS"""
    if IS_VPS:
        # Mode headless obligatoire sur VPS
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Chemins spécifiques VPS
        options.binary_location = '/usr/bin/chromium-browser'
    
    return options

# Configuration des chemins
CHROME_DRIVER_PATH = '/usr/bin/chromedriver' if IS_VPS else None

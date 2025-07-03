# stealth_config.py - Configuration pour LeBonCoin avec Selenium standard

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import random

def get_stealth_driver():
    """Créer un driver Chrome avec Selenium standard"""
    
    # Options Chrome
    options = Options()
    
    # Mode headless pour VPS (pas d'interface graphique)
    options.add_argument('--headless')
    
    # Arguments pour VPS
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    
    # Taille fenêtre
    options.add_argument('--window-size=1920,1080')
    
    # User agent
    options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Langue française
    options.add_argument('--lang=fr-FR')
    
    # Désactiver les images pour aller plus vite
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2
        }
    }
    options.add_experimental_option('prefs', prefs)
    
    # Créer le driver
    try:
        driver = webdriver.Chrome(options=options)
        print("✅ Chrome lancé avec succès!")
    except Exception as e:
        print(f"❌ Erreur Chrome: {e}")
        # Essayer avec chromium-driver
        options.binary_location = '/usr/bin/chromium-browser'
        driver = webdriver.Chrome(options=options)
        print("✅ Chromium lancé avec succès!")
    
    # JavaScript anti-détection
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    return driver

def inject_additional_stealth(driver):
    """Protections supplémentaires"""
    try:
        driver.execute_script("""
            window.chrome = {
                runtime: {},
            };
        """)
    except:
        pass

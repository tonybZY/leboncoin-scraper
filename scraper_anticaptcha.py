# stealth_config.py - Utilise la méthode qui fonctionne de scraper_with_login.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_stealth_driver():
    """Créer un driver Chrome comme dans scraper_with_login.py"""
    
    options = Options()
    
    # Options qui fonctionnent sur VPS
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    
    # Taille de fenêtre
    options.add_argument('--window-size=1920,1080')
    
    # User agent
    options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # Créer le driver exactement comme scraper_with_login.py
    driver = webdriver.Chrome(options=options)
    
    print("✅ Chrome lancé avec succès!")
    
    return driver

def inject_additional_stealth(driver):
    """Protections supplémentaires"""
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# stealth_config.py - Configuration anti-détection pour LeBonCoin

import undetected_chromedriver as uc
import random
import tempfile
import os

def get_stealth_driver():
    """Créer un driver Chrome ultra-furtif"""
    
    # Créer un dossier temporaire unique pour chaque session
    temp_dir = tempfile.mkdtemp()
    
    # Options Chrome
    options = uc.ChromeOptions()
    
    # Utiliser le profil temporaire
    options.add_argument(f'--user-data-dir={temp_dir}')
    
    # Arguments anti-détection
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Désactiver automation
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # User agent
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    options.add_argument(f'--user-agent={user_agent}')
    
    # Préférences
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    
    # Créer le driver
    driver = uc.Chrome(options=options, version_main=None)
    
    # JavaScript anti-détection
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    return driver

def inject_additional_stealth(driver):
    """Protections supplémentaires"""
    pass

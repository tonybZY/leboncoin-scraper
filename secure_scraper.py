# stealth_config.py - Configuration anti-détection pour LeBonCoin

import undetected_chromedriver as uc
import random

def get_stealth_driver():
    """Créer un driver Chrome pour scraper LeBonCoin"""
    
    # Options Chrome SANS profil utilisateur
    options = uc.ChromeOptions()
    
    # Arguments essentiels
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--no-zygote')
    
    # Taille fenêtre
    options.add_argument('--window-size=1920,1080')
    
    # Anti-détection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # User agent français
    options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Langue française
    options.add_argument('--lang=fr-FR')
    
    # Créer le driver SANS spécifier de profil
    driver = uc.Chrome(options=options, use_subprocess=False)
    
    # JavaScript anti-détection basique
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    print("✅ Chrome lancé avec succès!")
    
    return driver

def inject_additional_stealth(driver):
    """Protections supplémentaires après chargement de page"""
    try:
        driver.execute_script("""
            // Masquer webdriver
            delete window.navigator.__proto__.webdriver;
            
            // Simuler un vrai navigateur
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        """)
    except:
        pass

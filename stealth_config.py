# stealth_config.py - Configuration anti-détection pour LeBonCoin

import undetected_chromedriver as uc
import random
import os

def get_stealth_driver():
    """Créer un driver Chrome ultra-furtif"""
    
    # Options Chrome maximales anti-détection
    options = uc.ChromeOptions()
    
    # Arguments essentiels anti-détection
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=IsolateOrigins')
    options.add_argument('--disable-site-isolation-trials')
    options.add_argument('--disable-features=BlockInsecurePrivateNetworkRequests')
    
    # Désactiver les indicateurs d'automatisation
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Arguments pour éviter la détection
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-logging')
    options.add_argument('--disable-dev-tools')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-translate')
    options.add_argument('--disable-sync')
    options.add_argument('--no-first-run')
    options.add_argument('--no-service-autorun')
    options.add_argument('--password-store=basic')
    
    # Taille de fenêtre réaliste
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    
    # User-Agent rotatif ultra-réaliste
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
    ]
    options.add_argument(f'--user-agent={random.choice(user_agents)}')
    
    # PAS DE PROFIL PERSISTANT pour éviter les conflits
    # Chaque session aura son propre profil temporaire
    
    # Préférences pour simuler un vrai navigateur
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.geolocation": 1,
        "intl.accept_languages": "fr-FR,fr,en-US,en",
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.images": 1,
        "profile.default_content_setting_values.cookies": 1,
        "profile.default_content_setting_values.javascript": 1,
        "profile.cookie_controls_mode": 0
    }
    options.add_experimental_option("prefs", prefs)
    
    # Créer le driver avec undetected-chromedriver
    driver = uc.Chrome(options=options, version_main=None)
    
    # Injection JavaScript pour masquer l'automatisation
    stealth_js = """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };
    
    Object.defineProperty(navigator, 'languages', {
        get: () => ['fr-FR', 'fr', 'en-US', 'en']
    });
    
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
    """
    
    driver.execute_script(stealth_js)
    
    return driver

def inject_additional_stealth(driver):
    """Injecter des protections supplémentaires après le chargement de la page"""
    
    try:
        driver.execute_script("""
            // Remove Selenium attributes
            for (const key in window) {
                if (key.includes('selenium') || key.includes('webdriver')) {
                    delete window[key];
                }
            }
            
            Object.defineProperty(document, 'hidden', {value: false});
            Object.defineProperty(document, 'visibilityState', {value: 'visible'});
        """)
    except:
        pass

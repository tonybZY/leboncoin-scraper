#!/usr/bin/env python3
"""
Scraper LeBonCoin complet avec récupération des numéros de téléphone
Optimisé pour VPS 8GB RAM
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os
import logging

app = Flask(__name__)
CORS(app)

# Configuration
CONFIG = {
    'EMAIL': 'tnclim1@gmail.com',
    'PASSWORD': 'Underground780&',
    'MIN_DELAY': 30
}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

last_request_time = 0

def setup_chrome_driver():
    """Configuration Chrome optimisée pour VPS 8GB"""
    options = Options()
    
    # Mode headless pour VPS
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Optimisations pour performance
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-images')  # Pas besoin des images
    
    # Taille de fenêtre
    options.add_argument('--window-size=1920,1080')
    
    # User agent réaliste
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Chemins possibles pour Chrome
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium'
    ]
    
    chrome_binary = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_binary = path
            break
    
    if chrome_binary:
        options.binary_location = chrome_binary
        logger.info(f"✅ Chrome trouvé: {chrome_binary}")
    
    # Créer le driver
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except:
        # Essayer avec Service
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        return driver

def get_phone_number(driver, url):
    """Récupérer le numéro de téléphone d'une annonce"""
    try:
        logger.info(f"📱 Récupération du numéro pour: {url}")
        
        # Aller sur l'annonce
        driver.get(url)
        time.sleep(3)
        
        # Accepter les cookies si nécessaire
        try:
            cookie_button = driver.find_element(By.ID, 'didomi-notice-agree-button')
            cookie_button.click()
            time.sleep(1)
        except:
            pass
        
        # Faire défiler pour trouver le bouton téléphone
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        
        # Chercher le bouton "Voir le numéro"
        phone_button = None
        selectors = [
            "//button[contains(text(), 'Voir le numéro')]",
            "//button[contains(text(), 'Afficher le numéro')]",
            "//button[contains(., 'numéro')]",
            "//button[contains(@class, 'phone')]",
            "//span[contains(text(), 'Voir le numéro')]/..",
            "//*[contains(text(), 'Voir le numéro')]"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    phone_button = elements[0]
                    logger.info(f"✅ Bouton trouvé avec: {selector}")
                    break
            except:
                continue
        
        if not phone_button:
            # Chercher avec CSS
            try:
                phone_button = driver.find_element(By.CSS_SELECTOR, '[data-qa-id*="phone"]')
            except:
                pass
        
        if phone_button:
            # Scroll jusqu'au bouton
            driver.execute_script("arguments[0].scrollIntoView(true);", phone_button)
            time.sleep(1)
            
            # Cliquer
            driver.execute_script("arguments[0].click();", phone_button)
            logger.info("✅ Clic sur le bouton téléphone")
            time.sleep(3)
            
            # Chercher le numéro révélé
            # Méthode 1: Liens tel:
            phone_links = driver.find_elements(By.XPATH, "//a[starts-with(@href, 'tel:')]")
            if phone_links:
                phone = phone_links[0].get_attribute('href').replace('tel:', '').strip()
                logger.info(f"✅ Numéro trouvé (lien): {phone}")
                return phone
            
            # Méthode 2: Texte contenant un numéro
            import re
            page_text = driver.find_element(By.TAG_NAME, 'body').text
            phone_pattern = r'0[1-9](?:[\s.-]?\d{2}){4}'
            matches = re.findall(phone_pattern, page_text)
            
            if matches:
                # Prendre le dernier numéro trouvé (probablement celui qui vient d'apparaître)
                phone = matches[-1].replace(' ', '').replace('.', '').replace('-', '')
                logger.info(f"✅ Numéro trouvé (regex): {phone}")
                return phone
        
        logger.warning("❌ Bouton téléphone non trouvé")
        return None
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération téléphone: {str(e)}")
        return None

@app.route('/scrape', methods=['POST'])
def scrape():
    """Endpoint principal de scraping"""
    global last_request_time
    
    # Protection anti-spam
    current_time = time.time()
    if current_time - last_request_time < CONFIG['MIN_DELAY']:
        wait_time = CONFIG['MIN_DELAY'] - (current_time - last_request_time)
        time.sleep(wait_time)
    
    last_request_time = time.time()
    
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL requise'}), 400
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🔍 SCRAPING: {url}")
    logger.info(f"{'='*60}\n")
    
    driver = None
    
    try:
        # Lancer Chrome
        driver = setup_chrome_driver()
        
        # Aller sur l'annonce
        driver.get(url)
        time.sleep(3)
        
        # Extraire les données de base
        title = driver.find_element(By.TAG_NAME, 'h1').text if driver.find_elements(By.TAG_NAME, 'h1') else 'Non trouvé'
        
        price = None
        try:
            price_elem = driver.find_element(By.CSS_SELECTOR, '[data-qa-id="adview_price"]')
            price = price_elem.text
        except:
            try:
                price_elem = driver.find_element(By.CSS_SELECTOR, '[class*="price"]')
                price = price_elem.text
            except:
                price = 'Prix non trouvé'
        
        # Récupérer le numéro
        phone = get_phone_number(driver, url)
        
        driver.quit()
        
        logger.info(f"✅ Scraping terminé - Titre: {title}, Prix: {price}, Tél: {phone}")
        
        return jsonify({
            'success': True,
            'data': {
                'title': title,
                'price': price,
                'phone': phone,
                'url': url
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        if driver:
            driver.quit()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'url': url
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """Tester si Chrome fonctionne"""
    try:
        driver = setup_chrome_driver()
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        return jsonify({
            'status': 'OK',
            'chrome': '✅ Chrome fonctionne',
            'google_title': title,
            'message': 'Serveur prêt!'
        })
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'chrome': '❌ Chrome ne fonctionne pas',
            'error': str(e),
            'message': 'Installez Chrome avec: apt install google-chrome-stable'
        })

@app.route('/install-chrome', methods=['GET'])
def install_chrome_instructions():
    """Instructions d'installation de Chrome"""
    return jsonify({
        'instructions': [
            '# Installation Chrome sur votre VPS:',
            'wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -',
            'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list',
            'sudo apt update',
            'sudo apt install -y google-chrome-stable',
            '',
            '# Ou Chromium (plus léger):',
            'sudo apt install -y chromium-browser chromium-chromedriver'
        ]
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVEUR LEBONCOIN - VPS 8GB")
    print("="*60)
    print(f"📡 Port: 1373")
    print(f"💾 RAM: 8GB (largement suffisant!)")
    print(f"📧 Email: {CONFIG['EMAIL']}")
    print("\n📌 Endpoints:")
    print("   POST /scrape - Scraper avec numéro de téléphone")
    print("   GET  /test - Vérifier Chrome")
    print("   GET  /install-chrome - Instructions installation")
    print("\n" + "="*60 + "\n")
    
    app.run(port=1373, debug=True, host='0.0.0.0')

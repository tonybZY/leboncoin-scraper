#!/usr/bin/env python3
import os
import time
import base64
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

CONFIG = {
    'EMAIL': 'tnclim1@gmail.com',
    'PASSWORD': 'Underground780&',
    'MIN_DELAY': 30,
    'SCREENSHOT_DIR': '/root/leboncoin-scraper/screenshots'
}

# Créer le dossier screenshots
os.makedirs(CONFIG['SCREENSHOT_DIR'], exist_ok=True)

last_request_time = 0

def get_driver_with_display():
    """Créer un driver avec display virtuel"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Essayer avec display virtuel
    os.environ['DISPLAY'] = ':99'
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"❌ Erreur Chrome: {e}")
        raise

def take_screenshot(driver, name):
    """Prendre une capture d'écran"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{CONFIG['SCREENSHOT_DIR']}/{timestamp}_{name}.png"
    driver.save_screenshot(filename)
    print(f"📸 Screenshot: {filename}")
    return filename

@app.route('/scrape_debug', methods=['POST'])
def scrape_debug():
    """Version avec debug visuel"""
    global last_request_time
    
    # Protection anti-spam
    current_time = time.time()
    if current_time - last_request_time < CONFIG['MIN_DELAY']:
        time.sleep(CONFIG['MIN_DELAY'] - (current_time - last_request_time))
    
    last_request_time = time.time()
    
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL requise'}), 400
    
    print(f"\n{'='*60}")
    print(f"🔍 SCRAPING AVEC DEBUG VISUEL")
    print(f"📍 URL: {url}")
    print(f"{'='*60}\n")
    
    screenshots = []
    driver = None
    
    try:
        # Lancer Xvfb si pas déjà fait
        os.system("pkill Xvfb; Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &")
        time.sleep(2)
        
        print("🚀 Lancement de Chrome...")
        driver = get_driver_with_display()
        
        # Étape 1: Page d'accueil
        print("📄 Chargement de la page...")
        driver.get(url)
        time.sleep(3)
        screenshots.append(take_screenshot(driver, "1_page_loaded"))
        
        # Étape 2: Accepter cookies
        try:
            cookie_button = driver.find_element(By.ID, 'didomi-notice-agree-button')
            cookie_button.click()
            print("🍪 Cookies acceptés")
            time.sleep(2)
            screenshots.append(take_screenshot(driver, "2_cookies_accepted"))
        except:
            print("Pas de cookies à accepter")
        
        # Étape 3: Extraire les données
        print("📊 Extraction des données...")
        title = "Non trouvé"
        try:
            h1 = driver.find_element(By.TAG_NAME, 'h1')
            title = h1.text
            print(f"✅ Titre: {title}")
        except:
            print("❌ Titre non trouvé")
        
        # Étape 4: Chercher le bouton téléphone
        print("📞 Recherche du bouton téléphone...")
        phone = None
        
        # Faire défiler la page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        screenshots.append(take_screenshot(driver, "3_scrolled"))
        
        # Chercher le bouton
        phone_selectors = [
            "//button[contains(text(), 'Voir le numéro')]",
            "//button[contains(text(), 'Afficher le numéro')]",
            "//button[contains(., 'numéro')]",
            "//button[contains(@class, 'phone')]"
        ]
        
        phone_button = None
        for selector in phone_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    phone_button = elements[0]
                    print(f"✅ Bouton trouvé avec: {selector}")
                    # Scroll jusqu'au bouton
                    driver.execute_script("arguments[0].scrollIntoView(true);", phone_button)
                    time.sleep(1)
                    screenshots.append(take_screenshot(driver, "4_phone_button_found"))
                    break
            except:
                continue
        
        if phone_button:
            print("🖱️ Clic sur le bouton...")
            phone_button.click()
            time.sleep(3)
            screenshots.append(take_screenshot(driver, "5_after_click"))
            
            # Chercher le numéro
            try:
                phone_links = driver.find_elements(By.XPATH, "//a[starts-with(@href, 'tel:')]")
                if phone_links:
                    phone = phone_links[0].get_attribute('href').replace('tel:', '')
                    print(f"✅ Numéro trouvé: {phone}")
            except:
                print("❌ Numéro non trouvé")
        else:
            print("❌ Bouton téléphone introuvable")
            # Prendre une capture de toute la page
            driver.execute_script("window.scrollTo(0, 0);")
            screenshots.append(take_screenshot(driver, "full_page_top"))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            screenshots.append(take_screenshot(driver, "full_page_bottom"))
        
        driver.quit()
        
        return jsonify({
            'success': True,
            'data': {
                'title': title,
                'phone': phone,
                'screenshots': screenshots,
                'screenshot_count': len(screenshots)
            },
            'url': url
        })
        
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        if driver:
            take_screenshot(driver, "error")
            driver.quit()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'screenshots': screenshots,
            'url': url
        }), 500

@app.route('/screenshots', methods=['GET'])
def list_screenshots():
    """Lister toutes les captures d'écran"""
    files = os.listdir(CONFIG['SCREENSHOT_DIR'])
    files.sort(reverse=True)
    return jsonify({
        'screenshots': files,
        'count': len(files),
        'path': CONFIG['SCREENSHOT_DIR']
    })

@app.route('/screenshot/<filename>', methods=['GET'])
def get_screenshot(filename):
    """Récupérer une capture d'écran"""
    filepath = os.path.join(CONFIG['SCREENSHOT_DIR'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/png')
    return jsonify({'error': 'File not found'}), 404

@app.route('/test', methods=['GET'])
def test():
    # Test rapide de Chrome
    chrome_works = False
    try:
        os.system("pkill Xvfb; Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &")
        time.sleep(2)
        driver = get_driver_with_display()
        driver.get("https://www.google.com")
        take_screenshot(driver, "test_google")
        driver.quit()
        chrome_works = True
    except Exception as e:
        print(f"Test échoué: {e}")
    
    return jsonify({
        'status': 'OK',
        'chrome': '✅ Chrome fonctionne' if chrome_works else '❌ Chrome ne fonctionne pas',
        'email': CONFIG['EMAIL'],
        'screenshot_dir': CONFIG['SCREENSHOT_DIR'],
        'message': 'Serveur debug prêt!'
    })

@app.route('/clean_screenshots', methods=['DELETE'])
def clean_screenshots():
    """Nettoyer les vieilles captures"""
    files = os.listdir(CONFIG['SCREENSHOT_DIR'])
    for f in files:
        os.remove(os.path.join(CONFIG['SCREENSHOT_DIR'], f))
    return jsonify({'deleted': len(files)})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVEUR LEBONCOIN - MODE DEBUG VISUEL")
    print("="*60)
    print(f"📡 Port: 1373")
    print(f"📸 Screenshots: {CONFIG['SCREENSHOT_DIR']}")
    print("\n📌 Endpoints:")
    print("   POST /scrape_debug - Scraper avec captures")
    print("   GET  /screenshots - Lister les captures")
    print("   GET  /screenshot/<filename> - Voir une capture")
    print("   GET  /test - Tester Chrome")
    print("   DELETE /clean_screenshots - Nettoyer")
    print("\n" + "="*60 + "\n")
    
    # Lancer Xvfb au démarrage
    os.system("pkill Xvfb; Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &")
    time.sleep(2)
    
    app.run(port=1373, debug=True, host='0.0.0.0')

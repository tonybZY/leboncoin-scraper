#!/usr/bin/env python3
import time
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

# Configuration
CONFIG = {
    'EMAIL': 'tnclim1@gmail.com',
    'PASSWORD': 'Underground780&',
    'MIN_DELAY': 30
}

last_request_time = 0

def get_driver():
    """Créer un driver Chrome qui fonctionne sur VPS"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Essayer différents drivers
    drivers_to_try = [
        lambda: webdriver.Chrome(options=options),
        lambda: webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options),
        lambda: webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=options),
    ]
    
    for driver_func in drivers_to_try:
        try:
            return driver_func()
        except:
            continue
    
    raise Exception("Impossible de lancer Chrome")

@app.route('/scrape', methods=['POST'])
def scrape():
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
    
    print(f"\n{'='*60}")
    print(f"🔍 SCRAPING: {url}")
    print(f"{'='*60}\n")
    
    # Mode 1: Essayer avec Selenium
    try:
        driver = get_driver()
        driver.get(url)
        time.sleep(3)
        
        # Extraire les données
        title = driver.find_element(By.TAG_NAME, 'h1').text if driver.find_elements(By.TAG_NAME, 'h1') else 'Non trouvé'
        
        # Chercher le bouton téléphone
        phone = None
        try:
            phone_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Voir le numéro')]")
            phone_button.click()
            time.sleep(2)
            
            # Chercher le numéro
            phone_elements = driver.find_elements(By.XPATH, "//a[starts-with(@href, 'tel:')]")
            if phone_elements:
                phone = phone_elements[0].get_attribute('href').replace('tel:', '')
        except:
            pass
        
        driver.quit()
        
        return jsonify({
            'success': True,
            'data': {
                'title': title,
                'phone': phone,
                'method': 'selenium'
            },
            'url': url
        })
        
    except Exception as e:
        print(f"Selenium échoué: {e}")
    
    # Mode 2: Fallback avec requests
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('h1').text if soup.find('h1') else 'Non trouvé'
        
        return jsonify({
            'success': True,
            'data': {
                'title': title,
                'phone': None,
                'method': 'requests',
                'note': 'Mode basique - Installez Chrome pour récupérer les numéros'
            },
            'url': url
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'url': url
        }), 500

@app.route('/test', methods=['GET'])
def test():
    # Tester si Chrome fonctionne
    chrome_works = False
    try:
        driver = get_driver()
        driver.quit()
        chrome_works = True
    except:
        pass
    
    return jsonify({
        'status': 'OK',
        'chrome': '✅ Disponible' if chrome_works else '❌ Non disponible',
        'email': CONFIG['EMAIL'],
        'message': 'Serveur prêt!'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVEUR LEBONCOIN - VERSION QUI MARCHE")
    print("="*60)
    print(f"📡 Port: 1373")
    print(f"📧 Email: {CONFIG['EMAIL']}")
    print("\n📌 Endpoints:")
    print("   POST http://localhost:1373/scrape")
    print("   GET  http://localhost:1373/test")
    print("\n" + "="*60 + "\n")
    
    app.run(port=1373, debug=True, host='0.0.0.0')

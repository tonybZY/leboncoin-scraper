#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

app = Flask(__name__)
CORS(app)

CONFIG = {
    'EMAIL': 'tnclim1@gmail.com',
    'PASSWORD': 'Underground780&',
    'MIN_DELAY': 30
}

def get_chromium_driver():
    """Driver pour Chromium (pas Chrome)"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.binary_location = '/usr/bin/chromium-browser'  # Chemin Chromium
    
    # Service avec chromedriver
    service = Service('/usr/bin/chromedriver')
    
    return webdriver.Chrome(service=service, options=options)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL requise'}), 400
    
    print(f"\n🔍 SCRAPING: {url}")
    
    driver = None
    try:
        # Lancer Chromium
        print("🚀 Lancement de Chromium...")
        driver = get_chromium_driver()
        
        # Aller sur la page
        driver.get(url)
        time.sleep(3)
        
        # Extraire le titre
        title = "Non trouvé"
        try:
            h1 = driver.find_element(By.TAG_NAME, 'h1')
            title = h1.text
            print(f"✅ Titre: {title}")
        except:
            pass
        
        # Screenshot pour debug
        driver.save_screenshot('/root/page.png')
        print("📸 Screenshot: /root/page.png")
        
        driver.quit()
        
        return jsonify({
            'success': True,
            'data': {
                'title': title,
                'screenshot': '/root/page.png'
            },
            'url': url
        })
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if driver:
            driver.quit()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'url': url
        }), 500

@app.route('/test', methods=['GET'])
def test():
    # Test simple
    try:
        driver = get_chromium_driver()
        driver.get("https://www.google.com")
        driver.save_screenshot('/root/test.png')
        driver.quit()
        status = "✅ Chromium fonctionne!"
    except Exception as e:
        status = f"❌ Erreur: {e}"
    
    return jsonify({
        'status': 'OK',
        'chromium': status,
        'message': 'Serveur prêt!'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVEUR LEBONCOIN - CHROMIUM")
    print("="*60)
    print("📡 Port: 1373")
    print("\n" + "="*60 + "\n")
    
    app.run(port=1373, debug=True, host='0.0.0.0')

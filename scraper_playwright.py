#!/usr/bin/env python3
"""
Scraper LeBonCoin avec Playwright - FONCTIONNE sur tous les VPS
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import time
import re
import logging

app = Flask(__name__)
CORS(app)

# Configuration
CONFIG = {
    'EMAIL': 'tnclim1@gmail.com',
    'PASSWORD': 'Underground780&',
    'MIN_DELAY': 30
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

last_request_time = 0

def scrape_with_playwright(url):
    """Scraping avec Playwright - plus simple et fiable"""
    with sync_playwright() as p:
        # Lancer le navigateur
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        page = browser.new_page()
        
        try:
            logger.info(f"📱 Navigation vers: {url}")
            
            # Aller sur la page
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Accepter les cookies
            try:
                page.click('#didomi-notice-agree-button', timeout=5000)
                logger.info("🍪 Cookies acceptés")
            except:
                pass
            
            # Attendre que la page charge
            page.wait_for_timeout(3000)
            
            # Extraire les données de base
            title = page.query_selector('h1').inner_text() if page.query_selector('h1') else 'Non trouvé'
            
            price = 'Non trouvé'
            price_elem = page.query_selector('[data-qa-id="adview_price"]')
            if price_elem:
                price = price_elem.inner_text()
            
            logger.info(f"📊 Titre: {title}")
            logger.info(f"💰 Prix: {price}")
            
            # Chercher le bouton téléphone
            phone = None
            
            # Faire défiler
            page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
            page.wait_for_timeout(2000)
            
            # Chercher le bouton "Voir le numéro"
            phone_button = None
            
            # Méthode 1: Texte exact
            try:
                phone_button = page.get_by_text("Voir le numéro", exact=True)
                if phone_button.is_visible():
                    logger.info("✅ Bouton trouvé (texte exact)")
                else:
                    phone_button = None
            except:
                pass
            
            # Méthode 2: Sélecteurs
            if not phone_button:
                selectors = [
                    'button:has-text("Voir le numéro")',
                    'button:has-text("numéro")',
                    '[data-qa-id*="phone"]',
                    'button:has-text("Afficher")'
                ]
                
                for selector in selectors:
                    try:
                        elem = page.query_selector(selector)
                        if elem and elem.is_visible():
                            phone_button = elem
                            logger.info(f"✅ Bouton trouvé: {selector}")
                            break
                    except:
                        continue
            
            if phone_button:
                # Cliquer sur le bouton
                phone_button.click()
                logger.info("✅ Clic sur le bouton téléphone")
                
                # Attendre que le numéro apparaisse
                page.wait_for_timeout(3000)
                
                # Chercher le numéro
                # Méthode 1: Liens tel:
                tel_links = page.query_selector_all('a[href^="tel:"]')
                if tel_links:
                    phone = tel_links[0].get_attribute('href').replace('tel:', '').strip()
                    logger.info(f"✅ Numéro trouvé (lien): {phone}")
                else:
                    # Méthode 2: Regex dans le texte
                    page_text = page.content()
                    phone_pattern = r'0[1-9](?:[\s.-]?\d{2}){4}'
                    matches = re.findall(phone_pattern, page_text)
                    
                    if matches:
                        # Nettoyer et prendre le dernier
                        phone = matches[-1].replace(' ', '').replace('.', '').replace('-', '')
                        logger.info(f"✅ Numéro trouvé (regex): {phone}")
            else:
                logger.warning("❌ Bouton téléphone non trouvé")
                
                # Prendre une capture pour debug
                page.screenshot(path="/root/debug_phone_button.png")
                logger.info("📸 Screenshot sauvé: /root/debug_phone_button.png")
            
            browser.close()
            
            return {
                'success': True,
                'title': title,
                'price': price,
                'phone': phone
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur: {str(e)}")
            browser.close()
            return {
                'success': False,
                'error': str(e)
            }

@app.route('/scrape', methods=['POST'])
def scrape():
    """Endpoint principal"""
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
    
    result = scrape_with_playwright(url)
    
    if result['success']:
        return jsonify({
            'success': True,
            'data': {
                'title': result['title'],
                'price': result['price'],
                'phone': result['phone'],
                'url': url
            }
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error'],
            'url': url
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """Test Playwright"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://www.google.com')
            title = page.title()
            browser.close()
            
            return jsonify({
                'status': 'OK',
                'playwright': '✅ Playwright fonctionne',
                'google_title': title
            })
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'playwright': '❌ Erreur',
            'error': str(e)
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVEUR LEBONCOIN - PLAYWRIGHT")
    print("="*60)
    print("📡 Port: 1373")
    print("🎭 Utilise Playwright (plus simple que Selenium)")
    print("\n" + "="*60 + "\n")
    
    app.run(port=1373, debug=True, host='0.0.0.0')

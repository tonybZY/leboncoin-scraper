#!/usr/bin/env python3
"""
Scraper LeBonCoin avec Playwright - AVEC CONNEXION AUTOMATIQUE
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import time
import re
import logging
import os

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

def login_to_leboncoin(page):
    """Se connecter à LeBonCoin"""
    logger.info("🔐 Connexion à LeBonCoin...")
    
    # Aller sur la page de connexion
    page.goto('https://www.leboncoin.fr/deposer-une-annonce', wait_until='networkidle')
    page.wait_for_timeout(3000)
    
    # Accepter les cookies
    try:
        page.click('#didomi-notice-agree-button', timeout=5000)
        logger.info("🍪 Cookies acceptés")
        page.wait_for_timeout(2000)
    except:
        pass
    
    # Vérifier si on est sur la page de connexion
    if page.query_selector('input[name="email"]'):
        logger.info("📝 Formulaire de connexion détecté")
        
        # Remplir l'email
        page.fill('input[name="email"]', CONFIG['EMAIL'])
        logger.info("✅ Email rempli")
        page.wait_for_timeout(1000)
        
        # Remplir le mot de passe
        page.fill('input[name="password"]', CONFIG['PASSWORD'])
        logger.info("✅ Mot de passe rempli")
        page.wait_for_timeout(1000)
        
        # Cliquer sur connexion
        page.click('button[type="submit"]')
        logger.info("✅ Clic sur connexion")
        
        # Attendre la redirection
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(5000)
        
        # Vérifier si connecté
        if "mon-compte" in page.url or "deposer" in page.url:
            logger.info("✅ Connexion réussie!")
            return True
        else:
            logger.warning("⚠️ Connexion incertaine")
            # Prendre une capture pour debug
            page.screenshot(path="/root/login_result.png")
            return True  # On continue quand même
    else:
        logger.info("✅ Déjà connecté ou pas de formulaire")
        return True

def scrape_with_playwright(url):
    """Scraping avec Playwright - avec connexion"""
    with sync_playwright() as p:
        # Lancer le navigateur avec contexte persistant
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        # Créer un contexte avec stockage persistant
        context = browser.new_context(
            storage_state=None,  # Pour le moment pas de persistence
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        try:
            # Se connecter d'abord
            login_success = login_to_leboncoin(page)
            
            if not login_success:
                logger.warning("⚠️ Problème de connexion")
            
            logger.info(f"📱 Navigation vers l'annonce: {url}")
            
            # Aller sur l'annonce
            page.goto(url, wait_until='networkidle', timeout=30000)
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
            
            # Capture avant recherche du bouton
            page.screenshot(path="/root/before_phone_search.png")
            logger.info("📸 Screenshot avant recherche: /root/before_phone_search.png")
            
            # Chercher le bouton "Voir le numéro"
            phone_button = None
            
            # Liste de sélecteurs
            selectors = [
                'button:has-text("Voir le numéro")',
                'button:has-text("Afficher le numéro")',
                'button:has-text("numéro")',
                '[data-qa-id*="phone"]',
                'button[class*="phone"]',
                'button[class*="Phone"]',
                # Sélecteurs plus génériques
                'button:has-text("06")',
                'button:has-text("07")',
                'button:has-text("Contacter")',
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
                
                # Screenshot après clic
                page.screenshot(path="/root/after_phone_click.png")
                logger.info("📸 Screenshot après clic: /root/after_phone_click.png")
                
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
                
                # Lister tous les boutons pour debug
                all_buttons = page.query_selector_all('button')
                logger.info(f"📊 Nombre total de boutons: {len(all_buttons)}")
                
                for i, btn in enumerate(all_buttons[:10]):  # Les 10 premiers
                    try:
                        text = btn.inner_text()
                        logger.info(f"Bouton {i}: {text[:50]}")
                    except:
                        pass
            
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
    logger.info(f"🔍 SCRAPING AVEC CONNEXION")
    logger.info(f"📍 URL: {url}")
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
    """Test avec connexion"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Tester la connexion
            login_success = login_to_leboncoin(page)
            
            browser.close()
            
            return jsonify({
                'status': 'OK',
                'playwright': '✅ Playwright fonctionne',
                'login': '✅ Connexion OK' if login_success else '❌ Problème connexion'
            })
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'playwright': '❌ Erreur',
            'error': str(e)
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVEUR LEBONCOIN - PLAYWRIGHT AVEC CONNEXION")
    print("="*60)
    print("📡 Port: 1373")
    print("📧 Email:", CONFIG['EMAIL'])
    print("🔐 Connexion automatique activée")
    print("\n" + "="*60 + "\n")
    
    app.run(port=1373, debug=True, host='0.0.0.0')

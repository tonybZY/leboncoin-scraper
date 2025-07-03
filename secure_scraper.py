import undetected_chromedriver as uc
import time
import random
import json
import os
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, request, jsonify
from flask_cors import CORS
from python_anticaptcha import AnticaptchaClient, ImageToTextTask

app = Flask(__name__)
# CORS restrictif - n'accepte que localhost
CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*'])

# Configuration sécurisée - AJOUTEZ VOS 3 CHIFFRES À LA FIN DE L'API_KEY
API_KEY = 'sk_prod_LeBonCoin_Scraper_2025_xK9mP4nQ7vBz3jR8sT5wL123_'  # AJOUTEZ 3 CHIFFRES ICI
ANTICAPTCHA_API_KEY = '599bf5a3b86f1cabf7e23bca24237354'
LEBONCOIN_EMAIL = 'tnclim1@gmail.com'
LEBONCOIN_PASSWORD = 'Underground780&'

client = AnticaptchaClient(ANTICAPTCHA_API_KEY)

# Logging des accès
access_log = []

# Rate limiting
request_counts = {}
MAX_REQUESTS_PER_IP_PER_HOUR = 10

def require_auth(f):
    """Décorateur pour vérifier l'authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        # Log de l'accès
        access_log.append({
            'timestamp': datetime.now().isoformat(),
            'ip': request.remote_addr,
            'endpoint': request.endpoint,
            'authorized': False
        })
        
        # Vérification de l'API key
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        if token != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Rate limiting par IP
        client_ip = request.remote_addr
        current_hour = datetime.now().strftime('%Y-%m-%d-%H')
        key = f"{client_ip}:{current_hour}"
        
        if key not in request_counts:
            request_counts[key] = 0
        
        request_counts[key] += 1
        
        if request_counts[key] > MAX_REQUESTS_PER_IP_PER_HOUR:
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # Accès autorisé
        access_log[-1]['authorized'] = True
        
        return f(*args, **kwargs)
    return decorated_function

def random_delay(min_seconds, max_seconds):
    """Attendre un délai aléatoire"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def create_secure_driver():
    """Créer un driver Chrome sécurisé pour VPS"""
    options = uc.ChromeOptions()
    
    # Mode headless pour VPS
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Protection supplémentaire
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # User agent Linux
    user_agents = [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    options.add_argument(f'--user-agent={random.choice(user_agents)}')
    
    # Profil isolé
    profile_path = f'/tmp/chrome-profile-{random.randint(1000, 9999)}'
    options.add_argument(f'--user-data-dir={profile_path}')
    
    driver = uc.Chrome(options=options, version_main=None)
    
    # Anti-détection avancée
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['de-DE', 'de', 'en-US', 'en']});
        Object.defineProperty(navigator, 'platform', {get: () => 'Linux x86_64'});
    """)
    
    return driver, profile_path

def login_leboncoin(driver, wait):
    """Se connecter à LeBonCoin"""
    try:
        print("🔐 Connexion en cours...")
        
        # Page d'accueil
        driver.get("https://www.leboncoin.fr")
        random_delay(3, 5)
        
        # Accepter cookies
        try:
            cookie_btn = driver.find_element(By.ID, 'didomi-notice-agree-button')
            cookie_btn.click()
            random_delay(2, 3)
        except:
            pass
        
        # Aller sur page de connexion
        driver.get("https://www.leboncoin.fr/deposer-une-annonce")
        random_delay(3, 5)
        
        # Si formulaire présent
        if "email" in driver.page_source and "password" in driver.page_source:
            # Email
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_field.clear()
            for char in LEBONCOIN_EMAIL:
                email_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            random_delay(1, 2)
            
            # Password
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            for char in LEBONCOIN_PASSWORD:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            random_delay(1, 2)
            
            # Submit
            submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_btn.click()
            
            print("✅ Connexion soumise")
            random_delay(5, 8)
            
        return True
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False

def solve_captcha(driver):
    """Résoudre CAPTCHA si présent"""
    try:
        if "On s'assure qu'on s'adresse bien à vous" in driver.page_source:
            print("🔐 CAPTCHA détecté")
            
            # Screenshot du captcha
            driver.save_screenshot('/tmp/captcha_page.png')
            print("📸 Screenshot sauvegardé: /tmp/captcha_page.png")
            
            # Pour l'instant, on attend
            print("⏳ CAPTCHA détecté - attente de 60s...")
            time.sleep(60)
            
            return True
    except:
        pass
    return False

@app.route('/health', methods=['GET'])
def health():
    """Endpoint public de santé"""
    return jsonify({
        'status': 'healthy',
        'server': 'VPS Hostinger',
        'ip': '31.97.53.91',
        'location': 'Allemagne',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/scrape', methods=['POST'])
@require_auth
def scrape_leboncoin():
    data = request.json
    url = data.get('url')
    
    if not url or 'leboncoin.fr' not in url:
        return jsonify({'error': 'URL LeBonCoin valide requise'}), 400
    
    # Log sécurisé
    print(f"\n[{datetime.now()}] Scraping autorisé depuis {request.remote_addr}")
    print(f"URL: {url}")
    
    driver = None
    profile_path = None
    
    try:
        # Créer driver sécurisé
        driver, profile_path = create_secure_driver()
        wait = WebDriverWait(driver, 30)
        
        # Connexion
        login_leboncoin(driver, wait)
        
        # Navigation vers annonce
        print("📄 Navigation vers l'annonce...")
        driver.get(url)
        random_delay(5, 10)
        
        # Vérifier CAPTCHA
        solve_captcha(driver)
        
        # Scroll naturel
        total_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(3):
            scroll_to = (total_height / 3) * (i + 1)
            driver.execute_script(f"window.scrollTo(0, {scroll_to});")
            random_delay(2, 4)
        
        # Extraction données
        print("📊 Extraction des données...")
        scraped_data = driver.execute_script("""
            const getTextContent = (selector) => {
                const element = document.querySelector(selector);
                return element ? element.textContent.trim() : null;
            };

            return {
                title: getTextContent('h1'),
                price: getTextContent('[data-qa-id="adview_price"]'),
                description: getTextContent('[data-qa-id="adview_description"]'),
                location: getTextContent('[data-qa-id="adview_location"]'),
                seller: getTextContent('[data-qa-id="adview_seller_name"]')
            };
        """)
        
        # Recherche téléphone
        phone_number = None
        try:
            phone_selectors = [
                "//button[contains(text(), 'Voir le numéro')]",
                "//button[contains(., 'numéro')]",
                "//button[contains(., 'Afficher le numéro')]"
            ]
            
            phone_btn = None
            for selector in phone_selectors:
                buttons = driver.find_elements(By.XPATH, selector)
                if buttons:
                    phone_btn = buttons[0]
                    break
            
            if phone_btn:
                driver.execute_script("arguments[0].scrollIntoView(true);", phone_btn)
                random_delay(2, 4)
                phone_btn.click()
                random_delay(3, 5)
                
                # Chercher numéro
                phone_number = driver.execute_script("""
                    const telLinks = document.querySelectorAll('a[href^="tel:"]');
                    if (telLinks.length > 0) {
                        return telLinks[0].href.replace('tel:', '').replace(/\\D/g, '');
                    }
                    
                    // Recherche dans le texte
                    const phoneRegex = /0[1-9](?:[\\s.-]?\\d{2}){4}/g;
                    const pageText = document.body.innerText || '';
                    const matches = pageText.match(phoneRegex);
                    
                    if (matches && matches.length > 0) {
                        return matches[0].replace(/\\D/g, '');
                    }
                    
                    return null;
                """)
                
                if phone_number:
                    print(f"✅ Numéro trouvé: {phone_number}")
                else:
                    print("❌ Numéro non trouvé")
                    
        except Exception as e:
            print(f"❌ Erreur recherche téléphone: {e}")
        
        # Screenshot final
        driver.save_screenshot('/tmp/scraping_final.png')
        
        print("✅ Scraping terminé!")
        
        return jsonify({
            'success': True,
            'data': {
                **scraped_data,
                'phone': phone_number
            },
            'scraped_from': 'VPS Hostinger (31.97.53.91)',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        if driver:
            driver.save_screenshot('/tmp/error.png')
        
        return jsonify({
            'success': False,
            'error': 'Erreur lors du scraping',
            'details': str(e)
        }), 500
        
    finally:
        if driver:
            driver.quit()
        if profile_path and os.path.exists(profile_path):
            os.system(f'rm -rf {profile_path}')

@app.route('/logs', methods=['GET'])
@require_auth
def get_logs():
    """Obtenir les logs d'accès"""
    recent_logs = access_log[-50:]
    return jsonify({
        'total_requests': len(access_log),
        'recent_logs': recent_logs
    })

@app.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    """Statistiques d'utilisation"""
    return jsonify({
        'total_requests': len(access_log),
        'authorized_requests': len([log for log in access_log if log['authorized']]),
        'rate_limits': dict(request_counts),
        'server': 'VPS Hostinger',
        'ip': '31.97.53.91'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🛡️  SCRAPER SÉCURISÉ SUR VPS HOSTINGER")
    print("="*60)
    print("📍 Serveur: VPS Ubuntu 24.04")
    print("🌐 IP: 31.97.53.91 (Allemagne)")
    print("📡 Port: 1372 (localhost uniquement)")
    print("\n⚠️  Configuration:")
    print(f"   - API Key configurée (ajoutez vos 3 chiffres)")
    print(f"   - Email: {LEBONCOIN_EMAIL}")
    print(f"   - Rate limit: {MAX_REQUESTS_PER_IP_PER_HOUR} req/heure/IP")
    print("\n📌 Endpoints:")
    print("   GET  /health (public)")
    print("   POST /scrape (auth: Bearer YOUR_API_KEY)")
    print("   GET  /logs (auth requise)")
    print("   GET  /stats (auth requise)")
    print("\n🔒 Accès sécurisé:")
    print("   ssh -L 1372:localhost:1372 root@31.97.53.91")
    print("   curl http://localhost:1372/health")
    print("=" * 60 + "\n")
    
    # Écoute uniquement sur localhost
    app.run(host='127.0.0.1', port=1372, debug=False)

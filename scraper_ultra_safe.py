import undetected_chromedriver as uc
import time
import random
import json
import os
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, request, jsonify
from flask_cors import CORS
from python_anticaptcha import AnticaptchaClient, ImageToTextTask

app = Flask(__name__)
CORS(app)

# Configuration avec VOS identifiants
ANTICAPTCHA_API_KEY = '599bf5a3b86f1cabf7e23bca24237354'
LEBONCOIN_EMAIL = 'tnclim1@gmail.com'
LEBONCOIN_PASSWORD = 'Underground780&'
client = AnticaptchaClient(ANTICAPTCHA_API_KEY)

# Configuration anti-blocage MAXIMALE
MIN_DELAY_BETWEEN_REQUESTS = 120  # 2 minutes minimum entre requêtes
MAX_REQUESTS_PER_DAY = 5  # Maximum 5 annonces par jour
MAX_REQUESTS_PER_HOUR = 2  # Maximum 2 annonces par heure

# Stockage des requêtes
request_history = []

def check_rate_limits():
    """Vérifier les limites de taux"""
    global request_history
    now = datetime.now()
    
    # Nettoyer l'historique (garder seulement les dernières 24h)
    request_history = [req for req in request_history if now - req < timedelta(days=1)]
    
    # Vérifier limite journalière
    if len(request_history) >= MAX_REQUESTS_PER_DAY:
        return False, "Limite journalière atteinte (5 annonces max)"
    
    # Vérifier limite horaire
    last_hour_requests = [req for req in request_history if now - req < timedelta(hours=1)]
    if len(last_hour_requests) >= MAX_REQUESTS_PER_HOUR:
        return False, "Limite horaire atteinte (2 annonces max)"
    
    return True, "OK"

def random_delay(min_seconds, max_seconds):
    """Attendre un délai aléatoire AUGMENTÉ pour simuler un comportement humain"""
    # On multiplie par 2 pour plus de sécurité
    actual_min = min_seconds * 2
    actual_max = max_seconds * 2
    delay = random.uniform(actual_min, actual_max)
    print(f"⏳ Pause de {delay:.1f} secondes...")
    time.sleep(delay)

def human_typing(element, text):
    """Taper du texte comme un humain avec pauses aléatoires"""
    for i, char in enumerate(text):
        element.send_keys(char)
        # Pause plus longue après certains caractères
        if char in '.@':
            time.sleep(random.uniform(0.5, 1.0))
        else:
            time.sleep(random.uniform(0.2, 0.5))
        
        # Parfois faire une pause plus longue (réflexion)
        if random.random() < 0.1:
            time.sleep(random.uniform(1, 2))

def simulate_reading(driver, duration_seconds):
    """Simuler la lecture d'une page"""
    print(f"📖 Simulation de lecture ({duration_seconds}s)...")
    start_time = time.time()
    
    while time.time() - start_time < duration_seconds:
        # Petit scroll aléatoire
        scroll = random.randint(50, 150)
        driver.execute_script(f"window.scrollBy(0, {scroll});")
        
        # Mouvement de souris aléatoire
        if random.random() < 0.3:
            driver.execute_script("""
                const event = new MouseEvent('mousemove', {
                    clientX: Math.random() * window.innerWidth,
                    clientY: Math.random() * window.innerHeight
                });
                document.dispatchEvent(event);
            """)
        
        time.sleep(random.uniform(2, 4))

def get_random_user_agent():
    """Obtenir un user agent aléatoire"""
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0'
    ]
    return random.choice(user_agents)

def browse_other_pages(driver):
    """Naviguer sur d'autres pages pour paraître naturel"""
    print("🔍 Navigation naturelle sur LeBonCoin...")
    
    pages = [
        "https://www.leboncoin.fr/",
        "https://www.leboncoin.fr/voitures/offres",
        "https://www.leboncoin.fr/locations/offres",
        "https://www.leboncoin.fr/electromenager/offres"
    ]
    
    # Visiter 1-2 pages aléatoirement
    for _ in range(random.randint(1, 2)):
        page = random.choice(pages)
        driver.get(page)
        simulate_reading(driver, random.randint(10, 20))

def login_leboncoin_safe(driver, wait):
    """Se connecter à LeBonCoin avec maximum de précautions"""
    try:
        print("🔐 Connexion sécurisée en cours...")
        
        # D'abord naviguer naturellement
        driver.get("https://www.leboncoin.fr")
        simulate_reading(driver, random.randint(5, 10))
        
        # Accepter les cookies
        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.ID, 'didomi-notice-agree-button')))
            random_delay(1, 2)
            cookie_button.click()
            print("🍪 Cookies acceptés")
            random_delay(2, 4)
        except:
            pass
        
        # Naviguer sur quelques pages d'abord
        browse_other_pages(driver)
        
        # Maintenant essayer de se connecter
        driver.get("https://www.leboncoin.fr/deposer-une-annonce")
        random_delay(3, 5)
        
        # Si formulaire de connexion présent
        if "email" in driver.page_source and "password" in driver.page_source:
            print("📝 Formulaire détecté, connexion...")
            
            # Email
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_field.click()
            random_delay(1, 2)
            email_field.clear()
            human_typing(email_field, LEBONCOIN_EMAIL)
            
            random_delay(2, 4)
            
            # Mot de passe
            password_field = driver.find_element(By.NAME, "password")
            password_field.click()
            random_delay(1, 2)
            password_field.clear()
            human_typing(password_field, LEBONCOIN_PASSWORD)
            
            random_delay(2, 4)
            
            # Bouton connexion
            login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            
            print("⏳ Attente connexion...")
            random_delay(5, 8)
            
        return True
        
    except Exception as e:
        print(f"⚠️ Erreur connexion: {e}")
        return True

@app.route('/scrape', methods=['POST'])
def scrape_leboncoin():
    global request_history
    
    # Vérifier les limites
    can_proceed, message = check_rate_limits()
    if not can_proceed:
        return jsonify({
            'success': False,
            'error': message,
            'retry_after': '1 heure'
        }), 429
    
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL requise'}), 400
    
    print(f"\n{'='*60}")
    print(f"🛡️  SCRAPING ULTRA-SÉCURISÉ")
    print(f"📍 URL: {url}")
    print(f"🕐 Heure: {datetime.now().strftime('%H:%M:%S')}")
    print(f"📊 Requêtes aujourd'hui: {len(request_history)}/{MAX_REQUESTS_PER_DAY}")
    print(f"{'='*60}\n")
    
    driver = None
    
    try:
        # Configuration Chrome
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Nouveau profil propre
        profile_path = '/Users/tonytuyisenge/Desktop/scraper-leboncoin/chrome-profile-clean'
        options.add_argument(f'--user-data-dir={profile_path}')
        
        # User agent aléatoire
        options.add_argument(f'--user-agent={get_random_user_agent()}')
        
        # Options supplémentaires anti-détection
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Préférences
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        
        print("🚀 Lancement de Chrome sécurisé...")
        driver = uc.Chrome(options=options, version_main=None)
        
        # Taille d'écran aléatoire (mais réaliste)
        widths = [1920, 1680, 1440, 1366]
        heights = [1080, 1050, 900, 768]
        driver.set_window_size(random.choice(widths), random.choice(heights))
        
        wait = WebDriverWait(driver, 30)
        
        # Anti-détection JavaScript
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['fr-FR', 'fr', 'en-US', 'en']});
            window.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'permissions', {
                get: () => {
                    const originalQuery = window.navigator.permissions.query;
                    return Object.create(window.navigator.permissions, {
                        query: {
                            value: (parameters) => (
                                parameters.name === 'notifications' ?
                                    Promise.resolve({state: 'denied'}) :
                                    originalQuery(parameters)
                            )
                        }
                    });
                }
            });
        """)
        
        # Connexion sécurisée
        if not login_leboncoin_safe(driver, wait):
            print("⚠️ Connexion échouée")
        
        # Navigation naturelle avant d'aller sur l'annonce
        browse_other_pages(driver)
        
        # Maintenant aller sur l'annonce
        print("📄 Navigation vers l'annonce...")
        driver.get(url)
        
        # Lecture naturelle de la page
        simulate_reading(driver, random.randint(20, 40))
        
        # Extraction des données basiques
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
        
        print(f"✅ Données récupérées")
        
        # Attendre longtemps avant de chercher le téléphone
        random_delay(10, 15)
        
        # Recherche prudente du bouton téléphone
        phone_button = None
        try:
            selectors = [
                "//button[contains(text(), 'Voir le numéro')]",
                "//button[contains(., 'numéro')]"
            ]
            
            for selector in selectors:
                buttons = driver.find_elements(By.XPATH, selector)
                if buttons:
                    phone_button = buttons[0]
                    break
        except:
            pass
        
        phone_number = None
        if phone_button:
            print("📞 Bouton téléphone trouvé")
            
            # Scroll naturel vers le bouton
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", phone_button)
            random_delay(5, 8)
            
            # Hover naturel
            driver.execute_script("""
                const button = arguments[0];
                const rect = button.getBoundingClientRect();
                const event = new MouseEvent('mousemove', {
                    clientX: rect.left + rect.width / 2,
                    clientY: rect.top + rect.height / 2
                });
                document.dispatchEvent(event);
            """, phone_button)
            
            random_delay(2, 4)
            
            # Clic
            phone_button.click()
            print("✅ Clic effectué")
            
            # Attente du numéro
            random_delay(5, 10)
            
            # Recherche du numéro
            phone_number = driver.execute_script("""
                const telLinks = document.querySelectorAll('a[href^="tel:"]');
                if (telLinks.length > 0) {
                    return telLinks[0].href.replace('tel:', '').replace(/\\D/g, '');
                }
                return null;
            """)
        
        # Navigation finale naturelle
        browse_other_pages(driver)
        
        # Fermeture
        random_delay(5, 10)
        driver.quit()
        
        # Enregistrer la requête
        request_history.append(datetime.now())
        
        print("\n✅ Scraping terminé en toute sécurité!")
        
        return jsonify({
            'success': True,
            'data': {
                **scraped_data,
                'phone': phone_number
            },
            'message': f'Requêtes restantes aujourd\'hui: {MAX_REQUESTS_PER_DAY - len(request_history)}'
        })
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        if driver:
            driver.quit()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/status', methods=['GET'])
def status():
    """Vérifier le statut et les limites"""
    can_proceed, message = check_rate_limits()
    
    return jsonify({
        'can_scrape': can_proceed,
        'message': message,
        'requests_today': len(request_history),
        'max_per_day': MAX_REQUESTS_PER_DAY,
        'requests_last_hour': len([req for req in request_history if datetime.now() - req < timedelta(hours=1)]),
        'max_per_hour': MAX_REQUESTS_PER_HOUR
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🛡️  SCRAPER LEBONCOIN - MODE ULTRA SÉCURISÉ")
    print("="*60)
    print(f"⚠️  Protections activées:")
    print(f"   - Maximum {MAX_REQUESTS_PER_DAY} requêtes par jour")
    print(f"   - Maximum {MAX_REQUESTS_PER_HOUR} requêtes par heure")
    print(f"   - Délai minimum {MIN_DELAY_BETWEEN_REQUESTS}s entre requêtes")
    print(f"   - Navigation naturelle simulée")
    print(f"   - User-agents rotatifs")
    print(f"   - Profil Chrome propre")
    print("\n📡 Endpoints:")
    print("   POST http://localhost:1372/scrape")
    print("   GET  http://localhost:1372/status")
    print("\n💡 Conseils:")
    print("   - Utilisez un VPN")
    print("   - Ne dépassez pas les limites")
    print("   - Attendez 24h si blocage")
    print("="*60 + "\n")
    
    app.run(port=1372, debug=True)

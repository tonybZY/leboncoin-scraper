import undetected_chromedriver as uc
import time
import random
import json
import os
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

# Configuration anti-blocage
MIN_DELAY_BETWEEN_REQUESTS = 30  # Attendre minimum 30 secondes entre chaque requête
last_request_time = 0

def random_delay(min_seconds, max_seconds):
    """Attendre un délai aléatoire pour simuler un comportement humain"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def human_typing(element, text):
    """Taper du texte comme un humain"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def move_mouse_randomly(driver):
    """Bouger la souris aléatoirement"""
    try:
        driver.execute_script("""
            const event = new MouseEvent('mousemove', {
                view: window,
                bubbles: true,
                cancelable: true,
                clientX: Math.random() * window.innerWidth,
                clientY: Math.random() * window.innerHeight
            });
            document.dispatchEvent(event);
        """)
    except:
        pass

def login_leboncoin(driver, wait):
    """Se connecter à LeBonCoin avec protection anti-détection"""
    try:
        print("🔐 Processus de connexion...")
        
        # D'abord aller sur la page d'accueil
        driver.get("https://www.leboncoin.fr")
        random_delay(3, 5)
        
        # Accepter les cookies
        try:
            cookie_button = driver.find_element(By.ID, 'didomi-notice-agree-button')
            cookie_button.click()
            print("🍪 Cookies acceptés")
            random_delay(2, 3)
        except:
            pass
        
        # Cliquer sur "Se connecter" dans le menu
        try:
            # Chercher le bouton de connexion
            login_link = driver.find_element(By.XPATH, "//a[contains(@href, 'compte') or contains(text(), 'connecter')]")
            login_link.click()
            random_delay(2, 3)
        except:
            # Alternative : aller directement sur la page qui force la connexion
            driver.get("https://www.leboncoin.fr/deposer-une-annonce")
            random_delay(2, 3)
        
        # Vérifier si on est sur la page de connexion
        if "email" in driver.page_source and "password" in driver.page_source:
            print("📝 Formulaire de connexion détecté")
            
            # Bouger la souris
            move_mouse_randomly(driver)
            
            # Trouver et remplir l'email
            try:
                email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
                email_field.click()
                random_delay(0.5, 1)
                email_field.clear()
                human_typing(email_field, LEBONCOIN_EMAIL)
                print("✅ Email saisi")
                random_delay(1, 2)
            except Exception as e:
                print(f"❌ Erreur email: {e}")
                
            # Trouver et remplir le mot de passe
            try:
                password_field = driver.find_element(By.NAME, "password")
                password_field.click()
                random_delay(0.5, 1)
                password_field.clear()
                human_typing(password_field, LEBONCOIN_PASSWORD)
                print("✅ Mot de passe saisi")
                random_delay(1, 2)
            except Exception as e:
                print(f"❌ Erreur mot de passe: {e}")
            
            # Bouger la souris avant de cliquer
            move_mouse_randomly(driver)
            
            # Cliquer sur le bouton de connexion
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                login_button.click()
                print("✅ Clic sur connexion")
            except:
                # Alternative
                driver.find_element(By.XPATH, "//button[contains(text(), 'connecter')]").click()
            
            print("⏳ Attente de la connexion...")
            time.sleep(5)
            
            # Vérifier si CAPTCHA
            if "On s'assure qu'on s'adresse bien à vous" in driver.page_source:
                print("🔐 CAPTCHA détecté")
                solve_leboncoin_captcha(driver)
                
            # Vérifier si connecté
            if "mon-compte" in driver.current_url or "deposer" in driver.current_url:
                print("✅ Connexion réussie!")
                return True
            else:
                print("❓ Statut de connexion incertain")
                return True  # On continue quand même
        else:
            print("✅ Déjà connecté ou page de connexion non trouvée")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {str(e)}")
        # On continue quand même
        return True

def solve_leboncoin_captcha(driver):
    """Résoudre le CAPTCHA de LeBonCoin si présent"""
    try:
        if "On s'assure qu'on s'adresse bien à vous" in driver.page_source:
            print("🔐 CAPTCHA détecté, résolution en cours...")
            
            try:
                time.sleep(2)
                
                # Trouver l'élément du captcha
                captcha_element = None
                for selector in ['img[src*="captcha"]', 'canvas', '[class*="puzzle"]', 'img[alt*="puzzle"]']:
                    try:
                        captcha_element = driver.find_element(By.CSS_SELECTOR, selector)
                        if captcha_element:
                            break
                    except:
                        continue
                
                if captcha_element:
                    captcha_element.screenshot('captcha_temp.png')
                    print("📸 Screenshot du CAPTCHA pris")
                    
                    with open('captcha_temp.png', 'rb') as f:
                        task = ImageToTextTask(f)
                    
                    print("📤 Envoi à Anti-Captcha...")
                    job = client.createTask(task)
                    job.join()
                    
                    solution = job.get_solution_response()
                    print(f"✅ Solution reçue: {solution}")
                    
                    if solution and solution.isdigit():
                        slider = driver.find_element(By.CSS_SELECTOR, '[class*="slider"], [class*="drag"], button[class*="slide"]')
                        action = uc.ActionChains(driver)
                        action.click_and_hold(slider).move_by_offset(int(solution), 0).release().perform()
                        print("✅ Solution appliquée")
                    
                    if os.path.exists('captcha_temp.png'):
                        os.remove('captcha_temp.png')
                else:
                    print("❌ CAPTCHA non résolu automatiquement")
                    print("⚠️ Résolvez le CAPTCHA manuellement dans les 60 secondes!")
                    time.sleep(60)
                
            except Exception as e:
                print(f"❌ Erreur résolution CAPTCHA: {str(e)}")
                print("⚠️ Résolvez le CAPTCHA manuellement dans les 60 secondes!")
                time.sleep(60)
            
            time.sleep(5)
            return True
            
    except Exception as e:
        print(f"Pas de CAPTCHA détecté: {str(e)}")
    
    return False

@app.route('/scrape', methods=['POST'])
def scrape_leboncoin():
    global last_request_time
    
    # Protection anti-spam
    current_time = time.time()
    if current_time - last_request_time < MIN_DELAY_BETWEEN_REQUESTS:
        wait_time = MIN_DELAY_BETWEEN_REQUESTS - (current_time - last_request_time)
        print(f"⏳ Protection anti-blocage: attente de {wait_time:.0f} secondes...")
        time.sleep(wait_time)
    
    last_request_time = time.time()
    
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL requise'}), 400
    
    print(f"\n{'='*60}")
    print(f"🔍 DÉMARRAGE DU SCRAPING")
    print(f"📍 URL: {url}")
    print(f"{'='*60}\n")
    
    driver = None
    phone_number = None
    
    try:
        # Configuration Chrome avec protection maximale
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        
        # Profil Chrome persistant
        username = os.path.expanduser('~').split('/')[-1]
        profile_path = f'/Users/{username}/Desktop/scraper-leboncoin/chrome-profile-scraping'
        options.add_argument(f'--user-data-dir={profile_path}')
        print(f"📁 Profil Chrome: {profile_path}")
        
        # User agent réaliste
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Désactiver les notifications
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        
        # Lancer Chrome
        print("🚀 Lancement de Chrome...")
        driver = uc.Chrome(options=options, version_main=None)
        driver.maximize_window()
        wait = WebDriverWait(driver, 30)
        
        # Supprimer webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Se connecter à LeBonCoin
        if not login_leboncoin(driver, wait):
            print("⚠️ Problème de connexion, on continue quand même...")
        
        # Attendre un peu avant de naviguer (comportement humain)
        random_delay(3, 5)
        
        # Navigation vers l'annonce avec comportement humain
        print("🏠 Navigation vers l'annonce...")
        driver.get(url)
        
        # Attente variable
        random_delay(4, 7)
        
        # Vérifier les CAPTCHAs
        solve_leboncoin_captcha(driver)
        
        # Comportement humain : bouger la souris
        for _ in range(3):
            move_mouse_randomly(driver)
            random_delay(0.5, 1)
        
        # Défilement naturel de la page
        print("📜 Lecture de l'annonce...")
        total_height = driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        
        while current_position < total_height * 0.8:
            # Défilement variable
            scroll_distance = random.randint(100, 300)
            driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
            current_position += scroll_distance
            
            # Pauses variables
            if random.random() < 0.3:  # 30% de chance de pause longue
                random_delay(1.5, 3)
            else:
                random_delay(0.3, 0.8)
            
            # Parfois bouger la souris
            if random.random() < 0.2:
                move_mouse_randomly(driver)
        
        # Récupérer les données
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
                date: getTextContent('[data-qa-id="adview_date"]'),
                seller: getTextContent('[data-qa-id="adview_seller_name"]'),
                category: getTextContent('[data-qa-id="adview_category"]')
            };
        """)
        
        print(f"✅ Titre: {scraped_data.get('title')}")
        print(f"💰 Prix: {scraped_data.get('price')}")
        
        # Recherche du bouton téléphone avec délai humain
        print("\n📞 Recherche du bouton téléphone...")
        random_delay(3, 5)
        
        phone_button = None
        selectors = [
            "//button[contains(text(), 'Voir le numéro')]",
            "//button[contains(., 'numéro')]",
            "//button[contains(., 'Afficher le numéro')]",
            "//button[contains(@class, 'phone')]",
            "//span[contains(text(), 'Voir le numéro')]/..",
            "//button[contains(., 'téléphone')]"
        ]
        
        for selector in selectors:
            try:
                buttons = driver.find_elements(By.XPATH, selector)
                if buttons:
                    phone_button = buttons[0]
                    print(f"✅ Bouton trouvé!")
                    break
            except:
                continue
        
        if phone_button:
            # Comportement humain avant le clic
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", phone_button)
            random_delay(2, 3)
            
            # Hover
            driver.execute_script("""
                const button = arguments[0];
                const event = new MouseEvent('mouseover', {
                    view: window,
                    bubbles: true,
                    cancelable: true
                });
                button.dispatchEvent(event);
            """, phone_button)
            
            random_delay(1, 2)
            move_mouse_randomly(driver)
            random_delay(0.5, 1)
            
            # Clic
            phone_button.click()
            print("✅ Clic sur le bouton téléphone")
            
            # Attente du chargement
            random_delay(4, 6)
            
            # Vérifier CAPTCHA après clic
            solve_leboncoin_captcha(driver)
            
            # Recherche du numéro
            random_delay(2, 4)
            
            phone_number = driver.execute_script("""
                // Recherche du numéro de téléphone
                const telLinks = document.querySelectorAll('a[href^="tel:"]');
                if (telLinks.length > 0) {
                    const number = telLinks[0].href.replace('tel:', '').replace(/\\D/g, '');
                    if (number.length === 10) return number;
                }
                
                const phoneRegex = /0[1-9](?:[\\s.-]?\\d{2}){4}/g;
                const pageText = document.body.innerText || '';
                const matches = pageText.match(phoneRegex);
                
                if (matches && matches.length > 0) {
                    for (const match of matches) {
                        const cleaned = match.replace(/\\D/g, '');
                        if (cleaned.length === 10 && cleaned.startsWith('0')) {
                            return cleaned;
                        }
                    }
                }
                
                return null;
            """)
            
            if phone_number:
                print(f"✅ Numéro trouvé: {phone_number}")
            else:
                print("❌ Numéro non trouvé")
        else:
            print("❌ Bouton téléphone introuvable")
        
        # Screenshot final
        driver.save_screenshot('scraping_final.png')
        print("📸 Capture finale sauvegardée")
        
        # Attente finale (comportement humain)
        random_delay(3, 5)
        driver.quit()
        
        print(f"\n{'='*60}")
        print("✅ SCRAPING TERMINÉ AVEC SUCCÈS!")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'data': {
                **scraped_data,
                'phone': phone_number
            },
            'url': url
        })
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        if driver:
            driver.save_screenshot('error_screenshot.png')
            driver.quit()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'url': url
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """Endpoint de test"""
    try:
        balance = client.getBalance()
        return jsonify({
            'status': 'OK',
            'anticaptcha_balance': f"${balance}",
            'email': LEBONCOIN_EMAIL,
            'message': 'Serveur prêt!'
        })
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVEUR LEBONCOIN SCRAPER - VERSION ANTI-BLOCAGE")
    print("="*60)
    print(f"📡 Port: 1372")
    print(f"🔑 Clé API: {ANTICAPTCHA_API_KEY[:10]}...")
    print(f"📧 Email: {LEBONCOIN_EMAIL}")
    print(f"🔐 Mot de passe: {'*' * len(LEBONCOIN_PASSWORD)}")
    print(f"⏱️  Délai minimum entre requêtes: {MIN_DELAY_BETWEEN_REQUESTS}s")
    
    try:
        balance = client.getBalance()
        print(f"💰 Solde Anti-Captcha: ${balance}")
        print("✅ Connexion Anti-Captcha OK")
    except Exception as e:
        print(f"❌ Erreur Anti-Captcha: {str(e)}")
    
    print("\n📌 Endpoints:")
    print("   POST http://localhost:1372/scrape")
    print("   GET  http://localhost:1372/test")
    print("\n⚠️  Protection anti-blocage activée:")
    print("   - Délais aléatoires entre actions")
    print("   - Comportement humain simulé")
    print("   - Minimum 30s entre chaque requête")
    print("\n" + "="*60 + "\n")
    
    app.run(port=1372, debug=True)
import undetected_chromedriver as uc
import time
import random
import json
import os
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
import base64
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration Anti-Captcha - Remplacez par votre clé API
ANTICAPTCHA_API_KEY = '599bf5a3b86f1cabf7e23bca24237354'  # Votre clé API

class CapSolver:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.capsolver.com"
    
    def solve_image_captcha(self, image_base64):
        """Résoudre un captcha image"""
        data = {
            "clientKey": self.api_key,
            "task": {
                "type": "ImageToTextTask",
                "body": image_base64
            }
        }
        
        # Créer la tâche
        response = requests.post(f"{self.base_url}/createTask", json=data)
        result = response.json()
        
        if result.get("errorId") != 0:
            raise Exception(f"Erreur CapSolver: {result.get('errorDescription')}")
        
        task_id = result["taskId"]
        
        # Attendre la solution
        for i in range(30):  # 30 secondes max
            time.sleep(2)
            check_data = {
                "clientKey": self.api_key,
                "taskId": task_id
            }
            response = requests.post(f"{self.base_url}/getTaskResult", json=check_data)
            result = response.json()
            
            if result.get("status") == "ready":
                return result["solution"]["text"]
        
        raise Exception("Timeout résolution CAPTCHA")
    
    def solve_recaptcha(self, website_url, site_key):
        """Résoudre un reCAPTCHA"""
        data = {
            "clientKey": self.api_key,
            "task": {
                "type": "ReCaptchaV2TaskProxyless",
                "websiteURL": website_url,
                "websiteKey": site_key
            }
        }
        
        response = requests.post(f"{self.base_url}/createTask", json=data)
        result = response.json()
        
        if result.get("errorId") != 0:
            raise Exception(f"Erreur CapSolver: {result.get('errorDescription')}")
        
        task_id = result["taskId"]
        
        # Attendre la solution
        for i in range(60):  # 60 secondes max pour reCAPTCHA
            time.sleep(3)
            check_data = {
                "clientKey": self.api_key,
                "taskId": task_id
            }
            response = requests.post(f"{self.base_url}/getTaskResult", json=check_data)
            result = response.json()
            
            if result.get("status") == "ready":
                return result["solution"]["gRecaptchaResponse"]
        
        raise Exception("Timeout résolution reCAPTCHA")

# Initialiser CapSolver
solver = CapSolver(CAPSOLVER_API_KEY)

def random_delay(min_seconds, max_seconds):
    """Attendre un délai aléatoire pour simuler un comportement humain"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def solve_leboncoin_captcha(driver):
    """Résoudre le CAPTCHA de LeBonCoin si présent"""
    try:
        # Vérifier si on est sur la page de vérification
        if "On s'assure qu'on s'adresse bien à vous" in driver.page_source:
            print("🔐 CAPTCHA détecté, résolution en cours...")
            
            # Méthode 1: Captcha puzzle/slider LeBonCoin
            try:
                # Attendre que l'image soit visible
                time.sleep(2)
                
                # Prendre un screenshot du captcha
                captcha_element = driver.find_element(By.CSS_SELECTOR, 'img[src*="captcha"], canvas, [class*="puzzle"]')
                captcha_element.screenshot('captcha_temp.png')
                
                # Convertir en base64
                with open('captcha_temp.png', 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                # Résoudre avec CapSolver
                print("📤 Envoi du CAPTCHA à CapSolver...")
                solution = solver.solve_image_captcha(image_base64)
                print(f"✅ Solution reçue: {solution}")
                
                # Appliquer la solution (dépend du type de captcha)
                # Pour un puzzle slider, solution contient généralement la distance
                if solution.isdigit():
                    slider = driver.find_element(By.CSS_SELECTOR, '[class*="slider"], [class*="drag"]')
                    action = uc.ActionChains(driver)
                    action.click_and_hold(slider).move_by_offset(int(solution), 0).release().perform()
                
                # Nettoyer
                os.remove('captcha_temp.png')
                
            except Exception as e:
                print(f"Erreur CAPTCHA image: {e}")
                
                # Méthode 2: reCAPTCHA
                try:
                    # Chercher le sitekey
                    sitekey = driver.execute_script("""
                        const elements = document.querySelectorAll('[data-sitekey]');
                        return elements.length > 0 ? elements[0].getAttribute('data-sitekey') : null;
                    """)
                    
                    if sitekey:
                        print(f"🔍 reCAPTCHA détecté, sitekey: {sitekey}")
                        
                        # Résoudre avec CapSolver
                        print("📤 Résolution du reCAPTCHA...")
                        recaptcha_response = solver.solve_recaptcha(driver.current_url, sitekey)
                        
                        # Injecter la solution
                        driver.execute_script(f"""
                            document.getElementById('g-recaptcha-response').innerHTML = '{recaptcha_response}';
                            if (window.___grecaptcha_cfg) {{
                                Object.entries(window.___grecaptcha_cfg.clients).forEach(([key, client]) => {{
                                    if (client.callback) {{
                                        client.callback('{recaptcha_response}');
                                    }}
                                }});
                            }}
                        """)
                        
                        print("✅ reCAPTCHA résolu")
                        
                        # Soumettre si nécessaire
                        try:
                            submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], button[class*="submit"]')
                            submit_btn.click()
                        except:
                            pass
                            
                except Exception as e:
                    print(f"Erreur reCAPTCHA: {e}")
            
            # Attendre le rechargement
            time.sleep(5)
            return True
            
    except Exception as e:
        print(f"Pas de CAPTCHA ou erreur: {e}")
    
    return False

@app.route('/scrape', methods=['POST'])
def scrape_leboncoin():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL requise'}), 400
    
    print(f"🔍 Démarrage du scraping: {url}")
    
    driver = None
    phone_number = None
    
    try:
        # Configuration Chrome
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Profil dédié
        username = os.path.expanduser('~').split('/')[-1]
        profile_path = f'/Users/{username}/Desktop/scraper-leboncoin/chrome-profile'
        options.add_argument(f'--user-data-dir={profile_path}')
        
        # User agent
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        # Lancer Chrome
        print("🚀 Lancement de Chrome...")
        driver = uc.Chrome(options=options, version_main=None)
        driver.maximize_window()
        
        # Navigation naturelle via Google
        print("📱 Navigation...")
        driver.get('https://www.google.fr')
        random_delay(2, 3)
        
        # Aller sur l'annonce
        driver.get(url)
        random_delay(3, 5)
        
        # Gérer les CAPTCHAs
        if solve_leboncoin_captcha(driver):
            print("✅ CAPTCHA initial résolu")
            random_delay(2, 3)
        
        # Cookies
        try:
            cookie_btn = driver.find_element(By.ID, 'didomi-notice-agree-button')
            cookie_btn.click()
            print("🍪 Cookies acceptés")
            random_delay(1, 2)
        except:
            pass
        
        # Défiler naturellement
        print("📜 Lecture de l'annonce...")
        height = driver.execute_script("return document.body.scrollHeight")
        for i in range(0, int(height * 0.7), random.randint(200, 400)):
            driver.execute_script(f"window.scrollTo(0, {i});")
            random_delay(0.3, 0.8)
        
        # Récupérer les données
        print("📊 Extraction des données...")
        scraped_data = driver.execute_script("""
            const get = (selector) => {
                const el = document.querySelector(selector);
                return el ? el.textContent.trim() : null;
            };
            
            return {
                title: get('h1'),
                price: get('[data-qa-id="adview_price"]'),
                description: get('[data-qa-id="adview_description"]'),
                location: get('[data-qa-id="adview_location"]'),
                date: get('[data-qa-id="adview_date"]'),
                seller: get('[data-qa-id="adview_seller_name"]')
            };
        """)
        
        # Chercher le bouton téléphone
        print("📞 Recherche du téléphone...")
        phone_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Voir le numéro')]")
        
        if phone_buttons:
            btn = phone_buttons[0]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            random_delay(2, 3)
            
            # Cliquer
            btn.click()
            print("✅ Clic sur le bouton")
            random_delay(3, 5)
            
            # Gérer un éventuel nouveau CAPTCHA
            if solve_leboncoin_captcha(driver):
                print("✅ CAPTCHA après clic résolu")
                random_delay(2, 3)
            
            # Extraire le numéro
            phone_number = driver.execute_script("""
                // Liens tel:
                const telLinks = document.querySelectorAll('a[href^="tel:"]');
                if (telLinks.length > 0) {
                    return telLinks[0].href.replace('tel:', '').replace(/\\D/g, '');
                }
                
                // Regex dans le texte
                const phoneRegex = /0[1-9](?:[\\s.-]?\\d{2}){4}/g;
                const text = document.body.innerText;
                const matches = text.match(phoneRegex);
                
                if (matches) {
                    return matches[0].replace(/\\D/g, '');
                }
                
                return null;
            """)
            
            if phone_number:
                print(f"✅ Numéro trouvé: {phone_number}")
            else:
                print("❌ Numéro non trouvé")
        
        # Screenshot final
        driver.save_screenshot('result.png')
        
        # Fermer
        driver.quit()
        
        return jsonify({
            'success': True,
            'data': {
                **scraped_data,
                'phone': phone_number
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        if driver:
            driver.quit()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Serveur LeBonCoin Scraper")
    print("📡 Port: 1372")
    print("🔐 Anti-Captcha configuré")
    print(f"💰 Clé API: {ANTICAPTCHA_API_KEY[:10]}...")
    
    try:
        balance = client.getBalance()
        print(f"💳 Solde Anti-Captcha: ${balance}")
    except:
        print("⚠️  Vérifiez votre clé API ou ajoutez du crédit")
    
    app.run(port=1372, debug=True)
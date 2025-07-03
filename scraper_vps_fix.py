# scraper_vps_fix.py - Version spéciale pour VPS avec problème Chrome

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

# Configuration
LEBONCOIN_EMAIL = 'tnclim1@gmail.com'
LEBONCOIN_PASSWORD = 'Underground780&'
MIN_DELAY_BETWEEN_REQUESTS = 30
last_request_time = 0

def test_chrome():
    """Teste si Chrome fonctionne"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.quit()
        return True
    except:
        return False

@app.route('/scrape', methods=['POST'])
def scrape_leboncoin():
    global last_request_time
    
    # Protection anti-spam
    current_time = time.time()
    if current_time - last_request_time < MIN_DELAY_BETWEEN_REQUESTS:
        wait_time = MIN_DELAY_BETWEEN_REQUESTS - (current_time - last_request_time)
        time.sleep(wait_time)
    
    last_request_time = time.time()
    
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL requise'}), 400
    
    print(f"\n🔍 SCRAPING: {url}")
    
    # Teste si Chrome fonctionne
    if test_chrome():
        print("✅ Chrome disponible - mode complet")
        # Utilise le code complet avec Chrome
        from scraper_anticaptcha import scrape_leboncoin as scrape_full
        return scrape_full()
    else:
        print("⚠️ Chrome indisponible - mode basique")
        # Mode basique sans Chrome
        try:
            # Utilise requests pour récupérer la page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraction basique des données
            title = soup.find('h1').text if soup.find('h1') else 'Non trouvé'
            price = soup.find('span', class_='text-headline-2') 
            price_text = price.text if price else 'Prix non trouvé'
            
            print(f"📊 Titre: {title}")
            print(f"💰 Prix: {price_text}")
            
            return jsonify({
                'success': True,
                'data': {
                    'title': title,
                    'price': price_text,
                    'description': 'Mode basique - Chrome non disponible',
                    'phone': None,
                    'mode': 'basic'
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
    chrome_status = "✅ Disponible" if test_chrome() else "❌ Non disponible"
    return jsonify({
        'status': 'OK',
        'chrome': chrome_status,
        'message': 'Serveur prêt!',
        'mode': 'full' if test_chrome() else 'basic'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVEUR LEBONCOIN - VERSION VPS FIX")
    print("="*60)
    print(f"📡 Port: 1373")
    print(f"🔧 Test Chrome en cours...")
    
    if test_chrome():
        print("✅ Chrome disponible - Mode complet activé")
    else:
        print("⚠️ Chrome non disponible - Mode basique activé")
    
    print("\n📌 Endpoints:")
    print("   POST http://localhost:1373/scrape")
    print("   GET  http://localhost:1373/test")
    print("\n" + "="*60 + "\n")
    
    app.run(port=1373, debug=True, host='0.0.0.0')

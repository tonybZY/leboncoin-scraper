from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Configuration
ANTICAPTCHA_API_KEY = '599bf5a3b86f1cabf7e23bca24237354'
LEBONCOIN_EMAIL = 'tnclim1@gmail.com'
LEBONCOIN_PASSWORD = 'Underground780&'

@app.route('/status', methods=['GET'])
def status():
    """Endpoint de statut pour vérifier que l'API fonctionne"""
    return jsonify({
        'status': 'online',
        'service': 'LeBonCoin Scraper',
        'version': '1.0',
        'endpoints': {
            '/status': 'GET - Statut du service',
            '/scrape': 'POST - Scraper une annonce',
            '/test': 'GET - Test simple'
        }
    })

@app.route('/test', methods=['GET'])
def test():
    """Endpoint de test"""
    return jsonify({
        'message': 'Scraper LeBonCoin opérationnel!',
        'config': {
            'email': LEBONCOIN_EMAIL,
            'anticaptcha_key': ANTICAPTCHA_API_KEY[:10] + '...'
        }
    })

@app.route('/scrape', methods=['POST'])
def scrape():
    """Endpoint principal de scraping"""
    data = request.json
    url = data.get('url') if data else None
    
    if not url:
        return jsonify({'error': 'URL requise'}), 400
    
    # Pour l'instant, juste retourner un message de test
    return jsonify({
        'success': True,
        'message': 'Scraper en cours de configuration',
        'url': url,
        'note': 'Le scraping complet sera activé après les tests'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 1372))
    app.run(host='0.0.0.0', port=port, debug=False)
    print(f"🚀 Scraper démarré sur le port {port}")

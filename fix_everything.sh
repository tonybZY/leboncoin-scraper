#!/bin/bash
echo "🔧 RÉPARATION COMPLÈTE DU SERVEUR"
echo "=================================="

# 1. Mettre à jour le système
apt-get update -y

# 2. Installer Python et pip correctement
apt-get install -y python3 python3-pip python3-venv

# 3. Créer un environnement virtuel
cd /root/leboncoin-scraper
python3 -m venv venv
source venv/bin/activate

# 4. Installer les packages Python
pip install --upgrade pip
pip install flask flask-cors selenium requests beautifulsoup4

# 5. Installer Chrome et Chromedriver
apt-get install -y wget curl unzip

# Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# Chromedriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
wget -N https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION} -P ~/
CHROMEDRIVER_VERSION=$(cat ~/LATEST_RELEASE_${CHROME_VERSION})
wget -N https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip -P ~/
unzip ~/chromedriver_linux64.zip -d ~/
rm ~/chromedriver_linux64.zip
mv -f ~/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

# 6. Installer toutes les dépendances système
apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libxss1 libxtst6 xvfb

# 7. Tester Chrome
echo "Test de Chrome..."
google-chrome --version
chromedriver --version

# 8. Créer un script de lancement simple
cat > /root/leboncoin-scraper/start_server.sh << 'EOF'
#!/bin/bash
cd /root/leboncoin-scraper
source venv/bin/activate
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
python3 server_working.py
EOF

chmod +x /root/leboncoin-scraper/start_server.sh

echo "✅ INSTALLATION TERMINÉE!"
echo ""
echo "Pour lancer le serveur:"
echo "  /root/leboncoin-scraper/start_server.sh"
echo ""
echo "Pour tester:"
echo "  curl http://localhost:1373/test"

#!/bin/bash
# Script de déploiement en un clic depuis GitHub

echo "🚀 Déploiement LeBonCoin Scraper"
echo "================================"

# Variables (à remplacer par vos valeurs)
VPS_IP="31.97.53.91"
VPS_USER="root"
GITHUB_REPO="tonybZY/leboncoin-scraper"

# Fonction pour exécuter des commandes sur le VPS
remote_exec() {
    ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP "$1"
}

# 1. Installer Docker sur le VPS si nécessaire
echo "📦 Installation de Docker..."
remote_exec "
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com | sh
        systemctl start docker
        systemctl enable docker
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        curl -L 'https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-linux-x86_64' -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
"

# 2. Cloner/Mettre à jour le repo
echo "📥 Téléchargement du code..."
remote_exec "
    cd ~
    if [ -d 'leboncoin-scraper' ]; then
        cd leboncoin-scraper
        git pull
    else
        git clone https://github.com/$GITHUB_REPO.git leboncoin-scraper
        cd leboncoin-scraper
    fi
"

# 3. Créer le fichier .env
echo "🔐 Configuration des variables..."
remote_exec "
    cd ~/leboncoin-scraper
    cat > .env << EOF
ANTICAPTCHA_API_KEY=599bf5a3b86f1cabf7e23bca24237354
LEBONCOIN_EMAIL=tnclim1@gmail.com
LEBONCOIN_PASSWORD=Underground780&
DB_PASSWORD=secure_password_here
EOF
"

# 4. Lancer avec Docker Compose
echo "🐳 Lancement des conteneurs..."
remote_exec "
    cd ~/leboncoin-scraper
    docker-compose down
    docker-compose up -d --build
"

# 5. Vérifier le statut
echo "✅ Vérification..."
sleep 5
curl -s http://$VPS_IP:1372/status | jq '.' || echo "API pas encore prête"

echo ""
echo "✨ Déploiement terminé!"
echo "================================"
echo "🌐 API: http://$VPS_IP:1372"
echo "🗄️  Adminer: http://$VPS_IP:8080"
echo "📝 Logs: ssh $VPS_USER@$VPS_IP 'docker logs leboncoin-scraper'"

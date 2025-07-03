#!/bin/bash
echo "🚀 Déploiement Puppeteer sur VPS"

# Arrêter les anciens processus
pkill -f "node.*server"
pkill -f "python.*scraper"

# Aller dans le bon dossier
cd /root/leboncoin-scraper

# Pull les dernières modifications
git pull origin main

# Installer les dépendances
npm install

# Lancer le serveur
echo "✅ Lancement du serveur Puppeteer..."
node server.js

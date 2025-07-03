#!/bin/bash
# Script de déploiement rapide
ssh root@31.97.53.91 << 'EOF'
cd /root/leboncoin-scraper
git pull
npm install
pkill -f node
nohup node server.js > server.log 2>&1 &
echo "✅ Serveur déployé!"
EOF

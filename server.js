cat > server.js << 'EOF'
const express = require('express');
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const cors = require('cors');
const bodyParser = require('body-parser');

puppeteer.use(StealthPlugin());

const app = express();
app.use(cors());
app.use(bodyParser.json());

const LEBONCOIN_EMAIL = 'tnclim1@gmail.com';
const LEBONCOIN_PASSWORD = 'Underground780&';

async function scrapeLeboncoin(url) {
  console.log('🚀 Lancement du navigateur...');
  
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--single-process',
      '--disable-gpu'
    ]
  });

  try {
    const page = await browser.newPage();
    
    // User agent français
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    // Connexion à LeBonCoin
    console.log('🔐 Connexion à LeBonCoin...');
    await page.goto('https://www.leboncoin.fr/deposer-une-annonce');
    await page.waitForTimeout(3000);
    
    // Accepter les cookies
    try {
      await page.click('#didomi-notice-agree-button');
      console.log('🍪 Cookies acceptés');
    } catch (e) {}
    
    // Remplir le formulaire de connexion
    try {
      await page.waitForSelector('input[name="email"]', { timeout: 5000 });
      await page.type('input[name="email"]', LEBONCOIN_EMAIL);
      await page.type('input[name="password"]', LEBONCOIN_PASSWORD);
      await page.click('button[type="submit"]');
      console.log('✅ Formulaire soumis');
      await page.waitForTimeout(5000);
    } catch (e) {
      console.log('⚠️ Déjà connecté ou pas de formulaire');
    }
    
    // Aller sur l'annonce
    console.log('📍 Navigation vers l\'annonce...');
    await page.goto(url);
    await page.waitForTimeout(5000);
    
    // Récupérer les données
    const data = await page.evaluate(() => {
      const title = document.querySelector('h1')?.textContent || 'Non trouvé';
      const price = document.querySelector('[data-qa-id="adview_price"]')?.textContent || 'Prix non trouvé';
      return { title, price };
    });
    
    console.log(`✅ Titre: ${data.title}`);
    console.log(`💰 Prix: ${data.price}`);
    
    // Chercher et cliquer sur le bouton téléphone
    console.log('📞 Recherche du bouton téléphone...');
    
    const phoneButtonSelectors = [
      'button:has-text("Voir le numéro")',
      'button:has-text("numéro")',
      'button:has-text("téléphone")',
      '[data-qa-id="adview_contact_phone_button"]',
      'button[class*="phone"]'
    ];
    
    let phoneNumber = null;
    
    for (const selector of phoneButtonSelectors) {
      try {
        await page.click(selector);
        console.log('✅ Bouton téléphone cliqué!');
        await page.waitForTimeout(3000);
        
        // Récupérer le numéro
        phoneNumber = await page.evaluate(() => {
          // Chercher les liens tel:
          const telLink = document.querySelector('a[href^="tel:"]');
          if (telLink) {
            return telLink.href.replace('tel:', '').replace(/\D/g, '');
          }
          
          // Chercher par regex
          const phoneRegex = /0[1-9](?:[\s.-]?\d{2}){4}/g;
          const pageText = document.body.innerText || '';
          const matches = pageText.match(phoneRegex);
          
          if (matches && matches.length > 0) {
            return matches[0].replace(/\D/g, '');
          }
          
          return null;
        });
        
        if (phoneNumber) {
          console.log(`✅ Numéro trouvé: ${phoneNumber}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    await browser.close();
    
    return {
      success: true,
      data: {
        ...data,
        phone: phoneNumber
      }
    };
    
  } catch (error) {
    console.error('❌ Erreur:', error);
    await browser.close();
    throw error;
  }
}

app.post('/scrape', async (req, res) => {
  const { url } = req.body;
  
  if (!url) {
    return res.status(400).json({ error: 'URL requise' });
  }
  
  console.log(`\n🔍 SCRAPING: ${url}`);
  
  try {
    const result = await scrapeLeboncoin(url);
    res.json(result);
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/test', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'Serveur Puppeteer prêt!' 
  });
});

const PORT = 1373;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`
============================================================
🚀 SERVEUR LEBONCOIN PUPPETEER - 100% FONCTIONNEL
============================================================
📡 Port: ${PORT}
📧 Email: ${LEBONCOIN_EMAIL}
🔐 Mot de passe: configuré

📌 Endpoints:
   POST http://localhost:${PORT}/scrape
   GET  http://localhost:${PORT}/test
============================================================
  `);
});
EOF

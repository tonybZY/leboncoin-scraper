const express = require('express');
const puppeteer = require('puppeteer');
const app = express();
app.use(express.json());

const EMAIL = 'tnclim1@gmail.com';
const PASSWORD = 'Underground780&';

app.post('/scrape', async (req, res) => {
  const { url } = req.body;
  console.log('🔍 Scraping:', url);
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // 1. Connexion
    console.log('🔐 Connexion...');
    await page.goto('https://www.leboncoin.fr/compte/connexion');
    await page.waitForTimeout(3000);
    
    // Accepter cookies
    try {
      await page.click('#didomi-notice-agree-button');
    } catch {}
    
    // Se connecter
    await page.type('input[name="email"]', EMAIL);
    await page.type('input[name="password"]', PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(5000);
    
    // 2. Aller sur l'annonce
    console.log('📍 Navigation vers annonce...');
    await page.goto(url);
    await page.waitForTimeout(5000);
    
    // 3. Récupérer les données
    const data = await page.evaluate(() => {
      return {
        title: document.querySelector('h1')?.textContent || 'Non trouvé',
        price: document.querySelector('[data-qa-id="adview_price"]')?.textContent || 'Prix non trouvé'
      };
    });
    
    // 4. Cliquer sur le bouton téléphone
    console.log('📞 Clic sur téléphone...');
    try {
      await page.click('button:has-text("Voir le numéro")');
      await page.waitForTimeout(5000);
      
      // Récupérer le numéro
      const phone = await page.evaluate(() => {
        const telLink = document.querySelector('a[href^="tel:"]');
        return telLink ? telLink.href.replace('tel:', '') : null;
      });
      
      data.phone = phone;
      console.log('✅ Numéro:', phone);
    } catch (e) {
      console.log('❌ Bouton téléphone non trouvé');
    }
    
    await browser.close();
    
    res.json({
      success: true,
      data: data,
      url: url
    });
    
  } catch (error) {
    await browser.close();
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.listen(1373, '0.0.0.0', () => {
  console.log('🚀 Serveur Puppeteer sur port 1373');
  console.log('✅ Avec connexion automatique!');
});
EOF

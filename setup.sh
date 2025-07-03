#!/bin/bash
echo "🚀 Installation du scraper LeBonCoin..."

# Créer package.json
echo '{
  "name": "scraper-leboncoin",
  "version": "1.0.0",
  "main": "server.js",
  "dependencies": {
    "express": "^4.18.2",
    "puppeteer": "^21.6.0",
    "cors": "^2.8.5"
  }
}' > package.json

# Créer server.js
echo 'const express = require("express");
const puppeteer = require("puppeteer");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.json({ 
    status: "Scraper prêt!",
    endpoints: {
      "POST /scrape": "Scraper une page LeBonCoin"
    }
  });
});

app.post("/scrape", async (req, res) => {
  let browser;
  try {
    const { url } = req.body;
    console.log("Scraping:", url);
    
    browser = await puppeteer.launch({ 
      headless: false,
      args: ["--no-sandbox", "--disable-setuid-sandbox"]
    });
    
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(3000);
    
    const data = await page.evaluate(() => {
      const title = document.title;
      const html = document.documentElement.innerHTML;
      const phones = html.match(/0[1-9]\d{8}/g) || [];
      return { title, phones: [...new Set(phones)], htmlSize: html.length };
    });
    
    await browser.close();
    
    res.json({
      success: true,
      url: url,
      title: data.title,
      phones: data.phones,
      htmlSize: data.htmlSize
    });
    
  } catch (error) {
    if (browser) await browser.close();
    console.error("Erreur:", error);
    res.status(500).json({ error: error.message });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`
🎯 Scraper LeBonCoin démarré!
📡 URL: http://localhost:${PORT}
✅ Prêt à scraper!
  `);
});' > server.js

echo "📦 Installation des dépendances..."
/opt/homebrew/bin/npm install

echo "✅ Installation terminée!"
echo "🚀 Pour lancer: npm start"

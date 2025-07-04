const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());

// Configuration
const CONFIG = {
    LEBONCOIN_EMAIL: 'tnclim1@gmail.com',
    LEBONCOIN_PASSWORD: 'Underground780&',
    PORT: 1373
};

// Route de diagnostic
app.post('/diagnose', async (req, res) => {
    const { url } = req.body;
    
    if (!url) {
        return res.status(400).json({ error: 'URL requise' });
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('🔍 MODE DIAGNOSTIC');
    console.log(`📍 URL: ${url}`);
    console.log('='.repeat(60) + '\n');
    
    let browser = null;
    
    try {
        // Lancer Puppeteer en mode visible pour debug
        console.log('🚀 Lancement de Puppeteer...');
        browser = await puppeteer.launch({
            headless: false, // MODE VISIBLE pour debug
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--window-size=1920,1080'
            ],
            defaultViewport: null
        });
        
        const page = await browser.newPage();
        
        // Aller directement sur l'annonce (sans connexion pour simplifier)
        console.log('📱 Navigation vers l\'annonce...');
        await page.goto(url, {
            waitUntil: 'networkidle2',
            timeout: 30000
        });
        
        // Attendre un peu
        await page.waitForTimeout(3000);
        
        // Accepter les cookies si présents
        try {
            await page.click('#didomi-notice-agree-button');
            console.log('🍪 Cookies acceptés');
            await page.waitForTimeout(2000);
        } catch (e) {}
        
        // 1. Capturer le HTML complet
        const htmlContent = await page.content();
        fs.writeFileSync('/tmp/page_complete.html', htmlContent);
        console.log('📄 HTML complet sauvegardé: /tmp/page_complete.html');
        
        // 2. Screenshot de la page entière
        await page.screenshot({ path: '/tmp/page_complete.png', fullPage: true });
        console.log('📸 Screenshot complet: /tmp/page_complete.png');
        
        // 3. Analyser TOUS les boutons
        const buttonsAnalysis = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button, a[role="button"], div[role="button"], [onclick]'));
            return buttons.map((btn, index) => {
                const rect = btn.getBoundingClientRect();
                return {
                    index: index,
                    tag: btn.tagName,
                    text: btn.textContent.trim(),
                    classes: btn.className,
                    id: btn.id,
                    href: btn.href || null,
                    onclick: btn.onclick ? 'has onclick' : null,
                    isVisible: rect.width > 0 && rect.height > 0,
                    position: {
                        top: rect.top,
                        left: rect.left,
                        width: rect.width,
                        height: rect.height
                    },
                    attributes: Array.from(btn.attributes).map(attr => ({
                        name: attr.name,
                        value: attr.value.substring(0, 100)
                    }))
                };
            }).filter(btn => btn.text.length > 0);
        });
        
        // Sauvegarder l'analyse des boutons
        fs.writeFileSync('/tmp/buttons_analysis.json', JSON.stringify(buttonsAnalysis, null, 2));
        console.log(`\n📊 Analyse des boutons (${buttonsAnalysis.length} trouvés):`);
        console.log('Fichier complet: /tmp/buttons_analysis.json\n');
        
        // Afficher les boutons pertinents
        buttonsAnalysis.forEach(btn => {
            if (btn.isVisible && (
                btn.text.toLowerCase().includes('voir') ||
                btn.text.toLowerCase().includes('num') ||
                btn.text.toLowerCase().includes('tel') ||
                btn.text.toLowerCase().includes('phone') ||
                btn.text.toLowerCase().includes('contact') ||
                btn.text.toLowerCase().includes('appel')
            )) {
                console.log(`🔘 Bouton ${btn.index}: "${btn.text}"`);
                console.log(`   Tag: ${btn.tag}, Classes: ${btn.classes}`);
                console.log(`   Position: ${JSON.stringify(btn.position)}`);
            }
        });
        
        // 4. Chercher spécifiquement dans la zone vendeur
        const sellerSection = await page.evaluate(() => {
            const sellerElements = document.querySelectorAll('[class*="seller"], [class*="Seller"], [class*="vendor"], [class*="contact"]');
            return Array.from(sellerElements).map(el => ({
                tag: el.tagName,
                classes: el.className,
                html: el.innerHTML.substring(0, 500)
            }));
        });
        
        console.log('\n📦 Sections vendeur trouvées:', sellerSection.length);
        
        // 5. Rechercher des patterns de téléphone déjà visibles
        const phonePatterns = await page.evaluate(() => {
            const phoneRegex = /(?:(?:\+|00)33[\s.-]?(?:\(0\)[\s.-]?)?|0)[1-9](?:[\s.-]?\d{2}){4}/g;
            const text = document.body.textContent;
            const matches = text.match(phoneRegex);
            return matches ? matches.slice(0, 5) : [];
        });
        
        console.log('\n📞 Numéros de téléphone trouvés dans la page:', phonePatterns);
        
        // 6. Essayer de cliquer sur différents éléments
        console.log('\n🖱️ Tentative de clics sur éléments suspects...');
        
        // Attendre 30 secondes pour inspection manuelle
        console.log('\n⏰ NAVIGATEUR OUVERT PENDANT 30 SECONDES');
        console.log('👀 Inspectez manuellement la page pour trouver le bouton téléphone');
        console.log('📝 Notez les classes CSS ou le texte exact du bouton\n');
        
        await page.waitForTimeout(30000);
        
        await browser.close();
        
        res.json({
            success: true,
            diagnostic: {
                buttonsFound: buttonsAnalysis.length,
                phoneNumbersVisible: phonePatterns,
                sellerSections: sellerSection.length,
                files: {
                    html: '/tmp/page_complete.html',
                    screenshot: '/tmp/page_complete.png',
                    buttons: '/tmp/buttons_analysis.json'
                }
            }
        });
        
    } catch (error) {
        console.error('❌ ERREUR:', error);
        if (browser) await browser.close();
        res.status(500).json({ error: error.message });
    }
});

// Route simple pour tester sans connexion
app.post('/scrape-simple', async (req, res) => {
    const { url } = req.body;
    
    if (!url) {
        return res.status(400).json({ error: 'URL requise' });
    }
    
    let browser = null;
    
    try {
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const page = await browser.newPage();
        await page.goto(url, { waitUntil: 'networkidle2' });
        
        // Extraire les données basiques
        const data = await page.evaluate(() => {
            return {
                title: document.querySelector('h1')?.textContent || 'Non trouvé',
                price: document.querySelector('[data-qa-id="adview_price"]')?.textContent || 'Non trouvé',
                description: document.querySelector('[data-qa-id="adview_description"]')?.textContent || 'Non trouvé'
            };
        });
        
        await browser.close();
        
        res.json({
            success: true,
            data,
            note: 'Mode simple sans connexion ni téléphone'
        });
        
    } catch (error) {
        if (browser) await browser.close();
        res.status(500).json({ error: error.message });
    }
});

// Route de test
app.get('/test', (req, res) => {
    res.json({
        status: 'OK',
        message: 'Serveur de diagnostic prêt',
        endpoints: [
            'POST /diagnose - Mode diagnostic complet',
            'POST /scrape-simple - Scraping basique',
            'GET /test - Ce message'
        ]
    });
});

// Démarrage
app.listen(CONFIG.PORT, '0.0.0.0', () => {
    console.log('\n' + '='.repeat(60));
    console.log('🔍 SERVEUR DIAGNOSTIC LEBONCOIN');
    console.log('='.repeat(60));
    console.log(`📡 Port: ${CONFIG.PORT}`);
    console.log('\n📌 Endpoints:');
    console.log(`   POST http://localhost:${CONFIG.PORT}/diagnose`);
    console.log(`   POST http://localhost:${CONFIG.PORT}/scrape-simple`);
    console.log(`   GET  http://localhost:${CONFIG.PORT}/test`);
    console.log('\n💡 Le mode diagnostic ouvre un navigateur visible!');
    console.log('='.repeat(60) + '\n');
});

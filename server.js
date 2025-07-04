const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Configuration
const CONFIG = {
    LEBONCOIN_EMAIL: 'tnclim1@gmail.com',
    LEBONCOIN_PASSWORD: 'Underground780&',
    ANTICAPTCHA_API_KEY: '599bf5a3b86f1cabf7e23bca24237354',
    MIN_DELAY_BETWEEN_REQUESTS: 30,
    PORT: 1373
};

let lastRequestTime = 0;

// Fonctions utilitaires
const randomDelay = (min, max) => {
    const delay = Math.random() * (max - min) + min;
    return new Promise(resolve => setTimeout(resolve, delay * 1000));
};

const humanTyping = async (page, selector, text) => {
    await page.focus(selector);
    await page.evaluate((selector) => {
        document.querySelector(selector).value = '';
    }, selector);
    
    for (const char of text) {
        await page.type(selector, char);
        await randomDelay(0.1, 0.3);
    }
};

// Fonction de connexion
async function loginToLeboncoin(page) {
    console.log('🔐 Tentative de connexion...');
    
    try {
        // Aller sur la page de connexion
        await page.goto('https://www.leboncoin.fr/deposer-une-annonce', {
            waitUntil: 'networkidle2',
            timeout: 30000
        });
        
        // Accepter les cookies si présents
        try {
            await page.waitForSelector('#didomi-notice-agree-button', { timeout: 5000 });
            await page.click('#didomi-notice-agree-button');
            console.log('🍪 Cookies acceptés');
            await randomDelay(1, 2);
        } catch (e) {
            console.log('Pas de bannière de cookies');
        }
        
        // Vérifier si on doit se connecter
        const needsLogin = await page.evaluate(() => {
            const emailField = document.querySelector('input[name="email"]');
            const passwordField = document.querySelector('input[name="password"]');
            return emailField && passwordField;
        });
        
        if (needsLogin) {
            console.log('📝 Formulaire de connexion détecté');
            
            // Remplir l'email
            await humanTyping(page, 'input[name="email"]', CONFIG.LEBONCOIN_EMAIL);
            console.log('✅ Email saisi');
            
            await randomDelay(1, 2);
            
            // Remplir le mot de passe
            await humanTyping(page, 'input[name="password"]', CONFIG.LEBONCOIN_PASSWORD);
            console.log('✅ Mot de passe saisi');
            
            await randomDelay(1, 2);
            
            // Cliquer sur connexion
            await page.click('button[type="submit"]');
            console.log('✅ Clic sur connexion');
            
            // Attendre la redirection
            await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 });
            
            // Vérifier si CAPTCHA
            const hasCaptcha = await page.evaluate(() => {
                return document.body.textContent.includes("On s'assure qu'on s'adresse bien à vous");
            });
            
            if (hasCaptcha) {
                console.log('⚠️ CAPTCHA détecté - Résolvez-le manuellement dans le navigateur');
                // Attendre 60 secondes pour résolution manuelle
                await new Promise(resolve => setTimeout(resolve, 60000));
            }
            
            console.log('✅ Connexion réussie!');
        } else {
            console.log('✅ Déjà connecté');
        }
        
        return true;
    } catch (error) {
        console.error('❌ Erreur de connexion:', error.message);
        return false;
    }
}

// Fonction de scraping
async function scrapeListing(page, url) {
    console.log('🏠 Navigation vers l\'annonce...');
    
    await page.goto(url, {
        waitUntil: 'networkidle2',
        timeout: 30000
    });
    
    await randomDelay(3, 5);
    
    // Extraction des données de base
    const listingData = await page.evaluate(() => {
        const getText = (selector) => {
            const el = document.querySelector(selector);
            return el ? el.textContent.trim() : null;
        };
        
        return {
            title: getText('h1'),
            price: getText('[data-qa-id="adview_price"]'),
            description: getText('[data-qa-id="adview_description"]'),
            location: getText('[data-qa-id="adview_location"]'),
            date: getText('[data-qa-id="adview_date"]'),
            seller: getText('[data-qa-id="adview_seller_name"]')
        };
    });
    
    console.log('📊 Données extraites:', listingData.title);
    
    // Recherche améliorée du bouton téléphone
    console.log('📞 Recherche du bouton téléphone...');
    
    let phoneNumber = null;
    
    try {
        // Faire défiler pour voir plus de contenu
        await page.evaluate(() => {
            window.scrollTo(0, document.body.scrollHeight * 0.7);
        });
        
        await randomDelay(2, 3);
        
        // Debug: faire un screenshot
        await page.screenshot({ path: '/tmp/debug_phone_search.png' });
        console.log('📸 Screenshot de debug: /tmp/debug_phone_search.png');
        
        // Debug: lister tous les boutons
        const allButtons = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button, a[role="button"], div[role="button"]'));
            return buttons.map((btn, index) => ({
                index: index,
                text: btn.textContent.trim().substring(0, 50),
                classes: btn.className,
                isVisible: btn.offsetParent !== null
            }));
        });
        
        console.log('🔍 Boutons trouvés:');
        allButtons.filter(b => b.isVisible).forEach(btn => {
            console.log(`  - "${btn.text}"`);
        });
        
        // Méthode 1: Chercher par texte avec evaluate
        let phoneButton = await page.evaluateHandle(() => {
            // Chercher tous les éléments cliquables
            const clickableElements = document.querySelectorAll('button, a, div[role="button"], span[role="button"]');
            
            for (const el of clickableElements) {
                const text = el.textContent.toLowerCase().trim();
                // Chercher différentes variantes
                if (text.includes('voir le numéro') || 
                    text.includes('afficher le numéro') ||
                    text.includes('afficher le numero') ||
                    text.includes('voir le numero') ||
                    (text.includes('voir') && text.includes('num')) ||
                    text === 'téléphone' ||
                    text === 'appeler' ||
                    text === 'contacter') {
                    console.log('Bouton potentiel trouvé:', text);
                    return el;
                }
            }
            
            // Chercher aussi dans les icônes
            const phoneIcons = document.querySelectorAll('[data-icon*="phone"], [class*="PhoneIcon"], svg[class*="phone"]');
            for (const icon of phoneIcons) {
                let parent = icon.parentElement;
                while (parent && parent !== document.body) {
                    if (parent.tagName === 'BUTTON' || parent.hasAttribute('role')) {
                        console.log('Bouton trouvé via icône');
                        return parent;
                    }
                    parent = parent.parentElement;
                }
            }
            
            return null;
        });
        
        // Si pas trouvé, essayer d'autres méthodes
        if (!phoneButton || !(await phoneButton.evaluate(el => el !== null))) {
            console.log('Recherche alternative...');
            
            // Chercher dans la section contact/vendeur
            phoneButton = await page.evaluateHandle(() => {
                // Chercher la section vendeur
                const sellerSections = document.querySelectorAll('[data-qa-id*="seller"], [class*="seller"], [class*="contact"], [class*="Contact"]');
                
                for (const section of sellerSections) {
                    const buttons = section.querySelectorAll('button, a[href*="tel"], [role="button"]');
                    if (buttons.length > 0) {
                        console.log('Bouton trouvé dans section vendeur');
                        return buttons[0];
                    }
                }
                
                // Dernière tentative : chercher n'importe quel bouton après les infos principales
                const mainContent = document.querySelector('main, [role="main"]');
                if (mainContent) {
                    const allButtons = mainContent.querySelectorAll('button');
                    // Prendre les derniers boutons (souvent le téléphone est en bas)
                    if (allButtons.length > 0) {
                        return allButtons[allButtons.length - 1];
                    }
                }
                
                return null;
            });
        }
        
        if (phoneButton && await phoneButton.evaluate(el => el !== null)) {
            // Scroll jusqu'au bouton
            await phoneButton.evaluate(el => {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
            
            await randomDelay(1, 2);
            
            // Essayer de cliquer
            try {
                await phoneButton.click();
                console.log('✅ Clic sur le bouton');
            } catch (clickError) {
                // Si le clic direct échoue, essayer avec JavaScript
                await phoneButton.evaluate(el => el.click());
                console.log('✅ Clic JavaScript sur le bouton');
            }
            
            await randomDelay(3, 5);
            
            // Screenshot après clic
            await page.screenshot({ path: '/tmp/debug_after_click.png' });
            console.log('📸 Screenshot après clic: /tmp/debug_after_click.png');
            
            // Chercher le numéro de téléphone
            phoneNumber = await page.evaluate(() => {
                // Méthode 1: Chercher les liens tel:
                const telLinks = document.querySelectorAll('a[href^="tel:"]');
                if (telLinks.length > 0) {
                    const href = telLinks[0].href;
                    return href.replace('tel:', '').replace(/\D/g, '');
                }
                
                // Méthode 2: Chercher un numéro qui vient d'apparaître
                const phoneRegex = /(?:(?:\+|00)33[\s.-]?(?:\(0\)[\s.-]?)?|0)[1-9](?:[\s.-]?\d{2}){4}/g;
                
                // Chercher dans tous les éléments
                const allElements = Array.from(document.querySelectorAll('*'));
                for (const el of allElements) {
                    if (el.children.length === 0 && el.textContent) {
                        const matches = el.textContent.match(phoneRegex);
                        if (matches) {
                            const cleaned = matches[0].replace(/[\s.-]/g, '').replace(/^\+33/, '0').replace(/^0033/, '0');
                            if (cleaned.length === 10 && cleaned.startsWith('0')) {
                                return cleaned;
                            }
                        }
                    }
                }
                
                // Méthode 3: Chercher dans les nouveaux éléments (modal, popup)
                const modals = document.querySelectorAll('[role="dialog"], [class*="modal"], [class*="Modal"], [class*="popup"]');
                for (const modal of modals) {
                    const text = modal.textContent;
                    const matches = text.match(phoneRegex);
                    if (matches) {
                        return matches[0].replace(/[\s.-]/g, '').replace(/^\+33/, '0').replace(/^0033/, '0');
                    }
                }
                
                return null;
            });
            
            if (phoneNumber) {
                console.log('✅ Numéro trouvé:', phoneNumber);
            } else {
                console.log('❌ Numéro non trouvé après clic');
            }
        } else {
            console.log('❌ Bouton téléphone introuvable');
            
            // En dernier recours, chercher si le numéro est déjà visible
            phoneNumber = await page.evaluate(() => {
                const phoneRegex = /(?:(?:\+|00)33[\s.-]?(?:\(0\)[\s.-]?)?|0)[1-9](?:[\s.-]?\d{2}){4}/g;
                const text = document.body.textContent;
                const matches = text.match(phoneRegex);
                if (matches) {
                    return matches[0].replace(/[\s.-]/g, '').replace(/^\+33/, '0').replace(/^0033/, '0');
                }
                return null;
            });
            
            if (phoneNumber) {
                console.log('ℹ️ Numéro trouvé sans clic:', phoneNumber);
            }
        }
    } catch (error) {
        console.error('❌ Erreur récupération téléphone:', error.message);
    }
    
    return {
        ...listingData,
        phone: phoneNumber
    };
}

// Route de scraping
app.post('/scrape', async (req, res) => {
    const currentTime = Date.now();
    const timeSinceLastRequest = (currentTime - lastRequestTime) / 1000;
    
    if (timeSinceLastRequest < CONFIG.MIN_DELAY_BETWEEN_REQUESTS) {
        const waitTime = CONFIG.MIN_DELAY_BETWEEN_REQUESTS - timeSinceLastRequest;
        console.log(`⏳ Protection anti-blocage: attente de ${waitTime.toFixed(0)}s...`);
        await new Promise(resolve => setTimeout(resolve, waitTime * 1000));
    }
    
    lastRequestTime = Date.now();
    
    const { url } = req.body;
    
    if (!url) {
        return res.status(400).json({ error: 'URL requise' });
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('🔍 DÉMARRAGE DU SCRAPING');
    console.log(`📍 URL: ${url}`);
    console.log('='.repeat(60) + '\n');
    
    let browser = null;
    
    try {
        // Lancer Puppeteer
        console.log('🚀 Lancement de Puppeteer...');
        browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu',
                '--user-data-dir=/tmp/puppeteer',
                '--disable-software-rasterizer'
            ],
            ignoreDefaultArgs: ['--disable-extensions']
        });
        
        const page = await browser.newPage();
        
        // Configuration de la page
        await page.setViewport({ width: 1920, height: 1080 });
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        
        // Se connecter
        const loginSuccess = await loginToLeboncoin(page);
        if (!loginSuccess) {
            console.log('⚠️ Problème de connexion, on continue quand même...');
        }
        
        // Scraper l'annonce
        const data = await scrapeListing(page, url);
        
        await browser.close();
        
        console.log('\n' + '='.repeat(60));
        console.log('✅ SCRAPING TERMINÉ!');
        console.log('='.repeat(60) + '\n');
        
        res.json({
            success: true,
            data,
            url
        });
        
    } catch (error) {
        console.error('❌ ERREUR:', error);
        
        if (browser) {
            await browser.close();
        }
        
        res.status(500).json({
            success: false,
            error: error.message,
            url
        });
    }
});

// Route de test
app.get('/test', (req, res) => {
    res.json({
        status: 'OK',
        email: CONFIG.LEBONCOIN_EMAIL,
        anticaptcha_key: CONFIG.ANTICAPTCHA_API_KEY.substring(0, 10) + '...',
        message: 'Serveur Puppeteer prêt!',
        version: '2.1'
    });
});

// Route de santé
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});

// Démarrage du serveur
app.listen(CONFIG.PORT, '0.0.0.0', () => {
    console.log('\n' + '='.repeat(60));
    console.log('🚀 SERVEUR LEBONCOIN PUPPETEER V2.1');
    console.log('='.repeat(60));
    console.log(`📡 Port: ${CONFIG.PORT}`);
    console.log(`📧 Email: ${CONFIG.LEBONCOIN_EMAIL}`);
    console.log(`🔑 API Key: ${CONFIG.ANTICAPTCHA_API_KEY.substring(0, 10)}...`);
    console.log(`⏱️  Délai minimum: ${CONFIG.MIN_DELAY_BETWEEN_REQUESTS}s`);
    console.log('\n📌 Endpoints:');
    console.log(`   POST http://localhost:${CONFIG.PORT}/scrape`);
    console.log(`   GET  http://localhost:${CONFIG.PORT}/test`);
    console.log(`   GET  http://localhost:${CONFIG.PORT}/health`);
    console.log('\n' + '='.repeat(60) + '\n');
});

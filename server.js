const express = require('express');
const { Builder, By, until, Key } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const app = express();
const PORT = 1372;

app.use(express.json());

const randomDelay = (min, max) => {
    return new Promise(resolve => setTimeout(resolve, Math.random() * (max - min) + min));
};

// Fonction pour simuler la frappe humaine
const humanType = async (element, text) => {
    for (const char of text) {
        await element.sendKeys(char);
        await randomDelay(50, 150);
    }
};

app.post('/scrape', async (req, res) => {
    const { url } = req.body;
    
    if (!url) {
        return res.status(400).json({ error: 'URL requise' });
    }

    console.log('🔍 Démarrage du scraping avec Selenium:', url);

    let driver;
    let phoneNumber = null;
    
    try {
        // Configuration Chrome pour éviter la détection
        const options = new chrome.Options();
        
        // Arguments pour masquer Selenium
        options.addArguments('--disable-blink-features=AutomationControlled');
        options.addArguments('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36');
        options.addArguments('--window-size=1920,1080');
        options.addArguments('--start-maximized');
        options.addArguments('--disable-gpu');
        options.addArguments('--no-sandbox');
        options.addArguments('--disable-dev-shm-usage');
        options.addArguments('--disable-web-security');
        options.addArguments('--disable-features=VizDisplayCompositor');
        options.addArguments('--disable-notifications');
        
        // Exclure les switches qui révèlent l'automation
        options.excludeSwitches(['enable-automation']);
        options.addArguments('--disable-automation');
        
        // Preferences pour masquer l'automation
        const prefs = {
            'credentials_enable_service': false,
            'profile.password_manager_enabled': false,
            'profile.default_content_setting_values.notifications': 2
        };
        options.setUserPreferences(prefs);
        
        // Utiliser Chrome au lieu de Chromium
        options.setBinaryPath('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome');
        
        console.log('🚀 Lancement de Chrome avec Selenium...');
        driver = await new Builder()
            .forBrowser('chrome')
            .setChromeOptions(options)
            .build();
        
        // Exécuter du JavaScript pour masquer WebDriver
        await driver.executeScript(`
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    { name: 'Chrome PDF Plugin', length: 1 },
                    { name: 'Chrome PDF Viewer', length: 1 },
                    { name: 'Native Client', length: 1 }
                ]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['fr-FR', 'fr', 'en-US', 'en']
            });
            
            window.chrome = {
                runtime: {}
            };
            
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' })
                })
            });
        `);
        
        console.log('📱 Navigation vers Google d\'abord...');
        await driver.get('https://www.google.fr');
        await randomDelay(2000, 3000);
        
        // Simuler une recherche Google
        try {
            const searchBox = await driver.findElement(By.name('q'));
            await humanType(searchBox, 'leboncoin');
            await randomDelay(500, 1000);
            await searchBox.sendKeys(Key.RETURN);
            await randomDelay(2000, 3000);
        } catch (e) {
            console.log('Recherche Google ignorée');
        }
        
        console.log('🏠 Navigation vers LeBonCoin...');
        await driver.get(url);
        
        // Attendre le chargement
        await driver.wait(until.elementLocated(By.css('h1')), 30000);
        await randomDelay(3000, 5000);
        
        // Accepter les cookies
        try {
            const cookieButton = await driver.findElement(By.css('button[id*="didomi-notice-agree-button"]'));
            await driver.executeScript("arguments[0].scrollIntoView(true);", cookieButton);
            await randomDelay(500, 1000);
            await cookieButton.click();
            console.log('🍪 Cookies acceptés');
            await randomDelay(2000, 3000);
        } catch (e) {
            console.log('Pas de bannière de cookies');
        }
        
        // Faire défiler naturellement
        console.log('📜 Défilement de la page...');
        const scrollHeight = await driver.executeScript('return document.body.scrollHeight');
        for (let i = 0; i < scrollHeight; i += 100) {
            await driver.executeScript(`window.scrollTo(0, ${i})`);
            await randomDelay(50, 100);
        }
        
        await randomDelay(2000, 3000);
        
        // Récupérer les données
        console.log('📊 Récupération des données...');
        const data = await driver.executeScript(`
            const getTextContent = (selector) => {
                const element = document.querySelector(selector);
                return element ? element.textContent.trim() : null;
            };

            return {
                title: getTextContent('h1'),
                price: getTextContent('[data-qa-id="adview_price"]'),
                description: getTextContent('[data-qa-id="adview_description"]'),
                location: getTextContent('[data-qa-id="adview_location"]'),
                date: getTextContent('[data-qa-id="adview_date"]'),
                seller: getTextContent('[data-qa-id="adview_seller_name"]'),
                category: getTextContent('[data-qa-id="adview_category"]')
            };
        `);
        
        console.log('📞 Recherche du bouton téléphone...');
        
        // Méthode 1: Chercher le bouton avec Selenium
        try {
            // Chercher tous les boutons
            const buttons = await driver.findElements(By.css('button'));
            console.log(`Nombre de boutons trouvés: ${buttons.length}`);
            
            let phoneButton = null;
            for (const button of buttons) {
                const text = await button.getText();
                if (text.includes('Voir le numéro')) {
                    phoneButton = button;
                    console.log('✅ Bouton téléphone trouvé');
                    break;
                }
            }
            
            if (phoneButton) {
                // Faire défiler jusqu'au bouton
                await driver.executeScript("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", phoneButton);
                await randomDelay(2000, 3000);
                
                // Essayer plusieurs méthodes de clic
                try {
                    // Méthode 1: Actions chain
                    const actions = driver.actions({ async: true });
                    await actions
                        .move({ origin: phoneButton })
                        .pause(500)
                        .click()
                        .perform();
                    console.log('✅ Clic effectué avec Actions');
                } catch (e) {
                    // Méthode 2: JavaScript click
                    await driver.executeScript("arguments[0].click();", phoneButton);
                    console.log('✅ Clic effectué avec JavaScript');
                }
                
                // Attendre longtemps
                await randomDelay(8000, 12000);
                
                // Chercher le numéro
                phoneNumber = await driver.executeScript(`
                    // Chercher un lien tel:
                    const telLinks = document.querySelectorAll('a[href^="tel:"]');
                    if (telLinks.length > 0) {
                        return telLinks[0].href.replace('tel:', '').replace(/[\\s.-]/g, '');
                    }
                    
                    // Chercher dans le texte
                    const phoneRegex = /0[1-9](?:[\\s.-]?\\d{2}){4}/g;
                    const pageText = document.body.innerText || '';
                    const matches = pageText.match(phoneRegex);
                    
                    if (matches) {
                        for (const match of matches) {
                            const cleaned = match.replace(/[\\s.-]/g, '');
                            if (cleaned.length === 10) {
                                return cleaned;
                            }
                        }
                    }
                    
                    return null;
                `);
                
                if (phoneNumber) {
                    console.log('✅ Numéro trouvé:', phoneNumber);
                }
            }
        } catch (e) {
            console.error('Erreur lors de la recherche du bouton:', e.message);
        }
        
        // Méthode 2: Si pas de succès, essayer avec executeScript
        if (!phoneNumber) {
            console.log('⚠️ Tentative alternative avec executeScript...');
            
            const result = await driver.executeScript(`
                // Trouver et cliquer sur le bouton
                const buttons = Array.from(document.querySelectorAll('button'));
                const phoneButton = buttons.find(b => b.textContent && b.textContent.includes('Voir le numéro'));
                
                if (phoneButton) {
                    phoneButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    
                    // Simuler tous les événements
                    const events = ['mouseenter', 'mouseover', 'mousedown', 'mouseup', 'click'];
                    events.forEach(eventType => {
                        const event = new MouseEvent(eventType, {
                            view: window,
                            bubbles: true,
                            cancelable: true
                        });
                        phoneButton.dispatchEvent(event);
                    });
                    
                    return true;
                }
                return false;
            `);
            
            if (result) {
                await randomDelay(8000, 12000);
                
                phoneNumber = await driver.executeScript(`
                    const phoneRegex = /0[1-9](?:[\\s.-]?\\d{2}){4}/g;
                    const pageText = document.body.innerText || '';
                    const matches = pageText.match(phoneRegex);
                    
                    if (matches) {
                        const validPhones = matches.filter(m => {
                            const cleaned = m.replace(/[\\s.-]/g, '');
                            return cleaned.length === 10;
                        });
                        
                        if (validPhones.length > 0) {
                            return validPhones[validPhones.length - 1].replace(/[\\s.-]/g, '');
                        }
                    }
                    
                    return null;
                `);
            }
        }
        
        // Capture finale
        const screenshot = await driver.takeScreenshot();
        require('fs').writeFileSync('debug-selenium.png', screenshot, 'base64');
        console.log('📸 Capture sauvegardée: debug-selenium.png');
        
        await driver.quit();

        console.log('✅ Scraping terminé');
        console.log('📊 Résultat:', { ...data, phone: phoneNumber });
        
        res.json({
            success: true,
            data: {
                ...data,
                phone: phoneNumber
            },
            url: url
        });

    } catch (error) {
        console.error('❌ Erreur:', error);
        if (driver) await driver.quit();
        
        res.status(500).json({ 
            success: false,
            error: error.message,
            url: url
        });
    }
});

app.listen(PORT, () => {
    console.log('🚀 Serveur démarré sur http://localhost:1372');
    console.log('📡 Endpoint: POST http://localhost:1372/scrape');
    console.log('🔧 Utilisation de Selenium WebDriver');
});
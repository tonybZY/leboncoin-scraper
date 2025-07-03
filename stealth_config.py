# stealth_config.py - Configuration anti-détection pour LeBonCoin

import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
import random
import os

def get_stealth_driver():
    """Créer un driver Chrome ultra-furtif"""
    
    # Options Chrome maximales anti-détection
    options = uc.ChromeOptions()
    
    # Mode headless amélioré (commentez si vous voulez voir le navigateur)
    # options.add_argument('--headless=new')
    
    # Arguments essentiels anti-détection
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=IsolateOrigins')
    options.add_argument('--disable-site-isolation-trials')
    options.add_argument('--disable-features=BlockInsecurePrivateNetworkRequests')
    
    # Désactiver les indicateurs d'automatisation
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Arguments pour éviter la détection
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-logging')
    options.add_argument('--disable-dev-tools')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-translate')
    options.add_argument('--disable-sync')
    options.add_argument('--no-first-run')
    options.add_argument('--no-service-autorun')
    options.add_argument('--password-store=basic')
    
    # Taille de fenêtre réaliste
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    
    # User-Agent rotatif ultra-réaliste
    user_agents = [
        # Chrome Windows récents
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Chrome Mac récents
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Firefox Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        # Safari Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
    ]
    options.add_argument(f'--user-agent={random.choice(user_agents)}')
    
    # Profil Chrome persistant avec historique
    if os.path.exists('/root'):
        profile_path = '/root/chrome-profile-leboncoin'
    else:
        profile_path = os.path.expanduser('~/chrome-profile-leboncoin')
    
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
    
    options.add_argument(f'--user-data-dir={profile_path}')
    options.add_argument('--profile-directory=Default')
    
    # Préférences pour simuler un vrai navigateur
    prefs = {
        # Notifications
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        
        # Géolocalisation française
        "profile.default_content_setting_values.geolocation": 1,
        "profile.content_settings.exceptions.geolocation": {
            "*": {"setting": 1}
        },
        
        # Langue française
        "intl.accept_languages": "fr-FR,fr,en-US,en",
        
        # Downloads
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        
        # Passwords
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        
        # WebRTC
        "webrtc.ip_handling_policy": "default_public_interface_only",
        "webrtc.multiple_routes_enabled": False,
        "webrtc.nonproxied_udp_enabled": False,
        
        # Autres
        "profile.default_content_setting_values.images": 1,
        "profile.default_content_setting_values.plugins": 1,
        "profile.default_content_setting_values.popups": 0,
        "profile.default_content_setting_values.cookies": 1,
        "profile.default_content_setting_values.javascript": 1,
        "profile.default_content_setting_values.media_stream": 1,
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.cookie_controls_mode": 0
    }
    options.add_experimental_option("prefs", prefs)
    
    # Créer le driver avec undetected-chromedriver
    driver = uc.Chrome(options=options, version_main=None)
    
    # Injection JavaScript pour masquer l'automatisation
    stealth_js = """
    // Overwrite the navigator properties
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // Chrome specific
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };
    
    // Permissions
    Object.defineProperty(navigator, 'permissions', {
        get: () => ({
            query: () => Promise.resolve({ state: 'granted' })
        })
    });
    
    // Languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['fr-FR', 'fr', 'en-US', 'en']
    });
    
    // Platform
    Object.defineProperty(navigator, 'platform', {
        get: () => 'Win32'
    });
    
    // Plugins
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {
                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            },
            {
                0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                description: "Portable Document Format", 
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer"
            }
        ]
    });
    
    // Hardware concurrency
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => 8
    });
    
    // Device memory
    Object.defineProperty(navigator, 'deviceMemory', {
        get: () => 8
    });
    
    // Connection
    Object.defineProperty(navigator, 'connection', {
        get: () => ({
            rtt: 100,
            downlink: 10,
            effectiveType: '4g',
            saveData: false
        })
    });
    
    // Battery
    navigator.getBattery = () => Promise.resolve({
        charging: true,
        chargingTime: 0,
        dischargingTime: Infinity,
        level: 1
    });
    
    // Media devices
    navigator.mediaDevices = {
        getUserMedia: () => Promise.resolve(),
        enumerateDevices: () => Promise.resolve([])
    };
    
    // WebGL Vendor
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Intel Inc.';
        }
        if (parameter === 37446) {
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter.apply(this, arguments);
    };
    
    // Canvas fingerprint protection
    const toBlob = HTMLCanvasElement.prototype.toBlob;
    const toDataURL = HTMLCanvasElement.prototype.toDataURL;
    const getImageData = CanvasRenderingContext2D.prototype.getImageData;
    
    HTMLCanvasElement.prototype.toBlob = function() {
        return toBlob.apply(this, arguments);
    };
    
    HTMLCanvasElement.prototype.toDataURL = function() {
        return toDataURL.apply(this, arguments);
    };
    
    CanvasRenderingContext2D.prototype.getImageData = function() {
        return getImageData.apply(this, arguments);
    };
    """
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': stealth_js
    })
    
    # Modifier les propriétés CDP
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": driver.execute_script("return navigator.userAgent"),
        "acceptLanguage": "fr-FR,fr;q=0.9,en;q=0.8",
        "platform": "Win32"
    })
    
    return driver

def inject_additional_stealth(driver):
    """Injecter des protections supplémentaires après le chargement de la page"""
    
    additional_js = """
    // Remove Selenium attributes
    for (const key in window) {
        if (key.includes('selenium') || key.includes('webdriver')) {
            delete window[key];
        }
    }
    
    // Fix document attributes
    Object.defineProperty(document, 'hidden', {value: false});
    Object.defineProperty(document, 'visibilityState', {value: 'visible'});
    
    // Mock screen properties
    Object.defineProperty(screen, 'width', {value: 1920});
    Object.defineProperty(screen, 'height', {value: 1080});
    Object.defineProperty(screen, 'availWidth', {value: 1920});
    Object.defineProperty(screen, 'availHeight', {value: 1040});
    
    // Mock window properties
    Object.defineProperty(window, 'innerWidth', {value: 1920});
    Object.defineProperty(window, 'innerHeight', {value: 950});
    Object.defineProperty(window, 'outerWidth', {value: 1920});
    Object.defineProperty(window, 'outerHeight', {value: 1080});
    
    // Touch support (important for mobile detection)
    window.ontouchstart = null;
    navigator.maxTouchPoints = 0;
    
    // Timezone
    Date.prototype.getTimezoneOffset = function() { return -60; }; // France timezone
    
    // Console protection
    const originalConsole = window.console;
    Object.defineProperty(window, 'console', {
        get: () => {
            if (Error().stack.includes('leboncoin')) {
                return {};
            }
            return originalConsole;
        }
    });
    """
    
    driver.execute_script(additional_js)

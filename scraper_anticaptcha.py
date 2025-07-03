# stealth_config.py - Version minimale qui fonctionne

def get_stealth_driver():
    """Importer le driver depuis scraper_with_login.py qui fonctionne"""
    from scraper_with_login import create_driver
    return create_driver()

def inject_additional_stealth(driver):
    """Protections supplémentaires"""
    pass

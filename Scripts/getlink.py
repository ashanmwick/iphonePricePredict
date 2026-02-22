import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import random
import os

# ==========================================
# 0. SETUP PATHS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
AD_LINKS_DIR = os.path.join(DATA_DIR, 'phone-ad-links')

os.makedirs(AD_LINKS_DIR, exist_ok=True)

# ==========================================
# 1. SCRAPING PARAMETERS
# ==========================================
SEARCH_QUERY = "phone"
MAX_PAGES = 40

def smart_delay(min_seconds=3.0, max_seconds=6.0):
    """Randomized delay to mimic human reading time"""
    time.sleep(random.uniform(min_seconds, max_seconds))

# ==========================================
# 2. THE STEALTH BROWSER HARVESTER
# ==========================================
def harvest_links():
    all_ad_links = []
    
    print("Launching Stealth Chrome Browser...")
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    
    print(f"Starting harvest for '{SEARCH_QUERY}'...")
    print("-" * 50)

    try:
        for page in range(1, MAX_PAGES + 1):
            ##url = f"https://ikman.lk/en/ads/sri-lanka?by_paying_member=0&sort=date&order=desc&buy_now=0&urgent=0&query={SEARCH_QUERY}&page={page}"
            url=f"https://ikman.lk/en/ads/sri-lanka/mobile-phones?by_paying_member=0&sort=date&order=desc&buy_now=0&urgent=0&page={page}"
            print(f"Navigating to Page {page}...")
            
            driver.get(url)
            time.sleep(random.uniform(4.0, 7.0))
            
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            ad_cards = soup.find_all('a', class_='gtm-ad-item')
            
            # --- CAPTCHA PAUSE LOGIC ---
            if not ad_cards:
                print(f"No ads found on page {page}.")
                print("Look at the Chrome window. Is there a CAPTCHA?")
                
                # Freezes the script until you press Enter in the terminal
                input(">>> If there is a CAPTCHA, solve it, then PRESS ENTER HERE IN THE CONSOLE to continue...")
                
                # Re-fetch the HTML after the human solved the CAPTCHA
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                ad_cards = soup.find_all('a', class_='gtm-ad-item')
                
                if not ad_cards:
                    print("Still no ads found. We must actually be at the end of the results.")
                    break
            # ---------------------------
                
            for card in ad_cards:
                href = card.get('href')
                if href:
                    all_ad_links.append(f"https://ikman.lk{href}")
            
            print(f"  ✓ Found {len(ad_cards)} links on page {page}")
            smart_delay()

    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # --- FIX FOR WINERROR 6 ---
        try:
            driver.quit()
        except OSError:
            pass # Silently ignores the harmless Windows cleanup bug

    # ==========================================
    # 3. SAVE LINKS TO TXT FILE
    # ==========================================
    unique_links = list(set(all_ad_links))
    
    if unique_links:
        output_file = os.path.join(AD_LINKS_DIR, f"{SEARCH_QUERY}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            for link in unique_links:
                f.write(f"{link}\n")
                
        print("\n" + "="*50)
        print(f"✓ Success! Saved {len(unique_links)} unique links to {output_file}")
        print("="*50)
    else:
        print("\n✗ No links were found.")

if __name__ == "__main__":
    harvest_links()
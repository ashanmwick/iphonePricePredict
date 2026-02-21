import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from tqdm import tqdm
import os
import glob

# ==========================================
# 0. DEFINE DYNAMIC PATHS MATCHING FOLDER STRUCTURE
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
AD_LINKS_DIR = os.path.join(DATA_DIR, 'phone-ad-links')
DETAILS_DIR = os.path.join(DATA_DIR, 'phone-details')
FAILED_DIR = os.path.join(DATA_DIR, 'failed-links')

# ==========================================
# 1. DEFINE EXTRACTION LOGIC FOR PHONE DATA
# ==========================================
def extract_ad_data(url, max_retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.encoding = 'utf-8' # Preserve Emojis
            
            if response.status_code == 429:
                print(f"\n⚠️ Rate limited! Sleeping for 10s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(10)
                continue
                
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Start with a blank dictionary. Keys will be added dynamically!
            data = {}
            
            # 1. EXTRACT PRICE
            price_tag = soup.find('div', class_=lambda x: x and 'amount--' in x)
            data['Price'] = price_tag.get_text(strip=True).replace('Rs', '').replace(',', '').strip() if price_tag else ''
            
            # 2. EXTRACT ALL AD META DATA DYNAMICALLY (Brand, Model, Condition, etc.)
            # Find all the 'full-width' containers inside the ad-meta section
            meta_containers = soup.find_all('div', class_=lambda x: x and 'full-width--' in x)
            
            for container in meta_containers:
                label_div = container.find('div', class_=lambda x: x and 'label--' in x)
                value_div = container.find('div', class_=lambda x: x and 'value--' in x)
                
                if label_div and value_div:
                    # Clean up the key (remove colons and spaces) and value
                    key = label_div.get_text(strip=True).replace(':', '').strip()
                    value = value_div.get_text(strip=True)
                    data[key] = value

            # 3. EXTRACT FEATURES
            features_div = soup.find('div', class_=lambda x: x and 'features--' in x)
            if features_div:
                p_tags = features_div.find_all('p')
                if p_tags:
                    data['Features'] = ', '.join([p.get_text(strip=True) for p in p_tags])
                else:
                    # Fallback if no <p> tags
                    data['Features'] = features_div.get_text(separator=', ', strip=True).replace('Features, ', '')
            else:
                data['Features'] = ''

            # 4. EXTRACT DESCRIPTION
            desc_div = soup.find('div', class_=lambda x: x and 'description-section--' in x)
            if desc_div:
                p_tags = desc_div.find_all('p')
                if p_tags:
                    data['Description'] = ' | '.join([p.get_text(strip=True) for p in p_tags if p.get_text(strip=True)])
                else:
                    data['Description'] = desc_div.get_text(separator=' | ', strip=True)
            else:
                data['Description'] = ''

            return data

        except requests.exceptions.ReadTimeout:
            print(f"\n⏳ Timeout on {url}. Retrying... ({attempt + 1}/{max_retries})")
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            print(f"\n❌ Connection error on {url}: {e}")
            time.sleep(3)
            
    print(f"\n🚫 Failed to extract {url} after {max_retries} attempts.")
    return None

# ==========================================
# 2. PROCESS EACH BRAND FILE
# ==========================================
def process_brand_file(txt_file_path):
    brand_name = os.path.basename(txt_file_path).replace('.txt', '')
    
    print(f"\n{'='*50}")
    print(f"Processing: {brand_name.upper()}")
    print(f"{'='*50}")
    
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        raw_links = f.readlines()
    
    unique_links = list(set([link.strip() for link in raw_links if "ikman.lk" in link]))
    
    print(f"Original Count: {len(raw_links)}")
    print(f"Unique Links to Scrape: {len(unique_links)}")
    print("-" * 50)
    
    os.makedirs(DETAILS_DIR, exist_ok=True)
    os.makedirs(FAILED_DIR, exist_ok=True)
    
    csv_filename = os.path.join(DETAILS_DIR, f"{brand_name}_phones.csv")
    failed_links_filename = os.path.join(FAILED_DIR, f"{brand_name}_failed_links.txt")
    
    data_buffer = []
    failed_links = []
    
    print(f"Scraping {brand_name} ads...")
    
    for i, link in tqdm(enumerate(unique_links), total=len(unique_links)):
        row = extract_ad_data(link)
        
        if row:
            data_buffer.append(row)
        else:
            failed_links.append(link)
            
        # Generous Rate Limiting
        time.sleep(random.uniform(1.5, 3.5))
    
    # SAVE ALL DATA AT ONCE
    # This ensures Pandas sees every single dynamic key and creates the correct columns
    if data_buffer:
        df = pd.DataFrame(data_buffer)
        
        # If the file already exists (e.g. from a previous run), we will overwrite it 
        # to ensure the dynamic columns don't conflict. 
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"\n✓ Success! Data saved to {csv_filename} with {len(df.columns)} columns.")
    
    if failed_links:
        with open(failed_links_filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(failed_links))
        print(f"✗ Failed links saved to {failed_links_filename} ({len(failed_links)} links)")
    else:
        print("✓ No failed links!")

# ==========================================
# 3. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    target_directory = os.path.join(AD_LINKS_DIR, "*.txt")
    txt_files = glob.glob(target_directory)
    
    if not txt_files:
        print(f"No txt files found in {AD_LINKS_DIR}")
        os.makedirs(AD_LINKS_DIR, exist_ok=True)
        print("Please place your .txt files containing links in the 'data/phone-ad-links' folder and run again.")
        exit(1)
    
    print(f"Found {len(txt_files)} brand files to process:")
    for file in txt_files:
        print(f"  - {os.path.basename(file)}")
    
    for txt_file in txt_files:
        process_brand_file(txt_file)
    
    print(f"\n{'='*50}")
    print("ALL BRANDS PROCESSED SUCCESSFULLY!")
    print(f"{'='*50}")
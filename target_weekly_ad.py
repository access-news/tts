import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_folder():
    """Create folder structure for saving flyers"""
    base_folder = 'flyers/target_weekly_ad'
    date_folder = os.path.join(base_folder, datetime.now().strftime('%Y%m%d'))
    os.makedirs(date_folder, exist_ok=True)
    return date_folder

def get_webpage_content_selenium(url):
    """Fetch webpage content using Selenium to handle dynamic content"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "weekly-ad-carousel"))
        )
        
        html_content = driver.page_source
        driver.quit()
        return html_content
    except Exception as e:
        print(f"Error with Selenium: {e}")
        if 'driver' in locals():
            driver.quit()
        return None

def extract_image_urls(html_content):
    """Extract Target weekly ad image URLs from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all('img')
    
    image_data = []
    seen_urls = set()
    
    for img in images:
        src = img.get('src')
        # Only include images that:
        # 1. Are from scene7.com (Target's image server)
        # 2. Have a date-based ID (20241020)
        # 3. Are not GUEST images
        # 4. Haven't been seen before
        if (src 
            and 'Target' in src 
            and 'scene7.com' in src 
            and not 'GUEST_' in src
            and re.search(r'Target/\d{8}', src)
            and src not in seen_urls):
            
            seen_urls.add(src)
            image_id = re.search(r'Target/([^?]+)', src).group(1)
            image_data.append({
                'url': src,
                'id': image_id,
                'alt': img.get('alt', 'unnamed')
            })
    
    return image_data

def download_image(image_data, folder_path):
    """Download image and save to specified folder"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    # Clean filename of invalid characters
    clean_alt = re.sub(r'[<>:"/\\|?*]', '', image_data['alt'])
    filename = f"{image_data['id']}_{clean_alt[:50]}.jpg"
    filepath = os.path.join(folder_path, filename)
    
    if os.path.exists(filepath):
        print(f"Skipping {filename} - already exists")
        return True
    
    try:
        response = requests.get(image_data['url'], headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
        return True
    except requests.RequestException as e:
        print(f"Error downloading {filename}: {e}")
        return False

def main():
    url = 'https://www.target.com/weekly-ad'
    folder_path = create_folder()
    
    print("Fetching Target weekly ad page...")
    html_content = get_webpage_content_selenium(url)
    
    if not html_content:
        print("Failed to fetch webpage. Exiting.")
        return
    
    print("Extracting image URLs...")
    image_data_list = extract_image_urls(html_content)
    
    if not image_data_list:
        print("No images found. Exiting.")
        return
    
    print(f"Found {len(image_data_list)} images. Starting download...")
    
    successful_downloads = 0
    for image_data in image_data_list:
        if download_image(image_data, folder_path):
            successful_downloads += 1
        time.sleep(1)
    
    print(f"\nDownload complete!")
    print(f"Successfully downloaded {successful_downloads} out of {len(image_data_list)} images")
    print(f"Images saved in: {folder_path}")

if __name__ == "__main__":
    main()
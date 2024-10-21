from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from paddleocr import PaddleOCR
import requests
import time
import os
import tempfile

# FastAPI app
app = FastAPI()

# PaddleOCR setup
ocr = PaddleOCR(use_angle_cls=True, lang='pt')

# Configurations for Selenium WebDriver
gecko_driver_path = './geckodriver'
# MAC
# profile_path = '/Users/brpl20/Library/Application Support/Firefox/Profiles/5cri1tvj.default-release'

# LINUX
#profile_path = '/home/brpl/snap/firefox/common/.mozilla/firefox/xyssuzza.default'  

options = Options()
options.add_argument("-profile")
options.add_argument(profile_path)
# options.add_argument("-headless")  # Make it headless

def get_firefox_driver():
    service = Service(executable_path=gecko_driver_path)
    return webdriver.Firefox(service=service, options=options)

def get_initial_cookies():
    driver = get_firefox_driver()
    try:
        driver.get("https://cna.oab.org.br/")
        time.sleep(5)  # Wait for page to load

        cookies = driver.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        
        token_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "__RequestVerificationToken"))
        )
        token = token_element.get_attribute("value")
        
        return cookie_dict, token
    finally:
        driver.quit()

def search_lawyer(name, insc=None, state=None, cookies=None, token=None):
    search_url = "https://cna.oab.org.br/Home/Search"
    search_data = {
        "__RequestVerificationToken": token,
        "IsMobile": "false",
        "NomeAdvo": name,
        "Insc": insc or "",
        "Uf": state or "",
        "TipoInsc": ""
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Content-Type": "application/json",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    
    response = requests.post(search_url, json=search_data, headers=headers, cookies=cookies)
    time.sleep(5)  # Wait for 5 seconds
    search_result = response.json()
    
    if search_result['Success'] and search_result['Data']:
        detail_url = "https://cna.oab.org.br" + search_result['Data'][0]['DetailUrl']
        detail_response = requests.get(detail_url, headers=headers, cookies=cookies)
        detail_result = detail_response.json()
        
        if detail_result['Success'] and 'DetailUrl' in detail_result['Data']:
            image_url = "https://cna.oab.org.br" + detail_result['Data']['DetailUrl']
            image_response = requests.get(image_url, headers=headers, cookies=cookies)
            
            if image_response.status_code == 200:
                # Save image to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    tmp_file.write(image_response.content)
                    return tmp_file.name
            else:
                raise HTTPException(status_code=500, detail="Failed to download image.")
        else:
            raise HTTPException(status_code=404, detail="Failed to get image URL.")
    else:
        raise HTTPException(status_code=404, detail="Search failed or no results found.")

@app.post("/search-lawyer/")
def search_and_ocr(name: str = Query(..., min_length=1), insc: str = None, state: str = None):
    cookies, token = get_initial_cookies()
    image_path = search_lawyer(name, insc, state, cookies, token)
    
    # Perform OCR on the obtained image
    result = ocr.ocr(image_path, cls=True)
    
    # Clean up the temporary image file
    os.remove(image_path)
    
    return {"name": name, "ocr_result": result}



# curl -X POST "http://localhost:8000/search-lawyer/" \
# -H "Content-Type: application/json" \
# -d '{"name": "bruno pellizzetti", "insc": "", "state": ""}'
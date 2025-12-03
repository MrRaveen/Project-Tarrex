from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time

class GoogleTrendsSelenium:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

    def fetch_trending_now(self, country="LK"):
        url = f"https://trends.google.com/trending?geo={country}"
        self.driver.get(url)

        time.sleep(5)  # Let JS load

        trend_elements = self.driver.find_elements(By.CSS_SELECTOR, ".summary-text")

        results = []
        for el in trend_elements:
            text = el.text.strip()
            if text:
                results.append({
                    "keyword": text,
                    "scraped_at": datetime.utcnow().isoformat()
                })

        return results

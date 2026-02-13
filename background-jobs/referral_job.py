from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless=new")   # IMPORTANT
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from scrapper.login_scrape import login
from scrapper.referral_policy_scrape import scrape_referral_policy
from ingest.referral_ingest import ingest_referral_policy


def main():
    driver = webdriver.Chrome(options=options)

    try:
        print("🔐 Logging in...")
        login(driver)

        print("📄 Scraping Referral Policy...")
        scrape_referral_policy(driver)

        ingest_referral_policy()
        print("✅ Referral Policy updated")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        driver.quit()
        print("🧹 Driver closed")


if __name__ == "__main__":
    main()

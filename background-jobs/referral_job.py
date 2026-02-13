from selenium import webdriver
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from scrapper.login_scrape import login
from scrapper.referral_policy_scrape import scrape_referral_policy
from ingest.referral_ingest import ingest_referral_policy


def main():
    driver = webdriver.Chrome()

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

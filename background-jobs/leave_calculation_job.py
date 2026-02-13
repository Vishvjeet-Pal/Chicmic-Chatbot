from selenium import webdriver
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from scrapper.login_scrape import login
from scrapper.leave_calculation_scrape import scrape_leave_calculation
from ingest.leave_calculation_ingest import ingest_leave_calculation_policy


def main():
    driver = webdriver.Chrome()

    try:
        print("🔐 Logging in...")
        login(driver)

        print("📄 Scraping Leave Calculation Policy...")
        scrape_leave_calculation(driver)

        ingest_leave_calculation_policy()
        print("✅ Leave Calculation Policy updated")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        driver.quit()
        print("🧹 Driver closed")


if __name__ == "__main__":
    main()

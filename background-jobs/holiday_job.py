from selenium import webdriver
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from scrapper.login_scrape import login
from scrapper.holiday_scrape import scrape_holiday_calendar
from ingest.holiday_scrape_ingest import ingest_holiday_calendar


def main():
    driver = webdriver.Chrome()

    try:
        print("🔐 Logging in...")
        login(driver)

        print("📄 Scraping Holiday Policy...")
        scrape_holiday_calendar(driver)

        ingest_holiday_calendar()
        print("✅ Holiday Policy updated")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        driver.quit()
        print("🧹 Driver closed")


if __name__ == "__main__":
    main()

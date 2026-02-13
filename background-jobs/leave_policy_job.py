from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless=new")   # IMPORTANT
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# driver = webdriver.Chrome(options=options)
import os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from scrapper.leave_scrape import scrape_leave_policy
from ingest.leave_ingest import ingest_leave_policy
from scrapper.login_scrape import login


def main():
    driver = webdriver.Chrome(options=options)   # or your configured driver
    try:
        login(driver)
        scrape_leave_policy(driver)
        ingest_leave_policy()
        print("✅ Yearly scrape + ingest completed")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()

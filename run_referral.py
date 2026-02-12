from selenium import webdriver
from scrapper.login_scrape import login
from scrapper.referral_policy_scrape import scrape_policy


def run():
    driver = webdriver.Chrome()
    try:
        login(driver)
        scrape_policy(driver)
    finally:
        driver.quit()


if __name__ == "__main__":
    run()

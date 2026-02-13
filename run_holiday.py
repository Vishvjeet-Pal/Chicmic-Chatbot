from selenium import webdriver
from scrapper.login_scrape import login
from scrapper.holiday_scrape import scrape_holiday_calendar


def run():
    driver = webdriver.Chrome()
    try:
        login(driver)
        scrape_holiday_calendar(driver)
    finally:
        driver.quit()


if __name__ == "__main__":
    run()

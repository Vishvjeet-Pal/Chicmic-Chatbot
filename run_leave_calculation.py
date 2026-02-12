from selenium import webdriver
from scrapper.login_scrape import login
from scrapper.leave_calculation_scrape import scrape_leave_calculation


def run():
    driver = webdriver.Chrome()
    try:
        login(driver)
        scrape_leave_calculation(driver)
    finally:
        driver.quit()


if __name__ == "__main__":
    run()

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import settings


def login(driver):
    driver.get(settings.LOGIN_URL)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "timedragon_id_1859"))
    )

    driver.find_element(By.ID, "timedragon_id_1859").send_keys(settings.USERNAME)
    driver.find_element(By.ID, "timedragon_id_1867").send_keys(settings.PASSWORD)
    driver.find_element(By.ID, "timedragon_id_1867").send_keys(Keys.RETURN)

    WebDriverWait(driver, 15).until(
        EC.url_changes(settings.LOGIN_URL)
    )

    print("✅ Login successful")

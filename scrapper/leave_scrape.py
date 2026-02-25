import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import settings
from scrapper.login_scrape import login

DATA_FOLDER = "scrape_data"
os.makedirs(DATA_FOLDER, exist_ok=True)


def scrape_leave_policy(driver):
    print("Opening policy page...")
    driver.get(settings.LEAVE_URL)

    policy_element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "col-md-12"))
    )

    policy_text = policy_element.text
    # print(policy_text)

    # with open(os.path.join(DATA_FOLDER, "leave_policy.py"), "w", encoding="utf-8") as f:
    #     json.dump({"leave_policies": policy_text}, f, indent=4)

    file_path = os.path.join(DATA_FOLDER, "leave_policy.py")

    with open(file_path, "w", encoding="utf-8") as f:
     f.write(f'leave_policies = """{policy_text}"""')

    print("✅ Policy scraped and saved")
if __name__=='__main__':
    driver = webdriver.Chrome() 
    login(driver)
    scrape_leave_policy(driver)
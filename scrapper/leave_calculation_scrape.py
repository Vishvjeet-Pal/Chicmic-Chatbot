import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import settings


DATA_FOLDER = "scrape_data"
os.makedirs(DATA_FOLDER, exist_ok=True)


def scrape_leave_calculation(driver):
    print("Opening leave calculation page...")
    driver.get(settings.LEAVE_CALCULATION_URL)

    policy_element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "policy-content"))
    )

    policy_text = policy_element.text

    # with open(os.path.join(DATA_FOLDER, "leave_calculation_policy.json"), "w", encoding="utf-8") as f:
    #     json.dump({"leave_calculation_policies": policy_text}, f, indent=4)

    file_path = os.path.join(DATA_FOLDER, "leave_calculation_policy.py")

    with open(file_path, "w", encoding="utf-8") as f:
     f.write(f'leave_calculation_policies = """{policy_text}"""')

    print("✅ Policy scraped and saved")

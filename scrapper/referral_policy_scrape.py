import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import settings

DATA_FOLDER = "scrape_data"
os.makedirs(DATA_FOLDER, exist_ok=True)


def scrape_policy(driver):
    print("Opening policy page...")
    driver.get(settings.POLICY_URL)

    policy_element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "policy-content"))
    )

    policy_text = policy_element.text

    # with open(os.path.join(DATA_FOLDER, "referral_policy.json"), "w", encoding="utf-8") as f:
    #     json.dump({"referral_policies": policy_text}, f, indent=4)

    file_path = os.path.join(DATA_FOLDER, "referral_policy.py")

    with open(file_path, "w", encoding="utf-8") as f:
     f.write(f'referral_policies = """{policy_text}"""')

    print("✅ Policy scraped and saved")

import json
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from config import settings

DATA_FOLDER = "scrape_data"
os.makedirs(DATA_FOLDER, exist_ok=True)


def scrape_holiday_calendar(driver):
    print("Opening holiday calendar page...")
    driver.get(settings.HOLIDAY_URL)

    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    time.sleep(5)

    rows = driver.find_elements(By.CSS_SELECTOR, "table.p-datatable-table tbody tr")

    holidays = []

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 3:
            holidays.append({
                "date": cells[0].text.strip(),
                "day": cells[1].text.strip(),
                "holiday": cells[2].text.strip()
            })

    with open(os.path.join(DATA_FOLDER, "holiday_calendar.json"), "w", encoding="utf-8") as f:
        json.dump(holidays, f, indent=4)

    print("✅ Holiday calendar scraped successfully")

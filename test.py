import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com")

time.sleep(2)

html = driver.page_source
driver.quit()

with open("debug_google.html", "w", encoding="utf-8") as f:
    f.write(html)

print("DONE")

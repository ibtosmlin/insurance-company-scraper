import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def fetch_html(url: str, wait: float = 2.0) -> str:
    """
    JavaScript 実行後の HTML を取得する Selenium 専用 fetcher。
    全社共通で使用する。
    - AXA のような JS 生成ページに必須
    - Aflac / FWD / Asahi など JS 依存ページにも対応
    """

    options = Options()
    options.add_argument("--headless=new")  # 新しい headless モード
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # JS が DOM を構築するまで待つ
    time.sleep(wait)

    html = driver.page_source
    driver.quit()
    return html

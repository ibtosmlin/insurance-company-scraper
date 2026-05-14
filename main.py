import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from app.fetcher import fetch_html
from app.models import NewsItem
from app.parsers import axa_parser

# util
from utils.csv_utils import load_csv, write_csv
from utils.file_utils import backup_file

DATA_INPUT_DIR = Path("data/input")
DATA_OUTPUT_DIR = Path("data/output")
encoding = "utf-8"

mapping = {
    "Axa": axa_parser.parse,
}


# -----------------------------
# mode 正規化（T/F/True/False 全対応）
# -----------------------------
def normalize_mode(value: str) -> str:
    v = value.strip().lower()
    if v in ("t", "true"):
        return "True"
    if v in ("f", "false"):
        return "False"
    return ""


# -----------------------------
# 会社情報読み込み
# -----------------------------
def load_companies():
    companies = {}
    with open(DATA_INPUT_DIR / "companies.csv", encoding=encoding) as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies[row["company_id"]] = row
    return companies


# -----------------------------
# URL 情報読み込み
# -----------------------------
def load_urls(entry_mode: str) -> list[dict]:
    urls = []
    with open(DATA_INPUT_DIR / "urls.csv", encoding=encoding) as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_mode = normalize_mode(row["mode"])
            if row_mode != entry_mode:
                continue

            company_id = row["company_id"]
            url_type = row["url_type"]
            url = row["url"]

            row["url_id"] = generate_url_id(company_id, url_type, url)
            row["year"] = extract_year_from_url(url=url)

            urls.append(row)
    return urls


# -----------------------------
# url_id 生成
# -----------------------------
def generate_url_id(company_id: str, url_type: str, url: str) -> str:
    parsed = urlparse(url=url)
    path = parsed.path.strip("/")
    normalized_path = path.replace("/", "_")
    return f"{company_id}@{url_type}@{normalized_path}"


# -----------------------------
# 年度抽出
# -----------------------------
def extract_year_from_url(url: str) -> str:
    m = re.search(r"(20\d{2})", url)
    return m.group(1) if m else "0000"


# -----------------------------
# parser 選択
# -----------------------------
def select_parser(company_id):
    return mapping.get(company_id)


# -----------------------------
# URL 一括スクレイピング（関数化）
# -----------------------------
def scrape_urls(urls: list[dict], companies: dict) -> list[NewsItem]:
    all_results = []
    total = len(urls)

    for idx, entry in enumerate(urls, start=1):
        company_id = entry["company_id"]
        url = entry["url"]
        url_type = entry["url_type"]
        url_id = entry["url_id"]
        year = entry["year"]

        company_name = companies[company_id]["company_name"]
        company_url = companies[company_id]["company_url"]

        # ★ 進捗表示
        print(f"[{idx}/{total}] Scraping {company_name} ({url_type}) → {url}")

        parser_func = select_parser(company_id)
        if not parser_func:
            print(f"  → parser not found for {company_id}, skipped")
            continue

        html = fetch_html(url)

        results = parser_func(
            html=html,
            url=url,
            url_type=url_type,
            company_id=company_id,
            company_name=company_name,
            company_url=company_url,
            url_id=url_id,
            year=year,
        )

        all_results.extend(results)

    return all_results


# -----------------------------
# True/False 結果保存
# -----------------------------
def save_results(results: list[NewsItem], entry_mode: str):
    output_file = DATA_OUTPUT_DIR / f"scraped_results_{entry_mode}.csv"

    rows = []
    for item in results:
        rows.append(
            {
                "url_id": item.url_id,
                "company_id": item.company_id,
                "company_name": item.company_name,
                "company_url": item.company_url,
                "url_type": item.url_type,
                "url": item.url,
                "article_type": item.article_type,
                "article_date": item.article_date,
                "article_title": item.article_title,
                "article_url": item.article_url,
                "is_new": item.is_new,
            }
        )

    write_csv(output_file, rows)


# -----------------------------
# マージ処理（バックアップ＋差分 is_new）
# -----------------------------
def merge_results_daily():
    true_file = DATA_OUTPUT_DIR / "scraped_results_True.csv"
    false_file = DATA_OUTPUT_DIR / "scraped_results_False.csv"
    merged_file = DATA_OUTPUT_DIR / "scraped_results_merged.csv"

    # ★ 既存 merged をバックアップ
    backup_file(merged_file)

    true_rows = load_csv(true_file)
    false_rows = load_csv(false_file)

    merged_dict = {}

    # 過去データは is_new=False
    for row in false_rows:
        row["is_new"] = "False"
        merged_dict[row["article_url"]] = row

    # 最新データは差分判定
    for row in true_rows:
        url = row["article_url"]
        if url in merged_dict:
            row["is_new"] = "False"
        else:
            row["is_new"] = "True"
        merged_dict[url] = row

    merged_rows = list(merged_dict.values())
    merged_rows.sort(key=lambda r: r["article_date"], reverse=True)

    write_csv(merged_file, merged_rows)
    print("Merged file created:", merged_file)


# -----------------------------
# メイン処理（スクレイピング → マージ）
# -----------------------------
def main():
    if len(sys.argv) < 2:
        print("mode を指定してください（T / F / True / False）")
        return

    entry_mode_raw = sys.argv[1]
    entry_mode = normalize_mode(entry_mode_raw)

    if entry_mode == "":
        print(f"不正な mode です: {entry_mode_raw}")
        return

    companies = load_companies()
    urls = load_urls(entry_mode=entry_mode)

    # ★ スクレイピング処理（関数化）
    all_results = scrape_urls(urls, companies)

    save_results(results=all_results, entry_mode=entry_mode)
    print("Scraping completed.")

    # ★ スクレイピング後に毎日マージ
    merge_results_daily()

    print("Merge completed.")


if __name__ == "__main__":
    main()

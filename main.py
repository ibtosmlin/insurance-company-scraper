import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from app.fetcher import fetch_html
from app.models import NewsItem
from app.parsers import axa_parser

DATA_INPUT_DIR = Path("data/input")
DATA_OUTPUT_DIR = Path("data/output")
encoding = "utf-8"
mapping = {
    "Axa": axa_parser.parse,
    # "Aflac": aflac_parser.parse,
    # "Fwdlife": fwdlife_parser.parse,
}


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
# URL 情報読み込み + url_id 自動生成
# -----------------------------
def load_urls(entry_mode: str) -> list[dict]:
    urls = []
    with open(DATA_INPUT_DIR / "urls.csv", encoding=encoding) as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_id = row["company_id"]
            url_type = row["url_type"]
            url = row["url"]
            if row["mode"] != entry_mode:
                continue

            # url_id を生成
            row["url_id"] = generate_url_id(
                company_id=company_id, url_type=url_type, url=url
            )

            # 年度抽出（parser に渡すと便利）
            row["year"] = extract_year_from_url(url=url)

            urls.append(row)
    return urls


# -----------------------------
# url_id 生成ロジック
# -----------------------------
def generate_url_id(company_id: str, url_type: str, url: str) -> str:
    parsed = urlparse(url=url)

    # path を正規化
    # /company/newsrelease/2023.html → company_newsrelease_2023.html
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
# CSV 保存
# -----------------------------
def save_results(results: list[NewsItem], entry_mode: str):
    output_file = DATA_OUTPUT_DIR / f"scraped_results_{entry_mode}.csv"
    if output_file.exists():
        output_file.unlink()

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        # ★ ヘッダ行を書き込む
        writer.writerow(
            [
                "url_id",
                "company_id",
                "company_name",
                "company_url",
                "url_type",
                "url",
                "article_type",
                "article_date",
                "article_title",
                "article_url",
                "is_new",
            ]
        )

        # ★ データ行を書き込む
        for item in results:
            writer.writerow(
                [
                    item.url_id,
                    item.company_id,
                    item.company_name,
                    item.company_url,
                    item.url_type,
                    item.url,
                    item.article_type,
                    item.article_date,
                    item.article_title,
                    item.article_url,
                    item.is_new,
                ]
            )


# -----------------------------
# メイン処理
# -----------------------------
def main():
    # 引数チェック
    if len(sys.argv) < 2:
        print("mode を指定してください（T または F）")
        return

    entry_mode = sys.argv[1]

    # ★ mode のバリデーション
    if entry_mode not in ("True", "False"):
        print(f"不正な mode です: {entry_mode}")
        print("使用できるのは 'True'（最新URLのみ） または 'False'（過去URLのみ）です")
        return

    companies = load_companies()
    urls = load_urls(entry_mode=entry_mode)

    all_results = []

    for entry in urls:
        company_id = entry["company_id"]
        url = entry["url"]
        url_type = entry["url_type"]
        url_id = entry["url_id"]
        year = entry["year"]

        company_name = companies[company_id]["company_name"]
        company_url = companies[company_id]["company_url"]

        parser_func = select_parser(company_id)
        if not parser_func:
            print(f"Parser not found for company: {company_id}")
            continue

        print(f"Fetching: {company_id} - {url_type} - {url}")

        html = fetch_html(url)

        with open(".debug.html", "w", encoding=encoding) as f:
            f.write(html)
            f.write("/n")
            f.write(url)

        # ★ parser に必要な全引数を渡す（最新仕様）
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

    save_results(results=all_results, entry_mode=entry_mode)
    print("Scraping completed.")


if __name__ == "__main__":
    main()

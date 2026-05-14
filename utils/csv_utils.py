# util/csv_utils.py
import csv
from pathlib import Path

encoding = "utf-8"


# -----------------------------
# CSV 書き込み（共通）
# -----------------------------
def write_csv(path: Path, rows: list[dict]):
    with open(path, "w", encoding=encoding, newline="") as f:
        writer = csv.writer(f)
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
        for r in rows:
            writer.writerow(
                [
                    r["url_id"],
                    r["company_id"],
                    r["company_name"],
                    r["company_url"],
                    r["url_type"],
                    r["url"],
                    r["article_type"],
                    r["article_date"],
                    r["article_title"],
                    r["article_url"],
                    r["is_new"],
                ]
            )


# -----------------------------
# CSV 読み込み（共通）
# -----------------------------
def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding=encoding) as f:
        return list(csv.DictReader(f))

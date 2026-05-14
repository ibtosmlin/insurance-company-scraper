from dataclasses import dataclass

@dataclass
class NewsItem:
    url_id: str            # Axa@ニュースリリース@____2024 のようなID
    company_id: str        # Axa
    company_name: str      # アクサ生命保険株式会社
    company_url: str       # https://www.axa.co.jp
    url_type: str          # ← ここを変更（ニュースリリース / お知らせ）
    url: str               # 一覧ページURL
    article_type: str      # 記事の種類（ニュースリリース等）
    article_date: str      # 2024-12-24
    article_title: str     # 記事タイトル
    article_url: str       # 記事の個別URL
    is_new: str            # "True" / "False"
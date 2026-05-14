# app/parsers/axa_parser.py

from bs4 import BeautifulSoup
from utils.adj_utils import adj_dlt

from app.models import NewsItem


def parse(
    html: str,
    url: str,
    url_type: str,
    company_id: str,
    company_name: str,
    company_url: str,
    url_id: str,
    year: str,
) -> list[NewsItem]:

    soup = BeautifulSoup(html, "html.parser")
    results: list[NewsItem] = []

    # AXA のニュース一覧は ul[class^="News__Table"] に入っている
    news_list = soup.find("ul", class_=lambda c: c and c.startswith("News__Table"))
    if not news_list:
        return results

    # 年を取得
    year_el = soup.find("h2", class_=lambda c: c and c.startswith("BorderedTitle"))
    yyyy = ""
    if year_el:
        text = year_el.get_text(strip=True)
        import re

        m = re.match(r"(\d{4})年", text)
        if m:
            yyyy = m.group(1)

    for li in news_list.find_all(
        "li", class_=lambda c: c and c.startswith("News__Row")
    ):
        # 日付
        date_el = li.find(
            "span", class_=lambda c: c and c.startswith("News__DateColumn")
        )
        # タイトル
        title_el = li.find(
            "span", class_=lambda c: c and c.startswith("News__TextContent")
        )
        # リンク
        link_el = li.find("a", href=True)

        if not (date_el and title_el and link_el):
            continue

        raw_date = date_el.get_text(strip=True)
        raw_title = title_el.get_text(strip=True)
        raw_link = link_el["href"]
        raw_date = f"{yyyy}年{raw_date}"

        # adj_dlt で正規化
        date, link, title = adj_dlt(
            raw_date,
            raw_link,
            raw_title,
            company_url,
            url,
        )

        results.append(
            NewsItem(
                url_id=url_id,
                company_id=company_id,
                company_name=company_name,
                company_url=company_url,
                url_type=url_type,
                url=url,
                article_type="ニュースリリース",
                article_date=date,
                article_title=title,
                article_url=link,
                is_new="False",
            )
        )

    return results

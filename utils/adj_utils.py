"""
adj.py
スクレイピング結果の「日付・リンク・タイトル」を正規化する共通ユーティリティ。

提供関数:
- adj_dlt(d, l, t, server, cururl) → (date, link, title)
- _adj_date(date_str)
- _adj_link(link, server, cururl)
- _adj_title(title_str)
"""

import re


# ----------------------------------------
# タイトル補正
# ----------------------------------------
def _adj_title(title_str: str) -> str:
    """
    記事タイトルの表記ゆれを正規化する。
    - 改行・タブ除去
    - HTMLエスケープ除去
    - ゼロ幅スペース除去
    - 連続スペースを1つに
    """
    if not title_str:
        return ""

    title = title_str
    title = title.replace("\n", "").replace("\t", "")
    title = title.replace("&gt", "").replace("&lt", "")
    title = title.replace("\u200b", "").replace("\u3000", "")
    title = re.sub(r"\s+", " ", title)
    return title.strip()


# ----------------------------------------
# 日付補正
# ----------------------------------------
def _adj_date(date_str: str) -> str:
    """
    日付を yyyy-mm-dd に正規化する。
    - 「2024年12月24日」
    - 「2024/12/24」
    - 「2024.12.24」
    - 「2024-12-24」
    などをすべて統一。
    """
    if not date_str:
        return "----"

    date = _adj_title(date_str)
    if date == "":
        return "----"

    # 年月日 → yyyy-mm-dd
    date = date.replace("年", "-").replace("月", "-").replace("日", "")
    date = date.replace(".", "-").replace("/", "-")

    try:
        y, m, d = map(int, date.split("-"))
        return f"{y:04d}-{m:02d}-{d:02d}"
    except Exception:
        # 解析不能な場合はそのまま返す
        return date


# ----------------------------------------
# リンク補正（最強版）
# ----------------------------------------
def _adj_link(link: str | None, server: str, cururl: str) -> str:
    """
    リンクの表記ゆれを正規化し、絶対URLに変換する。
    - None / "" / "#" → cururl を返す
    - "../" → 親ディレクトリへ
    - "/" → ルート相対 → server + path
    - "http" → そのまま
    - その他 → 現在のURLからの相対パス
    """

    # cururl の親ディレクトリを取得
    base = cururl
    if base.endswith(".html") or base.endswith(".htm") or base.endswith("/"):
        base = base[: base.rfind("/")]

    # リンクが空の場合
    if not link or link == "#":
        return base

    # 親ディレクトリ参照 ../
    if link.startswith("../"):
        parent = base[: base.rfind("/")]
        return parent + link[2:]

    # 絶対URL
    if link.startswith("http"):
        return link

    # ルート相対
    if link.startswith("/"):
        return server.rstrip("/") + link

    # 現在のURLからの相対
    if base.endswith("/"):
        return base + link
    else:
        return base + "/" + link


# ----------------------------------------
# まとめて補正（date, link, title）
# ----------------------------------------
def adj_dlt(d: str, l: str, t: str, server: str, cururl: str) -> tuple[str, str, str]:
    """
    日付・リンク・タイトルをまとめて正規化する。
    parser からは基本的にこれだけ呼べばOK。
    """
    d = _adj_date(d)
    l = _adj_link(l, server, cururl)
    t = _adj_title(t)
    return (d, l, t)

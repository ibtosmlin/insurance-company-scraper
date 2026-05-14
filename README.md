insurance-company-scraper/
├── main.py
├── app/
│   ├── __init__.py
│   ├── fetcher.py
│   ├── models.py
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── axa_parser.py
│   │   └── aflac_parser.py
│   └── utils.py   ← 必要なら使う
├── data/
│   ├── input/
│   │   ├── companies.csv
│   │   └── urls.csv
│   └── output/
│       └── scraped_results.csv
├── README.md
├── pyproject.toml
└── uv.lock


✔ main.py
全体の流れをまとめるだけ
（URL → fetch → parse → print）
✔ fetcher.py
HTML を取るだけ
（requests + Selenium 両対応）
✔ models.py
データの型（NewsItem）を定義するだけ
✔ parsers/axa_parser.py
AXA の HTML を解析する
✔ parsers/aflac_parser.py
AFLAC の HTML を解析する

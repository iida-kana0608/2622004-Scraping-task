import time

import csv

import requests

from bs4 import BeautifulSoup

from urllib.parse import urljoin, urlparse, urldefrag

# 武蔵野大学のトップページ

start_url = "https://www.musashino-u.ac.jp/"

# 同じドメインかどうかを判定するための情報

domain = urlparse(start_url).netloc

# URLとタイトルを保存する辞書

sitemap = {}

# これから調べるURLを保存するリスト

url_list = [start_url]

# すでに調べたURLを保存する集合

visited = set()

# Webページを取得するための設定

headers = {

    "User-Agent": "Mozilla/5.0"

}

# 辞書の内容をCSVファイルに保存する関数

def save_csv():

    with open("sitemap.csv", "w", newline="", encoding="utf-8-sig") as f:

        writer = csv.writer(f)

        # ヘッダーを書く

        writer.writerow(["URL", "Title"])

        # 辞書の内容を書き出す

        for url, title in sitemap.items():

            writer.writerow([url, title])

    print(f"CSVに保存しました。取得件数：{len(sitemap)}")

try:

    # Webサイトを巡回する

    while url_list:

        # 調べるURLを1つ取り出す

        url = url_list.pop(0)

        # すでに調べたURLならスキップする

        if url in visited:

            continue

        visited.add(url)

        try:

            # Webサイトへの負荷を軽減するため、アクセス前に1秒待つ

            time.sleep(1)

            # Webページを取得する

            res = requests.get(

                url,

                headers=headers,

                timeout=15

            )

            # 正常に取得できなかった場合はエラーにする

            res.raise_for_status()

            # HTMLを解析する

            html_soup = BeautifulSoup(res.content, "html.parser")

            # ページのタイトルを取得する

            title_tag = html_soup.find("title")

            if title_tag is not None:

                title = title_tag.get_text(strip=True)

            else:

                title = ""

            # URLをキー、タイトルを値として辞書に保存する

            sitemap[url] = title

            print(f"取得件数：{len(sitemap)}")

            print(f"URL：{url}")

            print(f"タイトル：{title}")

            print("-" * 40)

            # 10ページ取得するごとにCSVへ保存する

            if len(sitemap) % 10 == 0:

                save_csv()

            # ページ内のリンクをすべて取得する

            a_list = html_soup.find_all("a", href=True)

            for a in a_list:

                # リンク先のURLを取得する

                link = urljoin(url, a["href"])

                # URLの末尾にあるフラグメントを取り除く

                link, _ = urldefrag(link)

                # URLを解析する

                parsed_url = urlparse(link)

                # HTTPまたはHTTPS以外のリンクは除外する

                if parsed_url.scheme not in ("http", "https"):

                    continue

                # 武蔵野大学の同一ホスト以外は除外する

                if parsed_url.netloc != domain:

                    continue

                # すでに調べたURLやリストにあるURLは追加しない

                if link not in visited and link not in url_list:

                    url_list.append(link)

        except requests.exceptions.RequestException as e:

            print(f"アクセスエラー：{url}")

            print(e)

        except Exception as e:

            print(f"処理エラー：{url}")

            print(e)

except KeyboardInterrupt:

    # Control + Cで停止した場合

    print("\n処理を中断しました。取得済みのデータを保存します。")

finally:

    # 最後に取得済みのデータをCSVへ保存する

    save_csv()

    print("処理を終了しました。")

    print(f"取得したページ数：{len(sitemap)}")

    print("sitemap.csv を確認してください。")
import requests
import json
import os
from dotenv import load_dotenv
import datetime
import requests.utils

# .envファイルからトークンをロード
load_dotenv()
token = os.environ.get("GITHUB_TOKEN")

# GitHub APIヘッダーの設定
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {token}"
}

# 検索クエリの設定
search_query = "management.azure.com/subscriptions/"
encoded_query = requests.utils.quote(search_query)
search_url = f"https://api.github.com/search/code?q={encoded_query}&per_page=10"

# コード検索リクエスト
response = requests.get(search_url, headers=headers)

if response.status_code == 200:
    code_results = response.json()['items']

    # 検索結果の表示
    print(f"Found {len(code_results)} code results containing the query \"{search_query}\".")

    urls = [code['html_url'] for code in code_results]

    # 現在時刻の取得
    current_time = str(datetime.datetime.now())
    # 検索結果をJSONファイルに保存
    with open(f"{current_time}-code_results.json", 'w') as f:
        json.dump(urls, f, indent=4)

    # 結果の表示（リポジトリ名、ファイルパス、URL）
    for result in urls:
        print(f"Repository: {result['repository']['full_name']}\nFile: {result['path']}\nURL: {result['html_url']}\n")
else:
    print(f"Failed to search code: {response.status_code}")
    print(f"Error response: {response.json()}")  # エラーの詳細を表示

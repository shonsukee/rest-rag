# Automatic correction of REST API misuse using Retrieval-Augmented Generation

## About

　Retrieval-Augmented Generation (RAG) is a technique that combines text generation by Large Language Models (LLMs) with retrieval of external information to improve response accuracy. By combining the retrieval of external information, it is expected to make it easier to update the output of the LLM with the latest information, clarify the basis of the output results, and suppress the phenomenon of generating information that is not based on facts (hallucination).

## Premise

- OpenAI API (charge)
- Pinecone API Key (free)

## Usage
1. URL, タグを用いてコンテキストを格納
```
> . ./bin/activate
> cd /lib
> python3 store_auto_llama.py
	> 実行する前にすること！
		> /dataset/{namespace}/url/{version}.txtに格納したいURLリストを格納
		> URLに共通しているタグをextractWithScrapingに格納(defaultではarticle)
		> PineconeDBのindex_nameを変更(.envに書き込むと良い)
		> namespaceにAPI名を格納
		> versionに latest / outdated のどちらかを記入
```

2. コードの自動修正
```
> python3 cui_by_llama.py
	> 実行する前にすること！
		> namespaceにAPI名を格納
		> data_typeにcommit / issueを指定
```

3. GUIで修正(legacy)
```
> cd /legacy/gui/
> streamlit run chat_by_llama.py
```

## File Usage

### Store
- lib/select_with_history.py
    - GUIで，ユーザが修正できていると評価した修正履歴のみDBに格納

- lib/store_llama.py
    - 格納する情報を`/data`に配置しておき，自動で格納

- lib/store_auto_llama.py ☆
    - URLをリストに格納してテキスト情報を自動で格納
    - どのタグを抽出するか指定可

### Retrieval
- lib/chat_by_llama.py
    - チャット形式で行う一番ベーシックなタイプ．
    - 全てのプロンプトに対して関連する情報を抽出し，自動修正を行う

- lib/cui_by_llama.py ☆
    - プロンプトコードに関連する情報を抽出して自動修正を行い，ファイル出力する

- lib/add_with_history.py
    - Llamaを用いて，プロンプトに関連した抽出情報の関連度を，修正結果の関連度が上回ると修正結果を新しくDBに格納する

- lib/with_history.py
    - add_with_history.pyのリッチ版

- lib/chat_by_langchain.py
    - LangChainを用いて，プロンプトに関連するデータをDBから抽出する．

- lib/chat_by_pinecone.py
    - ライブラリを使わず，プロンプトに関連するデータをDBから直接抽出する．

- lib/del_index.py
    - indexの削除

- lib/repo.py
    - API nameのファイルを作成して，出力のみをテキストファイルへ保存する

- lib/retrieve_with_history.py
    - プロンプトに 関連情報 + 過去の修正履歴 を加えて自動修正


## 仮想環境
```
# 仮想環境有効化
. ./bin/activate

# 必要モジュールインストール
pip install -r requirements.txt

# 仮想環境無効化
deactivate
```

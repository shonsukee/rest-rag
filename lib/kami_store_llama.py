from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core import SummaryIndex
from llama_index.core import Document
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
import logging
import os
import sys
import time
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

#################
## Data Config ##
#################
namespace = "switchbot"
version = "outdated"

class StoreDB:
	def __init__(self):
		# ログレベルの設定
		logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, force=True)
		logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

		logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, force=True)
		logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

		api_key = os.environ.get('PINECONE_API_KEY')
		if not api_key:
			raise ValueError("PineconeのAPIキーが見つかりません。'.env'ファイルにPINECONE_API_KEYを設定してください。")

		self.pc = Pinecone(api_key=api_key)

	# DBへ入力クエリとLLMからの回答を保存
	def insert_query_response_to_db(self, documents, index_name, chunk_size, chunk_over_lap, namespace = None):
		try:
			pinecone_index = self.pc.Index(index_name)
			Settings.chunk_size = chunk_size
			Settings.chunk_overlap = chunk_over_lap

			vector_store = PineconeVectorStore(
				pinecone_index=pinecone_index,
				add_sparse_vector=True,
				namespace=namespace
			)

			storage_context = StorageContext.from_defaults(vector_store=vector_store)
			# contextオブジェクトからチャンクを作成し，Embeddingしてる
			VectorStoreIndex.from_documents(
				documents=documents, storage_context=storage_context
			)

			print("--------------完成！---------------")
		except Exception as e:
			print("-----------エラー発生！ここから----------")
			print(e)
			print("-----------エラー発生！ここまで----------")

class ExtractContext:
	def __init__(self) -> None:
		load_dotenv()
		self.store_db = StoreDB()

	def extractWithScraping(self, url_list, chunk_size = 512, chunk_over_lap = 50):
		"""
		URLからスクレイピングしてテキストを抽出

		Args:
			url_list (str): URLのリスト
			chunk_size (int): テキストを分割するチャンクサイズ. Defaults to 512.
			chunk_over_lap (int): チャンク同士の重複する文字数. Defaults to 50.
		"""
		# 各URLからスクレイピングを行う
		natural_languages = []
		code_blocks = []
		for url in url_list:
			try:
				# URL からテキスト抽出
				html = requests.get(url).text
				soup = BeautifulSoup(html, "html.parser")
				tag = 'article'
				article = soup.find('article')

				if article == "":
					logging.warning(f"{url}: <{tag}>タグが見つかりませんでした。")
					continue

				# コードを抽出して自然言語と分離
				for pre in article.find_all(['pre', 'code']):
					code_blocks.append(pre.get_text())
					pre.extract()

				natural_languages.append(article.get_text(separator=" ").strip())
			except Exception as e:
				print(f"{url}: \n<{tag}>タグが見つかりませんでした。\n")
				print(f"{e}")

		if len(code_blocks) == 0:
			return

		# テキスト情報をドキュメント化して，ベクトルDBに格納
		n_documents = [Document(text=t) for t in natural_languages]
		c_documents = [Document(text=t) for t in code_blocks]

		self.store_db.insert_query_response_to_db(n_documents, f"{version}-lang", chunk_size, chunk_over_lap, namespace)
		self.store_db.insert_query_response_to_db(c_documents, f"{version}-code", chunk_size, chunk_over_lap, namespace)

	def extractWithFile(self, index_name = "revision-history", chunk_size = 512, chunk_over_lap = 50):
		"""
		ファイルからテキストを抽出

		Args:
			index_name (str): Pinecone DB の index name. Defaults to "revision-history".
			chunk_size (int): テキストを分割するチャンクサイズ. Defaults to 512.
			chunk_over_lap (int): チャンク同士の重複する文字数. Defaults to 50.
		"""
		namespace = "fitbit"
		directory_path = f"../history/db/{namespace}/"

		for root, dirs, files in os.walk(directory_path):
			for filename in files:
				# ファイルの内容を読み取る
				file_path = os.path.join(root, filename)
				with open(file_path, 'r') as file:
					content = file.read()
					# Documentオブジェクトを作成
					documents = [Document(text=content)]
				time.sleep(10)
				## コンテキストをベクトルDBに格納
				self.store_db.insert_query_response_to_db(documents, index_name, chunk_size, chunk_over_lap, namespace)


if __name__ == "__main__":
	context = ExtractContext()
	url_list = []
	file_path = f"../dataset/{namespace}/url/{version}.txt"

	with open(file_path, 'r') as file:
		url_list = [line.strip() for line in file.readlines()]

	context.extractWithScraping(url_list)
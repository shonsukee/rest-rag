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
		index_name = "rag-research"
		# 各URLからスクレイピングを行う
		content = []
		for url in url_list:
			try:
				## URL からテキスト抽出
				html = requests.get(url).text
				soup = BeautifulSoup(html, "html.parser")
				# タグを挿入
				tag = 'article'
				raw_context = soup.find(tag)

				# テキストのみを抽出
				if raw_context:
					context = raw_context.get_text(separator=' ').strip()
					content.append(' '.join(context.split()))
				else:
					logging.warning(f"{url}: <{tag}>タグが見つかりませんでした。")
			except Exception as e:
				print(raw_context)
				print(f"{url}: \n<{tag}>タグが見つかりませんでした。\n")

		documents = [Document(text=t) for t in content]

		## コンテキストをベクトルDBに格納
		self.store_db.insert_query_response_to_db(documents, index_name, chunk_size, chunk_over_lap, namespace)

if __name__ == "__main__":
	context = ExtractContext()
	url_list = []
	file_path = f"../dataset/{namespace}/url/{version}.txt"

	with open(file_path, 'r') as file:
		url_list = [line.strip() for line in file.readlines()]

	context.extractWithScraping(url_list)
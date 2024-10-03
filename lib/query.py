import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever, KeywordTableSimpleRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor

class Query:
	def __init__(self, namespace=None):
		load_dotenv()
		self.namespace = namespace
		self.client = OpenAI()

	def initialize_pinecone(self, index_name):
		pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
		index_name = os.environ.get(index_name)
		print(index_name)

		pinecone_index = pc.Index(index_name)
		vector_store = PineconeVectorStore(
			pinecone_index=pinecone_index,
			add_sparse_vector=True,
			namespace=self.namespace,
		)

		# vector retriever
		index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
		vector_retriever = VectorIndexRetriever(
			index=index,
			similarity_top_k=5, # 関連度上位5件取得
		)

		response_synthesizer = get_response_synthesizer()
		return RetrieverQueryEngine(
			retriever=vector_retriever,
			response_synthesizer=response_synthesizer,
			node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)], # 関連度の閾値
		)

	def query_index(self, user_query):
		"""
		ユーザー入力に関連するインデックスを検索する関数

		Args:
			user_query (string): ユーザが修正したいコード

		Returns:
			chatgpt_response.choices[0].message.content: LLMからの回答
			context: DBから抽出したコンテキスト
			similarity: DBから抽出したコンテキストの関連度の平均値
		"""
		context = ""
		similarities = []
		pinecone_indexes = [
			"latest_natural_language",
			"latest_code",
			"outdated_natural_language",
			"outdated_code",
		]

		# 4つ分のDBへ取得処理を行うためのループを回す
		for index in pinecone_indexes:
			self.query_engine = self.initialize_pinecone(index.upper())
			# クエリ結果から関連ノードを取得
			response = self.query_engine.query(user_query)
			related_nodes = response.source_nodes
			context += f"\n## Technical Specifications for {index.replace('_', ' ').capitalize()}\n"
			for idx, node in enumerate(related_nodes):
				context += f"""\nContext number {idx+1} (score: {node.score}): \n{node.text}"""
				similarities.append(node.score)

		# 関連度の平均計算
		similarity = np.mean(similarities) if len(similarities) > 0 else 0

		combined_query = f"""
### Instruction
You are an API-specific AI assistant, use the following pieces of context to answer the requirement at the end. If you don't know the answer, just say that you don't know, can I help with anything else, don't try to make up an answer.

### Context
{context}

### Input Data
{user_query}

### Output Indicator
Follow the contextual information when making modifications. Make all modifications in the function except for imports. Keep the answer as concise as possible. Output only code.
"""

		chatgpt_response = self.client.chat.completions.create(
			model="gpt-4o",
			messages=[
				{"role": "system", "content": f"You are a chatbot that modifies an old version of the {self.namespace} API to a new one. Relevant information must be followed."},
				{"role": "user", "content": combined_query}
			]
		)
		return chatgpt_response.choices[0].message.content, context, similarity

import os
from dotenv import load_dotenv
from pinecone import Pinecone

HISTORY_INDEX_NAME="rag-research"
NAMESPACE = "switchbot"

load_dotenv()

def del_index():
	pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
	index = pc.Index(HISTORY_INDEX_NAME)
	index.delete(delete_all=True, namespace=NAMESPACE)

def main():
	del_index()

if __name__ == "__main__":
	main()

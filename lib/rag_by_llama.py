import os
from rag_query import Query

def main():
	print("running...")

	### 変更点
	# 1. 対象を変更する場合はtargetを変更
	# 2. typeを指定
	namespace = "switchbot"
	data_type = "commit"
	query = Query(namespace=namespace)

	directory_path = f"../dataset/{namespace}/{data_type}/"
	for filename in os.listdir(directory_path):
		# ファイルの内容を読み取る
		file_path = os.path.join(directory_path, filename)
		prompt = ""
		with open(file_path, 'r') as file:
			prompt = file.read()

		# ファイルが空でないかつ，特定のディレクトリ指定
		if prompt != "":
		# if prompt != "" and (
			# filename.split(".")[0] == "19"): # 15.pyのみ実行
			# ディレクトリ作成
			new_file_name = filename.split(".")[0]
			new_dir_path = f"../history/{namespace}/{data_type}/{new_file_name}/"
			os.makedirs(new_dir_path, exist_ok=True)

			# RAGの適用
			idx = 0
			print(f"----- No. {new_file_name} ----")
			while idx < 5:
				idx+=1
				# context, similarity = query.query_index(prompt)
				response, context, similarity = query.query_index(prompt)
				with open(new_dir_path + f"{namespace}-{data_type}-{idx}.txt", "w") as f:
					f.write("---------------User Query---------------\n")
					f.write(prompt)
					f.write("\n\n---------------Relevant Context---------------\n")
					f.write(context)
					f.write("\n\n---------------Similarity Score---------------\n")
					f.write(str(similarity))
					f.write("\n\n---------------Response---------------\n")
					f.write(response)

				print(f"idx: {idx}-finish.")

	print("complete!")

if __name__ == "__main__":
	main()

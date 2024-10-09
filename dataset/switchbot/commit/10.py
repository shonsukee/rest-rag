#!usr/bin/env python3
import os
from dotenv import load_dotenv
import requests
import pprint
import pathlib
import json

# .envを読み込んで環境変数を設定
load_dotenv()

# 環境変数からAPIキーを取得
API_KEY = os.getenv("SWITCHBOT_APIKEY")
# 共通
output_dir = pathlib.Path("output")
base_url = "https://api.switch-bot.com"
headers = {
    "Authorization" : API_KEY
}
def save_json(json_dic, filename):
    output_dir.mkdir(exist_ok=True)
    filepath = output_dir / pathlib.Path(filename)
    with open(filepath, "w") as f:
        json.dump(json_dic, f, ensure_ascii=False, indent=4)
def get_devices():
    api_url = "/v1.0/devices"
    url = base_url + api_url
    r = requests.get(url, headers=headers)
    res_dic = r.json()
    return res_dic
def get_device_status(deviceId):
    api_url = "/v1.0/devices/" + deviceId + "/status"
    url = base_url + api_url
    r = requests.get(url, headers=headers)
    res_dic = r.json()
    return res_dic


def main():
    res_dic = get_devices()
    save_json(res_dic, "devicelist.json")
    print("完了")

if __name__ == "__main__":
    main()
import os
import json
import requests

CONFIG_FILE = "app_config.json"
APP_INFO_FILE = "data/app_info.json"

os.makedirs("data", exist_ok=True)

try :
    with open(CONFIG_FILE) as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"{CONFIG_FILE}ファイルがありません")
    exit()

# アプリを作成する
params= {
    'name': config['app_name'],   
    'description': config['description'], 
    'permission': config['permission']
}
r = requests.post(f"https://{config['host']}/api/app/create", json=params)

print(r)
if r.status_code != 200 :
    print("アプリ作成でエラーが発生しました。")
    print(r.text)
    exit()

print("アプリ作成完了")

app_info = json.loads(r.text)
print(f"id : {app_info['id']}")
print(f"secret : {app_info['secret']}")
print("")

# アプリ情報をファイルに保存
with open(APP_INFO_FILE, 'w') as f:
    json.dump(app_info, f, indent=4)

print("次に create_session.py を実行してください")
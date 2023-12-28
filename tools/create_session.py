import os
import json
import requests

CONFIG_FILE = "app_config.json"
APP_INFO_FILE = "data/app_info.json"
SESSION_INFO_FILE = "data/session_info.json"

os.makedirs("data", exist_ok=True)

try :
    with open(CONFIG_FILE) as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"{CONFIG_FILE}ファイルがありません")
    exit()

try :
    with open(APP_INFO_FILE) as f:
        app_info = json.load(f)
except FileNotFoundError:
    print(f"{APP_INFO_FILE}ファイルがありません")
    exit()


# セッションを作成する
params = {
    'appSecret' : app_info['secret']
}
r = requests.post(f"https://{config['host']}/api/auth/session/generate", json=params)
print(r)
if r.status_code != 200 :
    print("セッション作成でエラーが発生しました。")
    print(r.text)
    exit()

print("セッション作成完了")

session_info = json.loads(r.text)
print(f"token : {session_info['token']}")

# セッション情報をファイルに保存
with open(SESSION_INFO_FILE, 'w') as f:
    json.dump(session_info, f, indent=4)

print("")
print("Bot用のアカウントで以下のURLにアクセスし、認証してください")
print(session_info['url'])
print("")
print("認証後、 create_token.py を実行してください")


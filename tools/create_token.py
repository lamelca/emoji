import os
import json
import requests
import hashlib

CONFIG_FILE = "app_config.json"
APP_INFO_FILE = "data/app_info.json"
SESSION_INFO_FILE = "data/session_info.json"
USERKEY_INFO_FILE = "data/userkey_info.json"
TOKEN_INFO_FILE = "data/token_info.json"

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

try :
    with open(SESSION_INFO_FILE) as f:
        session_info = json.load(f)
except FileNotFoundError:
    print(f"{SESSION_INFO_FILE}ファイルがありません")
    exit()


# トークンを作成する
params ={
  'appSecret' : app_info['secret'],
  'token' : session_info['token']
}

r  = requests.post(f"https://{config['host']}/api/auth/session/userkey", json=params)
print(r)
if r.status_code != 200 :
    print("ユーザーキー取得でエラーが発生しました。")
    print(r.text)
    exit()

print("ユーザーキー取得完了")

userkey_info = json.loads(r.text)
print(f"userkey : {userkey_info['accessToken']}")
    
# ユーザーキー情報をファイルに保存
with open(USERKEY_INFO_FILE, 'w') as f:
    json.dump(userkey_info, f, indent=4)

# ユーザーキーとアプリ情報からアクセストークンを作成する
tmp_str = userkey_info['accessToken'] + app_info['secret']
access_token = hashlib.sha256(tmp_str.encode()).hexdigest()
print(f"access_token : {access_token}")

token_info = {
    'token' : access_token
}

# アクセストークンをファイルに保存
with open(TOKEN_INFO_FILE, 'w') as f:
    json.dump(token_info, f, indent=4)

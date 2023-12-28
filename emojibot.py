import json
import requests
import datetime
import time

CONFIG_FILE = "config.json"
EMOJIBOT_SAVEDARA_FILE = "emojibot_savedata.json"

try :
    with open(CONFIG_FILE) as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"{CONFIG_FILE}ファイルがありません")
    exit()

try :
    with open(EMOJIBOT_SAVEDARA_FILE) as f:
        emojibot_savedata = json.load(f)
        since_id = emojibot_savedata['since_id']
except FileNotFoundError:
    since_id = None
    emojibot_savedata  = {
        'since_id' : since_id,
    }

since_datetime = datetime.datetime.utcnow()

# ノートを投稿する
def create_note(text, visibility, localOnly, reaction_acceptance, cw = None):
    if cw is None:
        params ={
            'i': config['token'],
            'text': text,
            'visibility': visibility,
            'localOnly':  localOnly,
            'reactionAcceptance': reaction_acceptance,
        }
    else:
        params ={
            'i': config['token'],
            'text': text,
            'visibility': visibility,
            'localOnly':  localOnly,
            'reactionAcceptance': reaction_acceptance,
            'cw' : cw
        }

    r  = requests.post(f"https://{config['host']}/api/notes/create", json=params)
    print(r)
    if r.status_code != 200:
        print(f"{datetime.datetime.today()} : ノート投稿でエラーが発生しました。")
        print(r.text)
        return None
    else:
        print(f"{datetime.datetime.today()} : ノート投稿完了")

# 絵文字Botの挙動
def run():
    global since_id
    global since_datetime
    if since_id is None:
        params ={
            'i': config['token'],
            'limit': config['moderation_logs_limit'],
            'type': None
        }
    else:
        params ={
            'i': config['token'],
            'limit': config['moderation_logs_limit'],
            'type': None,
            'sinceId': since_id
        }
        
    # モデレーションログを取得する
    r  = requests.post(f"https://{config['host']}/api/admin/show-moderation-logs", json=params)
    print(r)
    if r.status_code != 200:
        print(f"{datetime.datetime.today()} : モデレーションログ取得でエラーが発生しました。")
        print(r.text)
        return None
    else:
        print(f"{datetime.datetime.today()} : モデレーションログ取得完了")

    moderation_logs_full = json.loads(r.text)
    if len(moderation_logs_full) == 0:
        print("モデレーションログはありません")
        return None

    # since_id を更新する
    if since_id is None: 
        since_id = moderation_logs_full[0]['id']
    else:
        since_id = moderation_logs_full[-1]['id']
    emojibot_savedata['since_id'] = since_id
    with open(EMOJIBOT_SAVEDARA_FILE, 'w') as f:
        json.dump(emojibot_savedata, f, indent=4)

    # モデレーションログを日付(until_datatime)で抽出する
    moderation_logs = list(filter(lambda x: datetime.datetime.strptime(x['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ') > since_datetime, moderation_logs_full))
    if len(moderation_logs) == 0:
        print("最新のモデレーションログはありません")

    # until_datatime を更新する
    since_datetime = datetime.datetime.strptime(moderation_logs_full[-1]['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')

    # 最新のモデレーションログが見つかった場合は古い順で通知する
    for ml in moderation_logs:
        if ml['type'] == 'addCustomEmoji':
            emoji = ml['info']['emoji']
            if config['use_cw_add']:
                cw = f"{config['message_emoji_add']} :{emoji['name']}:"
                header = ""
            else:
                cw = None
                header = f"{config['message_emoji_add']} :{emoji['name']}:\n\n"
            text =  header + \
                    "<small>" \
                    f"name        : `:{emoji['name']}:`\n" \
                    f"category    : `{emoji['category']}`\n" \
                    f"tags        : `{emoji['aliases']}`\n" \
                    f"license     : `{emoji['license']}`\n" \
                    f"isSensitive : `{emoji['isSensitive']}`\n" \
                    f"localOnly   : `{emoji['localOnly']}`\n\n" \
                    f"{config['message_emoji_add_user']}:@{ml['user']['username']}" \
                    "</small>"
            create_note(text, config['visibility_add'], config['local_only'], config['reaction_acceptance'], cw)

        elif ml['type'] == 'updateCustomEmoji':
            emoji = ml['info']['after']
            if config['use_cw_update']:
                cw = f"{config['message_emoji_update']} :{emoji['name']}:"
                header = ""
            else:
                cw = None
                header = f"{config['message_emoji_update']} :{emoji['name']}:\n\n"
            text =  header + \
                    "<small>" \
                    f"name        : `:{emoji['name']}:`\n" \
                    f"category    : `{emoji['category']}`\n" \
                    f"tags        : `{emoji['aliases']}`\n" \
                    f"license     : `{emoji['license']}`\n" \
                    f"isSensitive : `{emoji['isSensitive']}`\n" \
                    f"localOnly   : `{emoji['localOnly']}`\n\n" \
                    f"{config['message_emoji_update_user']}:@{ml['user']['username']}" \
                    "</small>"
            create_note(text, config['visibility_update'], config['local_only'], config['reaction_acceptance'], cw)
           
        elif ml['type'] == 'deleteCustomEmoji':
            emoji = ml['info']['emoji']
            if config['use_cw_delete']:
                cw = f"{config['message_emoji_delete']}"
                header = ""
            else:
                cw = None
                header = f"{config['message_emoji_delete']}\n\n"
            text =  header + \
                    "<small>" \
                    f"name        : `:{emoji['name']}:`\n" \
                    f"{config['message_emoji_delete_user']}:@{ml['user']['username']}" \
                    "</small>"
            create_note(text, config['visibility_delete'], config['local_only'], config['reaction_acceptance'], cw)

        elif ml['type'] == 'createAvatarDecoration':
            deco = ml['info']['avatarDecoration']
            if config['use_cw_add']:
                cw = f"{config['message_decoration_add']} : `{deco['name']}`"
                header = ""
            else:
                cw = None
                header = f"{config['message_decoration_add']}\n\n"
            text =  header + \
                    "<small>" \
                    f"name        : `{deco['name']}`\n" \
                    f"url         : `{deco['url']}`\n" \
                    f"description : `{deco['description']}`\n" \
                    f"{config['message_decoration_add_user']}:@{ml['user']['username']}" \
                    "</small>"
            create_note(text, config['visibility_add'], config['local_only'], config['reaction_acceptance'], cw)

        elif ml['type'] == 'updateAvatarDecoration':
            deco = ml['info']['after']
            if config['use_cw_add']:
                cw = f"{config['message_decoration_update']} : `{deco['name']}`"
                header = ""
            else:
                cw = None
                header = f"{config['message_decoration_update']}\n\n"
            text =  header + \
                    "<small>" \
                    f"name        : `{deco['name']}`\n" \
                    f"url         : `{deco['url']}`\n" \
                    f"description : `{deco['description']}`\n" \
                    f"{config['message_decoration_update_user']}:@{ml['user']['username']}" \
                    "</small>"
            create_note(text, config['visibility_update'], config['local_only'], config['reaction_acceptance'], cw)
 
        elif ml['type'] == 'deleteAvatarDecoration':
            deco = ml['info']['avatarDecoration']
            if config['use_cw_delete']:
                cw = f"{config['message_decoration_delete']} "
                header = ""
            else:
                cw = None
                header = f"{config['message_decoration_delete']}\n\n"
            text =  header + \
                    "<small>" \
                    f"name        : `{deco['name']}`\n" \
                    f"{config['message_decoration_delete_user']}:@{ml['user']['username']}" \
                    "</small>"
            create_note(text, config['visibility_delete'], config['local_only'], config['reaction_acceptance'], cw)
            
# 定期実行
while True:
    run()
    time.sleep(config['running_interval_seconds'])


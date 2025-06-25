import json
import requests
import os

# 本地 JSON 文件路径
LOCAL_JSON_PATH = 'JD.json'
# 远程 JSON 地址
REMOTE_JSON_URL = 'https://raw.githubusercontent.com/qist/tvbox/refs/heads/master/xiaosa/api.json'

# 指定要更新的 key 列表
KEYS_TO_UPDATE = [
    "热播影视", "仓鼠", "瓜萌", "晴天", "再看", "彼岸", "在看", "热播", "晚枫", "诺映", "趣看", "雄鹰"
]

def sync_selected_ext_by_key():
    with open(LOCAL_JSON_PATH, 'r', encoding='utf-8') as f:
        local_data = json.load(f)

    response = requests.get(REMOTE_JSON_URL)
    if response.status_code != 200:
        raise Exception(f"无法获取远程 JSON，状态码: {response.status_code}")
    remote_data = response.json()

    remote_dict = {item['key']: item['ext'] for item in remote_data}

    updated = False
    for item in local_data:
        key = item.get('key')
        if key in KEYS_TO_UPDATE and key in remote_dict:
            item['ext'] = remote_dict[key]
            updated = True

    if updated:
        with open(LOCAL_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(local_data, f, ensure_ascii=False, indent=4)
        print("✅ 已成功更新指定 key 的 ext 字段")
        return True
    else:
        print("⚠️ 没有找到可更新的内容")
        return False

if __name__ == '__main__':
    if sync_selected_ext_by_key():
        # 如果有更新，写入一个标记文件，供后续 Git 提交判断
        with open('.updated', 'w') as f:
            f.write('updated')

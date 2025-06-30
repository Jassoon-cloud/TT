import json
import requests

# 本地 JSON 文件路径
LOCAL_JSON_PATH = 'JD.json'
# 远程 JSON 地址
REMOTE_JSON_URL = 'https://raw.githubusercontent.com/qist/tvbox/refs/heads/master/xiaosa/api.json'

# 指定要更新的 key 列表
KEYS_TO_UPDATE = [
    "热播影视", "仓鼠", "瓜萌", "晴天", "再看", "彼岸", "在看", "热播", "晚枫", "诺映", "趣看", "雄鹰"
]

def sync_selected_ext_by_key():
    # 读取本地 JSON
    try:
        with open(LOCAL_JSON_PATH, 'r', encoding='utf-8') as f:
            local_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ 本地文件读取失败: {e}")
        return False

    # 下载远程 JSON
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(REMOTE_JSON_URL, headers=headers)
        response.raise_for_status()
        remote_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法获取远程 JSON: {e}")
        return False

    # 确保 remote_data 是一个字典并包含 sites 列表
    if not isinstance(remote_data, dict) or 'sites' not in remote_data:
        print("❌ 远程数据不是有效的字典或未包含 sites 字段")
        return False

    # 提取远程和本地的 sites 列表
    remote_sites = remote_data.get('sites', [])
    local_sites = local_data.get('sites', [])

    # 构建 remote_dict（只保留需要更新的 key）
    remote_dict = {}
    for item in remote_sites:
        if isinstance(item, dict) and 'key' in item and 'ext' in item and item['key'] in KEYS_TO_UPDATE:
            remote_dict[item['key']] = item['ext']

    # 遍历本地 sites，更新 ext 字段
    updated = False
    for item in local_sites:
        if not isinstance(item, dict):
            print(f"⚠️ 跳过非字典项: {item}")
            continue

        key = item.get('key')
        if key in KEYS_TO_UPDATE and key in remote_dict:
            new_ext = remote_dict[key]
            if item.get('ext') != new_ext:
                item['ext'] = new_ext
                updated = True

    # 写回文件
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

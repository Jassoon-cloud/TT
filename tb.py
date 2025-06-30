import json
import requests

# 本地 JSON 文件路径
LOCAL_JSON_PATH = 'TB.json'
# 远程 JSON 地址
REMOTE_JSON_URL = 'https://raw.githubusercontent.com/qist/tvbox/refs/heads/master/xiaosa/api.json'

# 白名单设置：这些 key 即使远程没有，也不会被删除
WHITELISTED_KEYS = {"豆瓣", "哔哩大全", "网盘配置", "虎牙直播", "JRKAN直播", "88看球", "瓜子", "荐片", "素白白", "4KAV", "哇哇APP", "零度APP", "低端"}

def sync_sites_with_condition():
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

    if not isinstance(remote_data, dict) or 'sites' not in remote_data:
        print("❌ 远程数据不是有效的字典或未包含 sites 字段")
        return False

    remote_sites = remote_data.get('sites', [])
    local_sites = local_data.get('sites', [])

    updated = False

    # 提取远程所有的 key
    remote_keys = set(site['key'] for site in remote_sites)

    # 更新或新增操作
    for remote_site in remote_sites:
        name = remote_site.get('name')
        key = remote_site.get('key')

        if name and 'APP' in name:
            base_name = name.split("｜")[0]
            new_name = base_name + "影视"

            existing_site = next((site for site in local_sites if site.get('key') == key), None)

            site_info = {
                'key': key,
                'name': new_name,
                'type': remote_site.get('type'),
                'api': remote_site.get('api'),
                'searchable': 1,  # 固定设置为 1
                'ext': remote_site.get('ext', "")  # 如果没有 ext 字段，默认设为空字符串 ""
            }

            # 只有当 quickSearch 存在时才添加到结果中
            if 'quickSearch' in remote_site:
                site_info['quickSearch'] = remote_site['quickSearch']

            # 只有当 filterable 存在时才添加到结果中
            if 'filterable' in remote_site:
                site_info['filterable'] = remote_site['filterable']

            if existing_site:
                existing_site.update(site_info)
            else:
                local_sites.append(site_info)

            updated = True

    # 删除不在远程中的条目，但跳过白名单中的 key
    keys_to_remove = [site['key'] for site in local_sites if
                      site['key'] not in remote_keys and site['key'] not in WHITELISTED_KEYS]

    if keys_to_remove:
        before_len = len(local_sites)
        local_sites[:] = [site for site in local_sites if site['key'] not in keys_to_remove]
        after_len = len(local_sites)
        print(f"🗑️ 已删除 {before_len - after_len} 个非白名单项")
        updated = True

    # 写回文件
    if updated:
        with open(LOCAL_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(local_data, f, ensure_ascii=False, indent=4)
        print("✅ 已成功更新 TB.json 中的 sites 列表")
        return True
    else:
        print("⚠️ 没有找到需要更新的内容")
        return False

if __name__ == '__main__':
    if sync_sites_with_condition():
        with open('.updated', 'w') as f:
            f.write('updated')

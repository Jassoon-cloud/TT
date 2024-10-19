import os
import re
import time
import shutil
import random
import requests
import subprocess
from selenium import webdriver
from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 获取IP
def search_and_save_ips(locations):
    # 设置 Chrome 选项
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # 无头模式（可选）
    chrome_options.add_argument("--no-sandbox")  # 解决 DevToolsActivePort 文件不存在的报错
    chrome_options.add_argument("--disable-dev-shm-usage")  # 解决资源限制的报错

    # 启动 Chrome 浏览器，指定可执行文件路径
    driver = webdriver.Chrome(executable_path='/usr/local/bin/chrome', options=chrome_options)
    
    # 打开网址
    driver.get("http://tonkiang.us/hoteliptv.php")
    time.sleep(10)

    # 定义文件名映射，输出路径为 'IP' 文件夹
    output_dir = 'IP'
    file_mapping = {
        "湖南电信": os.path.join(output_dir, "湖南IP.txt"),
        "湖北电信": os.path.join(output_dir, "湖北IP.txt"),
        "江西电信": os.path.join(output_dir, "江西IP.txt"),
        "上海电信": os.path.join(output_dir, "上海IP.txt"),
        "北京市": os.path.join(output_dir, "北京IP.txt"),
        "河北电信": os.path.join(output_dir, "河北IP.txt"),
        "河南电信": os.path.join(output_dir, "河南IP.txt"),
        "江苏电信": os.path.join(output_dir, "江苏IP.txt"),
        "重庆电信": os.path.join(output_dir, "重庆IP.txt"),
        "浙江电信": os.path.join(output_dir, "浙江IP.txt")
        # 可以继续添加其他地点和对应的文件名
    }

    # 确保输出文件夹存在
    os.makedirs(output_dir, exist_ok=True)

    # 遍历每个地点
    for location in locations:
        # 输入地点并点击搜索
        search_box = driver.find_element(By.XPATH, "//input[@id='search']")
        search_box.clear()
        search_box.send_keys(location)
        search_box.send_keys(Keys.RETURN)

        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'result')))
        results = driver.find_elements(By.CLASS_NAME, "result")
        
        continue_conditions = ["新上线"] + [f"存活{day}天" for day in range(1, 90)]

        # 获取对应的文件名
        output_filename = file_mapping.get(location, os.path.join(output_dir, f"{location}.txt"))  # 如果没有对应文件，默认使用地点名

        # 清空文件内容
        with open(output_filename, "w", encoding='utf-8') as file:
            pass

        for result in results:
            if any(condition in result.text for condition in continue_conditions) and '组播' in result.text:
                link = result.find_element(By.TAG_NAME, "a")
                ip_address = link.get_attribute("href").split('=')[-1]
                location_ip = f"{ip_address}"
                print(location_ip)

                # 写入文件
                with open(output_filename, "a", encoding='utf-8') as file:
                    file.write(location_ip + "\n")

        print(f"{location} 搜索完成，结果保存在 {output_filename}")

    driver.quit()

# 你可以在这里调用 search_and_save_ips 函数
if __name__ == "__main__":
    locations = ["湖南电信", "北京市", "上海电信", "湖北电信", "江苏电信", "重庆电信", "江西电信", "河北电信", "河南电信", "浙江电信"]  # 根据需要添加更多地点
    search_and_save_ips(locations)

# 测速
def test_http_speed(ip, target_url, target_bytes=1 * 1024 * 1024, timeout=2, attempts=5):
    """测试 HTTP 速度并返回响应时间和下载的字节数"""
    url = f"http://{ip}/{target_url}"
    total_speed = 0
    valid_speed_count = 0

    for attempt in range(attempts):
        start_time = time.time()
        try:
            response = requests.get(url, stream=True, timeout=timeout)  # 发送HTTP请求
            total_bytes_received = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                total_bytes_received += len(chunk)
                if total_bytes_received >= target_bytes:
                    break

            elapsed_time = time.time() - start_time
            
            if elapsed_time >= timeout or total_bytes_received < target_bytes:  # 超时或未达到目标字节数
                print(f"{ip} - 请求超时")
                return 0, 0  # 返回失败

            speed = total_bytes_received / elapsed_time / (1024 * 1024)  # 计算速度 (MB/s)
            total_speed += speed
            print(f"尝试 {attempt + 1}: {ip} - 速度: {speed:.4f} MB/s")

            if speed > 0.5:  # 如果速度大于0.5 MB/s
                valid_speed_count += 1
            
            # 如果第一个测速速度为0，直接跳出循环
            if attempt == 0 and speed <= 0.5:
                print(f"{ip} - 测速无效")
                return 0, 0  # 返回失败情况

        except requests.exceptions.RequestException as e:
            print(f"{ip} - 请求失败")
            return 0, 0  # 返回失败情况

    # 计算平均速度
    avg_speed = total_speed / attempts if attempts > 0 else 0
    return avg_speed, valid_speed_count

def main():
    # 每个文件对应的URL和结果文件
    urls_and_results = {
        'IP/湖南IP.txt': ('udp/239.76.253.151:9000', '测速/湖南测速.txt'),
        'IP/上海IP.txt': ('udp/239.45.3.145:5140', '测速/上海测速.txt'),
        'IP/北京IP.txt': ('rtp/239.3.1.129:8008', '测速/北京测速.txt'),
        'IP/湖北IP.txt': ('rtp/239.254.96.96:8550', '测速/湖北测速.txt'),
        'IP/江西IP.txt': ('udp/239.252.219.200:5140', '测速/江西测速.txt'),
        'IP/河南IP.txt': ('rtp/239.16.20.1:10010', '测速/河南测速.txt'),
        'IP/河北IP.txt': ('rtp/239.254.200.45:8008', '测速/河北测速.txt'),
        'IP/浙江IP.txt': ('rtp/233.50.201.118:5140', '测速/浙江测速.txt'),
        'IP/江苏IP.txt': ('rtp/239.49.8.129:6000', '测速/江苏测速.txt'),
        'IP/重庆IP.txt': ('rtp/235.254.198.51:1480', '测速/重庆测速.txt'),
    }
    
    for input_file, (target_url, result_file) in urls_and_results.items():
        # 读取 IP 地址
        with open(input_file, 'r', encoding='utf-8') as file:  # 指定读取编码为 UTF-8
            ips = file.readlines()

        # 记录最快的IP及其速度
        fastest_ip = None
        fastest_speed = 0
        fastest_avg_speed = 0  # 新增变量存储最快IP的平均速度

        # 遍历 IP 地址并测试速度
        for ip in ips:
            ip = ip.strip()  # 去掉换行符
            if ip:  # 确保 IP 地址不为空
                avg_speed, valid_count = test_http_speed(ip, target_url)
                if avg_speed > 0:
                    print(f"{ip} 平均速度: {avg_speed:.4f} MB/s")  # 修改输出格式
                    
                    # 检查当前速度是否是最快的
                    if avg_speed > fastest_speed:
                        fastest_speed = avg_speed
                        fastest_ip = ip
                        fastest_avg_speed = avg_speed  # 更新最快IP的平均速度
                else:
                    print(f"{ip} - 请求超时")

        # 将结果写入对应的结果文件，包含最快的IP和其平均速度
        os.makedirs(os.path.dirname(result_file), exist_ok=True)
        with open(result_file, 'w', encoding='utf-8') as res_file:  # 指定写入编码为 UTF-8
            if fastest_ip:
                res_file.write(f"{fastest_ip} 平均速度: {fastest_avg_speed:.4f} MB/s\n")  # 写入最快的IP及其速度

if __name__ == "__main__":
    main()

# 替换
# 读取测速文件，提取IP和端口或域名
def read_ips_from_file(filename):
    ips = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            # 使用正则表达式提取IP和端口或域名和端口
            match = re.search(r'(\d+\.\d+\.\d+\.\d+:\d+|[a-zA-Z0-9.-]+:\d+)', line)
            if match:
                ips.append(match.group(1))  # 将提取到的IP或域名添加到列表
    return ips

# 替换URL的函数
def replace_url_in_line(line, ips):
    # 删除平均速度相关的内容
    line = re.sub(r'平均速度：\d+(\.\d+)?MB/s', '', line)  # 删除包含平均速度的部分

    # 替换URL的正则模式
    url_pattern = r'(http://)([^/\s]+)((/udp|/rtp)[^\s]*)'
    replacement_index = 0

    def replace(match):
        nonlocal replacement_index
        if replacement_index < len(ips):
            base_url = match.group(1)
            replacement_value = ips[replacement_index]
            protocol_suffix = match.group(3)
            replacement_index += 1
            return f"{base_url}{replacement_value}{protocol_suffix}"
        return match.group(0)

    updated_line = re.sub(url_pattern, replace, line)
    return updated_line

# 主程序
def main():
    base_path = './'  # 确保替换为你的实际路径
    input_folder = os.path.join(base_path, '城市')
    replacement_folder = os.path.join(base_path, '测速')

    files_mapping = {
        '上海测速.txt': '上海市.txt',
        '北京测速.txt': '北京市.txt',
        '湖南测速.txt': '湖南省.txt',
        '湖北测速.txt': '湖北省.txt',
        '河南测速.txt': '河南省.txt',
        '河北测速.txt': '河北省.txt',
        '江西测速.txt': '江西省.txt',
        '江苏测速.txt': '江苏省.txt',
        '重庆测速.txt': '重庆市.txt',
        '浙江测速.txt': '浙江省.txt'
    }

    for input_file, city_file in files_mapping.items():
        replacement_file_path = os.path.join(replacement_folder, input_file)
        city_file_path = os.path.join(input_folder, city_file)

        print(f"检查替换文件路径: {replacement_file_path}")
        print(f"检查城市文件路径: {city_file_path}")

        if not os.path.exists(replacement_file_path):
            print(f"替换文件未找到: {replacement_file_path}")
            continue
        if not os.path.exists(city_file_path):
            print(f"城市文件未找到: {city_file_path}")
            continue
        
        ips = read_ips_from_file(replacement_file_path)
        content = []

        with open(city_file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()

        updated_content = []
        for line in content:
            updated_line = replace_url_in_line(line, ips)
            updated_content.append(updated_line)
        
        # 保存更新后的内容
        output_file = city_file_path
        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(updated_content)
        print(f"\n更新后的内容已保存至: {output_file}\n")

if __name__ == "__main__":
    main()

# 合并
def extract_average_speed(speed_file_path):
    """从测速文件中提取平均速度信息"""
    try:
        with open(speed_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "平均速度:" in line:  # 根据您提供的格式更新该行
                    # 分割字符串，提取速度部分
                    speed_str = line.split("平均速度:")[1].strip()  # 修改为 '平均速度:'
                    # 进一步处理，去掉单位并转换为浮点数
                    speed_value = float(speed_str.replace(' MB/s', '').strip())
                    return speed_value
    except Exception as e:
        print(f"读取文件失败: {speed_file_path}, 错误信息: {e}")
    return 0.0  # 返回0.0表示未能提取速度

def merge_files():
    base_path = './'
    input_folder = os.path.join(base_path, '城市')
    replacement_folder = os.path.join(base_path, '测速')
    output_folder = os.path.join(base_path, '其他')

    merged_file = os.path.join(output_folder, '合并.txt')
    os.makedirs(output_folder, exist_ok=True)

    # 定义测速文件与城市文件的映射
    merge_mapping = {
        '上海测速.txt': '上海市.txt',
        '北京测速.txt': '北京市.txt',
        '湖南测速.txt': '湖南省.txt',
        '湖北测速.txt': '湖北省.txt',
        '河北测速.txt': '河北省.txt',
        '河南测速.txt': '河南省.txt',
        '江苏测速.txt': '江苏省.txt',
        '江西测速.txt': '江西省.txt',
        '重庆测速.txt': '重庆市.txt',
        '浙江测速.txt': '浙江省.txt'
    }

    speed_files = []

    # 提取各测速文件的速度信息
    for speed_file in merge_mapping.keys():
        speed_file_path = os.path.join(replacement_folder, speed_file)
        speed = extract_average_speed(speed_file_path)
        # 只添加有效速度文件
        if speed > 0:
            speed_files.append((speed, speed_file, merge_mapping[speed_file]))

    # 根据速度降序排序，选择速度最快的3个文件
    speed_files.sort(reverse=True, key=lambda x: x[0])
    fastest_files = speed_files[:5]  # 取速度最快的3个文件

    # 合并文件
    with open(merged_file, 'w', encoding='utf-8') as merged:
        for speed, speed_file, city_file in fastest_files:
            speed_file_path = os.path.join(replacement_folder, speed_file)
            city_file_path = os.path.join(input_folder, city_file)

            print(f"合并 {city_file} 到合并文件.")
            if os.path.exists(city_file_path):
                with open(city_file_path, 'r', encoding='utf-8') as city_file_handle:
                    merged.writelines(city_file_handle.readlines())
            else:
                print(f"城市文件未找到: {city_file_path}")

    print(f"\n所有合并后的内容已保存至: {merged_file}\n")

if __name__ == "__main__":
    merge_files()

# 转换格式
def process_file(input_file, output_file):
    # 打开输入文件并读取所有内容
    with open(input_file, 'r', encoding='utf-8') as infile:
        content = infile.readlines()  # 读取所有行

    # 在内容的开头添加指定字符串
    content.insert(0, '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"\n')

    # 将内容写入到输出文件
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines(content)  # 写入所有行

def main():
    # 定义文件夹路径
    folder_path = '其他'
    
    # 输入和输出文件名
    input_file = os.path.join(folder_path, '合并.txt')  # 输入文件
    output_file = os.path.join(folder_path, 'IPTV4.m3u')  # 输出文件

    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"输入文件 {input_file} 不存在。")
        return

    # 处理文件
    try:
        process_file(input_file, output_file)
        print("处理完成")
    except Exception as e:
        print(f"处理文件时发生错误: {e}")

if __name__ == '__main__':
    main()

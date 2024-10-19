import os
import time
import requests

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

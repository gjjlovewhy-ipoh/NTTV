#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
南通广电 ntjoy.com 直播源抓取工具
自动获取 broadcastTvs.html 页面的真实直播 m3u8 地址
"""

import re
import requests
from lxml import etree

# 请求头（模拟浏览器，防止被拦截）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.ntjoy.com/",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 目标页面
TARGET_URL = "https://www.ntjoy.com/ntw/broadcastTvs.html?menuCode=ntw005"

def get_live_source():
    """抓取并解析直播源"""
    try:
        print("[+] 正在请求南通广电直播页面...")
        resp = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        html = resp.text

        # 1. 获取频道列表
        tree = etree.HTML(html)
        channels = tree.xpath('//div[contains(@class,"channel-item")]//a/@href')
        names = tree.xpath('//div[contains(@class,"channel-item")]//a/text()')

        if not channels:
            print("[!] 未获取到频道列表，页面结构可能已更新")
            return []

        result = []
        print(f"[+] 共找到 {len(channels)} 个频道")

        # 2. 逐个进入播放页提取真实 m3u8
        for idx, (url, name) in enumerate(zip(channels, names), 1):
            try:
                name = name.strip()
                play_url = url if url.startswith("http") else f"https://www.ntjoy.com{url}"
                
                print(f"[{idx}/{len(channels)}] 正在解析：{name}")
                play_resp = requests.get(play_url, headers=HEADERS, timeout=8)
                play_html = play_resp.text

                # 正则提取 m3u8 真实地址
                pattern = re.compile(r'https?://[^\s"\\]+?\.m3u8')
                m3u8_list = pattern.findall(play_html)

                if m3u8_list:
                    real_url = m3u8_list[0]
                    result.append({"name": name, "url": real_url})
                    print(f"    ✅ 成功：{real_url}")
                else:
                    print(f"    ❌ 未找到 m3u8 地址")
            except Exception as e:
                print(f"    ❌ 解析失败：{str(e)}")
                continue

        return result

    except Exception as e:
        print(f"[!] 请求失败：{str(e)}")
        return []

def save_result(data, save_type="txt"):
    """保存结果到文件"""
    if not data:
        print("[!] 无数据可保存")
        return

    # TXT 格式
    if save_type == "txt":
        with open("ntlive_result.txt", "w", encoding="utf-8") as f:
            f.write("=== 南通广电直播源抓取结果 ===\n")
            f.write(f"抓取时间：自动抓取\n\n")
            for item in data:
                f.write(f"{item['name']}\n{item['url']}\n\n")
        print("[+] 结果已保存到：ntlive_result.txt")

    # M3U 播放列表格式
    elif save_type == "m3u":
        with open("ntlive_list.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for item in data:
                f.write(f"#EXTINF:-1,{item['name']}\n")
                f.write(f"{item['url']}\n")
        print("[+] M3U播放列表已保存到：ntlive_list.m3u")

if __name__ == "__main__":
    print("=" * 50)
    print("   南通广电 ntjoy.com 直播源自动抓取工具")
    print("=" * 50)
    
    live_data = get_live_source()
    if live_data:
        save_result(live_data, "txt")
        save_result(live_data, "m3u")
    
    print("\n[✔] 抓取任务完成")
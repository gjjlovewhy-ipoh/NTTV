# -*- coding: utf-8 -*-
import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.ntjoy.com/"
}

def main():
    # 直接抓接口拿到所有直播源
    api_url = "https://www.ntjoy.com/ntw/api/getLiveChannelList"
    res = requests.get(api_url, headers=HEADERS, timeout=15)
    text = res.text

    # 匹配频道名 + m3u8
    m3u = "#EXTM3U\n"
    # 匹配格式：名称...url...m3u8
    urls = re.findall(r'https?://[^",]+?\.m3u8', text)
    names = re.findall(r'channelName["\']:\s*["\']([^"\']+)["\']', text)

    # 对齐写入
    for n, u in zip(names, urls):
        m3u += f"#EXTINF:-1,{n}\n{u}\n"

    # 强制覆盖写入，不管有没有变化
    with open("tv.m3u", "w", encoding="utf-8") as f:
        f.write(m3u)

    print(f"抓取完成，共 {len(urls)} 个直播源")

if __name__ == "__main__":
    main()

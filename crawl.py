# -*- coding: utf-8 -*-
import re
import time
import requests
from lxml import etree

# 关键：模拟真实浏览器头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.ntjoy.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "sec-ch-ua": '"Chromium";v="125", "Not=A?Brand";v="99", "Chrome";v="125"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
}

BASE_URL = "https://www.ntjoy.com"
INDEX_URL = "https://www.ntjoy.com/ntw/broadcastTvs.html?menuCode=ntw005"

# 更强正则：匹配带 token 的 m3u8
M3U8_PAT = re.compile(r'https?://[^"\']+?\.m3u8(?:\?[^"\']*)?')

def main():
    sess = requests.Session()
    sess.headers.update(HEADERS)

    # 1. 先访问列表页，拿 cookie
    try:
        r = sess.get(INDEX_URL, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"列表页访问失败：{e}")
        return

    tree = etree.HTML(r.text)
    a_links = tree.xpath('//div[contains(@class,"channel-item")]//a/@href')
    a_names = tree.xpath('//div[contains(@class,"channel-item")]//a/text()')
    print(f"共找到 {len(a_links)} 个频道")

    m3u_content = "#EXTM3U\n"

    for idx, (link, name) in enumerate(zip(a_links, a_names), 1):
        name = name.strip()
        if not name:
            continue

        play_url = link if link.startswith("http") else BASE_URL + link
        print(f"\n[{idx}] 正在抓：{name} → {play_url}")

        try:
            # 2. 访问播放页（带 cookie + 正确 Referer）
            sess.headers.update({"Referer": INDEX_URL})
            r2 = sess.get(play_url, timeout=15)
            r2.raise_for_status()

            # 3. 搜索 m3u8（含参数）
            html = r2.text
            match = M3U8_PAT.search(html)
            if match:
                real_url = match.group()
                m3u_content += f"#EXTINF:-1,{name}\n{real_url}\n"
                print(f"✅ 成功：{real_url}")
            else:
                # 备用：在 script 里再搜一次
                scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.S)
                found = False
                for js in scripts:
                    m = M3U8_PAT.search(js)
                    if m:
                        real_url = m.group()
                        m3u_content += f"#EXTINF:-1,{name}\n{real_url}\n"
                        print(f"✅ 从JS抓到：{real_url}")
                        found = True
                        break
                if not found:
                    print(f"❌ 未找到 m3u8")
        except Exception as e:
            print(f"❌ 失败：{e}")
        time.sleep(2)  # 防封禁，延时 2 秒

    # 写入文件
    with open("tv.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print(f"\n📺 完成！共抓到 {m3u_content.count('.m3u8')} 个有效源")

if __name__ == "__main__":
    main()

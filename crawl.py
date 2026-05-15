# -*- coding: utf-8 -*-
import re
import requests
from lxml import etree

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.ntjoy.com/"
}
BASE_URL = "https://www.ntjoy.com"
INDEX_URL = "https://www.ntjoy.com/ntw/broadcastTvs.html?menuCode=ntw005"

def main():
    res = requests.get(INDEX_URL, headers=HEADERS, timeout=15)
    html = res.text
    tree = etree.HTML(html)

    # 提取频道链接和名称
    a_links = tree.xpath('//div[contains(@class,"channel-item")]//a/@href')
    a_names = tree.xpath('//div[contains(@class,"channel-item")]//a/text()')

    m3u_content = "#EXTM3U\n"

    for link, name in zip(a_links, a_names):
        name = name.strip()
        if not name:
            continue
        play_url = link if link.startswith("http") else BASE_URL + link
        try:
            play_res = requests.get(play_url, headers=HEADERS, timeout=10)
            # 匹配真实m3u8
            m3u8_pat = re.compile(r'https?://[^"\']+?\.m3u8')
            match = m3u8_pat.search(play_res.text)
            if match:
                m3u_content += f"#EXTINF:-1,{name}\n{match.group()}\n"
                print(f"✅ 成功获取：{name}")
        except Exception as e:
            print(f"❌ 失败 {name}：{e}")
            continue

    # 写入m3u文件
    with open("tv.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print("📺 直播源已生成 tv.m3u")

if __name__ == "__main__":
    main()

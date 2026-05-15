# -*- coding: utf-8 -*-
import re
import time
from playwright.sync_api import sync_playwright

INDEX_URL = "https://www.ntjoy.com/ntw/broadcastTvs.html?menuCode=ntw005"
BASE_URL = "https://www.ntjoy.com"

def main():
    m3u_content = "#EXTM3U\n"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 打开列表页
        page.goto(INDEX_URL, timeout=30000)
        time.sleep(3)

        # 获取频道a标签
        items = page.locator('div[class*="channel-item"] a')
        count = items.count()
        print(f"检测到频道数量：{count}")

        for i in range(count):
            try:
                name = items.nth(i).text_content().strip()
                href = items.nth(i).get_attribute("href")
                if not name or not href:
                    continue

                play_url = href if href.startswith("http") else BASE_URL + href
                print(f"正在解析：{name} {play_url}")

                # 打开播放页
                page2 = context.new_page()
                page2.goto(play_url, timeout=30000)
                time.sleep(2)

                # 抓取所有m3u8
                html = page2.content()
                m3u8_list = re.findall(r'https?://[^"\']+?\.m3u8(\?[^"\']+)?', html)
                if m3u8_list:
                    real_url = m3u8_list[0]
                    m3u_content += f"#EXTINF:-1,{name}\n{real_url}\n"
                    print(f"✅ 成功：{real_url}")
                else:
                    print(f"❌ 未找到直播源：{name}")
                page2.close()
            except Exception as e:
                print(f"❌ 解析异常：{e}")
                continue

        browser.close()

    # 写入m3u
    with open("tv.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print("✅ 已生成 tv.m3u")

if __name__ == "__main__":
    main()

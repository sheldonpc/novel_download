import os
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def fetch_html_content(url, headers, cache_file="baidu.html"):
    """
    获取网页内容（优先从缓存读取）
    :param url: 目标URL
    :param headers: 请求头
    :param cache_file: 缓存文件名
    :return: HTML内容
    """
    if os.path.exists(cache_file):
        print(f"从缓存文件 {cache_file} 读取内容...")
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print("从网络获取最新内容...")
        response = requests.get(url=url, headers=headers)
        response.encoding = 'utf-8'
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        return response.text


def parse_hot_search(html_content):
    """
    解析xxxx热搜内容
    :param html_content: HTML内容
    :return: 热搜条目列表
    """
    soup = BeautifulSoup(html_content, "lxml")
    items = []

    # 获取所有热搜条目
    divs = soup.select("#sanRoot > main > div.container.right-container_2EFJr > div > div:nth-child(2) > div")

    for index, div in enumerate(divs, start=1):
        try:
            # 提取图片链接
            img_tag = div.select_one("a > img")
            img_src = img_tag["src"] if img_tag else "无图片"

            # 提取标题
            name_tag = div.select_one("div.content_1YWBm a div.c-single-text-ellipsis")
            title = name_tag.get_text().strip() if name_tag else "无标题"

            # 提取简介
            brief_tag = div.select("div.content_1YWBm div:last-of-type")
            description = brief_tag[1].get_text().replace("查看更多>", "").strip() if len(brief_tag) > 1 else "无简介"

            items.append({
                "rank": index,
                "image": img_src,
                "title": title,
                "description": description
            })
        except Exception as e:
            print(f"解析第{index}条热搜时出错: {e}")
            continue

    return items


def display_hot_search(items):
    """
    打印热搜内容
    :param items: 热搜条目列表
    """
    for item in items:
        print("\n" + "=" * 40)
        print(f"【第{item['rank']}条热搜】")
        print(f"标题: {item['title']}")
        print(f"图片: {item['image']}")
        print(f"简介: {item['description']}")
        print("=" * 40)


def main():
    # 初始化请求头
    headers = {
        "User-Agent": UserAgent().chrome,
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    # 目标URL
    url = "https://top.xxxxxx.com/board?tab=realtime"

    try:
        # 获取HTML内容
        html_content = fetch_html_content(url, headers)

        # 解析热搜内容
        hot_search_items = parse_hot_search(html_content)

        # 显示结果
        display_hot_search(hot_search_items)

        print(f"\n共获取到 {len(hot_search_items)} 条热搜")
    except Exception as e:
        print(f"程序运行出错: {e}")


if __name__ == "__main__":
    import requests  # 延迟导入，仅在直接运行时需要

    main()
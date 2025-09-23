import random
import time
import requests
import os
from fake_useragent import UserAgent
from lxml import etree


class NovelDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": UserAgent().chrome,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.qishuxia.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.session.headers.update(self.headers)

    def download_novel(self, url):
        """下载小说所有章节"""
        print(f"开始下载小说，目标URL: {url}")

        # 获取小说目录页
        response = self.session.get(url)
        response.encoding = 'utf-8'  # 强制使用UTF-8编码
        content = response.text

        # 解析HTML获取小说信息
        html_content = etree.HTML(content)

        # 获取小说标题
        try:
            novel_title = html_content.xpath('/html/body/div[3]/div[1]/div/div/div[2]/div[1]/h1//text()')[0].strip()
            # 清理标题中的非法字符
            novel_title = "".join(c for c in novel_title if c not in r'\/:*?"<>|').strip()
            print(f"小说标题: {novel_title}")
        except IndexError:
            print("无法获取小说标题，使用默认标题")
            novel_title = "未知小说"

        # 创建小说文件夹
        folder_path = os.path.join(os.getcwd(), novel_title)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"创建文件夹: {folder_path}")
        else:
            print(f"文件夹已存在: {folder_path}")

        # 获取所有章节链接
        a_links = html_content.xpath('//*[@id="section-list"]/li/a')
        print(f"找到 {len(a_links)} 个章节")

        # 下载每个章节
        for index, li in enumerate(a_links):
            chapter_link = li.get("href")
            chapter_title = li.text.strip() if li.text else f"第{index + 1}章"

            # 构建完整章节链接
            if chapter_link.startswith('/'):
                subchapter_link = f"https://www.qishuxia.com{chapter_link}"
            else:
                subchapter_link = f"{url}{chapter_link}"

            print(f"正在下载第{index + 1}/{len(a_links)}章：{chapter_title}")

            # 随机延迟，避免被封
            random_sleep = random.uniform(1, 4)
            time.sleep(random_sleep)

            try:
                # 下载章节内容
                sub_response = self.session.get(subchapter_link, timeout=30)
                sub_response.encoding = 'utf-8'

                # 保存章节内容
                chapter_file = os.path.join(folder_path, f"{index + 1}.txt")
                with open(chapter_file, "w", encoding="utf-8") as f:
                    f.write(sub_response.text)

                print(f"已保存: {chapter_file}")

            except Exception as e:
                print(f"下载第{index + 1}章失败: {e}")
                # 创建空文件或错误标记
                chapter_file = os.path.join(folder_path, f"{index + 1}.txt")
                with open(chapter_file, "w", encoding="utf-8") as f:
                    f.write(f"下载失败: {e}")

        print(f"所有章节下载完成，保存在: {folder_path}")
        return novel_title

    def merge_novel(self, folder_name):
        """合并所有章节为完整小说"""
        print(f"开始合并小说: {folder_name}")

        folder_path = os.path.join(os.getcwd(), folder_name)
        if not os.path.exists(folder_path):
            print(f"文件夹不存在: {folder_path}")
            return

        # 获取所有章节文件并按数字排序
        files_list = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        files_list.sort(key=lambda x: int(x.split('.')[0]))

        print(f"找到 {len(files_list)} 个章节文件")

        # 合并文件
        output_file = f"{folder_name}_完整版.txt"
        with open(output_file, "w", encoding="utf-8") as complete_novel:
            complete_novel.write(f"《{folder_name}》完整版\n")
            complete_novel.write("=" * 50 + "\n\n")

            for i, file_name in enumerate(files_list):
                file_path = os.path.join(folder_path, file_name)
                chapter_num = file_name.split('.')[0]

                print(f"正在处理第{chapter_num}章: {file_name}")

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 解析HTML内容
                    sub_content_obj = etree.HTML(content)
                    if sub_content_obj is not None:
                        # 提取正文内容
                        sub_content_text = sub_content_obj.xpath('//*[@id="content"]//text()')
                        if sub_content_text:
                            cleaned_content = "".join(text.strip() for text in sub_content_text if text.strip())

                            # 写入章节标题和内容
                            complete_novel.write(f"第{chapter_num}章\n")
                            complete_novel.write("-" * 30 + "\n")
                            complete_novel.write(cleaned_content + "\n\n")
                        else:
                            # 如果没有找到content，尝试其他选择器或直接使用原始内容
                            complete_novel.write(f"第{chapter_num}章 - 内容解析异常\n")
                            complete_novel.write("-" * 30 + "\n")
                            complete_novel.write("【本章内容解析异常，请查看原始文件】\n\n")
                    else:
                        # 如果不是HTML，直接写入
                        complete_novel.write(f"第{chapter_num}章\n")
                        complete_novel.write("-" * 30 + "\n")
                        complete_novel.write(content + "\n\n")

                except Exception as e:
                    print(f"处理文件 {file_name} 时出错: {e}")
                    complete_novel.write(f"第{chapter_num}章 - 处理异常\n")
                    complete_novel.write("-" * 30 + "\n")
                    complete_novel.write(f"【文件处理异常: {e}】\n\n")

        print(f"小说合并完成，保存为: {output_file}")


def main(url):
    # 初始化下载器
    downloader = NovelDownloader()

    # 小说目录页URL
    novel_url = url

    # 下载小说
    novel_title = downloader.download_novel(novel_url)

    # 等待一下，让所有文件都写完
    time.sleep(2)

    # 合并小说
    downloader.merge_novel(novel_title)

    print("所有操作完成！")


if __name__ == "__main__":
    url = "qis"
    main(url)
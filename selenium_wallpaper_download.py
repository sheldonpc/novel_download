import os
import random
import time
import requests
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from urllib.parse import urlparse


class ImageDownloader:
    def __init__(self, driver_path="chromedriver.exe", download_dir="downloads"):
        self.driver_path = driver_path
        self.download_dir = download_dir
        self.driver = None
        self.setup_directories()

    def setup_directories(self):
        """确保下载目录存在"""
        os.makedirs(self.download_dir, exist_ok=True)

    def initialize_driver(self):
        """初始化Chrome浏览器驱动"""
        service = Service(executable_path=self.driver_path)
        self.driver = Chrome(service=service)
        self.driver.implicitly_wait(10)

    def download_image(self, url):
        """下载单个图片"""
        try:
            # 从URL中提取文件名
            parsed_url = urlparse(url)
            file_name = os.path.basename(parsed_url.path)
            save_path = os.path.join(self.download_dir, file_name)

            if os.path.exists(save_path):
                print(f"{file_name}已存在，跳过下载")
                return False

            headers = {"User-Agent": UserAgent().random}

            response = requests.get(url=url, headers=headers, stream=True)
            response.raise_for_status()

            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"成功下载: {file_name}")
            return True
        except Exception as e:
            print(f"下载失败: {file_name}, 错误: {str(e)}")
            return False

    def get_image_links(self, page_url):
        """从页面获取所有图片链接"""
        self.driver.get(page_url)

        img_elements = WebDriverWait(self.driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'item-img'))
        )

        return [element.get_attribute('href') for element in img_elements]

    def process_image_page(self, image_url):
        """处理单个图片页面并下载图片"""
        self.driver.get(image_url)
        time.sleep(random.uniform(1, 3))

        try:
            download_link = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, 'changeTxtdn'))
            ).get_attribute('href')

            time.sleep(random.uniform(1, 2))
            return self.download_image(download_link)
        except Exception as e:
            print(f"获取图片下载链接失败: {str(e)}")
            return False

    def run(self, target_url):
        """运行下载流程"""
        try:
            self.initialize_driver()
            print("浏览器初始化成功")

            print(f"开始处理页面: {target_url}")
            image_links = self.get_image_links(target_url)
            print(f"找到 {len(image_links)} 个图片链接")

            for idx, link in enumerate(image_links, 1):
                print(f"\n处理第 {idx}/{len(image_links)} 个图片: {link}")
                self.process_image_page(link)
                time.sleep(random.uniform(1, 3))

                # 返回上一页
                self.driver.back()
                time.sleep(random.uniform(1, 2))

            print("\n所有图片处理完成")
        except Exception as e:
            print(f"运行过程中发生错误: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                print("浏览器已关闭")


if __name__ == "__main__":
    # 配置参数
    config = {
        "driver_path": os.path.join(os.getcwd(), "chromedriver.exe"),
        "download_dir": "downloads",
        "target_url": "https://www.bixxxxxx.com/page/2/?order=views"
    }

    # 创建下载器并运行
    downloader = ImageDownloader(
        driver_path=config["driver_path"],
        download_dir=config["download_dir"]
    )

    start_time = time.time()
    downloader.run(config["target_url"])
    end_time = time.time()

    print(f"总耗时: {end_time - start_time:.2f}秒")
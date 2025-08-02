# scraping/base_scraper.py
import requests
from config import HEADERS

class BaseScraper:
    """
    爬虫基类，封装通用的HTTP请求逻辑。
    """
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_page(self, url, params=None):
        """
        获取单个页面的HTML内容或API数据。
        :param url: 目标页面的URL
        :param params: 请求参数
        :return: 页面的文本内容，如果失败则返回None
        """
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def scrape(self, keyword, **kwargs):
        """
        具体的抓取逻辑。子类必须重写此方法。
        :param keyword: 用户输入的搜索关键字
        """
        raise NotImplementedError("每个爬虫子类都必须实现scrape方法！")
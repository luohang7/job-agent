# scraping/tianyancha_client.py
import requests
from config import TIANYANCHA_API_KEY, TIANYANCHA_API_URL
from scraping.base_scraper import BaseScraper

class TianyanchaClient(BaseScraper):
    """
    通过调用天眼查API获取招聘信息。
    将用户的搜索关键字作为职位关键字进行查询。
    """
    def __init__(self):
        super().__init__(TIANYANCHA_API_URL)
        if not TIANYANCHA_API_KEY or TIANYANCHA_API_KEY == "YOUR_API_KEY_HERE":
            print("警告: 天眼查API密钥未在config.py中配置，将跳过此数据源。")
            self.enabled = False
        else:
            self.enabled = True
            self.session.headers.update({'Authorization': TIANYANCHA_API_KEY})

    def scrape(self, keyword, **kwargs):
        """
        调用API获取数据。
        :param keyword: 用户输入的职位关键字。
        :return: 职位信息列表
        """
        if not self.enabled:
            return []

        # 更新日志信息，明确是按职位关键字搜索
        print(f"开始通过天眼查API按职位关键字 '{keyword}' 查询招聘信息...")
        params = {'keyword': keyword}

        try:
            response = self.fetch_page(self.base_url, params=params)
            if not response:
                return []
            
            api_result = response.json()

            if api_result.get('error_code') != 0:
                print(f"天眼查API返回错误: {api_result.get('reason', '未知错误')}")
                return []

            raw_jobs = api_result.get('result', {}).get('items', [])
            jobs = []
            for item in raw_jobs:
                job_data = {
                    'title': item.get('title', 'N/A'),
                    'company': item.get('name', 'N/A'),
                    'location': item.get('city', 'N/A'),
                    'description': item.get('description', 'N/A'),
                    'url': item.get('url', 'N/A'),
                    'source': 'Tianyancha API'
                }
                jobs.append(job_data)

            print(f"通过天眼查API找到 {len(jobs)} 个职位。")
            return jobs

        except requests.RequestException:
            return []
        except ValueError:
            print("解析天眼查API响应失败，返回的可能不是有效的JSON格式。")
            return []
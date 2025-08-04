# scraping/zhaolian_scraper.py
import json
from scraping.base_scraper import BaseScraper

class ZhaolianScraper(BaseScraper):
    """
    针对智联招聘的具体爬虫实现（基于API）。
    """
    def __init__(self):
        # 智联招聘的搜索API URL
        super().__init__(base_url="https://fe-api.zhaopin.com/c/i/search/positions")

    def scrape(self, keyword, max_pages=1):
        """
        从智联招聘API抓取数据。
        :param keyword: 搜索关键词
        :param max_pages: 要抓取的最大页数
        """
        print(f"开始从智联招聘API抓取关于‘{keyword}’的数据...")
        jobs = []
        
        # 构造包含cookie的完整请求头
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie': 'selectCity_search=489; x-zp-client-id=5ba7104e-790f-47f6-cd7f-fab9e8944b84',
            'Origin': 'https://www.zhaopin.com',
            'Referer': 'https://www.zhaopin.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'x-zp-business-system': '1',
            'x-zp-page-code': '0',
            'x-zp-platform': '13',
        }

        for page in range(1, max_pages + 1):
            # 构造请求体 (Payload)
            payload = {
                "S_SOU_WORK_CITY": "489",
                "order": 4,
                "S_SOU_FULL_INDEX": keyword,
                "pageSize": 20,
                "pageIndex": page,
                "eventScenario": "pcSearchedSouSearch",
                "anonymous": 1
            }
            
            print(f"正在抓取第 {page} 页...")
            
            # 使用POST请求并发送JSON数据和完整请求头
            try:
                response = self.session.post(self.base_url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                response_data = response.json()
            except Exception as e:
                print(f"请求API失败: {e}")
                break

            if response_data.get("code") != 200 or not response_data.get("data"):
                print(f"API返回错误或无数据: {response_data.get('message', '未知错误')}")
                break

            job_list = response_data.get("data", {}).get("list", [])
            if not job_list:
                print(f"在第 {page} 页未找到任何职位信息。")
                break

            print(f"在第 {page} 页找到 {len(job_list)} 个职位信息，开始解析...")

            for item in job_list:
                try:
                    job_data = {
                        'title': item.get('jobName'),
                        'company': item.get('company', {}).get('name'),
                        'location': item.get('jobCity'),
                        'description': f"薪资: {item.get('salary')} | 经验: {item.get('workExp')} | 学历: {item.get('education')}",
                        'url': item.get('positionUrl'),
                        'source': '智联招聘'
                    }
                    jobs.append(job_data)
                except Exception as e:
                    print(f"解析职位信息时出错: {e}")
                    continue
        
        print(f"从智联招聘共抓取到 {len(jobs)} 个职位。")
        return jobs

# 用于独立测试
if __name__ == '__main__':
    scraper = ZhaolianScraper()
    scraped_jobs = scraper.scrape(keyword="python", max_pages=1)
    
    if scraped_jobs:
        print("\n抓取到的职位信息:")
        for job in scraped_jobs:
            print(json.dumps(job, indent=2, ensure_ascii=False))
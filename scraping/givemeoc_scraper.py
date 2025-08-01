# scraping/givemeoc_scraper.py
from bs4 import BeautifulSoup
from scraping.base_scraper import BaseScraper
from config import GIVE_ME_OC_URL
import time
import urllib.parse

class GiveMeOcScraper(BaseScraper):
    """
    针对 givemeoc.com 的具体爬虫实现。
    """
    def __init__(self):
        super().__init__(GIVE_ME_OC_URL)

    def scrape(self, keyword, max_pages=1):
        print(f"开始从 givemeoc.com 抓取关于 '{keyword}' 的数据...")
        jobs = []
        
        for page in range(1, max_pages + 1):
            encoded_keyword = urllib.parse.quote(keyword)
            search_url = f"{self.base_url}?s={encoded_keyword}&paged={page}"
            
            print(f"正在抓取页面: {search_url}")
            response = self.fetch_page(search_url)
            if not response:
                print(f"无法获取第 {page} 页内容，停止抓取。")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('article', class_=lambda x: x and 'post' in x.split())

            if not job_cards:
                print(f"警告: 在页面 {page} 未找到职位列表。")
                break
                
            for card in job_cards:
                try:
                    title_element = card.find('h2', class_='entry-title')
                    link_element = title_element.find('a') if title_element else None
                    description_element = card.find('div', class_='entry-summary')

                    if not title_element or not link_element:
                        continue

                    job_data = {
                        'title': title_element.text.strip(),
                        'company': 'N/A',
                        'location': 'N/A',
                        'description': description_element.text.strip() if description_element else '无描述',
                        'url': link_element['href'],
                        'source': 'givemeoc.com'
                    }
                    jobs.append(job_data)
                except Exception as e:
                    print(f"解析职位卡片时出错: {e}")
                    continue
            
            print(f"第 {page} 页抓取完成，暂停1秒...")
            time.sleep(1)

        print(f"从 givemeoc.com 共抓取到 {len(jobs)} 个职位。")
        return jobs
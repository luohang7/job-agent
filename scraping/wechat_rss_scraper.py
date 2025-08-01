# scraping/wechat_rss_scraper.py

import feedparser
import requests
import time
from bs4 import BeautifulSoup
from config import HEADERS

class WechatRssScraper:
    """
    通过微信公众号的RSS源，抓取指定公众号的文章内容。
    这是一个比基于搜狗网页抓取更稳定、更现代的方案。
    """
    def __init__(self, rss_url):
        """
        初始化RSS爬虫。
        :param rss_url: 公众号的RSS订阅链接。
                       例如: 'https://rss.imzhao.com/{wechat_id}.xml'
        """
        self.rss_url = rss_url

    def scrape_article_content(self, url):
        """抓取单篇文章的HTML内容"""
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status() # 如果请求失败则抛出HTTPError
            return response.text
        except requests.RequestException as e:
            print(f"抓取文章失败 {url}: {e}")
            return ""

    def scrape(self, **kwargs):
        """
        主刮取方法。
        :return: 职位信息列表
        """
        if not self.rss_url:
            print("错误：未提供RSS URL。")
            return []

        print(f"开始从RSS源抓取文章: {self.rss_url}")
        
        jobs = []
        try:
            # 1. 解析RSS源
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:
                # bozo位为1表示RSS源可能存在格式问题，但feedparser仍会尝试解析
                print(f"警告: RSS源可能存在格式问题。错误信息: {feed.bozo_exception}")

            if not feed.entries:
                print("未能从RSS源中获取到任何文章。")
                return []

            # 2. 遍历文章条目
            for entry in feed.entries:
                title = entry.title
                article_url = entry.link
                
                # 简单判断标题是否和招聘相关
                if '招聘' in title or '求职' in title or '内推' in title:
                    print(f"  发现相关文章:《{title}》，正在抓取内容...")
                    
                    # 3. 抓取并解析文章内容
                    article_html = self.scrape_article_content(article_url)
                    if article_html:
                        soup = BeautifulSoup(article_html, 'html.parser')
                        # 'js_content' 是微信文章正文通常所在的div的id
                        content_div = soup.find('div', id='js_content')
                        description = content_div.get_text('\n', strip=True) if content_div else ""
                        
                        # 尝试从RSS条目中获取公众号名称，如果失败则使用备用值
                        company_name = getattr(entry, 'author', 'N/A')
                        if company_name == 'N/A' and hasattr(feed.feed, 'title'):
                            company_name = feed.feed.title

                        job_data = {
                            'title': title,
                            'company': company_name,
                            'location': 'N/A', # 需要从正文解析
                            'description': description,
                            'url': article_url,
                            'source': f"WeChat RSS: {company_name}"
                        }
                        jobs.append(job_data)
                    
                    # 礼貌性延迟，避免请求过于频繁
                    time.sleep(2)

            print(f"从RSS源抓取到 {len(jobs)} 个相关职位信息。")
            return jobs

        except Exception as e:
            print(f"通过RSS抓取时发生未知错误: {e}")
            return []
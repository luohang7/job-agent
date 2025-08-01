# scraping/wechat_sogou_scraper.py

import wechatsogou
from bs4 import BeautifulSoup
import requests
import time
from config import HEADERS

class WechatSogouScraper:
    """
    通过搜狗微信搜索，抓取指定公众号的文章内容。
    注意：此方法依赖于搜狗的页面结构和wechatsogou库，可能因对方更新而失效。
    """
    def __init__(self):
        try:
            # 初始化API，可以处理Cookie等，提高稳定性
            self.ws_api = wechatsogou.WechatSogouAPI()
        except Exception as e:
            print(f"初始化wechatsogou API失败，可能是网络问题或需要验证码: {e}")
            self.ws_api = None

    def scrape_article_content(self, url):
        """抓取单篇文章的HTML内容"""
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"抓取文章失败 {url}: {e}")
            return ""

    def scrape(self, official_account_name, **kwargs):
        """
        主刮取方法。
        :param official_account_name: 要抓取的公众号名称，例如 "互联网人才招聘"
        :return: 职位信息列表
        """
        if not self.ws_api:
            return []

        print(f"开始通过搜狗搜索公众号: '{official_account_name}'")
        try:
            # 1. 搜索公众号
            gzh_info_list = self.ws_api.search_gzh(official_account_name)
            if not gzh_info_list:
                print(f"未能在搜狗上找到名为 '{official_account_name}' 的公众号。")
                return []
            
            # 默认选择第一个搜索结果，因为通常最匹配
            gzh_profile = gzh_info_list[0]
            print(f"成功找到公众号: {gzh_profile['name']},微信号: {gzh_profile['wechat_id']}")

            # 2. 获取该公众号的最近文章列表
            # get_gzh_article_by_history方法可以获取最近10篇文章
            article_list = self.ws_api.get_gzh_article_by_history(gzh_profile['wechat_id'])

            jobs = []
            for article_meta in article_list['article']:
                title = article_meta['title']
                article_url = article_meta['content_url']
                
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
                        
                        job_data = {
                            'title': title,
                            'company': gzh_profile['name'], # 暂用公众号名作为公司名
                            'location': 'N/A', # 需要从正文解析
                            'description': description,
                            'url': article_url,
                            'source': f"WeChat OA: {gzh_profile['name']}"
                        }
                        jobs.append(job_data)
                    
                    # 礼貌性延迟
                    time.sleep(2)

            print(f"从公众号 '{official_account_name}' 抓取到 {len(jobs)} 个相关职位信息。")
            return jobs

        except Exception as e:
            print(f"通过搜狗抓取时发生未知错误: {e}")
            # wechatsogou库在频繁请求后可能会要求验证码，并抛出异常
            print("提示: 如果持续失败，可能是因为搜狗出现了验证码。请尝试在浏览器中访问 'weixin.sogou.com' 并手动验证。")
            return []
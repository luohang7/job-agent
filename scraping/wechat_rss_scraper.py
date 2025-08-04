# scraping/wechat_rss_scraper.py

import feedparser
import requests
import time
import calendar
from bs4 import BeautifulSoup
from config import HEADERS
from datetime import datetime, timedelta, timezone

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
        """抓取单篇文章的HTML内容，并处理编码问题"""
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status() # 如果请求失败则抛出HTTPError
            
            # 显式检测并使用正确的编码解码内容
            # response.encoding 会根据headers猜测编码，但可能不准
            # response.apparent_encoding 会根据内容分析编码，更可靠
            if response.encoding != response.apparent_encoding:
                print(f"  警告：检测到编码不一致。Headers: {response.encoding}, Apparent: {response.apparent_encoding}。将使用 Apparent Encoding。")
                response.encoding = response.apparent_encoding
            
            return response.text
        except requests.RequestException as e:
            print(f"抓取文章失败 {url}: {e}")
            return ""
        except Exception as e:
            # 捕获其他可能的解码错误
            print(f"处理文章内容时发生未知错误 {url}: {e}")
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
        # 定义招聘相关的关键词列表
        keywords = ['招聘', '求职', '内推', '实习', '校招', '社招', '岗位', '职位', 'Hiring', 'hiring']
        
        # 计算24小时前的时间点 (使用UTC以正确比较)
        twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)

        try:
            # 1. 解析RSS源
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:
                # bozo位为1表示RSS源可能存在格式问题，但feedparser仍会尝试解析
                print(f"警告: RSS源可能存在格式问题。错误信息: {feed.bozo_exception}")

            if not feed.entries:
                print("未能从RSS源中获取到任何文章。")
                return []

            print(f"从RSS源获取到 {len(feed.entries)} 篇文章，开始根据时间和关键词进行过滤...")

            # 2. 遍历文章条目
            for entry in feed.entries:

                # 检查文章发布时间
                published_time = None
                # 放弃使用 *_parsed 字段，直接解析原始日期字符串
                date_string = entry.get('updated') or entry.get('published')
                
                if date_string:
                    try:
                        # 手动解析RFC 822/1123格式的日期字符串, e.g., "Mon, 04 Aug 2025 08:00:00"
                        # 用户指出此时间为UTC+8
                        cst_tz = timezone(timedelta(hours=8))
                        naive_dt = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S")
                        # 将其指定为UTC+8时区
                        aware_dt = naive_dt.replace(tzinfo=cst_tz)
                        # 转换为UTC时区以便与 twenty_four_hours_ago (UTC) 进行比较
                        published_time = aware_dt.astimezone(timezone.utc)
                    except ValueError:
                        print(f"  [警告] 无法自动解析日期字符串: {date_string}，跳过此文章。")
                        continue

                # 如果没有发布时间，或者时间早于24小时前，则跳过
                if not published_time or published_time < twenty_four_hours_ago:
                    continue

                title = entry.title
                article_url = entry.link
                
                # 判断标题是否包含任何一个关键词
                if any(keyword in title for keyword in keywords):
                    print(f"  发现相关文章:《{title}》(发布于 {published_time.strftime('%Y-%m-%d %H:%M:%S %Z')})，正在抓取内容...")
                    
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
                    
                    time.sleep(2)

            print(f"从RSS源抓取到 {len(jobs)} 个相关职位信息。")
            return jobs

        except Exception as e:
            print(f"通过RSS抓取时发生未知错误: {e}")
            return []


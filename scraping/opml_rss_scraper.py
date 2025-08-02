# scraping/opml_rss_scraper.py
import xml.etree.ElementTree as ET
from scraping.wechat_rss_scraper import WechatRssScraper
import time

class OpmlRssScraper:
    """
    解析OPML文件并批量抓取其中所有RSS源的爬虫。
    """
    def __init__(self, opml_file_path):
        """
        初始化OPML RSS爬虫。
        :param opml_file_path: OPML文件的路径
        """
        self.opml_file_path = opml_file_path
        self.rss_feeds = []

    def _parse_opml(self):
        """
        解析OPML文件，提取所有RSS源的xmlUrl。
        """
        try:
            tree = ET.parse(self.opml_file_path)
            root = tree.getroot()
            
            # OPML文件中的outline标签通常在body下
            for outline in root.findall('.//outline'):
                xml_url = outline.get('xmlUrl')
                text = outline.get('text') # 订阅源的名称
                if xml_url and xml_url.startswith('http'):
                    self.rss_feeds.append({'name': text, 'url': xml_url})
            
            print(f"成功从OPML文件 '{self.opml_file_path}' 中解析出 {len(self.rss_feeds)} 个RSS订阅源。")
            return True
        except ET.ParseError as e:
            print(f"解析OPML文件失败: {e}")
            return False
        except FileNotFoundError:
            print(f"未找到OPML文件: {self.opml_file_path}")
            return False

    def scrape_all(self, max_items_per_feed=10):
        """
        抓取OPML文件中所有RSS源的最新文章。
        :param max_items_per_feed: 每个RSS源最多抓取的文章数量
        :return: 包含所有文章的列表
        """
        if not self._parse_opml():
            return []

        all_jobs = []
        
        print(f"开始批量抓取 {len(self.rss_feeds)} 个RSS源...")

        for i, feed in enumerate(self.rss_feeds):
            print(f"\n--- 正在抓取第 {i+1}/{len(self.rss_feeds)} 个源: {feed['name']} ---")
            print(f"RSS链接: {feed['url']}")
            
            try:
                # 使用现有的 WechatRssScraper 来抓取单个RSS源
                rss_scraper = WechatRssScraper(rss_url=feed['url'])
                # 假设 WechatRssScraper 的 scrape 方法可以接受一个限制数量的参数
                # 如果不能，我们需要在 WechatRssScraper 内部或之后进行切片
                jobs_from_feed = rss_scraper.scrape()
                
                if jobs_from_feed:
                    # 限制每个源抓取的数量，避免某个源文章过多导致整体失衡
                    jobs_from_feed = jobs_from_feed[:max_items_per_feed]
                    all_jobs.extend(jobs_from_feed)
                    print(f"成功从 '{feed['name']}' 抓取到 {len(jobs_from_feed)} 条信息。")
                else:
                    print(f"从 '{feed['name']}' 未能抓取到任何信息。")

            except Exception as e:
                print(f"抓取RSS源 '{feed['name']}' 时出错: {e}")
                continue
            
            # 在抓取每个源之间稍作暂停，礼貌性爬取
            if i < len(self.rss_feeds) - 1:
                print("暂停1秒...")
                time.sleep(1)
        
        print(f"\n批量抓取完成！总共从 {len(self.rss_feeds)} 个源中抓取到 {len(all_jobs)} 条信息。")
        return all_jobs

if __name__ == '__main__':
    # 用于测试这个模块
    # 假设 WeWeRSS-All.opml 文件在项目根目录
    opml_file = "WeWeRSS-All.opml"
    scraper = OpmlRssScraper(opml_file_path=opml_file)
    all_articles = scraper.scrape_all(max_items_per_feed=5)
    
    if all_articles:
        print("\n--- 抓取到的部分文章预览 ---")
        for i, article in enumerate(all_articles[:3]): # 只打印前3条作为预览
            print(f"\n[文章 {i+1}]")
            print(f"  标题: {article.get('title', 'N/A')}")
            print(f"  来源: {article.get('source', 'N/A')}")
            print(f"  链接: {article.get('url', 'N/A')}")
    else:
        print("未能抓取到任何文章。")
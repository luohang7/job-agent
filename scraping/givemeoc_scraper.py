# scraping/givemeoc_scraper.py
from bs4 import BeautifulSoup
from scraping.base_scraper import BaseScraper
from config import GIVE_ME_OC_URL
import time
import urllib.parse
from datetime import datetime, timedelta

class GiveMeOcScraper(BaseScraper):
    """
    针对 givemeoc.com 的具体爬虫实现。
    """
    def __init__(self):
        super().__init__(GIVE_ME_OC_URL)

    def scrape(self, keyword=None, max_pages=1):
        """
        从 givemeoc.com 的校招首页抓取数据。
        注意：此方法现在忽略keyword和max_pages，直接抓取首页列表。
        """
        print("开始从 givemeoc.com 校招首页抓取数据...")
        jobs = []
        
        # 直接访问首页，不再进行分页或搜索
        target_url = self.base_url
        print(f"正在抓取页面: {target_url}")
        
        response = self.fetch_page(target_url)
        if not response:
            print("无法获取页面内容，停止抓取。")
            return jobs

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到主要的容器
        crt_container = soup.find('div', class_='crt-container')
        if not crt_container:
            print("警告: 未找到 'crt-container'，页面结构可能已改变。")
            return jobs

        # 在容器内查找所有职位行
        job_rows = crt_container.select('table tbody tr[data-id]')

        if not job_rows:
            print("警告: 在页面中未找到任何职位行。")
            return jobs
            
        print(f"找到 {len(job_rows)} 个职位信息，开始解析并过滤近半个月的职位...")

        # 计算半个月前的日期
        half_month_ago = datetime.now() - timedelta(days=15)
        filtered_jobs_count = 0

        for row in job_rows:
            try:
                # 提取更新时间
                update_time_element = row.select_one('td.crt-col-update-time')
                if not update_time_element:
                    continue # 如果没有更新时间，跳过此条目
                
                update_time_str = update_time_element.get_text(strip=True)
                # 将字符串 "YYYY-MM-DD" 转换为 datetime 对象
                # 处理 "招满为止" 这种特殊情况
                if update_time_str == "招满为止":
                    # 可以选择跳过，或者将其视为一个很新的日期
                    # 这里我们选择跳过，因为它没有一个确切的更新日期
                    continue 
                update_date = datetime.strptime(update_time_str, '%Y-%m-%d')

                # 判断日期是否在近半个月内
                if update_date < half_month_ago:
                    continue # 如果日期早于半个月前，跳过此条目

                # 如果通过了日期过滤，则继续提取其他信息
                filtered_jobs_count += 1
                
                company = row.select_one('td.crt-col-company').get_text(strip=True)
                location = row.select_one('td.crt-col-location').get_text(strip=True)
                
                position_element = row.select_one('td.crt-col-position .crt-position-tag')
                position = position_element.get_text(strip=True) if position_element else 'N/A'
                
                # 优先使用投递链接，如果没有则使用公告链接
                apply_link_element = row.select_one('td.crt-col-links a.crt-link')
                notice_link_element = row.select_one('td.crt-col-notice a.crt-notice-link')
                
                url = apply_link_element['href'] if apply_link_element else \
                      (notice_link_element['href'] if notice_link_element else 'N/A')

                # 构造职位标题
                title = f"{company} - {position}" if position != 'N/A' else company
                
                # 构造描述，可以包含更多上下文信息
                recruitment_type_element = row.select_one('td.crt-col-recruitment-type .crt-badge')
                recruitment_type = recruitment_type_element.get_text(strip=True) if recruitment_type_element else 'N/A'
                
                description = f"招聘类型: {recruitment_type} | 工作地点: {location} | 更新时间: {update_time_str}"

                job_data = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'description': description,
                    'url': url,
                    'source': 'givemeoc.com'
                }
                jobs.append(job_data)
            except ValueError as ve:
                # 日期解析失败
                print(f"日期解析错误，跳过此条目: {ve}")
                continue
            except Exception as e:
                print(f"解析职位行时出错: {e}")
                continue
        
        print(f"经过日期过滤，从 {len(job_rows)} 个职位中筛选出 {len(jobs)} 个近半个月内的职位。")

        print(f"从 givemeoc.com 共抓取到 {len(jobs)} 个职位。")
        return jobs
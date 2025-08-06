# scraping/firecrawl_scraper.py
import json
import os
import subprocess
from config import FIRECRAWL_API_KEY

class FirecrawlScraper:
    """
    使用 Firecrawl API 来抓取需要JavaScript渲染的网站。
    """
    def __init__(self):
        if not FIRECRAWL_API_KEY:
            raise ValueError("FIRECRAWL_API_KEY 未在环境变量中设置。")
        self.api_key = FIRECRAWL_API_KEY
        self.api_url = "https://api.firecrawl.dev/v1/scrape" # Updated to v1

    def scrape(self, url):
        """
        使用 Firecrawl API 抓取单个URL。
        :param url: 要抓取的URL
        :return: 抓取到的数据 (JSON格式)
        """
        print(f"开始使用 Firecrawl 抓取URL: {url}...")

        # Payload structure updated based on user feedback and v1 API
        payload = {
            "url": url,
            "parsePDF": False, 
            "onlyMainContent": True # Changed to False to get the full page content
        }
        payload_str = json.dumps(payload)

        # 构建curl命令
        command = [
            'curl', '-s', '-X', 'POST', self.api_url,
            '-H', f'Authorization: Bearer {self.api_key}',
            '-H', 'Content-Type: application/json',
            '-d', payload_str
        ]

        print("正在执行 Firecrawl API 调用...")
        try:
            # 使用subprocess执行命令，并指定UTF-8编码
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            stdout = result.stdout
            
            if not stdout:
                print("Firecrawl API 调用成功，但未返回任何内容。")
                return None

            return json.loads(stdout)
        except subprocess.CalledProcessError as e:
            print(f"Firecrawl API 调用失败。退出码: {e.returncode}")
            print(f"Stderr: {e.stderr}")
            return None
        except json.JSONDecodeError as e:
            print(f"解析Firecrawl API响应失败: {e}")
            print(f"收到的原始输出: {stdout}")
            return None
        except Exception as e:
            print(f"执行curl命令时发生未知错误: {e}")
            return None

# 用于独立测试
if __name__ == '__main__':
    test_url = "https://www.zhaopin.com/sou/jl489/kwJ3FL9G8042CMSPCP00G9J6BCN4020NF5G9T0/p1"
    scraper = FirecrawlScraper()
    scraped_data = scraper.scrape(test_url)
    
    if scraped_data:
        print("\nFirecrawl API 抓取成功！")
        if scraped_data.get("data") and scraped_data["data"].get("markdown"):
            print("--- 返回的Markdown内容预览 ---")
            print(scraped_data["data"]["markdown"][:1000] + "...")
        else:
            print("--- 完整的返回JSON数据 ---")
            print(json.dumps(scraped_data, indent=2, ensure_ascii=False))
    else:
        print("\nFirecrawl API 抓取失败。")

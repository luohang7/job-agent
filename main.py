# main.py
import pandas as pd
import json
import os
import re

# 导入配置
from config import OPML_FILE_PATH, MATCHED_JOBS_SUMMARY_PATH, ZHAOPIN_SEARCH_URL, ZHAOPIN_MAX_PAGES

# 导入我们的模块
from scraping.givemeoc_scraper import GiveMeOcScraper
from scraping.opml_rss_scraper import OpmlRssScraper
from scraping.firecrawl_scraper import FirecrawlScraper
from nlp.standardize import process_jobs_dataframe, match_jobs_in_chunk, summarize_market_trends

def parse_zhaopin_markdown(markdown_content):
    """
    解析Firecrawl返回的智联招聘页面的Markdown内容。
    :param markdown_content: Firecrawl返回的Markdown字符串
    :return: 结构化的职位信息列表
    """
    print("  正在解析Firecrawl返回的Markdown内容...")
    jobs = []
    if not markdown_content:
        return jobs

    job_blocks = markdown_content.split("收藏")
    print(f"  初步分割出 {len(job_blocks)} 个职位信息块，开始逐一解析...")

    for block in job_blocks:
        if not block.strip() or "jobdetail" not in block:
            continue

        try:
            title_url_match = re.search(r'\[([^\]]+)\]\((https?://www\.zhaopin\.com/jobdetail/[^\)]+)\)', block)
            title = title_url_match.group(1).strip() if title_url_match else 'N/A'
            url = title_url_match.group(2).strip() if title_url_match else 'N/A'

            if url == 'N/A': continue

            salary_match = re.search(r'\n\s*((?:[\d.-]+(?:万|元))|面议)(?:·\d+薪)?\s*\n?', block)
            salary = salary_match.group(1).strip() if salary_match else '面议'

            company_match = re.search(r'\[([^\]]+)\]\(https?://www\.zhaopin\.com/companydetail/[^\)]+\)', block)
            company = company_match.group(1).strip() if company_match else 'N/A'

            location, experience, education = 'N/A', 'N/A', 'N/A'
            details_match = re.search(r'location\.png\)\s*([^\n]+)\s+([^\n]+)\s+([^\n]+)', block)
            if details_match:
                location = details_match.group(1).strip().replace('·', ' ')
                experience = details_match.group(2).strip()
                education = details_match.group(3).strip()

            description = f"薪资: {salary} | 地点: {location} | 经验: {experience} | 学历: {education}"

            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': url,
                'source': '智联招聘 (Firecrawl)'
            }
            jobs.append(job_data)

        except Exception as e:
            print(f"  解析职位块时出错: {e}\n块内容: {block[:150]}...")
            continue

    print(f"  成功从Markdown中解析出 {len(jobs)} 个结构化职位信息。")
    return jobs

def run_job_agent_pipeline():
    """
    运行AI求职代理的核心流程：数据获取 -> NLP分析 -> 保存结果
    """
    print("="*50)
    print("AI求职代理启动，开始今日职位信息处理流程...")
    
    all_raw_jobs = []

    # --- 1. 数据获取 ---
    print("\n[STEP 1/3] 开始获取职位数据...")

    # 1.1 (新增) 从智联招聘 (通过Firecrawl) 获取数据
    print("  正在从 智联招聘(Firecrawl) 获取数据...")
    if not ZHAOPIN_SEARCH_URL:
        print("  警告: 未在.env文件中设置ZHAOPIN_SEARCH_URL，跳过智联招聘抓取。")
    else:
        try:
            firecrawl_scraper = FirecrawlScraper()
            for page in range(1, ZHAOPIN_MAX_PAGES + 1):
                zhaopin_url = ZHAOPIN_SEARCH_URL.format(page=page)
                print(f"    正在抓取智联招聘第 {page}/{ZHAOPIN_MAX_PAGES} 页: {zhaopin_url}")
                
                scraped_data = firecrawl_scraper.scrape(zhaopin_url)
                if scraped_data and scraped_data.get("data") and scraped_data["data"].get("markdown"):
                    markdown = scraped_data["data"]["markdown"]
                    zhaopin_jobs = parse_zhaopin_markdown(markdown)
                    if zhaopin_jobs:
                        all_raw_jobs.extend(zhaopin_jobs)
                        print(f"    成功从该页解析出 {len(zhaopin_jobs)} 条数据。")
                    else:
                        print("    未能从该页解析出任何职位，可能已到达末页。")
                        break
                else:
                    print("    未能从Firecrawl获取有效数据，停止抓取该渠道。")
                    break
        except Exception as e:
            print(f"  从 智联招聘(Firecrawl) 获取数据时出错: {e}")

    # 1.2 从GiveMeOC获取数据
    print("  正在从 GiveMeOC 获取数据...")
    try:
        givemeoc_scraper = GiveMeOcScraper()
        givemeoc_jobs = givemeoc_scraper.scrape(keyword="工程师") 
        if givemeoc_jobs:
            all_raw_jobs.extend(givemeoc_jobs)
            print(f"  成功从 GiveMeOC 获取 {len(givemeoc_jobs)} 条数据。")
        else:
            print("  未能从 GiveMeOC 获取数据。")
    except Exception as e:
        print(f"  从 GiveMeOC 获取数据时出错: {e}")

    # 1.3 从OPML RSS源获取数据
    print(f"  正在从OPML文件 '{OPML_FILE_PATH}' 批量抓取RSS订阅...")
    try:
        if os.path.exists(OPML_FILE_PATH):
            opml_scraper = OpmlRssScraper(opml_file_path=OPML_FILE_PATH)
            rss_jobs = opml_scraper.scrape_all(max_items_per_feed=10) 
            if rss_jobs:
                all_raw_jobs.extend(rss_jobs)
                print(f"  成功从RSS源获取 {len(rss_jobs)} 条数据。")
            else:
                print("  未能从RSS源获取数据。")
        else:
            print(f"  OPML文件未找到: {OPML_FILE_PATH}，跳过RSS抓取。")
    except Exception as e:
        print(f"  从RSS源获取数据时出错: {e}")

    if not all_raw_jobs:
        print("\n所有数据源均未能获取任何职位信息。程序退出。")
        return

    print(f"\n总共获取到 {len(all_raw_jobs)} 条原始职位数据。")

    # --- 2. 数据处理与NLP分析 (分块处理) ---
    print("\n[STEP 2/3] 正在清洗数据并进行AI分块分析...")
    
    df_jobs = process_jobs_dataframe(all_raw_jobs)
    if df_jobs.empty:
        print("数据清洗后无有效数据，程序退出。")
        return

    # 初始化用于收集所有匹配结果的列表
    all_matched_jobs = []
    all_other_jobs = []
    chunk_size = 20 # 每次处理20个职位
    num_chunks = (len(df_jobs) - 1) // chunk_size + 1

    print(f"职位数据将被分为 {num_chunks} 块进行处理...")

    for i in range(num_chunks):
        start_index = i * chunk_size
        end_index = start_index + chunk_size
        df_chunk = df_jobs.iloc[start_index:end_index]
        
        print(f"\n--- 处理第 {i+1}/{num_chunks} 块 (职位 {start_index+1}-{end_index}) ---")
        chunk_result = match_jobs_in_chunk(df_chunk)
        
        if chunk_result.get("matched_jobs"):
            all_matched_jobs.extend(chunk_result["matched_jobs"])
        if chunk_result.get("other_jobs"):
            all_other_jobs.extend(chunk_result["other_jobs"])
        
        print(f"本块处理完成。累计核心匹配: {len(all_matched_jobs)}，其他关注: {len(all_other_jobs)}")

    # (Reduce步骤) 对所有职位进行最终的宏观市场总结
    print("\n所有职位块匹配完成，开始生成最终市场总结...")
    final_summary = summarize_market_trends(df_jobs)

    # --- 3. 保存结果 ---
    print("\n[STEP 3/3] 正在整合并保存AI处理结果...")
    
    os.makedirs(os.path.dirname(MATCHED_JOBS_SUMMARY_PATH), exist_ok=True)
    
    final_output = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "summary": final_summary,
        "matched_jobs": all_matched_jobs,
        "other_jobs": all_other_jobs
    }

    with open(MATCHED_JOBS_SUMMARY_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
    
    print(f"AI处理结果已成功保存到 '{MATCHED_JOBS_SUMMARY_PATH}'。")
    print("="*50)
    print("流程执行完毕。定时任务将在指定时间发送邮件。")


if __name__ == "__main__":
    try:
        run_job_agent_pipeline()
    except KeyboardInterrupt:
        print("\n程序已由用户中断。")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
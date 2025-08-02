# main.py
import pandas as pd
import json
import os

# 导入配置
from config import OPML_FILE_PATH, MATCHED_JOBS_SUMMARY_PATH

# 导入我们的模块
from scraping.givemeoc_scraper import GiveMeOcScraper
from nlp.standardize import process_jobs_dataframe, summarize_and_match_jobs
from scraping.opml_rss_scraper import OpmlRssScraper

def run_job_agent_pipeline():
    """
    运行AI求职代理的核心流程：数据获取 -> NLP分析 -> 保存结果
    """
    print("="*50)
    print("AI求职代理启动，开始今日职位信息处理流程...")
    
    all_raw_jobs = []

    # --- 1. 数据获取 ---
    print("\n[STEP 1/3] 开始获取职位数据...")
    
    # 1.1 从GiveMeOC获取数据
    print("  正在从 GiveMeOC 获取数据...")
    try:
        givemeoc_scraper = GiveMeOcScraper()
        # GiveMeOcScraper 目前需要一个关键字，我们可以用一个通用的词，比如"工程师"
        # 或者修改 GiveMeOcScraper 使其可以获取最新列表而不需要关键字
        # 暂时用 "工程师" 作为示例
        givemeoc_jobs = givemeoc_scraper.scrape(keyword="工程师") 
        if givemeoc_jobs:
            all_raw_jobs.extend(givemeoc_jobs)
            print(f"  成功从 GiveMeOC 获取 {len(givemeoc_jobs)} 条数据。")
        else:
            print("  未能从 GiveMeOC 获取数据。")
    except Exception as e:
        print(f"  从 GiveMeOC 获取数据时出错: {e}")

    # 1.2 从OPML RSS源获取数据
    print(f"  正在从OPML文件 '{OPML_FILE_PATH}' 批量抓取RSS订阅...")
    try:
        if os.path.exists(OPML_FILE_PATH):
            opml_scraper = OpmlRssScraper(opml_file_path=OPML_FILE_PATH)
            # 每个源最多抓取10条，避免数据量过大
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

    # --- 2. 数据处理与NLP分析 ---
    print("\n[STEP 2/3] 正在清洗数据并进行AI分析...")
    
    # 2.1 数据清洗
    df_jobs = process_jobs_dataframe(all_raw_jobs)
    if df_jobs.empty:
        print("数据清洗后无有效数据，程序退出。")
        return

    # 2.2 AI汇总与匹配
    # 注意：entity_extraction 模块暂时未用，因为AI模型可以直接理解文本
    # 如果需要，可以在AI prompt中要求提取特定实体
    ai_result = summarize_and_match_jobs(df_jobs)

    # --- 3. 保存结果 ---
    print("\n[STEP 3/3] 正在保存AI处理结果...")
    
    os.makedirs(os.path.dirname(MATCHED_JOBS_SUMMARY_PATH), exist_ok=True)
    
    # 添加时间戳，方便追踪
    final_output = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "summary": ai_result.get("summary", "无总结"),
        "matched_jobs": ai_result.get("matched_jobs", [])
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
        # 可以选择在这里添加错误日志记录

# main.py
import pandas as pd
import json
import os
import re

# 导入我们的模块
from scraping.givemeoc_scraper import GiveMeOcScraper
from scraping.tianyancha_client import TianyanchaClient
from nlp.standardize import process_jobs_dataframe
from nlp.entity_extraction import add_entities_to_dataframe
from matching.similarity import rank_jobs_by_keyword
from scraping.wechat_rss_scraper import WechatRssScraper

def run_job_agent(user_keyword, salary_range=None, use_cache=True):
    """
    运行AI求职代理的核心流程
    :param user_keyword: 用户输入的职位关键字
    :param salary_range: 一个包含(min_salary, max_salary)的元组，或None
    :param use_cache: 是否使用缓存
    """
    print("="*50)
    print(f"🚀 AI求职代理启动，正在为关键字 '{user_keyword}' 搜索工作...")
    if salary_range:
        print(f"薪资范围要求: {salary_range[0]} - {salary_range[1]} 元/月")
    
    # --- 1. 数据获取 ---
    print("\n[STEP 1/5] 开始获取职位数据...")
    raw_jobs = []
    os.makedirs(os.path.dirname(JOBS_DATA_PATH), exist_ok=True)
    # 缓存文件名现在只与关键字相关
    cache_file_path = f"{JOBS_DATA_PATH.split('.')[0]}_{user_keyword.replace(' ', '_')}.json"
    
    if use_cache:
        try:
            with open(cache_file_path, 'r', encoding='utf-8') as f:
                raw_jobs = json.load(f)
            print(f"已从缓存 '{cache_file_path}' 加载 {len(raw_jobs)} 条数据。")
        except FileNotFoundError:
            print(f"未找到针对 '{user_keyword}' 的缓存文件。")
            use_cache = False
            
    if not use_cache or not raw_jobs:
        print("执行实时数据获取...")
        scrapers = [GiveMeOcScraper(), TianyanchaClient()] 
        all_fetched_jobs = []
        for scraper in scrapers:
            fetched = scraper.scrape(keyword=user_keyword)
            all_fetched_jobs.extend(fetched)
        raw_jobs = all_fetched_jobs
        
        with open(cache_file_path, 'w', encoding='utf-8') as f:
            json.dump(raw_jobs, f, ensure_ascii=False, indent=4)
        print(f"数据已获取并缓存到 '{cache_file_path}'。")

    if not raw_jobs:
        print("所有数据源均未能获取任何职位信息。程序退出。")
        return

    # --- 2. 数据处理 ---
    print("\n[STEP 2/5] 正在清洗和标准化数据...")
    df = process_jobs_dataframe(raw_jobs)
    
    # --- 3. 新增步骤：薪资筛选 ---
    if salary_range and 'estimated_salary' in df.columns:
        print("\n[STEP 3/5] 正在按薪资范围进行筛选...")
        min_sal, max_sal = salary_range
        original_count = len(df)
        # Drop rows where salary couldn't be estimated for a clean filter
        df_with_salary = df.dropna(subset=['estimated_salary']).copy()
        # Apply the filter
        df = df_with_salary[
            (df_with_salary['estimated_salary'] >= min_sal) & 
            (df_with_salary['estimated_salary'] <= max_sal)
        ]
        print(f"筛选完成，{original_count}个职位中有{len(df)}个符合薪资要求。")

    if df.empty:
        print("经过筛选后，没有符合条件的职位。程序退出。")
        return

    # --- 4. NLP分析 ---
    print("\n[STEP 4/5] 正在进行NLP分析...")
    df = add_entities_to_dataframe(df)
    
    # --- 5. 匹配与排序 ---
    print("\n[STEP 5/5] 正在根据您的关键字进行匹配和排序...")
    ranked_df = rank_jobs_by_keyword(df, user_keyword)

    # --- 结果展示 ---
    print("\n" + "="*50)
    print("🎉 匹配完成！以下是最相关的5个职位：")
    print("="*50)
    
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', 200)
    
    if ranked_df.empty:
        print("没有找到匹配的职位。")
    else:
        display_columns = ['title', 'company', 'source', 'estimated_salary', 'similarity_score', 'url']
        display_columns = [col for col in display_columns if col in ranked_df.columns]
        
        for index, row in ranked_df.head(5).iterrows():
            print(f"【职位{index + 1}】: {row.get('title', 'N/A')}")
            print(f"  公司: {row.get('company', 'N/A')}")
            print(f"  来源: {row.get('source', 'N/A')}")
            # 格式化薪资输出
            salary = row.get('estimated_salary')
            salary_str = f"{salary:,.0f} 元/月" if pd.notna(salary) else "未提供"
            print(f"  估算月薪: {salary_str}")
            print(f"  匹配得分: {row.get('similarity_score', 0.0):.4f}")
            print(f"  链接: {row.get('url', 'N/A')}")
            print("-" * 40)


if __name__ == "__main__":
    try:
        search_type = input("请选择搜索类型: 1.按职位关键字搜索  2.按公众号名称抓取\n请输入数字: ")

        if search_type == '1':
            # ... 此处是之前按关键字和薪资搜索的逻辑 ...
            keywords = input("请输入职位关键字 (可输入多个，用空格隔开): ")
            # ...
            if keywords:
                run_job_agent(user_keyword=keywords, salary_range=salary_range, use_cache=False)

        elif search_type == '2':
            # 注意：RSS抓取需要公众号的RSS链接，而不是名称。
            # 用户需要自行找到目标公众号的RSS链接。
            # 例如，一些第三方服务可以生成RSS链接，如 https://rss.imzhao.com/
            rss_url = input("请输入要抓取的公众号的RSS链接 (例如: https://rss.imzhao.com/xxxxxxxx.xml): ")
            if rss_url:
                # 直接调用新的RSS爬虫
                rss_scraper = WechatRssScraper(rss_url=rss_url)
                raw_jobs = rss_scraper.scrape()

                if raw_jobs:
                    # 获取数据后，可以走同样的数据处理和展示流程
                    df = process_jobs_dataframe(raw_jobs)
                    df = add_entities_to_dataframe(df)
                    print("\n" + "="*50)
                    print(f"来自RSS源的最新招聘信息:")
                    print("="*50)
                    print(df[['title', 'company', 'url']].head(10)) # 简单展示结果
                else:
                    print("未能从该RSS源获取到招聘信息。")
        else:
            print("无效的输入。")

    except KeyboardInterrupt:
        print("\n程序已由用户中断。")
    except Exception as e:
        print(f"\n程序运行出错: {e}")

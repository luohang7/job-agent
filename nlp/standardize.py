# nlp/standardize.py
import re
import pandas as pd
import json
import openai
from config import OPENAI_API_KEY, OPENAI_BASE_URL, GEMINI_MODEL_NAME, USER_EDUCATION, USER_MAJOR

# 初始化OpenAI客户端
try:
    client = openai.OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )
except Exception as e:
    print(f"初始化OpenAI客户端失败: {e}")
    client = None

def clean_text(text):
    if not isinstance(text, str): return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('\\', '\\\\').replace('"', '\\\"')
    return text

def process_jobs_dataframe(jobs_list):
    """
    对原始职位列表进行初步清洗和格式化。
    """
    if not jobs_list: 
        return pd.DataFrame()
    df = pd.DataFrame(jobs_list)
    
    for col in ['title', 'description', 'company', 'source', 'url']:
        if col not in df.columns: 
            df[col] = ''
    
    df['title'] = df['title'].fillna('')
    df['description'] = df['description'].fillna('')
    df['company'] = df['company'].fillna('')
    df['source'] = df['source'].fillna('未知来源')
    df['url'] = df['url'].fillna('')
    
    df['clean_description'] = df['description'].apply(clean_text)
    
    return df

def match_jobs_in_chunk(df_chunk):
    """
    (新) 使用Gemini模型仅对一小块职位进行匹配，不进行总结。
    :param df_chunk: 包含一小块职位信息的DataFrame
    :return: 一个包含匹配职位列表的字典
    """
    if not client:
        print("OpenAI客户端未初始化，无法进行AI匹配。")
        return {"matched_jobs": [], "other_jobs": []}

    if df_chunk.empty:
        return {"matched_jobs": [], "other_jobs": []}

    jobs_json_string = df_chunk.to_json(orient='records', force_ascii=False)
    user_profile = f"用户学历: {USER_EDUCATION}, 专业: {USER_MAJOR}"

    prompt = f"""
    你是一个专业的求职顾问。请根据以下用户背景和一小批职位信息，筛选出匹配的职位。

    **用户背景:**
    {user_profile}

    **本批次的职位信息 (JSON格式):**
    ```json
    {jobs_json_string}
    ```

    **请严格执行以下任务:**
    1.  **核心匹配岗位筛选**: 严格根据用户的学历和专业背景，从上述职位中筛选出 **最多5个** 最匹配的职位。
    2.  **其他值得关注岗位筛选**: 从剩余职位中筛选出 **最多5个** 其他值得关注的岗位（例如：行业前景好、技能可迁移等）。
    3.  **格式化输出**: 严格按照下面的JSON格式返回结果，确保每个对象都包含`title`, `company`, `source`, `url`和`reason`。

    **输出格式:**
    ```json
    {{
      "matched_jobs": [
        {{"title": "职位1", "company": "公司1", "source": "来源1", "url": "链接1", "reason": "推荐理由1..."}}
      ],
      "other_jobs": [
        {{"title": "职位2", "company": "公司2", "source": "来源2", "url": "链接2", "reason": "推荐理由2..."}}
      ]
    }}
    ```
    """

    print(f"正在对 {len(df_chunk)} 个职位进行AI匹配...")
    try:
        response = client.chat.completions.create(
            model=GEMINI_MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个专业的求职顾问，专注于精准筛选职位。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"调用AI进行职位匹配时出错: {e}")
        return {"matched_jobs": [], "other_jobs": []}

def summarize_market_trends(df_jobs):
    """
    (新) 使用Gemini模型对所有职位进行最终的宏观市场总结。
    :param df_jobs: 包含所有职位信息的DataFrame
    :return: 一个包含市场总结的字符串
    """
    if not client or df_jobs.empty:
        return "因数据不足或AI服务未配置，无法生成市场总结。"

    # 为了节省token，我们只给AI看职位标题和来源
    sample_jobs_string = df_jobs.head(100)[['title', 'source']].to_string(index=False)

    prompt = f"""
    你是一个敏锐的市场分析师。请根据以下近百个职位列表的概览，为求职者撰写一段150-200字的宏观市场趋势分析。
    请重点分析：
    - 当前招聘需求最旺盛的技术方向或职位类型是什么？
    - 有哪些值得关注的新兴行业或公司？
    - 对于求职者，你有什么具体的求职建议？

    **职位概览:**
    {sample_jobs_string}

    请直接返回分析文本，不要包含任何额外的前缀或标题。
    """

    print("正在调用AI模型进行最终的市场趋势总结...")
    try:
        response = client.chat.completions.create(
            model=GEMINI_MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个专业的市场分析师，擅长从职位列表中洞察趋势。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"调用AI进行市场总结时出错: {e}")
        return f"AI市场总结生成失败: {e}"

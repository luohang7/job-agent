# nlp/standardize.py
import re
import pandas as pd
import json
import openai
from config import OPENAI_API_KEY, OPENAI_BASE_URL, GEMINI_MODEL_NAME, USER_EDUCATION, USER_MAJOR

# 初始化OpenAI客户端
# 注意：这里假设Gemini模型可以通过OpenAI兼容的接口调用
# 如果不是，需要使用Google的GenerativeAI库
try:
    client = openai.OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL # 如果使用官方OpenAI，此行可省略或为默认值
    )
except Exception as e:
    print(f"初始化OpenAI客户端失败: {e}")
    client = None

def clean_text(text):
    if not isinstance(text, str): return ""
    # 移除多余的空白字符和换行符
    text = re.sub(r'\s+', ' ', text).strip()
    # 移除可能干扰JSON解析的特殊字符
    text = text.replace('\\', '\\\\').replace('"', '\\\"')
    return text

def process_jobs_dataframe(jobs_list):
    """
    对原始职位列表进行初步清洗和格式化。
    """
    if not jobs_list: 
        return pd.DataFrame()
    df = pd.DataFrame(jobs_list)
    
    # 确保关键列存在
    for col in ['title', 'description', 'company', 'source', 'url']:
        if col not in df.columns: 
            df[col] = ''
    
    df['title'] = df['title'].fillna('')
    df['description'] = df['description'].fillna('')
    df['company'] = df['company'].fillna('')
    df['source'] = df['source'].fillna('未知来源')
    df['url'] = df['url'].fillna('')
    
    # 清理描述文本
    df['clean_description'] = df['description'].apply(clean_text)
    
    return df

def summarize_and_match_jobs(df_jobs):
    """
    使用Gemini模型汇总和匹配职位。
    :param df_jobs: 包含所有职位信息的DataFrame
    :return: 一个包含匹配职位和AI总结的字典
    """
    if not client:
        print("OpenAI客户端未初始化，无法进行AI匹配。")
        return {"summary": "AI服务未配置，无法生成总结。", "matched_jobs": []}

    if df_jobs.empty:
        print("没有职位数据可供分析。")
        return {"summary": "今日没有新的职位信息。", "matched_jobs": []}

    # 将DataFrame转换为JSON字符串，方便发送给AI
    # 限制发送的职位数量，避免超出token限制
    # 增加发送的职位数量到100个，为AI提供更多选择以满足数量要求
    jobs_json_string = df_jobs.head(100).to_json(orient='records', force_ascii=False)
    
    user_profile = f"用户学历: {USER_EDUCATION}, 专业: {USER_MAJOR}"

    # 构建发送给AI的Prompt
    prompt = f"""
    你是一个专业的求职顾问。请根据以下用户背景和今日最新的职位信息，进行汇总、分析，并筛选出职位。

    **用户背景:**
    {user_profile}

    **今日职位信息 (JSON格式):**
    ```json
    {jobs_json_string}
    ```

    **请严格执行以下任务:**
    1.  **汇总与分析**: 对所有职位信息进行简要汇总，分析今日职位市场的整体趋势和亮点。
    2.  **核心匹配岗位筛选**: 你必须严格根据用户的学历和专业背景，从上述职位中筛选出 **10-15个** 最匹配的职位。这些职位应与用户的背景高度相关。**这是一个硬性数量要求，请务必遵守。** 如果高度相关的职位不足10个，请尽量选择最接近的，直到凑够10个。如果无法凑够，请在推荐理由中说明“因高度相关岗位较少，此岗位为次优选择”。
    3.  **核心匹配岗位说明**: 对每个核心匹配的职位，说明推荐理由（例如：技能匹配度高、行业相关、发展前景好等）。
    4.  **其他值得关注岗位筛选**: 除了核心匹配岗位外，你**必须**再从剩余的职位中筛选出 **15-20个** 其他值得关注的岗位。这些岗位可能：
        -   属于新兴或交叉领域，虽然不完全对口，但未来发展潜力巨大。
        -   要求的技能与用户现有技能有较高的可迁移性。
        -   公司或行业本身非常有吸引力，即使职位不完全匹配。
        -   提供了独特的职业发展路径或学习机会。
        **这也是一个硬性数量要求，请务必遵守。** 如果值得关注的岗位不足15个，请尽量选择有潜力的，直到凑够15个。如果无法凑够，请在推荐理由中说明“因值得关注的岗位较少，此岗位为备选推荐”。
    5.  **其他岗位说明**: 对每个其他值得关注的岗位，简要说明推荐理由（例如：行业前景好、技能可迁移、公司平台优秀等）。
    6.  **格式化输出**: 请严格按照下面的JSON格式返回结果，确保`matched_jobs`和`other_jobs`列表中的每个对象都包含原始职位信息中的`title`, `company`, `source`, `url`。

    **输出格式:**
    ```json
    {{
      "summary": "这里是你的汇总分析文本...",
      "matched_jobs": [
        // 注意：此列表必须包含 10-15 个核心匹配职位对象
        {{
          "title": "核心匹配职位标题1",
          "company": "公司名称1",
          "source": "来源1",
          "url": "链接1",
          "reason": "核心匹配推荐理由1..."
        }}
        // ... 更多核心匹配职位
      ],
      "other_jobs": [
        // 注意：此列表必须包含 15-20 个其他值得关注职位对象
        {{
          "title": "其他值得关注职位标题1",
          "company": "公司名称3",
          "source": "来源3",
          "url": "链接3",
          "reason": "其他岗位推荐理由1..."
        }}
        // ... 更多其他值得关注职位
      ]
    }}
    ```
    """

    print("正在调用AI模型进行职位分析和匹配...")
    try:
        response = client.chat.completions.create(
            model=GEMINI_MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个专业的求职顾问，擅长分析职位信息并为用户提供个性化建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5, # 控制创造性，0.5比较平衡
            response_format={"type": "json_object"} # 强制AI返回JSON格式
        )
        
        ai_response_content = response.choices[0].message.content
        
        # 解析AI返回的JSON
        result = json.loads(ai_response_content)
        print("AI分析和匹配完成。")
        return result

    except openai.APIError as e:
        print(f"OpenAI API返回错误: {e}")
        return {"summary": f"AI服务调用出错: {e}", "matched_jobs": []}
    except json.JSONDecodeError as e:
        print(f"解析AI返回的JSON失败: {e}")
        print(f"AI原始返回: {ai_response_content}")
        return {"summary": "AI返回结果格式错误，无法解析。", "matched_jobs": []}
    except Exception as e:
        print(f"调用AI模型时发生未知错误: {e}")
        return {"summary": f"处理过程中发生未知错误: {e}", "matched_jobs": []}
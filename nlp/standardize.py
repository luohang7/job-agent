# nlp/standardize.py
import re
import pandas as pd

def clean_text(text):
    if not isinstance(text, str): return ""
    return re.sub(r'\s+', ' ', text).strip()

def standardize_salary(description):
    """从职位描述中提取估算的月薪（单位：元）"""
    if not isinstance(description, str): return None
    
    # 匹配 "15-25K", "15k-25k"
    match = re.search(r'(\d+)\s*[-–—]\s*(\d+)\s*k', description, re.IGNORECASE)
    if match:
        min_salary = int(match.group(1)) * 1000
        max_salary = int(match.group(2)) * 1000
        return (min_salary + max_salary) / 2
        
    # 匹配 "30K"
    match = re.search(r'(\d+)\s*k', description, re.IGNORECASE)
    if match:
        return int(match.group(1)) * 1000
        
    # 匹配 "20-30万/年", "20万-30万/年"
    match = re.search(r'(\d+)\s*[-–—]\s*(\d+)\s*万\s*/\s*年', description)
    if match:
        min_annual = int(match.group(1)) * 10000
        max_annual = int(match.group(2)) * 10000
        return (min_annual + max_annual) / 2 / 12 # 返回月薪中位数
        
    # 匹配 "30万/年"
    match = re.search(r'(\d+)\s*万\s*/\s*年', description)
    if match:
        return int(match.group(1)) * 10000 / 12
        
    return None

def process_jobs_dataframe(jobs_list):
    if not jobs_list: return pd.DataFrame()
    df = pd.DataFrame(jobs_list)
    for col in ['title', 'description']:
        if col not in df.columns: df[col] = ''
    df['title'] = df['title'].fillna('')
    df['description'] = df['description'].fillna('')
    df['clean_description'] = df['description'].apply(clean_text)
    df['estimated_salary'] = df['description'].apply(standardize_salary)
    df['text_for_matching'] = df['title'] + ' ' + df['clean_description']
    return df
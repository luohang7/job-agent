# config.py

# --- 爬虫相关配置 ---
GIVE_ME_OC_URL = "https://www.givemeoc.com/"

# 模拟浏览器请求头，防止被识别为爬虫
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
}

# --- API 相关配置 ---
# 天眼查API配置 (请替换为您的真实信息)
# 注意: 以下URL是一个示例，请根据您购买的API文档填写正确的URL
TIANYANCHA_API_URL = "https://api.tianyancha.com/services/v3/open/search/recruitment" 
TIANYANCHA_API_KEY = "YOUR_API_KEY_HERE" # <-- 在这里填入你的真实密钥

# --- 数据存储 ---
JOBS_DATA_PATH = "data/jobs.json"

# --- NLP 模型 ---
SPACY_MODEL_NAME = "zh_core_web_md"
# config.py
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# --- 爬虫相关配置 ---
GIVE_ME_OC_URL = os.getenv("GIVE_ME_OC_URL", "https://www.givemeoc.com/")

# 模拟浏览器请求头，防止被识别为爬虫
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
}

# --- 数据存储 ---
OPML_FILE_PATH = os.getenv("OPML_FILE_PATH", "data/WeWeRSS-All.opml")
MATCHED_JOBS_SUMMARY_PATH = os.getenv("MATCHED_JOBS_SUMMARY_PATH", "data/matched_jobs_summary.json")

# --- 用户个人信息 ---
USER_EDUCATION = os.getenv("USER_EDUCATION", "本科")  # 例如: 高中, 大专, 本科, 硕士, 博士
USER_MAJOR = os.getenv("USER_MAJOR", "计算机科学与技术")  # 例如: 计算机科学与技术, 软件工程, 市场营销

# --- OpenAI API (用于调用Gemini) ---
# 如果使用Google Cloud Vertex AI或OpenAI兼容的Gemini代理，请填写相应的BASE_URL和API_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 你的OpenAI API密钥或代理服务的密钥
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")  # 默认为OpenAI官方地址，如果使用代理请修改
# Gemini模型名称，例如 'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest', 'gemini-2.0-flash-exp'
# 确认你的API提供商支持的模型名称
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")

# --- SMTP 邮件服务配置 ---
SMTP_SERVER = os.getenv("SMTP_SERVER")  # 例如: smtp.gmail.com, smtp.qq.com
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # 例如: 587 (TLS), 465 (SSL)
SMTP_USERNAME = os.getenv("SMTP_USERNAME")  # 你的邮箱地址 (发件人)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # 你的邮箱密码或应用专用密码
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")  # 收件人邮箱地址

# --- 定时任务配置 ---
# 邮件发送时间，格式为 "HH:MM"，24小时制
EMAIL_SEND_TIME = os.getenv("EMAIL_SEND_TIME", "09:00")  # 例如: "09:00" 表示每天上午9点发送

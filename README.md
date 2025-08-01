# AI求职代理系统 🤖

一个智能的求职助手，能够自动搜索、分析和匹配职位信息，帮助用户找到最相关的工作机会。

## ✨ 主要功能

- 🔍 **多源数据获取**: 支持从GiveMeOc、天眼查、微信公众号等多个来源获取职位信息
- 🧠 **智能数据处理**: 自动清洗、标准化和实体提取
- 🎯 **智能匹配算法**: 基于关键词相似度的职位推荐
- 💰 **薪资筛选**: 支持按薪资范围筛选职位
- ⚡ **缓存机制**: 智能缓存避免重复爬取

## 🚀 快速开始

### 环境要求
- Python 3.7+
- pip

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/job-agent.git
cd job-agent
```

2. **创建虚拟环境**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **安装中文NLP模型**
```bash
python -m spacy download zh_core_web_md
```

5. **配置API密钥**
编辑 `config.py` 文件，填入您的天眼查API密钥：
```python
TIANYANCHA_API_KEY = "YOUR_API_KEY_HERE"
```

### 使用方法

运行主程序：
```bash
python main.py
```

选择搜索模式：
- **模式1**: 按职位关键字搜索
- **模式2**: 按公众号名称抓取

## 📁 项目结构

```
job-agent/
├── main.py                 # 主程序入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖包列表
├── README.md             # 项目说明
├── scraping/             # 数据爬取模块
│   ├── base_scraper.py
│   ├── givemeoc_scraper.py
│   ├── tianyancha_client.py
│   └── wechat_sogou_scraper.py
├── nlp/                  # 自然语言处理模块
│   ├── standardize.py
│   └── entity_extraction.py
├── matching/             # 匹配算法模块
│   └── similarity.py
└── data/                 # 数据存储目录
```

## 🔧 技术栈

- **Python**: 主要开发语言
- **pandas**: 数据处理和分析
- **spaCy**: 自然语言处理
- **scikit-learn**: 机器学习算法
- **requests**: HTTP请求
- **BeautifulSoup**: 网页解析
- **wechatsogou**: 微信公众号爬取

## 📝 使用示例

### 按关键字搜索
```python
from main import run_job_agent

# 搜索Python开发工程师，薪资范围15k-25k
run_job_agent(
    user_keyword="Python开发工程师",
    salary_range=(15000, 25000),
    use_cache=True
)
```

### 按公众号抓取
```python
from scraping.wechat_sogou_scraper import WechatSogouScraper

scraper = WechatSogouScraper()
jobs = scraper.scrape("招聘公众号名称")
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## ⚠️ 注意事项

- 请遵守各网站的robots.txt和使用条款
- 建议合理设置爬取频率，避免对目标网站造成压力
- API密钥请妥善保管，不要提交到公开仓库

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件至：[your-email@example.com]

---

⭐ 如果这个项目对您有帮助，请给个Star支持一下！ 
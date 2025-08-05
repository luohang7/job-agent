# AI 智能求职代理 🤖💼

一个由 AI 驱动的自动化求职助手，能够每日自动抓取、分析和匹配职位信息，并通过邮件为你推送个性化的求职报告。

## ✨ 核心功能

- 📡 **多源数据聚合**: 通过 RSS 订阅源（如 WeWeRSS 导出的 OPML 文件）和特定网站（如 GiveMeOC）自动获取最新职位信息。
- 🕷️ **Firecrawl强力抓取**: 集成 Firecrawl.dev 服务，能够绕过反爬虫机制，抓取由JavaScript动态渲染的复杂网站（如智联招聘）。
- 🧠 **AI 智能分析与分块处理**: 利用强大的大语言模型（如 Gemini）对所有职位进行深度分析。通过先进的“分块处理”机制，确保即使有海量职位信息也能稳定处理，不受Token限制。
- 🎯 **个性化匹配**: 根据你的学历和专业背景，AI 会筛选出高度相关的核心岗位和值得关注的潜力岗位，并提供推荐理由。
- 📬 **定时邮件推送**: 每日定时将精美的 HTML 格式求职报告发送到你的邮箱，让你不错过任何机会。
- ⚙️ **高度灵活配置**: 通过 `.env` 文件轻松配置 AI 模型、邮件服务、爬虫目标和个人信息，无需修改代码。

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1.  **克隆项目**
    ```bash
    git clone https://github.com/luohang7/job-agent.git
    cd job-agent
    ```

2.  **创建并激活虚拟环境**
    ```bash
    # 创建虚拟环境
    python -m venv .venv

    # Windows (激活)
    .venv\Scripts\activate

    # macOS/Linux (激活)
    source .venv/bin/activate
    ```

3.  **安装项目依赖**
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置环境变量**
    *   在项目根目录下复制 `.env.example` 文件，并重命名为 `.env`。
    *   编辑 `.env` 文件，填入你的个人配置。**请务必填写所有必需的配置项**。

    ```ini
    # .env

    # --- AI 模型与服务 ---
    # Firecrawl API，用于抓取JS渲染的网站 (必需)
    FIRECRAWL_API_KEY=fca_...

    # 大语言模型 API (必需)
    OPENAI_API_KEY=你的OpenAI_API_Key或代理服务密钥
    OPENAI_BASE_URL=https://api.openai.com/v1 # 或你的代理地址
    GEMINI_MODEL_NAME=gemini-1.5-flash-latest # 或其他你使用的模型名

    # --- SMTP 邮件服务配置 (必需) ---
    SMTP_SERVER=smtp.example.com
    SMTP_PORT=465
    SMTP_USERNAME=你的发信邮箱地址
    SMTP_PASSWORD=你的邮件服务专用密码
    RECIPIENT_EMAIL=接收报告的邮箱地址

    # --- 用户个人信息 (必需) ---
    USER_EDUCATION=本科
    USER_MAJOR=计算机科学与技术

    # --- 爬虫目标配置 (必需) ---
    # 智联招聘搜索URL，用 {page} 作为页码占位符
    ZHAOPIN_SEARCH_URL=https://www.zhaopin.com/sou/jl489/kwpython/p{page}
    ZHAOPIN_MAX_PAGES=3 # 希望抓取的总页数

    # RSS订阅源文件路径
    OPML_FILE_PATH=data/WeWeRSS-All.opml

    # --- 定时任务配置 ---
    EMAIL_SEND_TIME=09:00 # 每日发送时间，24小时制
    ```

### 使用方法

#### 方式一：立即执行一次完整流程

```bash
python main.py
```
执行成功后，分析结果会保存在 `data/matched_jobs_summary.json` 文件中。

#### 方式二：启动定时任务（推荐）

```bash
python scheduler.py
```
启动后，调度器会根据你在 `.env` 文件中设置的 `EMAIL_SEND_TIME` 每天自动执行一次完整的流程。

## 🐳 Docker 部署 (推荐)

使用 Docker 进行部署可以简化环境配置。

### 前置条件

-   已安装 [Docker](https://www.docker.com/get-started) 和 [Docker Compose](https://docs.docker.com/compose/install/)。

### 部署步骤

1.  **准备 `.env` 文件**: 在项目根目录下，根据 `.env.example` 创建并填写好你的 `.env` 文件。Docker Compose 会自动加载此文件。

2.  **准备数据文件**: 确保你的 `data/` 目录下有 `WeWeRSS-All.opml` 文件（如果需要）。

3.  **构建并启动容器**:
    ```bash
    docker-compose up --build -d
    ```

4.  **查看日志**:
    ```bash
    docker-compose logs -f job-agent
    ```

5.  **停止服务**:
    ```bash
    docker-compose down
    ```

## 📁 项目结构

```
job-agent/
├── main.py                 # 主程序入口
├── scheduler.py            # 定时任务调度器
├── config.py               # 配置加载逻辑
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
├── Dockerfile              # Docker镜像构建文件
├── docker-compose.yml      # Docker编排文件
├── README.md               # 项目说明
│
├── scraping/               # 数据爬取模块
│   ├── base_scraper.py     # 爬虫基类
│   ├── firecrawl_scraper.py  # Firecrawl 服务调用实现
│   ├── givemeoc_scraper.py # GiveMeOC 网站爬虫
│   ├── opml_rss_scraper.py # OPML RSS 批量爬虫
│   └── wechat_rss_scraper.py # 微信公众号 RSS 爬虫
│
├── nlp/                    # AI分析模块
│   └── standardize.py      # 数据清洗、AI模型调用与分块处理逻辑
│
└── data/                   # 数据存储目录
    ├── WeWeRSS-All.opml    # RSS 订阅源 (需自行配置)
    └── matched_jobs_summary.json # AI 分析结果
```

## 🔧 技术栈

- **核心**: Python, Pandas, OpenAI Python Client, Schedule
- **数据抓取**: Requests, BeautifulSoup4, Feedparser, Firecrawl API
- **配置管理**: python-dotenv
- **部署**: Docker, Docker Compose

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

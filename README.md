# AI 智能求职代理 🤖💼

一个由 AI 驱动的自动化求职助手，能够每日自动抓取、分析和匹配职位信息，并通过邮件为你推送个性化的求职报告。

## ✨ 核心功能

- 📡 **多源数据聚合**: 通过 RSS 订阅源（如 WeWeRSS 导出的 OPML 文件）和特定网站（如 GiveMeOC）自动获取最新职位信息。
- 🧠 **AI 智能分析**: 利用强大的大语言模型（如 Gemini）对所有职位进行深度分析，生成市场趋势汇总。
- 🎯 **个性化匹配**: 根据你的学历和专业背景，AI 会筛选出高度相关的核心岗位和值得关注的潜力岗位，并提供推荐理由。
- 📬 **定时邮件推送**: 每日定时将精美的 HTML 格式求职报告发送到你的邮箱，让你不错过任何机会。
- ⚙️ **灵活配置**: 通过 `.env` 文件轻松配置 AI 模型、邮件服务和个人信息，无需修改代码。

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1.  **克隆项目**
    ```bash
    git clone https://github.com/your-username/job-agent.git
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
    *   编辑 `.env` 文件，填入你的个人配置：

    ```ini
    # --- OpenAI API (用于调用Gemini或其他大模型) ---
    OPENAI_API_KEY=你的OpenAI_API_Key或代理服务密钥
    OPENAI_BASE_URL=https://api.openai.com/v1 # 或你的代理地址
    GEMINI_MODEL_NAME=gemini-2.0-flash-exp # 或其他你使用的模型名

    # --- SMTP 邮件服务配置 (以阿里云邮件推送为例) ---
    SMTP_SERVER=smtpdm.aliyun.com
    SMTP_PORT=465
    SMTP_USERNAME=你的发信邮箱地址
    SMTP_PASSWORD=你的邮件推送专用密码
    RECIPIENT_EMAIL=接收报告的邮箱地址

    # --- 用户个人信息 ---
    USER_EDUCATION=本科 # 例如: 高中, 大专, 本科, 硕士, 博士
    USER_MAJOR=计算机科学与技术 # 你的专业

    # --- 定时任务配置 ---
    EMAIL_SEND_TIME=09:00 # 每日发送时间，24小时制，例如 "09:00"
    ```

### 使用方法

#### 方式一：立即执行一次完整流程

如果你想立即抓取数据并生成报告，可以运行主程序：

```bash
python main.py
```

执行成功后，分析结果会保存在 `data/matched_jobs_summary.json` 文件中。

#### 方式二：启动定时任务（推荐）

让代理在后台自动运行，每天定时为你发送报告：

```bash
python scheduler.py
```

启动后，调度器会根据你在 `.env` 文件中设置的 `EMAIL_SEND_TIME` 每天自动执行一次完整的抓取、分析和邮件发送流程。程序会持续运行，直到你手动关闭它（按 `Ctrl+C`）。

## 🐳 Docker 部署 (推荐)

使用 Docker 进行部署可以避免环境配置问题，并简化应用的启动和管理。这是推荐的部署方式。

### 前置条件

-   已安装 [Docker](https://www.docker.com/get-started)。
-   已安装 [Docker Compose](https://docs.docker.com/compose/install/) (通常随 Docker Desktop 一起安装)。

### 部署步骤

#### 1. 准备 Docker 环境变量文件

在项目根目录（与 `docker-compose.yml` 同级）下，创建一个名为 `.env` 的文件。**这个文件是给 Docker Compose 使用的，包含了所有敏感配置。**

你可以复制项目中的 `.env.example` 文件内容，并根据下面的模板进行修改：

```ini
# ./.env (Docker Compose 专用)

# --- OpenAI API (用于调用Gemini或其他大模型) ---
OPENAI_API_KEY=你的OpenAI_API_Key或代理服务密钥
OPENAI_BASE_URL=https://api.openai.com/v1 # 或你的代理地址
GEMINI_MODEL_NAME=gemini-2.0-flash-exp # 或其他你使用的模型名

# --- SMTP 邮件服务配置 (以阿里云邮件推送为例) ---
SMTP_SERVER=smtpdm.aliyun.com
SMTP_PORT=465
SMTP_USERNAME=你的发信邮箱地址
SMTP_PASSWORD=你的邮件推送专用密码
RECIPIENT_EMAIL=接收报告的邮箱地址

# --- 用户个人信息 ---
USER_EDUCATION=本科
USER_MAJOR=计算机科学与技术

# --- 定时任务配置 ---
EMAIL_SEND_TIME=09:00

# --- 数据存储路径 (通常保持默认即可) ---
OPML_FILE_PATH=data/WeWeRSS-All.opml
MATCHED_JOBS_SUMMARY_PATH=data/matched_jobs_summary.json
```

**⚠️ 重要提示**：
*   请务必将所有占位符替换为你的真实配置。
*   此 `.env` 文件包含敏感信息，**绝对不要**提交到 Git 仓库。它已被 `.gitignore` 忽略。

#### 2. 准备数据文件

确保你的 `data/` 目录下有 `WeWeRSS-All.opml` 文件（如果你使用RSS源）。Docker Compose 会将本地的 `data/` 目录挂载到容器内，因此数据可以持久化保存。

#### 3. 构建并启动容器

在项目根目录下，打开终端并运行以下命令：

```bash
# 构建镜像并在后台启动服务
docker-compose up --build -d
```

*   `--build`: 强制重新构建镜像（当你修改了 `Dockerfile` 或 `requirements.txt` 时需要）。
*   `-d`: 在后台运行容器。

#### 4. 查看日志和状态

*   **查看容器运行状态**：
    ```bash
    docker-compose ps
    ```

*   **查看实时日志**（用于调试和观察输出）：
    ```bash
    docker-compose logs -f job-agent
    ```
    按 `Ctrl+C` 可退出日志查看，但容器会继续运行。

#### 5. 停止和更新服务

*   **停止服务**：
    ```bash
    docker-compose stop
    ```

*   **停止并删除容器**（配置和镜像会保留）：
    ```bash
    docker-compose down
    ```

*   **重新构建并启动**（当你修改了代码或配置后）：
    ```bash
    docker-compose up --build -d
    ```

## 📁 项目结构

```
job-agent/
├── main.py                 # 主程序入口，执行一次完整的抓取与分析流程
├── scheduler.py            # 定时任务调度器，负责每日自动执行和邮件发送
├── config.py              # 核心配置加载逻辑
├── requirements.txt       # Python 依赖包列表
├── .env.example           # 环境变量配置模板
├── .gitignore             # Git 忽略文件配置
├── LICENSE                # 开源许可证
├── README.md              # 项目说明文档
│
├── scraping/              # 数据爬取模块
│   ├── __init__.py
│   ├── base_scraper.py    # 爬虫基类
│   ├── givemeoc_scraper.py # GiveMeOC 网站爬虫实现
│   ├── opml_rss_scraper.py # OPML RSS 订阅源批量爬虫实现
│   └── wechat_rss_scraper.py # 微信公众号 RSS 爬虫实现
│
├── nlp/                   # 自然语言处理与AI分析模块
│   ├── __init__.py
│   └── standardize.py     # 数据清洗、标准化及AI模型调用逻辑
│
└── data/                  # 数据存储目录
    ├── WeWeRSS-All.opml   # RSS 订阅源列表 (需自行配置)
    └── matched_jobs_summary.json # AI 分析结果缓存
```

## 🔧 技术栈

- **Python**: 核心开发语言
- **Pandas**: 数据处理与分析
- **OpenAI Python Client**: 用于调用 Gemini 或其他兼容 OpenAI API 的大语言模型
- **Schedule**: 简单的 Python 定时任务库
- **Smtplib & Email**: Python 内置库，用于发送邮件
- **Requests & BeautifulSoup**: HTTP 请求与 HTML 解析
- **python-dotenv**: 从 `.env` 文件加载环境变量

## 📝 配置详解

### 1. AI 模型配置

-   `OPENAI_API_KEY`: 你的 API 密钥。如果你使用的是 Google Gemini，可以通过 [Google AI Studio](https://aistudio.google.com/) 获取 API Key，或者使用第三方代理服务。
-   `OPENAI_BASE_URL`: API 的基础 URL。如果使用官方 OpenAI，无需修改。如果使用 Gemini 或其他代理，请填写对应的地址。
-   `GEMINI_MODEL_NAME`: 你希望使用的模型名称，例如 `gemini-pro`, `gemini-1.5-flash` 等。

### 2. 邮件服务配置

-   **阿里云邮件推送**:
    -   `SMTP_SERVER`: `smtpdm.aliyun.com`
    -   `SMTP_PORT`: `465` (SSL) 或 `8080` (SSL)
    -   `SMTP_USERNAME`: 在阿里云邮件推送控制台配置的发信地址。
    -   `SMTP_PASSWORD`: 在阿里云邮件推送控制台为该地址生成的专用密码。
-   **其他邮箱 (如 Gmail, QQ邮箱)**:
    -   请查找对应服务商的 SMTP 服务器地址和端口。
    -   **重要**: 强烈建议使用“应用专用密码”而非你的登录密码，以提高安全性。

### 3. 数据源配置

-   **GiveMeOC**: 无需额外配置，`main.py` 会自动调用。
-   **RSS 订阅源**:
    1.  使用 [WeWeRSS](https://wewe.tom.com/) 或类似工具订阅你感兴趣的招聘公众号或网站。
    2.  导出 OPML 格式的订阅文件。
    3.  将导出的 `.opml` 文件放置在 `data/` 目录下，并确保 `.env` 文件中的 `OPML_FILE_PATH` 指向它（默认为 `data/WeWeRSS-All.opml`）。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目！

1.  Fork 本仓库。
2.  创建你的特性分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交你的更改 (`git commit -m 'Add some AmazingFeature'`)。
4.  推送到分支 (`git push origin feature/AmazingFeature`)。
5.  打开一个 Pull Request。

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 免责声明与注意事项

-   **API 密钥安全**: 请妥善保管你的 `.env` 文件，**切勿**将其提交到 Git 或任何公共代码仓库。`.gitignore` 文件已默认忽略它。
-   **遵守服务条款**: 在使用爬虫获取数据时，请务必遵守目标网站的 `robots.txt` 协议和服务条款，合理控制请求频率。
-   **AI 结果仅供参考**: AI 提供的职位分析和匹配结果仅供参考，最终决策请结合个人判断。
-   **项目维护**: 本项目为个人开发并维护，可能存在 Bug 或不足，欢迎反馈。

## 📞 联系方式

如有任何问题、建议或需求，请通过以下方式联系：

-   在 GitHub 上提交 [Issue](https://github.com/your-username/job-agent/issues)。
-   发送邮件至：[your-email@example.com]

---

如果这个项目对你有帮助，请考虑给它一个 ⭐ **Star**！你的支持是我持续更新的动力。
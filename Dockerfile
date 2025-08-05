# 使用官方 Python 3.12 镜像作为基础镜像
FROM python:3.12-slim

# 设置维护者信息
LABEL maintainer="luoh3405@gmail.com"

# --- 新增 ---
# 1. 为 PyPI 镜像源设置构建参数（ARG），增加灵活性
# 默认使用国内清华镜像源，以解决网络问题并加速构建
ARG PYPI_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 设置容器内的工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 创建一个非 root 用户来运行应用
RUN adduser --disabled-password --gecos '' appuser

# 复制依赖文件
COPY requirements.txt .

# --- 修改 ---
# 2. 安装 Python 依赖
#    - 首先升级 pip
#    - 使用 ARG 定义的镜像源进行安装
RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -i ${PYPI_INDEX_URL} -r requirements.txt

# 复制项目代码到工作目录，并设置所有者
COPY --chown=appuser:appuser . .

# 切换到非 root 用户
USER appuser

# --- 新增 ---
# 3. 增加健康检查（HEALTHCHECK）
#    - Docker 会定期运行此命令来检查容器内的应用是否正常
#    - 这里我们检查 python scheduler.py 进程是否存在
#    - --interval: 检查间隔, --timeout: 超时, --start-period: 启动保护期, --retries: 重试次数
HEALTHCHECK --interval=5m --timeout=30s --start-period=1m --retries=3 \
  CMD ps -ef | grep "[p]ython scheduler.py" || exit 1

# 容器启动时执行的命令
CMD ["python", "scheduler.py"]
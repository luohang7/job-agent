# 使用官方 Python 3.12 镜像作为基础镜像
FROM python:3.12-slim

# 设置维护者信息
LABEL maintainer="luoh3405@gmail.com"

# 为 PyPI 镜像源设置构建参数
ARG PYPI_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 设置容器内的工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 将 Debian 的软件源替换为国内镜像（如阿里云），以解决 apt-get 的 DNS 和网络问题。
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 在安装Python依赖前，先安装系统级的构建工具。
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libxml2-dev \
    libxslt1-dev \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# 创建一个非 root 用户来运行应用
RUN adduser --disabled-password --gecos '' appuser

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -i ${PYPI_INDEX_URL} -r requirements.txt

# 复制项目代码到工作目录
COPY --chown=appuser:appuser . .

# 切换到非 root 用户
USER appuser

# 增加健康检查
HEALTHCHECK --interval=5m --timeout=30s --start-period=1m --retries=3 \
  CMD ps -ef | grep "[p]ython scheduler.py" || exit 1

# 容器启动时执行的命令
CMD ["python", "scheduler.py"]

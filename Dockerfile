# 使用官方 Python 3.12 镜像作为基础镜像
FROM python:3.12-slim

# 设置维护者信息
LABEL maintainer="your-email@example.com"

# 设置容器内的工作目录
WORKDIR /app

# 设置环境变量，防止 Python 写入 pyc 文件，并且将输出直接发送到终端
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖（如果需要）
# 对于这个项目，通常不需要额外的系统包
# RUN apt-get update && apt-get install -y \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

# 创建一个非 root 用户来运行应用，出于安全考虑
RUN adduser --disabled-password --gecos '' appuser

# 复制依赖文件并安装 Python 依赖
# 先复制 requirements.txt 可以利用 Docker 的层缓存
# 只有当 requirements.txt 变化时，才会重新安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码到工作目录
# 将所有者设置为之前创建的非 root 用户
COPY --chown=appuser:appuser . .

# 切换到非 root 用户
USER appuser

# 暴露端口（如果未来有 Web 服务，可以取消注释）
# EXPOSE 8000

# 容器启动时执行的命令
# 我们使用一个启动脚本来确保逻辑清晰
CMD ["python", "scheduler.py"]
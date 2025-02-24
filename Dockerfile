
# 使用官方 Python 镜像作为基础
FROM python:3.12.0-slim

# 设置工作目录
WORKDIR /app

# 复制应用文件到容器中
COPY . /app

RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

CMD ["python", "main.py"] 
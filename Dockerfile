# 双休购 app 容器镜像
# 构建上下文必须是仓库根目录：
#   docker build -t shuangxiu-app .
#   docker run -p 8000:8000 -e DEEPSEEK_API_KEY=sk-... shuangxiu-app
# 只用 Python 标准库；镜像在构建期用 CSV 重建数据库（*.db 不入 Git）。
FROM python:3.12-slim

WORKDIR /app

COPY assignments/week-04 ./assignments/week-04
COPY assignments/week-05 ./assignments/week-05

# 构建期重建数据库，避免运行时冷启动重建
RUN python3 assignments/week-04/code/seed_data.py \
 && python3 assignments/week-04/code/build_db.py

ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000

# 密钥只从环境变量注入，绝不写进镜像
CMD ["python3", "assignments/week-05/server.py"]

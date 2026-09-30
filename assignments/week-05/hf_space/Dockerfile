# Hugging Face Space（Docker SDK）镜像
# 目录布局由 code/deploy_hf.py 组装：
#   README.md  Dockerfile  app/(server.py,index.html,skills)  week-04/(code,data)
FROM python:3.12-slim

WORKDIR /app

COPY week-04 ./week-04
COPY app ./app

# 构建期用 CSV 重建数据库；HF 要求以非 root 用户运行
RUN python3 week-04/code/build_db.py \
 && useradd -m -u 1000 appuser \
 && chown -R appuser:appuser /app

USER appuser

ENV HOST=0.0.0.0
ENV PORT=7860
EXPOSE 7860

CMD ["python3", "app/server.py"]

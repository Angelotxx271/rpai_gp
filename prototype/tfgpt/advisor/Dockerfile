# Built from prototype/tfgpt (railway up --path-as-root), so the shared package is in the context
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY shared/requirements.txt shared/requirements.txt
COPY advisor/requirements.txt advisor/requirements.txt
RUN pip install -r advisor/requirements.txt
COPY shared shared
RUN pip install ./shared
COPY advisor advisor
WORKDIR /app/advisor
RUN useradd --create-home tfgpt
USER tfgpt
EXPOSE 8000
CMD ["python", "-m", "tfgpt_shared.serve", "advisor.app:create_app"]

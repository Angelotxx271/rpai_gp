# Built from prototype/tfgpt (railway up --path-as-root), so the shared package is in the context
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 BIND_HOST=::
WORKDIR /app
COPY shared/requirements.txt shared/requirements.txt
COPY web/requirements.txt web/requirements.txt
RUN pip install -r web/requirements.txt
COPY shared shared
RUN pip install ./shared
COPY web web
WORKDIR /app/web
RUN useradd --create-home tfgpt
USER tfgpt
EXPOSE 8000
CMD ["python", "-m", "tfgpt_shared.serve", "web.app:create_app"]

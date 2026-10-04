FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=30 \
    PIP_RETRIES=1

COPY requirements.txt .
# Deliberately use plain uvicorn, not uvicorn[standard]. The standard extra
# downloads optional compiled packages that are unnecessary for this workshop.
RUN python -m pip install --progress-bar off -r requirements.txt

COPY . .
RUN chmod +x /app/scripts/docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

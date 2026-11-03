FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# curl for the container health check; procps and ping for debugging inside the container
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl procps iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY backend /app

EXPOSE 8000
CMD ["bash", "docker-entrypoint.sh"]

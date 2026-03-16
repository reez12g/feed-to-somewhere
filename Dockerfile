FROM python:3.12-slim

ENV APP_ROOT=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR ${APP_ROOT}

COPY setup.py ./
COPY requirements.txt ./
COPY src ./src

RUN pip install --no-cache-dir .

COPY feed_list.csv ./feed_list.csv

RUN useradd -r -s /bin/false appuser && chown -R appuser:appuser ${APP_ROOT}
USER appuser

ENTRYPOINT ["feed-to-somewhere"]

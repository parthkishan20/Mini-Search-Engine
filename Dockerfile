FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY app.py search_engine.py crawler.py ./
COPY templates ./templates
COPY static ./static
COPY input_pages ./input_pages
COPY stopwords.txt ./stopwords.txt

RUN pip install --no-cache-dir .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health/live')"

CMD ["python", "app.py"]

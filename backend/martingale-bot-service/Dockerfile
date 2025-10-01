# martingale-bot-service Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update &amp;&amp; apt-get install -y gcc g++ &amp;&amp; rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8038

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8038/health')"

CMD ["python", "src/main.py"]

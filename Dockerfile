FROM python:3.14-slim

WORKDIR /app

RUN addgroup --system spider && adduser --system --ingroup spider spider

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R spider:spider /app

USER spider

ENV SPIDER_CONFIG=/config/config.ini

CMD ["python", "main.py"]

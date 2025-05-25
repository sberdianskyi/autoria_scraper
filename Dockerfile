FROM python:3.12-slim
LABEL maintainer="sberdianskyi@gmail.com"
ENV PYTHONBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN sed -i 's|/app/chromedriver-linux64/chromedriver|/usr/bin/chromedriver|g' autoria_scraper/spiders/car.py
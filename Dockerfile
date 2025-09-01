# docker build -t anime_scrapy:*-test .
# docker save -o anime_scrapy.tar anime_scrapy
# docker load -i anime_scrapy.tar
FROM python:3.13-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]

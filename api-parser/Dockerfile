FROM python:alpine3.20

WORKDIR /usr/src/app

COPY requirements.txt .
COPY rest-parse-createWebsite.py .
COPY crontab .
COPY run.sh .

RUN pip install --no-cache-dir -r requirements.txt && \
    mkdir -p webserver/static/images

RUN chmod +x run.sh
CMD ["/bin/sh", "run.sh"]
# RUN crontab crontab

# CMD ["crond", "-f"]
# CMD ["python", "rest-parse-createWebsite.py", "-u"]
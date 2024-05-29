FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    mkdir -p webserver/static/images

COPY rest-parse-createWebsite.py .
COPY run.sh .

CMD ["python", "rest-parse-createWebsite.py", "60"]
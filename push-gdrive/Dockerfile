FROM python:alpine3.20

WORKDIR /usr/src/app

COPY requirements.txt .
COPY push-to-gdrive.py .
COPY crontab .
COPY run.sh .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x run.sh
CMD ["/bin/sh", "run.sh"]
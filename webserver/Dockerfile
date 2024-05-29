FROM python:3

WORKDIR /usr/src/app/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /static/images/ images/
COPY /static/favicon.ico .
COPY start-server.sh .
COPY serve-html.py .

RUN chmod +x start-server.sh
CMD ["./start-server.sh"]
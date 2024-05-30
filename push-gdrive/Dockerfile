FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY push-to-gdrive.py .
COPY start-server.sh .

RUN chmod +x start-server.sh
CMD ["./start-server.sh"]
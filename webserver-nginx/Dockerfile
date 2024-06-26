FROM nginx:stable-perl

WORKDIR /usr/share/nginx/html

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

COPY /static/images/ images/
COPY /static/favicon.ico .
# COPY default.conf /usr/share/nginx/html/default.conf
COPY start-server.sh .
# COPY serve-html.py .

RUN chmod +x start-server.sh
CMD ["./start-server.sh"]
# CMD ["nginx", "-g", "daemon off;"]
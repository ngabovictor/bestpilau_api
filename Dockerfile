FROM python:3.10.16-slim

COPY . /app
WORKDIR /app

RUN python3 -m venv /opt/venv

RUN /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r requirements.txt && \
    chmod +x entrypoint.sh

# Install Nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/*

# Copy Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for Nginx
EXPOSE 80

CMD ["/app/entrypoint.sh"]
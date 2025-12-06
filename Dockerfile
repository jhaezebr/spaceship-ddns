FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN chmod a+w /app

ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN adduser snek
USER snek
ADD . .

#CMD ["python3", "spaceship_ddns.py"]

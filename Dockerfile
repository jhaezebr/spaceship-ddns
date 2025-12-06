FROM python:3.13-slim AS production

WORKDIR /app
ADD spaceship_ddns.py spaceship/ requirements.txt /app

RUN pip install --progress-bar off --no-cache-dir -r requirements.txt
ENTRYPOINT ["python3", "spaceship_ddns.py"]


# DEVCONTAINER
FROM production AS devcontainer

RUN apt-get update && \
    apt-get install -y --no-install-recommends git openssh-client && \
    rm -rf /var/lib/apt/lists/*

RUN adduser snek
USER snek

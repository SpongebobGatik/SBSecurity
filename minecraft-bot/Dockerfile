FROM node:18-bullseye

RUN sed -i 's/deb.debian.org/mirror.yandex.ru/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirror.yandex.ru\/debian-security/g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    unzip \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY project.zip /tmp/
RUN unzip /tmp/project.zip -d /app && rm /tmp/project.zip

RUN if [ -f /app/package.json ]; then npm install; fi

COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt || true

# Установка mcpi и picraft из папки packages если есть
RUN if [ -d /app/packages ]; then \
        for pkg in /app/packages/*/; do \
            if [ -f "$pkg/setup.py" ]; then \
                pip3 install --no-cache-dir "$pkg" || true; \
            fi; \
        done; \
    fi

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 10020 25565 4711

ENTRYPOINT ["/app/entrypoint.sh"]
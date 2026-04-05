FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y \
        wget \
        gnupg \
        unzip \
        curl \
        ffmpeg \
        libu2f-udev \
        libvulkan1 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        libnss3 \
        libxss1 \
        libxtst6 \
        xdg-utils \
        procps \
        fonts-liberation \
        libappindicator3-1 \
        libasound2 \
        libnspr4 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxfixes3 \
        libxi6 \
        libxrandr2 \
        libxrender1 \
        libxss1 \
        libxtst6 \
        && \
    rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /etc/apt/trusted.gpg.d/google.gpg && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

RUN chown root:root /opt/google/chrome/chrome-sandbox && \
    chmod 4755 /opt/google/chrome/chrome-sandbox

RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') && \
    wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver*

RUN google-chrome --headless --no-sandbox --disable-gpu --dump-dom https://example.com || (echo "Chrome test failed" && exit 1)

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/downloads && \
    useradd -m -u 1000 downloader && \
    chown -R downloader:downloader /app

USER downloader

CMD ["python", "-m", "main"]
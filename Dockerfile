FROM python:3.10-slim

# Installer Google Chrome
RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip fonts-liberation libnss3 libxss1 libasound2 \
    libatk-bridge2.0-0 libgtk-3-0 libx11-xcb-dev libxcomposite1 libxcursor1 libxdamage1 libxi6 \
    libxtst6 libxrandr2 xdg-utils ca-certificates libgbm1 --no-install-recommends && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install && \
    rm google-chrome-stable_current_amd64.deb

# Chrome path
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV PATH=$PATH:/usr/bin

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "scraper_api:app", "--host", "0.0.0.0", "--port", "8080"]
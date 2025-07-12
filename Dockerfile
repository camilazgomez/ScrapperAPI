FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium=138.0.7204.92-1~deb12u1 \
    chromium-driver=138.0.7204.92-1~deb12u1 \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    libasound2 libxss1 libu2f-udev libvulkan1 \
    fonts-liberation curl ca-certificates \
 && chromium --version \
 && chromedriver --version \
 && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV UC_TEMP_DIR=/tmp/uc_cache
ENV CHROME_VERSION_MAIN=138

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "\
import undetected_chromedriver as uc; \
d = uc.Chrome(headless=True); \
d.quit()"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

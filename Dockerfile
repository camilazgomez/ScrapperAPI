FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    libasound2 libxss1 libu2f-udev libvulkan1 \
    fonts-liberation curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV UC_TEMP_DIR=/tmp/uc_cache

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "\
import undetected_chromedriver as uc; \
d = uc.Chrome(headless=True); \
d.quit()"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    libmariadb-dev \
    libmariadb-dev-compat \
    ffmpeg \
    libsm6 \
    libxext6 \
 && rm -rf /var/lib/apt/lists/*

# 升級 pip
RUN pip install --no-cache-dir --upgrade pip

# 先裝一些比較小的、且依賴關係少的
RUN pip install --no-cache-dir --default-timeout=120 \
    Django==4.2.16 \
    django-cors-headers==4.4.0 \
    djangorestframework==3.15.2 \
    djangorestframework-simplejwt==5.3.1 \
    channels==4.2.0 \
    channels-redis==4.2.1 \
    mysqlclient==2.2.6 \
    pillow==10.4.0 \
    numpy==1.24.4 \
    redis==5.2.0 \
    requests==2.32.3 \
    protobuf==3.20.3 \
    six==1.16.0 \
    async-timeout==5.0.1 \
    cryptography==44.0.0 \
    PyJWT==2.9.0

# 再裝 opencv, mediapipe, torch... 這些比較龐大/常失敗的
RUN pip install --no-cache-dir --default-timeout=120 \
    opencv-python==4.10.0.84 

RUN pip install --no-cache-dir --default-timeout=120 \
    opencv-contrib-python==4.10.0.84 

RUN pip install --no-cache-dir --default-timeout=120 \
    mediapipe==0.10.11

RUN pip install --no-cache-dir --default-timeout=120 \
daphne==4.1.2

WORKDIR /app
COPY . .

# 確保數據庫遷移
# RUN python manage.py makemigrations
# RUN python manage.py migrate

EXPOSE 20000
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "handrecognition_websocket.asgi:application"]

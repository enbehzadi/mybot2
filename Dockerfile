# استفاده از تصویر پایه Python
FROM python:3.10-slim

# نصب وابستگی‌های سیستمی برای psycopg2
RUN apt-get update && apt-get install -y libpq-dev

# تنظیم دایرکتوری کاری داخل کانتینر
WORKDIR /app

# کپی کردن فایل requirements.txt به داخل کانتینر
COPY requirements.txt /app/requirements.txt

# نصب وابستگی‌ها از فایل requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن کدهای Flask و ربات تلگرام
COPY . /app

# اجرای هر دو سرویس (Flask API و ربات تلگرام)
CMD ["bash", "-c", "python app.py & python bot.py"]
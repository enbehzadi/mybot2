# استفاده از یک تصویر پایه پایتون
FROM python:3.9-slim

# تنظیم دایرکتوری کاری داخل کانتینر
WORKDIR /app

# کپی فایل‌های مورد نیاز به داخل کانتینر
COPY . .

# نصب وابستگی‌ها
RUN pip install --no-cache-dir -r requirements.txt

# دستور اجرای سرور Flask
CMD ["python", "app.py"]
# Royalty Events — Deployment Guide

This document outlines the steps required to deploy the **Royalty Events** application to production (Ubuntu Linux with Nginx and Gunicorn or containerized platforms such as Render, Railway, or Heroku).

---

## 1. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Generate a secure `SECRET_KEY` and update the file:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
3. Set `DEBUG=False` and set `ALLOWED_HOSTS` to your production domain(s):
   ```ini
   DEBUG=False
   ALLOWED_HOSTS=events.yourdomain.com,www.events.yourdomain.com
   ```
4. Set up production email SMTP credentials:
   ```ini
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=your_sendgrid_api_key
   DEFAULT_FROM_EMAIL=Royalty Events <concierge@yourdomain.com>
   STAFF_NOTIFICATION_EMAIL=events@yourdomain.com
   ```

---

## 2. Dependencies & Static Files

1. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Run database migrations:
   ```bash
   python manage.py migrate
   ```
3. Collect static files for WhiteNoise/Nginx:
   ```bash
   python manage.py collectstatic --noinput
   ```

---

## 3. Superuser Account

Create the initial administrative account:
```bash
python manage.py createsuperuser
```

---

## 4. Production Server Execution (Gunicorn)

Run Gunicorn using the WSGI configuration:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## 5. Security & Verification Checklist

- [x] `SECRET_KEY` loaded exclusively from environment variables
- [x] `DEBUG` set to `False` in production
- [x] SSL redirection and secure session cookies enabled automatically when `DEBUG=False`
- [x] WhiteNoise configured for serving static files efficiently
- [x] CSRF protection and clickjacking defense active on all forms
- [x] Atomic transactions prevent overbooking concurrency issues
- [x] Automated test suite passing with zero failures

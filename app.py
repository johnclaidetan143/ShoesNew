import os
import random
import smtplib
import ssl
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
)
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    login_required,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash

from forms import (
    LoginForm,
    RegisterForm,
    SearchForm,
    QuantityForm,
    CartUpdateForm,
    CheckoutForm,
    AddressForm,
    PasswordChangeForm,
    NotificationSettingsForm,
    PrivacyForm,
    ProductForm,
)
from models import db, User, Product, CartItem, Order, OrderItem, Notification, Rating


load_dotenv(override=False)


def send_otp_email(to_email, otp, name):
    gmail_user = os.getenv("GMAIL_USER", "").strip()
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD", "").strip()

    print(f"[OTP] Sending to: {to_email}")
    print(f"[OTP] GMAIL_USER: {gmail_user or 'NOT SET'}")
    print(f"[OTP] GMAIL_APP_PASSWORD: {'set' if gmail_pass else 'NOT SET'}")

    if not gmail_user or not gmail_pass:
        print(f"[OTP] FALLBACK OTP for {to_email}: {otp}")
        return False, "GMAIL_USER or GMAIL_APP_PASSWORD not set"

    body = (
        f"Hi {name},\n\n"
        f"Your verification code for Shoes is:\n\n"
        f"    {otp}\n\n"
        f"This code expires in 10 minutes.\n"
        f"Do not share it with anyone.\n\n"
        f"-- Shoes Team"
    )
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "Your OTP Verification Code - Shoes"
    msg["From"] = gmail_user
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, to_email, msg.as_string())
        print(f"[OTP] Successfully sent to {to_email}")
        return True, ""
    except smtplib.SMTPAuthenticationError:
        err = "Gmail authentication failed. Check GMAIL_APP_PASSWORD."
        print(f"[OTP] ERROR: {err}")
        return False, err
    except Exception as e:
        print(f"[OTP] ERROR: {e}")
        return False, str(e)




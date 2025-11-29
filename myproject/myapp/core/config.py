import os
from dotenv import load_dotenv

class Settings():
    """
    Load all environment variable from .env
    """
    # Email Integration
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")


    # Razorpay Integration : suhas
    RAZORPAY_API_KEY= os.getenv("RAZORPAY_API_KEY")
    RAZORPAY_API_PASS= os.getenv("RAZORPAY_API_PASS")


    # Twilio SMS Integration
    ACCOUNT_SID = os.getenv("ACCOUNT_SID")
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


settings = Settings()
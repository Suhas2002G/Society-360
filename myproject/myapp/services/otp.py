import secrets
import hmac
import hashlib
from django.conf import settings

class OtpService:
    
    @staticmethod
    def generate_otp(length=6):
        digits = "0123456789"
        return ''.join(secrets.choice(digits) for _ in range(length))
    
    @staticmethod
    def generate_hashed_otp(otp: str, identifier: str) -> str:
        """
        otp        → generated OTP (plain)
        identifier → email / phone / user_id
        returns    → secure hashed OTP (HMAC-SHA256)
        """
        message = f"{otp}:{identifier}".encode()

        return hmac.new(
            key=settings.SECRET_KEY.encode(),
            msg=message,
            digestmod=hashlib.sha256
        ).hexdigest()
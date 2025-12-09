
from myapp.core.config import settings
from twilio.rest import Client
from django.core.mail import send_mail
import logging
from typing import List

# from django.core.mail import EmailMultiAlternatives
# from django.utils.html import format_html

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        # twilio
        self.account_sid = settings.ACCOUNT_SID
        self.auth_token = settings.AUTH_TOKEN
        self.from_number = settings.TWILIO_PHONE_NUMBER  # Twilio number
        self.to_number = '+917755994279'  # TODO: make dynamic later

        # smtp
        self.from_email = settings.EMAIL_HOST_USER

    def send_sms(self):
        """
        Send an SMS to the configured number.
        Returns the Twilio 'message' object on success, or None on failure.
        """
        try:
            client = Client(self.account_sid, self.auth_token)
            message = client.messages.create(
                from_=self.from_number,
                body=(
                    'Admin Alert: A new notice has been added. '
                    'Please check it on the Society-360 portal for details.'
                ),
                to=self.to_number,
            )
            return message
        except Exception as e:
            logger.error(f"Twilio SMS sending failed: {e}")
            return None

    def send_email(self, subject: str, message: str, to_email: List[str]):
        try:
            message = send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=to_email,
                fail_silently=False,
            )
            logger.info('Email sent successfully...!')
            return message
        except Exception as e:
            logger.error(f"Email OTP sending failed: {e}")
            return None


## Alternative to send template like email
    # def send_email(self, subject: str, message: str, to_email: List[str]):
    #     """
    #     Send a styled HTML email using the existing function signature.

    #     :param subject: Email subject
    #     :param message: Plain message (automatically formatted into HTML)
    #     :param to_email: Recipient list
    #     """
    #     try:
    #         # Convert plain message into simple but clean HTML
    #         html_content = format_html(
    #             """
    #             <div style="font-family: Arial, sans-serif; max-width: 600px; margin:auto; padding: 20px; 
    #                         background:#ffffff; border-radius:10px; border:1px solid #e0e0e0;">
    #                 <h2 style="color:#2563eb; margin-bottom:12px;">Society 360 Notification</h2>
                    
    #                 <p style="font-size:15px; color:#444; line-height:1.6;">
    #                     {}
    #                 </p>

    #                 <hr style="margin:24px 0; border-top:1px solid #e4e4e4;" />

    #                 <p style="font-size:12px; color:#888;">
    #                     This is an automated message — please do not reply.
    #                 </p>
    #             </div>
    #             """,
    #             message.replace("\n", "<br>")  # Convert line breaks
    #         )

    #         # Create email object with text + HTML fallback
    #         email = EmailMultiAlternatives(
    #             subject=subject,
    #             body=message,  # fallback plain text version
    #             from_email=self.from_email,
    #             to=to_email
    #         )

    #         email.attach_alternative(html_content, "text/html")
    #         email.send()

    #         logger.info("HTML Email sent successfully.")
    #         return True

    #     except Exception as e:
    #         logger.error(f"HTML Email sending failed: {e}")
    #         return False

        
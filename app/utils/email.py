"""Email utility - Real SMTP implementation"""
import logging
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """
    Send email via SMTP
    
    Uses Gmail SMTP configuration from environment variables
    """
    try:
        # Get SMTP configuration from environment
        smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        smtp_port = getattr(settings, 'SMTP_PORT', 587)
        smtp_user = getattr(settings, 'SMTP_USER', 'websyncai@gmail.com')
        smtp_pass = getattr(settings, 'SMTP_PASS', '')
        email_from = getattr(settings, 'EMAIL_FROM', 'WebSync-Ai <websyncai@gmail.com>')
        
        # Create message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = email_from
        message['To'] = to
        
        # Attach plain text
        text_part = MIMEText(body, 'plain')
        message.attach(text_part)
        
        # Attach HTML if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)
        
        # Log email (for debugging)
        logger.info("=" * 60)
        logger.info("SENDING EMAIL")
        logger.info("=" * 60)
        logger.info(f"To: {to}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body: {body[:100]}...")
        logger.info("=" * 60)
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(message)
        
        logger.info(f"Email sent successfully to {to}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        # Don't raise exception - email failure shouldn't break the app
        return False

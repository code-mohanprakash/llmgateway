"""
Email service for authentication
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("email_service")

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        self.app_url = os.getenv('APP_URL', 'http://localhost:3000')
        
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send an email"""
        if not self.smtp_username or not self.smtp_password:
            # Development mode: log email instead of sending
            logger.info("📧 EMAIL SERVICE - DEVELOPMENT MODE")
            logger.info(f"TO: {to_email}")
            logger.info(f"SUBJECT: {subject}")
            logger.info(f"HTML CONTENT: {html_content}")
            logger.info("✅ Email logged successfully (SMTP not configured)")
            return True
            
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_password_reset_email(self, email: str, token: str) -> bool:
        """Send password reset email"""
        reset_url = f"{self.app_url}/reset-password?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #9B5967 0%, #8a4d5a 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #9B5967 0%, #8a4d5a 100%);
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    margin-top: 30px;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Model Bridge</h1>
                <h2>Password Reset Request</h2>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>We received a request to reset your password for your Model Bridge account.</p>
                <p>Click the button below to reset your password:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{reset_url}</p>
                <p><strong>This link will expire in 1 hour.</strong></p>
                <p>If you didn't request this password reset, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2024 Model Bridge. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, "Reset Your Password - Model Bridge", html_content)
    
    def send_verification_email(self, email: str, token: str) -> bool:
        """Send email verification"""
        verification_url = f"{self.app_url}/verify-email?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Email Verification</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #9B5967 0%, #8a4d5a 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #9B5967 0%, #8a4d5a 100%);
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    margin-top: 30px;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Model Bridge</h1>
                <h2>Welcome! Please verify your email</h2>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Thank you for signing up for Model Bridge! To complete your registration, please verify your email address.</p>
                <p>Click the button below to verify your email:</p>
                <p style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify Email</a>
                </p>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{verification_url}</p>
                <p><strong>This link will expire in 24 hours.</strong></p>
                <p>If you didn't create an account, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2024 Model Bridge. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, "Verify Your Email - Model Bridge", html_content)


# Global instance
email_service = EmailService()
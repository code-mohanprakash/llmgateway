from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import os
from typing import Optional
import logging
import sys
import os

# Add the utils directory to the path so we can import the email service
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils', 'auth'))
from email_service import email_service

router = APIRouter()

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    message: str

@router.post("/contact")
async def submit_contact_form(form: ContactForm):
    """
    Handle contact form submissions and send email notifications
    """
    try:
        # Get the recipient email from environment variable
        recipient_email = os.getenv("RECIPIENT_EMAIL", "mohan@modelbridge.ai")  # Default to your email
        
        # Create HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>New Contact Form Submission</title>
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
                    background: linear-gradient(135deg, #000000 0%, #14213d 100%);
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
                .field {{
                    margin-bottom: 15px;
                }}
                .label {{
                    font-weight: bold;
                    color: #555;
                }}
                .value {{
                    color: #333;
                    margin-top: 5px;
                }}
                .message-box {{
                    background: white;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #000000;
                    margin-top: 10px;
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
                <h2>New Contact Form Submission</h2>
            </div>
            <div class="content">
                <p>A new contact form has been submitted from the Model Bridge website.</p>
                
                <div class="field">
                    <div class="label">Name:</div>
                    <div class="value">{form.name}</div>
                </div>
                
                <div class="field">
                    <div class="label">Email:</div>
                    <div class="value">{form.email}</div>
                </div>
                
                <div class="field">
                    <div class="label">Company:</div>
                    <div class="value">{form.company or 'Not provided'}</div>
                </div>
                
                <div class="field">
                    <div class="label">Message:</div>
                    <div class="message-box">{form.message}</div>
                </div>
                
                <p><strong>This contact form was submitted from the Model Bridge website.</strong></p>
            </div>
            <div class="footer">
                <p>© 2024 Model Bridge. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        # Send email using the existing email service
        success = email_service.send_email(
            recipient_email, 
            f"New Contact Form Submission from {form.name}", 
            html_content
        )
        
        if success:
            logging.info(f"Contact form submitted by {form.name} ({form.email})")
            return {"message": "Contact form submitted successfully"}
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to send contact form email"
            )
        
    except Exception as e:
        logging.error(f"Error sending contact form email: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to send contact form. Please try again later."
        ) 
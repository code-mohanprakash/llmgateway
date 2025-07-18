# Email Configuration for Contact Form

## Environment Variables to Set

Add these to your `.env` file in the root directory:

```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
RECIPIENT_EMAIL=your-email@gmail.com  # Where contact forms will be sent
APP_URL=http://localhost:3000
```

## Gmail Setup Instructions

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings > Security
   - Find "App passwords" under 2-Step Verification
   - Generate a new app password for "Mail"
   - Use this app password as `SMTP_PASSWORD` (not your regular password)

## Testing the Contact Form

1. Fill out the contact form on your website
2. Check your email for the contact form submission
3. If SMTP is not configured, check the server logs for the email content

## Current Status

The contact form now uses the same email service as password reset emails, so it should work immediately if your email is already configured for password resets. 
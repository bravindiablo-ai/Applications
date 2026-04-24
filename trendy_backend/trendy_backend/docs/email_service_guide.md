# Email Service Implementation Guide

## Overview
This document provides a comprehensive guide to the email service implementation in the TRENDY App backend. The email service handles sending verification emails, password reset emails, and welcome emails to users.

## Features
1. HTML email templates with responsive design
2. SMTP configuration with environment variables
3. Multiple email types:
   - Email verification
   - Password reset
   - Welcome emails
4. Error handling and logging
5. Asynchronous email sending

## Implementation Details

### Email Service Class
The `EmailService` class in `app/services/email_service.py` provides all email functionality:

```python
class EmailService:
    def __init__(self):
        # Configure SMTP settings from environment variables
        self.conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME", "test@example.com"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "password"),
            MAIL_FROM=os.getenv("MAIL_FROM", "test@example.com"),
            MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
            MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "TRENDY App"),
            MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
            MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
```

### Environment Variables
The email service uses the following environment variables for configuration:
- `MAIL_USERNAME`: SMTP username
- `MAIL_PASSWORD`: SMTP password
- `MAIL_FROM`: Sender email address
- `MAIL_PORT`: SMTP port (default: 587)
- `MAIL_SERVER`: SMTP server (default: smtp.gmail.com)
- `MAIL_FROM_NAME`: Sender name (default: TRENDY App)
- `MAIL_STARTTLS`: Enable STARTTLS (default: True)
- `MAIL_SSL_TLS`: Enable SSL/TLS (default: False)

### Email Templates
HTML templates are stored in `app/templates/`:
- `email_verification.html`: Email verification template
- `password_reset.html`: Password reset template

Templates use simple placeholder syntax with double curly braces:
```html
<p>Hello {{username}},</p>
```

### Usage Examples

#### Sending Verification Email
```python
from app.services.email_service import email_service

await email_service.send_verification_email(
    email="user@example.com",
    username="Test User",
    token="verification_token_123"
)
```

#### Sending Password Reset Email
```python
await email_service.send_password_reset_email(
    email="user@example.com",
    username="Test User",
    token="reset_token_123"
)
```

#### Sending Welcome Email
```python
await email_service.send_welcome_email(
    email="user@example.com",
    username="Test User"
)
```

## Integration with Authentication

The email service is integrated with the authentication system in `app/routes/auth.py`:

```python
# Send verification email in background
background_tasks.add_task(send_verification_email, user.id, user.email)

# Send welcome email
background_tasks.add_task(email_service.send_welcome_email, user.email, user.username)
```

## Testing

A test script is available at `scripts/test_email_service.py` to verify email functionality:

```bash
cd trendy_backend
python scripts/test_email_service.py
```

## Error Handling

The email service includes comprehensive error handling:
- SMTP connection errors
- Template rendering errors
- Network timeouts
- Invalid email addresses

All errors are wrapped in HTTP exceptions with descriptive messages.

## Security Considerations

1. Email credentials are loaded from environment variables
2. Password reset tokens expire after 1 hour
3. Verification tokens expire after 24 hours
4. Email addresses are not revealed in error messages for security

## Future Enhancements

1. Email queuing system for better performance
2. Email tracking and analytics
3. Support for additional email providers
4. Email template localization
5. A/B testing for email content

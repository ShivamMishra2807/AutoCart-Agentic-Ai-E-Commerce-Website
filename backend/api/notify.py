"""
Email notifications (free).

By default emails are printed in the server console, so nothing is sent while you build and test.
To send real email with a free Gmail account, set these in the project's .env file (use an app password, not your login password):

    EMAIL_HOST_USER=you@gmail.com
    EMAIL_HOST_PASSWORD=your-16-character-app-password

A failed email never breaks the request that triggered it.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> bool:
    if not to:
        return False
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to], fail_silently=False)
        return True
    except Exception as exc:  # network down, bad credentials ...
        logger.warning('Email to %s was not sent: %s', to, exc)
        return False

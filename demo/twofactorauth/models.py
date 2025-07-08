from random import choice

from twilio.rest import Client

from django.db import models
from django.contrib.auth.models import User

from api.models import ActivityLog


class TwoFactorAuthCode(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    code = models.CharField(max_length=6)
    sent_on = models.DateTimeField(auto_now_add=True)

    @classmethod  # type: ignore
    def send_code(cls, user: User, to_phone: str) -> None:
        import os
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_phone = os.getenv('TWILIO_FROM_PHONE', '+12057363740')

        if not account_sid or not auth_token:
            raise ValueError(
                "TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables must be set")

        client = Client(account_sid, auth_token)
        digits = '0123456789'
        code = ''.join([choice(digits) for _ in range(6)])
        cls.objects.create(
            user=user,
            code=code,
        )
        client.messages.create(
            to=to_phone,  
            from_=from_phone,
            body='Your auth code: ' + code,
        )

    @classmethod  # type: ignore
    def validate_code(cls, user: User, code: str) -> bool:
        if user.is_anonymous:
            return False
        existing = cls.objects.filter(
            user=user, code=code
        ).order_by('-sent_on').first()
        if existing is None:
            ActivityLog.objects.create(
                user=user,
                action='User entered incorrect two-factor auth code'
            )
            return False
        existing.delete()
        ActivityLog.objects.create(
            user=user,
            action='User entered correct two-factor auth code'
        )
        return True

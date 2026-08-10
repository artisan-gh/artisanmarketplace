# notifications/management/commands/test_sms.py
from django.core.management.base import BaseCommand
from notifications.tasks import send_notification_task
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Send a test SMS notification'

    def handle(self, *args, **options):
        email = 'shazdataconsult@gmail.com'
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                password='Dawuda@2024',
                first_name='ZAKARI',
                last_name='MORO',
                phone_number='+233547880172'
            )
            self.stdout.write(f"✅ Created user: {user.email}")

        send_notification_task.delay(
            user_id=user.id,
            subject='Test SMS',
            message='This is a test SMS from Django via Twilio.',
            channel='sms',
            notification_type='SYSTEM'
        )
        self.stdout.write(self.style.SUCCESS("📤 Task sent – check Celery logs!"))
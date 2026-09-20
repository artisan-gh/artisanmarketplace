
from django.core.management.base import BaseCommand
from accounts.sms import send_sms


class Command(BaseCommand):
    help = "Send a test SMS via the configured backend."

    def add_arguments(self, parser):
        parser.add_argument("phone")
        parser.add_argument("--message", default="Tumakonect test message")

    def handle(self, *args, **opts):
        ok = send_sms(opts["phone"], opts["message"])
        self.stdout.write(self.style.SUCCESS("sent") if ok else self.style.ERROR("failed"))

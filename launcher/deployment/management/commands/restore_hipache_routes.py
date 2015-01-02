from django.core.management.base import BaseCommand
from deployment.models import Deployment


class Command(BaseCommand):
    help = 'Restores Hipache routes for all apps'

    def info(self, message):
        self.stdout.write(message)

    def error(self, message):
        self.stderr.write(message)

    def handle(self, *args, **options):
        active_apps = Deployment.objects.filter(status='Completed')
        for app in active_apps:
            app.restore_routes(logger_instance=self)

        expired_apps = Deployment.objects.filter(status='Expired')
        for app in expired_apps:
            app.set_status_page_routes(logger_instance=self)

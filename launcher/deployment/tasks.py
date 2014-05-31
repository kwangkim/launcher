import os
import requests
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from celery import Celery
from celery.utils.log import get_task_logger

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launcher.settings.production')

app = Celery('launcher')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

logger = get_task_logger(__name__)


@app.task
def deploy(deploy_instance):
    logger.info("Deploying {0.project.name}: {0.deploy_id} for {0.email}".format(deploy_instance))
    deploy_instance.deploy()


@app.task
def destroy_expired_apps():
    # protection against circular imports
    from .models import Deployment
    expired = Deployment.objects.filter(expiration_time__lt=timezone.now(),
                                        status='Completed')
    if expired:
        for app in expired:
            app.status = 'Expired'
            app.save()
            r = requests.delete(
                "{0}/api/v1/containers/{1}/?username={2}&api_key={3}".format(
                    settings.SHIPYARD_HOST,
                    app.remote_container_id,
                    settings.SHIPYARD_USER,
                    settings.SHIPYARD_KEY
                ),
            )
            for app_id in app.remote_app_id.split(" "):
                r = requests.delete(
                    "{0}/api/v1/applications/{1}/?username={2}&api_key={3}".format(
                        settings.SHIPYARD_HOST,
                        app_id,
                        settings.SHIPYARD_USER,
                        settings.SHIPYARD_KEY
                    ),
                )


@app.task
def app_expiring_soon_reminder():
    # protection against circular imports
    from .models import Deployment

    #finds deployed apps that have less than 15mins left and
    #haven't been notified yet
    t = timezone.now() + timedelta(minutes=15)
    expiring_soon = Deployment.objects.filter(expiration_time__lt=t,
                                              reminder_mail_sent=False)

    for app in expiring_soon:
        app.send_reminder_email()
        app.reminder_mail_sent = True
        app.save()

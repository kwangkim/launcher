import datetime
import dateutil.relativedelta
import json
import logging
import time
from urlparse import urlparse

from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.core.exceptions import ValidationError

import intercom
import pusher
import redis
import requests
from allauth.account.models import EmailAddress
from customerio import CustomerIO
from model_utils.fields import StatusField
from model_utils import Choices
from .tasks import deploy

logger = logging.getLogger(__name__)

intercom.Intercom.app_id = settings.INTERCOM_APP_ID
intercom.Intercom.api_key = settings.INTERCOM_API_KEY
intercom.Intercom.api_endpoint = 'https://api.intercom.io/'


class Project(models.Model):
    STATUS = Choices('Active', 'Hidden', 'Inactive')

    name = models.CharField(max_length=100)
    github_url = models.CharField(max_length=200)
    image_name = models.CharField(max_length=300)
    ports = models.CharField(max_length=300, help_text="Internally exposed ports separated by spaces, example: 80 8080")
    hostnames = models.CharField(
        max_length=300,
        help_text="Hostnames separated by spaces, needed when multiple ports are exposed, example: lms cms",
        blank=True
    )
    env_vars = models.CharField(max_length=500, blank=True,
                                help_text="Space separated environment variables, example: key1=val1 key2=val2")
    number_of_cpus = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    amount_of_ram = models.PositiveIntegerField('Amount of RAM in MB', blank=True, null=True)
    trial_duration = models.IntegerField(blank=True, null=True, help_text="Trial duration in minutes")
    unconfirmed_trial_duration = models.IntegerField(blank=True, null=True, help_text="Trial duration in minutes")
    slug = models.SlugField(max_length=40, editable=True, blank=True, null=True)
    status = StatusField(default=STATUS.Inactive)
    default_username = models.CharField(max_length=30, blank=True)
    default_password = models.CharField(max_length=30, blank=True)
    survey_form_url = models.URLField(blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        self.full_clean()
        super(Project, self).save(*args, **kwargs)

    @property
    def port_list(self):
        return [int(port) for port in self.ports.split(' ') if port]

    @property
    def hostname_list(self):
        return [hostname for hostname in self.hostnames.split(' ') if hostname]

    @property
    def env_var_dict(self):
        d = {}
        for pair in self.env_vars.split(' '):
            if not pair:
                continue
            key, equals, value = pair.partition('=')
            if not key or not value or equals != '=':
                raise ValueError
            d[key] = value
        return d

    def clean(self):
        try:
            port_list = self.port_list
        except ValueError:
            raise ValidationError({'ports': ['Invalid port(s).']})
        hostname_list = self.hostname_list
        assert len(port_list) > 0
        if len(port_list) == 1:
            if hostname_list:
                raise ValidationError({'hostnames': ['You cannot specify hostnames as there is only one forwarded port.']})
        else:
            if len(port_list) != len(hostname_list):
                raise ValidationError({'hostnames': ['The number of hostnames has to match the number of ports.']})
        try:
            self.env_var_dict
        except ValueError:
            raise ValidationError({'env_vars': ['This string has an incorrect format.']})


    def landing_page_url(self):
        return reverse('landing_page', kwargs={'slug': self.slug})

    def get_trial_duration(self, account_activated=False):
        if account_activated:
            return self.trial_duration or settings.DEFAULT_TRIAL_DURATION
        else:
            return self.unconfirmed_trial_duration or settings.DEFAULT_UNCONFIRMED_TRIAL_DURATION

    def get_human_readable_trial_duration(self, account_activated=False):
        trial_duration = self.get_trial_duration(account_activated)
        if trial_duration <= 60:
            return "{0} minutes".format(trial_duration)
        else:
            delta = dateutil.relativedelta.relativedelta(minutes=trial_duration)
            text = "{0} hour".format(delta.hours)
            # add an 's' if there multiple hours
            if delta.hours > 1:
                text += "s"
            if delta.minutes > 0:
                text += " and {0} minutes".format(delta.minutes)
        return text


class Deployment(models.Model):
    STATUS_CHOICES = (
        ('Deploying', 'Deploying'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Expired', 'Expired')
    )
    project = models.ForeignKey(Project, related_name='deployments')
    url = models.CharField(max_length=600)
    user = models.ForeignKey(User, blank=True, null=True, related_name="deployments")
    email = models.EmailField()
    deploy_id = models.CharField(max_length=100)
    remote_container_id = models.CharField(max_length=64)
    remote_app_id = models.CharField(max_length=100, blank=True)
    launch_time = models.DateTimeField(blank=True, null=True)
    expiration_time = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,
                              default='Deploying')
    reminder_mail_sent = models.BooleanField(default=False)

    def __unicode__(self):
        return self.deploy_id

    def save(self, *args, **kwargs):
        """
        Save the object with the "deploying" status to the DB to get
        the ID, and use that in a celery deploy task
        """
        if not self.id:
            self.status = 'Deploying'
        super(Deployment, self).save(*args, **kwargs)
        if self.status == 'Deploying':
            deploy.delay(self)
            try:
                intercom.User.create(
                    email=self.email
                )
            except:
                pass

    def get_remaining_seconds(self):
        if self.expiration_time and self.expiration_time > timezone.now():
            diff = self.expiration_time - timezone.now()
            return int(diff.total_seconds())
        return 0

    def get_remaining_minutes(self):
        if self.expiration_time and self.expiration_time > timezone.now():
            diff = self.expiration_time - timezone.now()
            remaining_minutes = int(diff.total_seconds() / 60)
            return remaining_minutes
        return 0
    get_remaining_minutes.short_description = 'Minutes remaining'

    def calculate_expiration_datetime(self, email):
        account_activated = EmailAddress.objects.filter(email=email, verified=True).exists()
        trial_duration = self.project.get_trial_duration(account_activated)
        expiration_datetime = self.launch_time + datetime.timedelta(minutes=trial_duration)
        return expiration_datetime

    def deploy(self):
        instance = self._get_pusher_instance()
        cio = CustomerIO(settings.CUSTOMERIO_SITE_ID, settings.CUSTOMERIO_API_KEY)
        cio.identify(id=self.email, email=self.email)
        instance[self.deploy_id].trigger('info_update', {
            'message': "Creating a new container...",
            'percent': 30
        })
        headers = {
            'content-type': 'application/json',
            'X-Service-Key': settings.SHIPYARD_KEY
        }
        # run the container
        env_vars_dict = self.project.env_vars_dict
        port_list = self.project.port_list
        bind_ports = [{"proto": "tcp", "container_port": port} for port in port_list]
        if "edx" in self.project.name.lower():
            env_vars_dict["EDX_LMS_BASE"] = "lms-{0}.{1}".format(self.deploy_id, settings.DEMO_APPS_CUSTOM_DOMAIN)
            env_vars_dict["EDX_PREVIEW_LMS_BASE"] = "preview.lms-{0}.{1}".format(self.deploy_id, settings.DEMO_APPS_CUSTOM_DOMAIN)
            env_vars_dict["EDX_CMS_BASE"] = "cms-{0}.{1}".format(self.deploy_id, settings.DEMO_APPS_CUSTOM_DOMAIN)
            env_vars_dict["INTERCOM_APP_ID"] = settings.INTERCOM_EDX_APP_ID
            env_vars_dict["INTERCOM_APP_SECRET"] = settings.INTERCOM_EDX_APP_SECRET
            env_vars_dict["INTERCOM_USER_EMAIL"] = self.email

        payload = {
            "name": self.project.image_name,
            "cpus": float(self.project.number_of_cpus or settings.DEFAULT_NUMBER_OF_CPUS),
            "memory": self.project.amount_of_ram or settings.DEFAULT_AMOUNT_OF_RAM,
            "type": "service",
            "container_name": self.deploy_id,
            "hostname": self.deploy_id,
            "labels": ["dev"],
            "environment": env_vars_dict,
            "bind_ports": bind_ports
        }
        r = requests.post(
            "{0}/api/containers".format(settings.SHIPYARD_HOST),
            data=json.dumps(payload),
            headers=headers
        )
        if r.status_code == 201:
            response = r.json()
            self.remote_container_id = response[0]['id']
            # This sleep is needed to avoid problems with the API
            time.sleep(2)
            instance[self.deploy_id].trigger('info_update', {
                'message': "Assigning an URL to the app...",
                'percent': 75
            })
            time.sleep(7)
            docker_server = urlparse(response[0]['engine']['addr'])
            docker_server_ip = docker_server.hostname
            domains = []
            hostname_list = self.project.hostname_list
            if not hostname_list:
                domains.append("{0}.{1}".format(self.deploy_id, settings.DEMO_APPS_CUSTOM_DOMAIN))
            else:
                for hostname in hostname_list:
                    domains.append("{0}-{1}.{2}".format(hostname, self.deploy_id, settings.DEMO_APPS_CUSTOM_DOMAIN))
            # maps internal container ports to domains
            port_domain_mapping = {port: domain for port, domain in zip(port_list, domains)}
            # maps internal container ports to public ports (for example: 80 -> 49302)
            public_container_port_mapping = {port["container_port"]: port["port"] for port in response[0]["ports"]}
            scheme = "https" if 443 in port_list else "http"
            app_urls = []
            r = redis.StrictRedis(host=settings.HIPACHE_REDIS_IP, port=settings.HIPACHE_REDIS_PORT, db=0)
            for internal_port, public_port in public_container_port_mapping.items():
                domain = port_domain_mapping[internal_port]
                app_url = "{0}://{1}".format(scheme, domain)
                app_urls.append(app_url)
                r.rpush("frontend:{0}".format(domain), self.deploy_id)
                r.rpush("frontend:{0}".format(domain), "{0}://{1}:{2}".format(scheme, docker_server_ip, public_port))

            self.url = " ".join(app_urls)
            self.status = 'Completed'
            self.launch_time = timezone.now()
            self.expiration_time = self.calculate_expiration_datetime(self.email)
            instance[self.deploy_id].trigger('deployment_complete', {
                'app_name': self.project.name,
                'message': "Deployment complete!",
                'app_url': self.url,
                'username': self.project.default_username,
                'password': self.project.default_password
            })
            try:
                intercom.Event.create(
                    event_name="deployed_app",
                    email=self.email,
                    metadata={
                        'app_name': self.project.name,
                        'app_url': self.url,
                        'deploy_id': self.deploy_id,
                    }
                )
            except:
                pass
            if self.email:
                account_activated = EmailAddress.objects.filter(email=self.email, verified=True).exists()
                cio.track(customer_id=self.email,
                          name='app_deploy_complete',
                          app_url=self.url.replace(" ", "\n"),
                          app_name=self.project.name,
                          status_url="http://launcher.appsembler.com" + reverse(
                              'deployment_detail', kwargs={'deploy_id': self.deploy_id}),
                          trial_duration=self.project.get_human_readable_trial_duration(account_activated),
                          username=self.project.default_username,
                          password=self.project.default_password
                )
        else:
            self.status = 'Failed'
            error_log = DeploymentErrorLog(deployment=self, http_status=r.status_code, error_log=r.text)
            error_log.save()
            send_mail(
                "Deployment failed: {0}".format(self.deploy_id),
                "Error log link: http://launcher.appsembler.com{0}".format(
                    reverse('admin:deployment_deploymenterrorlog_change', args=(error_log.id,))),
                'info@appsembler.com',
                ['filip@appsembler.com', 'nate@appsembler.com']

            )
            instance[self.deploy_id].trigger('deployment_failed', {
                'message': "Deployment failed!",
            })
        self.save()

    def send_reminder_email(self):
        if self.email:
            cio = CustomerIO(settings.CUSTOMERIO_SITE_ID, settings.CUSTOMERIO_API_KEY)
            cio.track(
                customer_id=self.email,
                name='app_expiring_soon',
                app_name=self.project.name,
                app_url=self.url,
                status_url="http://launcher.appsembler.com" + reverse(
                    'deployment_detail', kwargs={'deploy_id': self.deploy_id}),
                remaining_minutes=self.get_remaining_minutes(),
                expiration_time=timezone.localtime(self.expiration_time).isoformat()
            )

    def _get_pusher_instance(self):
        push = pusher.Pusher(
            app_id=settings.PUSHER_APP_ID,
            key=settings.PUSHER_APP_KEY,
            secret=settings.PUSHER_APP_SECRET
        )
        return push


class DeploymentErrorLog(models.Model):
    deployment = models.OneToOneField(Deployment, related_name='error_log')
    http_status = models.CharField(max_length=3)
    error_log = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=600)),
                ('email', models.EmailField(max_length=75)),
                ('deploy_id', models.CharField(max_length=100)),
                ('remote_container_id', models.CharField(max_length=64)),
                ('remote_app_id', models.CharField(max_length=100, blank=True)),
                ('launch_time', models.DateTimeField(null=True, blank=True)),
                ('expiration_time', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'Deploying', max_length=50, choices=[(b'Deploying', b'Deploying'), (b'Completed', b'Completed'), (b'Failed', b'Failed'), (b'Expired', b'Expired')])),
                ('reminder_mail_sent', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeploymentErrorLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('http_status', models.CharField(max_length=3)),
                ('error_log', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('deployment', models.OneToOneField(related_name='error_log', to='deployment.Deployment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('github_url', models.CharField(max_length=200)),
                ('image_name', models.CharField(max_length=300)),
                ('ports', models.CharField(help_text=b'Internally exposed ports separated by spaces, example: 80 8080', max_length=300)),
                ('hostnames', models.CharField(help_text=b'Hostnames separated by spaces, needed when multiple ports are exposed, example: lms cms', max_length=300, blank=True)),
                ('env_vars', models.CharField(help_text=b'Space separated environment variables, example: key1=val1 key2=val2', max_length=500, blank=True)),
                ('number_of_cpus', models.DecimalField(null=True, max_digits=4, decimal_places=2, blank=True)),
                ('amount_of_ram', models.PositiveIntegerField(null=True, verbose_name=b'Amount of RAM in MB', blank=True)),
                ('trial_duration', models.IntegerField(help_text=b'Trial duration in minutes', null=True, blank=True)),
                ('unconfirmed_trial_duration', models.IntegerField(help_text=b'Trial duration in minutes', null=True, blank=True)),
                ('slug', models.SlugField(max_length=40, null=True, blank=True)),
                ('status', model_utils.fields.StatusField(default=b'Inactive', max_length=100, no_check_for_status=True, choices=[(b'Active', b'Active'), (b'Hidden', b'Hidden'), (b'Inactive', b'Inactive')])),
                ('default_username', models.CharField(max_length=30, blank=True)),
                ('default_password', models.CharField(max_length=30, blank=True)),
                ('survey_form_url', models.URLField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='deployment',
            name='project',
            field=models.ForeignKey(related_name='deployments', to='deployment.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deployment',
            name='user',
            field=models.ForeignKey(related_name='deployments', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]

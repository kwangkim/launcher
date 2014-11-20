from allauth.account.models import EmailAddress
from allauth.utils import generate_unique_username
from django.contrib.auth.models import User

from allauth.account.forms import SignupForm
from allauth.account.utils import send_email_confirmation, setup_user_email
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource
from .models import Deployment, Project


class ProjectResource(ModelResource):
    class Meta:
        resource_name = 'projects'
        queryset = Project.objects.exclude(status=Project.STATUS.Inactive).order_by('name')
        limit = 0
        authorization = Authorization()
        excludes = ('env_vars',)


class DeploymentResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        resource_name = 'deployments'
        queryset = Deployment.objects.all()
        authorization = Authorization()
        always_return_data = True

    def hydrate_email(self, bundle):
        email = bundle.data['email'].strip().lower().replace(" ", "")
        bundle.data['email'] = email
        return bundle

    def obj_create(self, bundle, **kwargs):
        # create user if it doesn't exist already
        email = bundle.data['email'].strip().lower()
        try:
            user = User.objects.get(email=email)
            account_activated = EmailAddress.objects.filter(email=email, verified=True).exists()
            if not account_activated:
                send_email_confirmation(bundle.request, user, signup=False)
        except User.DoesNotExist:
            username = generate_unique_username([email, 'user'])
            user = User.objects.create_user(username=username, email=email)
            user.set_unusable_password()
            setup_user_email(bundle.request, user, [])
            send_email_confirmation(bundle.request, user, signup=True)
        return super(DeploymentResource, self).obj_create(bundle, user=user, **kwargs)

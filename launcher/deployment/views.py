from allauth.account import views as allauth_views
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, RedirectView
from .api import ProjectResource
from .models import Deployment, Project


class DeployerMixin(object):
    def get_context_data(self, **kwargs):
        data = super(DeployerMixin, self).get_context_data(**kwargs)
        res = ProjectResource()
        objects = self.get_queryset()
        bundles = []

        for obj in objects:
            bundle = res.build_bundle(obj=obj, request=None)
            bundles.append(res.full_dehydrate(bundle, for_list=True))

        data["apps"] = res.serialize(None, bundles, 'application/json')
        data["app_count"] = len(objects)
        return data


class DeployerListView(DeployerMixin, ListView):
    template_name = 'deployment/deployer_list.html'

    def get_queryset(self):
        qs = Project.objects.filter(status='Active')
        return qs


class ProjectDeployerView(DeployerMixin, DetailView):
    template_name = 'deployment/deployer_detail.html'

    def get_queryset(self):
        return Project.objects.filter(slug=self.kwargs['slug']).exclude(status=Project.STATUS.Inactive)

    def get_context_data(self, **kwargs):
        data = super(ProjectDeployerView, self).get_context_data(**kwargs)
        data['sizes'] = ('mini', 'small', 'medium', 'large')
        data['colors'] = (
            'grey',
            'blue',
            'green',
            'orange',
            'red',
            'black'
        )
        return data


class ProjectDeployerEmbedView(ProjectDeployerView):
    def get_queryset(self):
        return Project.objects.filter(pk=self.kwargs['pk'])


class AppRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        app = self.request.GET.get('app', '')[:255]
        deployment = get_object_or_404(Deployment, url__icontains=app)
        # At the moment we support only the default status page
        return deployment.get_status_page_url()


class DeploymentDetailView(DetailView):
    def get_object(self, queryset=None):
        return get_object_or_404(Deployment, deploy_id=self.kwargs['deploy_id'])

    def get_context_data(self, **kwargs):
        data = super(DeploymentDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        if obj.status == 'Completed':
            remaining = obj.get_remaining_seconds()
            data['remaining'] = remaining
            data['expiration'] = obj.expiration_time
            data['percentage'] = (remaining / 3600.0) * 100
            data['username'] = obj.project.default_username
            data['password'] = obj.project.default_password
        return data


class ConfirmEmail(allauth_views.ConfirmEmailView):
    def post(self, *args, **kwargs):
        response = super(ConfirmEmail, self).post(*args, **kwargs)
        email = self.object.email_address.email
        self.extend_apps_trial(email)
        return response

    def extend_apps_trial(self, email):
        # extend currently running apps when the user confirms his email address
        apps = Deployment.objects.filter(status='Completed', email=email)
        for app in apps:
            app.expiration_time = app.calculate_expiration_datetime(email)
            app.save()

    def get_redirect_url(self):
        return reverse('main')

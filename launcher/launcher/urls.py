from django.conf.urls import include, patterns, url
from django.contrib import admin
from deployment import views as deployment_views
from .api import v1_api

admin.autodiscover()

urlpatterns = patterns('',
    url(r"^accounts/confirm-email/(?P<key>\w+)/$", deployment_views.ConfirmEmail.as_view(),
        name="account_confirm_email"),
    url(r'^api/', include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^embed/(?P<pk>[\d]+)/$', deployment_views.ProjectDeployerEmbedView.as_view(), name='project_embed'),
    url(r'^redirect/$', deployment_views.AppRedirectView.as_view()),
    url(r'^deployment/(?P<deploy_id>[\w]+)/$', deployment_views.DeploymentDetailView.as_view(), name='deployment_detail'),
    url(r'^(?P<slug>[\w-]+)/$', deployment_views.ProjectDeployerView.as_view(), name='landing_page'),
    (r'^accounts/', include('allauth.urls')),
    url(r'^$', deployment_views.DeployerListView.as_view(), name='main'),
)

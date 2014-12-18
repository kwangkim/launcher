from django.contrib import admin, messages
from django.http import HttpResponse
from .models import Deployment, DeploymentErrorLog, Project


class ProjectModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'github_url', 'slug', 'status')
    list_filter = ('status',)


class TextLogger(object):
    def __init__(self):
        self.log = []

    def info(self, message):
        self.log.append('[INFO] {}'.format(message))

    def error(self, message):
        self.log.append('[ERROR] {}'.format(message))


def restore_app(modeladmin, request, queryset):
    logger = TextLogger()
    apps_to_restore = queryset.filter(status='Expired')
    logger.info('Number of apps to restore: {}'.format(len(apps_to_restore)))
    for app in apps_to_restore:
        app.restore(logger_instance=logger)
    # TODO: Make this nicer!
    return HttpResponse('<html><body><textarea style="width: 100%" rows={}>{}</textarea>'
                        '<br><a href="{}">Go back</a></body></html>'.format(
                            2 * len(logger.log), '\n'.join(logger.log), '/admin/deployment/deployment/'))

restore_app.short_description = 'Restore expired apps'


class DeploymentModelAdmin(admin.ModelAdmin):
    list_display = ('deploy_id', 'project', 'deployed_app_url', 'email',
                    'status', 'launch_time', 'get_remaining_minutes')
    list_filter = ('status', 'project__name')
    ordering = ['-id', 'project']
    actions = [restore_app]

    def deployed_app_url(self, obj):
        return '<a href="{0}">{0}</a>'.format(obj.url)
    deployed_app_url.short_description = "App URL"
    deployed_app_url.allow_tags = True


class DeploymentErrorLogModelAdmin(admin.ModelAdmin):
    list_display = ('deployment', 'http_status', 'created')


admin.site.register(Deployment, DeploymentModelAdmin)
admin.site.register(Project, ProjectModelAdmin)
admin.site.register(DeploymentErrorLog, DeploymentErrorLogModelAdmin)

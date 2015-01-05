from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from .models import Project, Deployment
from .utils import get_app_container_routing_data, get_status_page_routing_data


class ProjectModelUnitTests(SimpleTestCase):
    def setUp(self):
        self.project = Project(name='Big Project',
                               github_url='http://github.com/BigProject.git',
                               image_name='appsembler/big-project')

    def test_ports(self):
        self.project.ports = '80 8080'
        self.assertListEqual(self.project.port_list, [80, 8080])

        self.project.ports = '  81   8000  16800 '
        self.assertListEqual(self.project.port_list, [81, 8000, 16800])

        self.project.ports = ''
        self.assertListEqual(self.project.port_list, [])

        self.project.ports = 'aaa'
        with self.assertRaises(ValueError):
            self.project.port_list

        self.project.ports = ' 80  8080  aaa  16800 '
        with self.assertRaises(ValueError):
            self.project.port_list

    def test_ports_validation(self):
        self.project.ports = 'aaa'
        with self.assertRaisesMessage(ValidationError, "{'ports': [u'Invalid port(s).']}"):
            self.project.full_clean()

        self.project.ports = ' 80  8080  aaa  16800 '
        with self.assertRaisesMessage(ValidationError, "{'ports': [u'Invalid port(s).']}"):
            self.project.full_clean()

    def test_hostnames(self):
        self.project.hostnames = 'lms cms'
        self.assertListEqual(self.project.hostname_list, ['lms', 'cms'])

        self.project.hostnames = '  lms   cms  preview.lms   '
        self.assertListEqual(self.project.hostname_list, ['lms', 'cms', 'preview.lms'])

        self.project.hostnames = ''
        self.assertListEqual(self.project.hostname_list, [])

    def test_ports_and_hostnames_validation(self):
        self.project.ports = '80'
        self.project.hostnames = 'lms cms preview.lms'
        with self.assertRaisesMessage(ValidationError, "{'hostnames': [u'You cannot specify hostnames "
                                                       "as there is only one forwarded port.']}"):
            self.project.full_clean()

        self.project.ports = '80 8080'
        self.project.hostnames = 'lms cms preview.lms'
        with self.assertRaisesMessage(ValidationError, "{'hostnames': [u'The number of hostnames "
                                                       "has to match the number of ports.']}"):
            self.project.full_clean()

    def test_ports_and_hostnames_validation_2(self):
        self.project.ports = '80 8080'
        self.project.hostnames = 'lms cms'
        self.project.full_clean()

    def test_env_vars(self):
        self.project.env_vars = ''
        self.assertDictEqual(self.project.env_vars_dict, {})

        self.project.env_vars = '   key=val  '
        self.assertDictEqual(self.project.env_vars_dict, {'key': 'val'})

        self.project.env_vars = '   key=val  key2=val2'
        self.assertDictEqual(self.project.env_vars_dict, {'key': 'val',
                                                         'key2': 'val2'})

        self.project.env_vars = '   key=val  key2=val2  key3=  '
        with self.assertRaises(ValueError):
            self.project.env_vars_dict

    def test_env_vars_validation(self):
        self.project.ports = '80'  # required by Project.full_clean()

        self.project.env_vars = ''
        self.project.full_clean()

        self.project.env_vars = '   key=val  '
        self.project.full_clean()

        self.project.env_vars = '   key=val  key2=val2'
        self.project.full_clean()

        self.project.env_vars = '   key=val  key2=val2  key3=  '
        with self.assertRaisesMessage(ValidationError, "{'env_vars': [u'This string has an incorrect format.']}"):
            self.project.full_clean()

        self.project.env_vars = '   key=val  key2=val2  key3=  key4=1234'
        with self.assertRaisesMessage(ValidationError, "{'env_vars': [u'This string has an incorrect format.']}"):
            self.project.full_clean()


class ProjectModelTests(TestCase):
    def test_setting_slug(self):
        project = Project(name='Big Project',
                          github_url='http://github.com/BigProject.git',
                          image_name='appsembler/big-project',
                          ports='80')
        self.assertIsNone(project.slug)
        project.save()
        self.assertEqual(project.slug, 'big-project')
        project.name = 'Other Big Project'
        project.save()
        # Slug shouldn't change
        self.assertEqual(project.slug, 'big-project')


class UtilsTestCase(SimpleTestCase):
    def test_app_single_endpoint_routing_data(self):
        deployment = Deployment(deploy_id='testproject123456',
                                project=Project(hostnames='', ports='80'))
        routing_data, app_urls = get_app_container_routing_data(
            deployment_instance=deployment,
            shipyard_response=[{'engine': {'addr': 'http://123.234.135.246:2375'},
                                'ports': [{'container_port': 80,
                                           'port': 47930}]}],
            deployment_domain='demo.test')
        self.assertListEqual(routing_data, [['frontend:testproject123456.demo.test',
                                             'testproject123456',
                                             'http://123.234.135.246:47930']])
        self.assertListEqual(app_urls, ['http://testproject123456.demo.test'])

    def test_app_multi_endpoint_routing_data(self):
        deployment = Deployment(deploy_id='testproject123456',
                                project=Project(hostnames='endpoint1 endpoint2 endpoint3', ports='80 8080 16080'))
        routing_data, app_urls = get_app_container_routing_data(
            deployment_instance=deployment,
            shipyard_response=[{'engine': {'addr': 'http://123.234.135.246:2375'},
                                'ports': [{'container_port': 80,
                                           'port': 47930},
                                          {'container_port': 8080,
                                           'port': 47931},
                                          {'container_port': 16080,
                                           'port': 47932}]}],
            deployment_domain='demo.test')
        self.assertListEqual(routing_data, [['frontend:endpoint1-testproject123456.demo.test',
                                             'testproject123456',
                                             'http://123.234.135.246:47930'],
                                            ['frontend:endpoint2-testproject123456.demo.test',
                                             'testproject123456',
                                             'http://123.234.135.246:47931'],
                                            ['frontend:endpoint3-testproject123456.demo.test',
                                             'testproject123456',
                                             'http://123.234.135.246:47932']])
        self.assertListEqual(app_urls, ['http://endpoint1-testproject123456.demo.test',
                                        'http://endpoint2-testproject123456.demo.test',
                                        'http://endpoint3-testproject123456.demo.test'])

    def test_status_page_single_endpoint_routing_data(self):
        deployment = Deployment(deploy_id='testproject123456',
                                project=Project(hostnames='', ports='80'))
        with self.settings(LAUNCHER_IP='111.222.333.444'):
            routing_data = get_status_page_routing_data(deployment_instance=deployment,
                                                        deployment_domain='demo.test')
        self.assertListEqual(routing_data, [['frontend:testproject123456.demo.test',
                                             'testproject123456',
                                             'http://111.222.333.444:8002']])

    def test_status_page_multi_endpoint_routing_data(self):
        deployment = Deployment(deploy_id='testproject123456',
                                project=Project(hostnames='endpoint1 endpoint2 endpoint3', ports='80 8080 16080'))
        with self.settings(LAUNCHER_IP='111.222.333.444'):
            routing_data = get_status_page_routing_data(deployment_instance=deployment,
                                                        deployment_domain='demo.test')
        self.assertListEqual(routing_data, [['frontend:endpoint1-testproject123456.demo.test',
                                             'testproject123456',
                                             'http://111.222.333.444:8002'],
                                            ['frontend:endpoint2-testproject123456.demo.test',
                                             'testproject123456',
                                             'http://111.222.333.444:8002'],
                                            ['frontend:endpoint3-testproject123456.demo.test',
                                             'testproject123456',
                                             'http://111.222.333.444:8002']])

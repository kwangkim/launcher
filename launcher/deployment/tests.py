from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from .models import Project


class ProjectModelTests(SimpleTestCase):
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
        self.assertDictEqual(self.project.env_var_dict, {})

        self.project.env_vars = '   key=val  '
        self.assertDictEqual(self.project.env_var_dict, {'key': 'val'})

        self.project.env_vars = '   key=val  key2=val2'
        self.assertDictEqual(self.project.env_var_dict, {'key': 'val',
                                                         'key2': 'val2'})

        self.project.env_vars = '   key=val  key2=val2  key3=  '
        with self.assertRaises(ValueError):
            self.project.env_var_dict

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

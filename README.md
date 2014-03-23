# Appsembler Launch
## Local development set up

This instructions are written under the assumption that you have [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) set up on your machine.

You also need working [Pusher](http://pusher.com/), [Customer.io](http://customer.io/) accounts, and have [Docker](http://docker.io) and [Shipyard](http://shipyard-project.com/) running on a server somewhere.

1. Create a new virtual env: `mkvirtualenv appsemblerlaunch`
2. Set the required env variables in your virtual environments `bin/postactivate` script:

		#!/usr/local/bin/zsh
		# This hook is run after this virtualenv is activated.
		
		# Django settings
		export DJANGO_SETTINGS_MODULE='launcher.settings.local'
		export SECRET_KEY=''

		# Pusher settings
		export PUSHER_APP_ID=''
		export PUSHER_APP_KEY=''
		export PUSHER_APP_SECRET=''

		# Shipyard settings
		export SHIPYARD_HOST=''
		export SHIPYARD_USER=''
		export SHIPYARD_KEY=''

		# Customer.io settings
		export CUSTOMERIO_SITE_ID=''
		export CUSTOMERIO_API_KEY=''


3. Clone this repo: `git clone git@github.com:appsembler/appsembler-launch.git`
4. Switch to the Docker branch: `git checkout docker`
5. Activate the virtualenv: `workon appsemblerlaunch`
6. `cd appsembler-launch; setvirtualenvproject`
7. Install the requirements: `pip install -r requirements/local.txt`
8. Run syncdb: `./manage.py syncdb --settings=openshift_deploy.settings.local`
9. Run migrations: `./manage.py migrate --settings=launcher.settings.local`
10. Install JS libraries with Bower: `./manage.py bower_install -- --allow-root -f --settings=launcher.settings.local`
11. Load test projects: `./manage.py loaddata deployment/fixtures/sample_projects.json`
12. Start celery in one shell: `CELERY_ALWAYS_EAGER=True celery -A deployment.tasks worker -c 2 -l info -B`
13. And runserver in other: `./manage.py runserver --settings=launcher.settings.local`

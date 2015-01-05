# Appsembler Launch

## New instructions

Install Vagrant and Virtualbox (note that [vagrant-dns](https://github.com/BerlinVagrant/vagrant-dns) works only on OS X so if you use Linux you have to find an [alternative solution](http://serverfault.com/questions/118378/in-my-etc-hosts-file-on-linux-osx-how-do-i-do-a-wildcard-subdomain)): 

	$ vagrant plugin install vagrant-dns
	$ vagrant dns --install
	$ git clone --recursive git@github.com:appsembler/launcher.git
	$ cd launcher/deploy
	$ cp secret_vars.yml.example hosts/vagrant/secret_vars.yml  (<-- edit this file with your settings)
	$ vagrant up
	
If you forgot to use `--recursive` the first time you cloned the repository, you can pull the submodules (`docker_pull` in this case), using this command:

	$ git submodule update --init --recursive
	
# Old instructions

## Local development set up

This instructions are written under the assumption that you have [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) set up on your machine.

You also need working [Pusher](http://pusher.com/), [Customer.io](http://customer.io/) accounts, and have [Docker](http://docker.io) and [Shipyard](http://shipyard-project.com/) running on a server somewhere.

1. Create a new virtual env: `mkvirtualenv launcher`
2. Set the required env variables in your virtual environments `bin/postactivate` script, which is usually located in `~/.virtualenvs/launcher/bin/postactivate`

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
		
		# Intercom.io settings
		export INTERCOM_APP_ID=''
		export INTERCOM_API_KEY=''
		export INTERCOM_EDX_APP_ID=''
		export INTERCOM_EDX_APP_SECRET=''


3. Clone this repo: `git clone git@github.com:appsembler/launcher.git`
4. Activate the virtualenv: `workon launcher`
5. `cd launcher; setvirtualenvproject`
6. Install the requirements: `pip install -r requirements/local.txt`
7. Run syncdb: `./manage.py syncdb`
8. Run migrations: `./manage.py migrate`
9. Install JS libraries with Bower: `./manage.py bower_install -- --allow-root -f`
10. Load sample projects: `./manage.py loaddata deployment/fixtures/sample_projects.json`
11. Start Celery in one shell: `CELERY_ALWAYS_EAGER=True celery -A deployment.tasks worker -c 2 -l info -B`
12. And runserver in other: `./manage.py runserver --settings=launcher.settings.local`

# Changelog

### 2.1.2
### 2.1.1

* fixed human readable project trial duration
* added DB backups to provisioning with automatic upload to S3

### 2.1

* upgraded to Django 1.7
* restoring expired applications from the admin
* dynamic routing, show status page for expired apps
* shipyard wrapper refactored
* improved logging
* removed New Relic server monitoring from vagrant provisioning

### 2.0.3

* fix a bug that crashed loggers when dealing with unicode
* reorganized local settings
* allow `Deployment.remote_app_id ` to be blank

### 2.0.2

* fix a bug that extended the time trial for all users, not just the one confirming the email address

### 2.0.1

* send confirmation emails to existing users with unverified accounts
* sleep a bit longer when deploying to allow apps in the deployed container to start

## 2.0

* uses Shipyard 2.0 for deploying docker containers
* custom hipache routing
* per project configurable cpu/ram settings
* complete ansible scripts for deploying
* local Vagrant setup for testing
* email address confirmation after deploy
* per project time trial duration for confirmed and unconfirmed users
* lots of minor bug fixes and improvements


### 1.5.4

* use correct Intercom app id

### 1.5.3

* send app url to Intercom

### 1.5.2

* forgot to include app secret in the settings file

### 1.5.1

* enable secure mode for Intercom edX tracking

### 1.5

* enable Intercom tracking for launched edX containers

### 1.4.5

* add required customer.io identify call

### 1.4.4

* fix the app id for intercom

### 1.4.3

* use Intercom v2 API to create a user

### 1.4.2

* fixed calculating remaining time for a deployment

### 1.4.1

* add Intercom keys to Ansible secret_keys

### 1.4

* replaced Segment.io with Intercom analytics

### 1.3.4

* upgrade raven(Sentry) to 5.0.0

### 1.3.3

* fix for app names containing multiple space/dash/colon characters

### 1.3.2

* updated Django to 1.6.5

### 1.3.1

* edx specific env settings added
* survey form opens when the deploy button is clicked
* project slugs are editable in the admin

### 1.3

* multiple exposed ports on a container are now exposed on different URLs
* updated the Vagrantfile to work with version 1.5 of Vagrant

### 1.2.1

* fix for API timing bug on newer versions of Shipyard

### 1.2

* optimizations to celery worker settings
* refactoring of frontend JS code
* fix to work with newer version of Shipyard API

### 1.1

* now using Bower for managing frontend packages
* updated Django to 1.6.2 and python packages to newest versions
* enabled django pipeline for compressing the asset files
* added far future expires for compressed assets
* updated Bootstrap to 3.1.1

### 1.0.3

* deploying using ansible now creates an admin user and some sample projects

### 1.0.2

* added the option to run only the deployment of new code using ansible and tags

### 1.0.1

* fixed the bug where the reminder email wouldn't get sent
* fixed the RST embed codes
* fixed the URL of the embed buttons

## 1.0

* added ansible scripts for deploying to Debian/Ubuntu servers
* removed all OpenShift data
* Celery workers and beat worker now controlled by supervisor

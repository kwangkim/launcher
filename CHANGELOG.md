# Changelog

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

### 1.0

* added ansible scripts for deploying to Debian/Ubuntu servers
* removed all OpenShift data
* Celery workers and beat worker now controlled by supervisor

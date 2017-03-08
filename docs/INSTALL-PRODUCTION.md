
Installation notes for the python web server and asynchronous task manager for DSpace submissions, Zendesk submission and deposit updates from DSpace

#1. Install essential packages
-------------------------------------
```
$ sudo apt-get update
$ sudo apt-get install build-essential python-dev
$ sudo apt-get install mlocate #installing locate
$ sudo updatedb #needed to setup locate
$ sudo apt-get install git
$ sudo apt-get install libxml2-dev and libxslt1-dev #needed by magnificent octopus
$ sudo apt-get install zlib1g-dev #needed by magnificent octopus
$ sudo apt-get install links2 # text based browser
```
# 2. Install and run Elastic search
-------------------------------------------------
```
$ sudo apt-get install elasticsearch
$ sudo systemctl start elasticsearch
```
If elastic search does not run with systemctl, uncomment ```
START_DAEMON=true ``` in /etc/default/elasticsearch

 Elastic search runs on port 9200 by default. Visit http://localhost:9200 and make sure elasticsearch is running

# 3. Install the flask application
-------------------------------------------------

## Create a python virtual environment
Install python virtual env
```
$ sudo apt-get install python-pip
$ pip install virtualenv
```
Create the virtual env and activate it
```
$ virtualenv lodestone-venv
$ source ~/lodestone-venv/bin/activate
```

## Clone the git repository

Clone the git repository and initialize the submodules
```
$ git clone https://github.com/CottageLabs/lodestone.git
$ ls -l
$ cd lodestone
$ git submodule update --init --recursive
```

## Install the flask application
```
$ cd esprit/
$ pip install -e .
$ cd ../magnificent-octopus/
$ pip install -e .
$ cd ../
$ pip install -e .
```

## Set the application configuration
```
$ cp template.local.cfg local.cfg
```

Then go into local.cfg and set the configuration values for your specific installation

The following are critical to correct operation of the application:

* The zendesk URL and credentials, depending on whether you are using the Zendesk Sandbox or the Production instance
* The zendesk field mappings for Theses and Data.  Ensure you use the correct mappings depending on whether you are using the Zendesk Sandbox or the Production instance
* Outgoing mail server configuration.  The server must be able to support sending of mail (i.e. relevant permissions on the firewall)

## Start the web server (just to see that we can)
```
$ python service/web.py
```
This runs the flask web application on port 5000. Visit http://localhost:5000 to ensure the application is running. On initializing, the app also setup the index for lodestone in elastic search with the correct default mapping

You should now shut this down (Ctrl-C) then go on to step (4) where we will install the supervisor, and then start the web app in that environment.

# 4. Running the supervisor
-------------------

## Install supervisor

Supervisor is required to ensure that the background-tasks, such as synchronising content to the repository, remain operational.

```
sudo apt-get install supervisor
```

## Install gunicorn
Gunicorn is used to execute the multi-threaded web application under nginx (if you are using Apache, you can skip this step)

```
sudo apt-get install gunicorn
```

## Install Redis
Redis is used as a queue for the supervisor tasks
```
sudo apt-get install redis-server
```

## Configure supervisor
The asynchronous tasks for the DSpace SWORD integration and Zendesk integration is available in the code at service/tasks

There are 4 tasks, 2 for thesis and 2 for data
 * Deposit record to Dspace using Sword and create a ticket in Zendesk
 * Poll Dspace for updates to the deposit through the workflow until it is archived, and update Zendesk if necessary

 Supervisor manages these asynchronous tasks.

 1. Copy the config file config/supervisord.conf to /etc/supervisor/conf.d/lodestone.conf and restart supervisor
 ```
 sudo systemctl restart supervisor
 ```
 The config file assumes the user cottagelabs is running all of the services. If the user running the services is different, change the user in the config file

 2. Run supervisorctl to check the status of the jobs
 ```
 sudo supervisorctl
 status
 exit
 ```

To start at stop jobs at a later date, you can use the supervisorctl command on the "sword" group of services:

    sudo supervisorctl stop sword:*
    sudo supervisorctl start sword:*
    sudo supervisorctl restart sword:*

# 5. Configuring Apache
-------------------

You need to configure your virtual host as follows, setting the appropriate paths for your deployment:

```
<virtualhost localhost:5000>

    WSGIDaemonProcess webtool python-path=/opt/lodestone:/opt/lodestone_venv/lib/python2.7/site-packages user=www-data group=www-data threads=5
    WSGIProcessGroup webtool
    WSGIScriptAlias / /opt/lodestone/service/apache.wsgi
 
 
    <directory /opt/lodestone/>
        WSGIProcessGroup webtool
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptReloading On
        Order deny,allow
        Allow from all
    </directory>
    ErrorLog /var/log/apache2/flask_error.log
</virtualhost>
```
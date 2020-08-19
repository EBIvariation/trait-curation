# Deploying the application in Ubuntu Server

This guide assumes Ubuntu Server 16.04+ has been installed in the host machine. It mostly follows the excellent instructions provided by Digital Ocean (https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04) so visit this set up guide for more details and troubleshooting.

Throughout these instructions, the user will be referenced as *ubuntu* and the project and database name as *traitcuration*.

## 1. Install prerequisites

1. ```sudo apt update``` To make sure the system is up to date.

2. ```sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx git``` This will install pip, the Python development files needed to build Gunicorn later, the Postgres database system and the libraries needed to interact with it the Nginx web server, plus git to clone the original repo.

## 2. Create PostgreSQL database and user

1. Log into an interactive Postgres session by typing: `sudo -u postgres psql`

2. You should now be inside a PostgreSQL prompt. First, create the project database, here with the name *traitcuration*: 
```
CREATE DATABASE traitcuration;

```

3. Next, create a psql user for our project.

```
CREATE USER ubuntu WITH PASSWORD 'password';
```

 **Important: PostgreSQL uses an authentication scheme called “peer authentication” for local connections. Basically, this means that if the user’s operating system username matches a valid Postgres username, that user can login with no further authentication. So make sure that the PSQL username matches the host OS username**:

4. Next, modify a few of the connection parameters for the user we just created. We are setting the default encoding to UTF-8, which Django expects. We are also setting the default transaction isolation scheme to “read committed”, which blocks reads from uncommitted transactions. Lastly, we are setting the timezone to UTC.

```
ALTER ROLE ubuntu SET client_encoding TO 'utf8';
ALTER ROLE ubuntu SET default_transaction_isolation TO 'read committed';
ALTER ROLE ubuntu SET timezone TO 'UTC';
```

5. Now, give our new user access to administer our new database:

```
GRANT ALL PRIVILEGES ON DATABASE traitcuration TO ubuntu;
```

6. When you are finished, exit out of the PostgreSQL prompt by typing:

```
\q
```

## 3. Clone the project's code and create a virtual environment

1. Navigate to the host user's home directory and then clone the GitHub repository and move inside its directory:
```
cd ~
git clone git@github.com:EBIvariation/trait-curation.git
cd trait-curation
````

2. Make sure pip is upgraded, and install the virtualenv package for creating virtual environments in Python:
```
sudo -H pip3 install --upgrade pip
sudo -H pip3 install virtualenv
```

3. Within the project directory, create a Python virtual environment and activate it:
```
virtualenv traitcurationenv
source traitcurationenv/bin/activate

```
Your prompt should change to indicate that you are now operating within a Python virtual environment.

4. Install the project's requirements using the requirements.txt file.
```
pip3 install -r requirements.txt
```

## 4. Configure the project's settings
1.  Open the settings file in your text editor:

```
nano ~/trait-curation/traitcuration/settings.py
```
2. Start by locating the ALLOWED_HOSTS directive and set this to the server's IP or hostname.

```python
# The simplest case: just add the domain name(s) and IP addresses of your Django server
ALLOWED_HOSTS = [ 'example.com', '203.0.113.5']
# To respond to 'example.com' and any subdomains, start the domain with a dot
# ALLOWED_HOSTS = ['.example.com', '203.0.113.5']
#ALLOWED_HOSTS = ['your_server_domain_or_IP', 'second_domain_or_IP', . . .]
```

3. Next, find the section that configures database access. It will start with DATABASES. The configuration in the file is for a SQLite database. We already created a PostgreSQL database for our project, so we need to adjust the settings. You can leave the PORT setting as an empty string:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'traitcuration',
        'USER': 'ubuntu',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

4. Make sure the static files settings, located at the bottom of the files, are correctly configured as follows: 
```python
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
COMPRESS_ENABLED = True

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'traitcuration/static/'),]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
COMPRESS_ROOT = os.path.join(BASE_DIR, 'traitcuration/static/')

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    'compressor.finders.CompressorFinder'
)

COMPRESS_PRECOMPILERS = (
    ('text/x-sass', 'django_libsass.SassCompiler'),
    ('text/x-scss', 'django_libsass.SassCompiler'),
)
```
The `STATICFILES_DIRS` options lets Django know where to look for static files indide the project, the `STATIC_URL` option indicates the url that the server serves static files from, and the `STATIC_ROOT` option is where the directory within the server where static files are all collected to and served from.

Basically, Django collects all files from directories specified in `STATICFILES_DIRS`, moves them to `STATIC_ROOT`, and NginX will serve them from that directory, with clients requesting static files from the `STATIC_URL` endpoint.

6. Now, we can migrate the initial database schema to our PostgreSQL database using the management script. Then we collect our static files.
```
~/trait-curation/manage.py migrate
~/trait-curation/manage.py collectstatic
```

7. Finally, we test the application. First of all ensure that the firewall allows connections to the 8000 port and then start up a development server:
```
sudo ufw allow 8000
~/trait-curation/manage.py runserver 0.0.0.0:8000
```
Visit http://server_domain_or_IP:8000 and you should see the project running.

8. The last thing we want to do before leaving our virtual environment is test Gunicorn to make sure that it can serve the application. We can do this by entering our project directory and using gunicorn to load the project’s WSGI module:
```
cd ~/trait-curation
gunicorn --bind 0.0.0.0:8000 traitcuration.wsgi
```
Navigate to the same address again. You should see the project page without any styling, since Gunicorn doesn't yet know where to find the project's static files.

## 5. Create a Gunicorn systemd Service File
1. Create and open a systemd service file for Gunicorn with sudo privileges in your text editor:
```
sudo nano /etc/systemd/system/gunicorn.service
```

2. Use the following settings
```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/trait-curation
ExecStart=/home/ubuntu/trait-curation/traitcurationenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/trait-curation/traitcuration.sock traitcuration.wsgi:application

[Install]
WantedBy=multi-user.target

```
The `[Unit]` section isused to specify metadata and dependencies. We’ll put a description of our service here and tell the init system to only start this after the networking target has been reached.

I the `[Service]` section we’ll specify the user and group that we want to process to run under. We will give our regular user account ownership of the process since it owns all of the relevant files. We’ll give group ownership to the www-data group so that Nginx can communicate easily with Gunicorn.

We’ll then map out the working directory and specify the command to use to start the service. In this case, we’ll have to specify the full path to the Gunicorn executable, which is installed within our virtual environment. We will bind it to a Unix socket within the project directory since Nginx is installed on the same computer. This is safer and faster than using a network port. We can also specify any optional Gunicorn tweaks here. In our case, we have specified 3 workers.

Finally, in the `[Install]` section we will tell systemd what to link this service to if we enable it to start at boot. We want this service to start when the regular multi-user system is up and running.

3. We can now start the Gunicorn service we created and enable it so that it starts at boot:
```
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```
We can confirm that the operation was successful by checking for the socket file. First check the status of the process to find out whether it was able to start:
```
sudo systemctl status gunicorn
```
Next, check for the existence of the myproject.sock file within your project directory where you should find a `traitcuration.sock` file:
```
ls /home/ubuntu/trait-curation
```

If in need of troubleshooting, visit https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04.

## 6. Configure Nginx to Proxy Pass to Gunicorn
1. Start by creating and opening a new server block in Nginx’s sites-available directory:
```
sudo nano /etc/nginx/sites-available/traitcuration
```

2. Add the following configuration: 
```
server {
    listen 80;
    server_name server_domain_or_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        autoindex on;
        alias /home/ubuntu/trait-curation/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/trait-curation/traitcuration.sock;
    }
}

```

 We will start by specifying that this block should listen on the normal port 80 and that it should respond to our server’s domain name or IP address.
 
 Next, we will tell Nginx to ignore any problems with finding a favicon. We will also tell it where to find the static assets that we collected in our ~/trait-curation/static directory. All of these files have a standard URI prefix of “/static”, so we can create a location block to match those requests.
 
 Finally, we’ll create a location / {} block to match all other requests. Inside of this location, we’ll include the standard proxy_params file included with the Nginx installation and then we will pass the traffic to the socket that our Gunicorn process created.
 
3. Save and close the file when you are finished. Now, we can enable the file by linking it to the sites-enabled directory:
```
sudo ln -s /etc/nginx/sites-available/traitcuration /etc/nginx/sites-enabled
```

4. Test your Nginx configuration for syntax errors by typing:
```
sudo nginx -t
```

5. If no errors are reported, go ahead and restart Nginx by typing:
```
sudo systemctl restart nginx
```

6. Finally, we need to open up our firewall to normal traffic on port 80. Since we no longer need access to the development server, we can remove the rule to open port 8000 as well:
```
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'
```

Note:  After configuring Nginx, the next step before going into production should be securing traffic to the server using SSL/TLS. 

If you have a domain name, the easiest way get an SSL certificate to secure your traffic is using Let’s Encrypt. Follow [this guide](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04) to set up Let’s Encrypt with Nginx on Ubuntu 16.04.

## 7. Install Redis for background task scheduling
The suggested way of installing Redis is compiling it from sources as Redis has no dependencies other than a working GCC compiler and libc. Installing it using the Ubuntu package manager is somewhat discouraged as usually the available version is not the latest.

1. Move to the home folder, download and compile Redis:
```
cd ~
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
```

2. Copy both the Redis server and the command line interface into the proper places:
```
make install
```

3. Check the installation by manually starting the redis-server:
```
redis-server
```

You should also check whether you can ping it by opening another terminal and running:
```
redis-cli ping
```
You should receive a "PONG" response.

4. Create a directory in which to store your Redis config files and your data:
```
sudo mkdir /etc/redis
sudo mkdir /var/redis
```

5. Copy the init script that you'll find in the Redis distribution under the utils directory into /etc/init.d and call it with the name of the port where you are running this instance of Redis:
```
sudo cp utils/redis_init_script /etc/init.d/redis_6379
```

6. Copy the template configuration file you'll find in the root directory of the Redis distribution into /etc/redis/ using the port number as name:
```
sudo cp redis.conf /etc/redis/6379.conf
```

7. Edit the configuration file, making sure to perform the following changes:

- Set daemonize to yes (by default it is set to no).
- Set the logfile to /var/log/redis_6379.log
- Set the dir to /var/redis/6379

8. Create a directory inside /var/redis that will work as data and working directory for this Redis instance:
```
sudo mkdir /var/redis/6379
```

9. Finally add the new Redis init script to all the default runlevels using the following command:
```
sudo update-rc.d redis_6379 defaults
```

10. You are done! Now you can try running your instance with:
```
sudo /etc/init.d/redis_6379 start
```
Make sure that everything is working as expected:

- Try pinging your instance with redis-cli.
- Do a test save with `redis-cli save` and check that the dump file is correctly stored into /var/redis/6379/ (you should find a file called dump.rdb).
- Check that your Redis instance is correctly logging in the log file.
- Make sure that after a reboot everything is still working.

## 8. Daemonize Celery for background task execution

1. First we need to create a configuration file for celery.
```
sudo nano /etc/default/celeryd
```

Add the following configuration:

```python
# Names of nodes to start
#   most people will only start one node:
CELERYD_NODES="worker1"
#   but you can also start multiple and configure settings
#   for each in CELERYD_OPTS
#CELERYD_NODES="worker1 worker2 worker3"
#   alternatively, you can specify the number of nodes to start:
#CELERYD_NODES=10

# Absolute or relative path to the 'celery' command:
CELERY_BIN="/home/trait-curation/traitcurationenv/bin/celery"

# App instance to use
CELERY_APP="traitcuration"

# Where to chdir at start.
CELERYD_CHDIR="/opt/django_projects/your_proj/"

# Extra command-line arguments to the worker
CELERYD_OPTS="--time-limit=7200 --concurrency=8"
# Configure node-specific settings by appending node name to arguments:
#CELERYD_OPTS="--time-limit=7200 -c 8 -c:worker2 4 -c:worker3 2 -Ofair:worker1"

# Set logging level to DEBUG
#CELERYD_LOG_LEVEL="DEBUG"

# %n will be replaced with the first part of the nodename.
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"

CELERYD_USER="ubuntu"
CELERYD_GROUP="ubuntu"

# If enabled pid and log directories will be created if missing,
# and owned by the userid/group configured.
CELERY_CREATE_DIRS=1
```
  
2. Then, we create the init.d script. The generic init.d script provided by celery works well, so we download it and move it to `/etc/init.d/`

```
wget https://raw.githubusercontent.com/celery/celery/3.1/extra/generic-init.d/celeryd
chmod +x celeryd
sudo mv celeryd /etc/init.d/
```

3. Create the logs directory:
```
sudo mkdir /var/log/celery
```

4. Verbose the init-scripts. 
```
sudo sh -x /etc/init.d/celeryd start
```

The output should return:
```
> Starting nodes...
	> worker1@vhcalnplci: OK
+ exit 0
```

5. Enable the daemon
```
sudo update-rc.d celeryd defaults
sudo service celeryd start
```

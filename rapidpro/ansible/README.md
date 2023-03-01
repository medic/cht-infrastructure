# CHT - RapidPro

Table of Contents:

1. [EC2 Network Setup](#EC2-Network-Setup)
2. [Ansible Configuration](#Ansible-Config)
3. [Django + Celery Configuration](#Main-Server-Config)
4. [Mailroom, Courier, RapidPro-Indexier, RapidPro-Archiver Configuration](#Secondary-Server-Config)
5. [Troubleshooting](#Troubleshooting)
6. [Pushing Logs to Logtrail](#Logs-config)

## EC2 Network Setup <a name="EC2-Network-Setup"></a>

Ansible uses ssh to log into servers (hosts) and do installs of required components.

Our architechure choice was to install the rapidpro components on two servers, eventually separating out services into further isolation as needed:

1. Courier, Mailroom, indexer, archiver on one server
2. Django and Celery on another server

The first step in setting up  would be to set up your networks and instances. Create EC2 instances with the following settings:
- Availability Zone: eu-west-2a
- VPC: vpc-342ea25c
- Subnet IDs: subnet-9872aee2
- Security Groups: rapidpro-access
- Tags: { backup: true }
- Key-Pair: rapidpro

Create our backend services (RDS - Postgres, AWS ElastiCache - Redis, AWS ElasticSearch, AWS S3 Bucket and IAM credentials)
Backend services should be placed in identical settings above except:
- Security Groups: rapidpro-backend

## Ansible Configuration <a name="Ansible-Config"></a>

Ansible uses ssh to login and install software. Pull down the rapidpro.pem keypair from our 1password Vault: RapidPro and use that as an identity file for ansible during ssh. If you are restoring a production instance, you should re-associate the original elastic IP with the new ec2 instance in order to prevent updating DNS. 

Prior to running the ansible playbook, you will want to add your IP to the security group: rapidpro-access. In the Security Group edit menu, add a SSH protocol and select My IP address on the drop-down menu. Remember to remove this after provisioning, especially if you have a dynamic IP. The first file to configure for ansible is the hosts inventory file. Replace your ec2 public IP addresses instead of our production elastic IPs. 

This file lists the instances that ansible will install the software to. You can read more [here](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) on how to set up the inventory. Below is a sample inventory.

```yaml
[controller]

control ansible_connection=local

[courier_mail_room_indexer_archiver]

ec2-18-xxx-y-85.eu-west-2.compute.amazonaws.com ansible_user=ubuntu 

[celery]

ec2-18-xxx-yyy-240.eu-west-2.compute.amazonaws.com ansible_user=ubuntu 


```

You then need to refer to this inventory in the ansible.cfg file.

In order to deploy software ansible uses roles. A role is basically a set of steps to deploy software. These roles are organised in ymall files and stored in folders. 
You can read more about ansible roles [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html). These roles are then set up in a playbook `site.yml`. You can read more about ansible playbooks [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html).

To install the software you run the playbook like below. 
First ensure that your syntax is okay

`ansible-playbook site.yml --syntax-check`

Then install the software.

`ansible-playbook --ask-become-pass site.yml`

## Main Server Configuration <a name="Main-Server-Config"></a>

You need to set a number of environment varibles in the roles folders. 

### Django/Celery Environment Variables

Prior to configuring the Django and Celery server, you will want to make sure your backend services (Postgres, Redis, ElasticSearch, S3) are all accessible.
You will have to configure Post-GIS extension on your Postgres server before continuing. After creating RDS inside the network settings in the above sections, please follow: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.PostgreSQL.CommonDBATasks.html#Appendix.PostgreSQL.CommonDBATasks.PostGIS

Also run:
```
rapidpro=# create extension hstore;
rapidpro=# create extension "uuid-ossp";
```

Ensure that your nginx.conf located in `medic-infrastructure/rapidpro/ansible/roles/django/templates/etc/nginx/nginx.conf` is updated with internal_ip's for your two servers.

These are set in the main.yml file in the defaults folder, please search and replace the variables with your values and deploy the playbooks. Variables that could change in the event of a new backend deploy or contain sensitive information are listed below. Remember to update the values in our 1password RapidPro Vault.

```bash
├── django
│   │   |
│   │   ├── defaults
│   │   │   └── main.yml
```

```yaml
django_settings:
  HOSTNAME: "'rapidpro.app.medicmobile.org'"
DATABASES: |
    {
      'default': {
          'ENGINE': 'django.contrib.gis.db.backends.postgis',
          'NAME': 'rapidpro',
          'USER': 'rapidpro',
          'PASSWORD': '1Password:Vault:RapidPro:Production Postgres RapidPro User,
          'HOST': '1Password:Vault:RapidPro:Production Postgres RapidPro User',
          'PORT': '5432',
          'ATOMIC_REQUESTS': True,
          'CONN_MAX_AGE': 60,
          'OPTIONS': {},
      }
    }
Be sure to walk through the rest of this yaml and change all values for REDIS_HOST, BROKER_URL, EMAIL_HOST, MAILROOM_URL, MAILROOM_AUTH_TOKEN, ELASTICSEARCH_URL, SECRET_KEY, and ALLOWED_HOSTS = ['elastic_ip']
```

## Secondary Server Configuration <a name="Secondary-Server-Config"></a>

### Courier Environment Varriables

These are set in the main.yml file in the defaults folder.

```bash
├── courier
│   │   ├── defaults
│   │   │   └── main.yml

```

```yaml
  COURIER_DOMAIN: "rapidpro.app.medicmobile.org"
  COURIER_SPOOL_DIR: "{{ courier_system_home }}/spool"
  COURIER_DB: "postgres://rapidpro:xxxxxx@postgres-yyyyy.com:5432/rapidpro"
  COURIER_REDIS: "redis://redis.yyyyy.com:6379/15"
  COURIER_S3_REGION: "eu-west-2"
  COURIER_S3_MEDIA_BUCKET: "xxxxxx"
  COURIER_S3_MEDIA_PREFIX: "media"
  COURIER_AWS_ACCESS_KEY_ID: xxxxxx
  COURIER_AWS_SECRET_ACCESS_KEY: xxxxxx
  COURIER_ADDRESS: "internal_ip"
  COURIER_PORT: 8005
```


### Mail Room Environment Vars

```bash
├── mailroom
│   │   ├── defaults
│   │   │   └── main.yml

```

```yaml
  MAILROOM_ADDRESS: "internal_ip"
  MAILROOM_ATTACHMENT_DOMAIN: "rapidpro.app.medicmobile.org"
  MAILROOM_AUTH_TOKEN: <hidden>
  MAILROOM_AWS_ACCESS_KEY_ID: <hidden>
  MAILROOM_AWS_SECRET_ACCESS_KEY: <hidden>
  MAILROOM_DB: "postgres://<hidden>@<hidden>/rapidpro?sslmode=disable"
  MAILROOM_DOMAIN: "rapidpro.app.medicmobile.org"
  MAILROOM_LOG_LEVEL: "INFO"
  MAILROOM_REDIS: "redis://<hidden>:6379/15"
  MAILROOM_S3_ENDPOINT: "https://<hidden>.s3.eu-west-2.amazonaws.com"
  MAILROOM_SMTP_SERVER: "smtp://<hidden>%40<hidden>@gmail.com:587/?from=<hidden>%40medicmobile.org"
```

### Rapid Pro Archiver Environment Variables

```bash
├── rp-archiver
│   │   ├── defaults
│   │   │   └── main.yml

```

```yaml
    ARCHIVER_AWS_ACCESS_KEY_ID: "xxxxx",
    ARCHIVER_AWS_SECRET_ACCESS_KEY : "xxxxxx",
    ARCHIVER_DB : "postgres://rapidpro:xxxxx@<hidden>.com/rapidpro?sslmode=disable",
    ARCHIVER_S3_BUCKET : "xxxxxx",

```

### Rapid Pro Indexer Environment variables

```bash
| rp-indexer
│       ├── defaults
│       │   └── main.yml

```

```yaml
rapidpro_indexer_postgresql_url: "postgres://<hidden>/rapidpro"
rapidpro_indexer_elasticsearch_url: "http://elasticsearch_url"
    INDEXER_DB: "postgres://rapidpro:xxxxx@rapidpro.yyyyy.com/rapidpro?sslmode=disable",
    INDEXER_ELASTIC_URL: "https://elasticsearch_url",
    INDEXER_INDEX: "contacts",
    INDEXER_POLL: 5,
    INDEXER_LOG_LEVEL: "info",
    INDEXER_CLEANUP: true
```

## Troubleshooting <a name="Troubleshooting"></a>

After debugging from logs, stop the necessary service and run it from your shell. In order to load Django correctly, you will need to activate a virtualenv.

First log into the Django-Celery server after adding only your IP address to `rapidpro-access` Security Group. Once logged into the server, switch to the django user, export variables and install necessary dependencies as below. Here are common reasons to start the application with this boot method:

If there is an error in the wsgi.ini, you will want to import the module in a django shell to trace the entire error, debug why migrations aren't working, or debug staticfiles for s3/local
```
# sudo -su django
$ virtualenv env
$ source env/bin/activate
(env) $ pip3.6 install -r pip-freeze.txt
(env) $ python manage.py shell
(shell) $ import wsgi

(env) $ pip3.6 install -r pip-freeze.txt
(env) $ python manage.py migrate
```
At this point for Django troubleshooting, you could also invoke a localserver instead of using wsgi and nginx for further debugging.

For other services, after stopping the service: `sudo service celery-django stop`, export the variables in your shell from `/home/<service>/app/environment` or `/home/django/app/temba/settings.py`

RapidPro service names can be found in this repo: ansible/roles/<service>/etc/systemd/system/<name>.service


## Pushing Logs to Logtrail <a name="Logs-config"></a>
Logs are read from systemd logs and pushed to elastic search using Treasure Data's fleuntd. The fluentd plugin is deployed by the td-agent role.  
*NB:*  The Django and celery logs are not pushed to the systemd journal but pushed to logs on disc. The td-agent role for to push these logs has extra steps to create systemd unit files that read these logs and push them to journalctl so that the fluentd systemd plugin can read them and render them in logtrail appropriately. 


*TO DO*: 
- Run nginx as a service with our config. It currently runs as a screen session.
- Create Ansible work that creates SRE users with appropriate privs
- Create tiny dev environment
- Monitoring / Alerting on ec2 servers (disk utilization, cpu metrics) to Prometheus & Slack
- Cloudwatch alerting to Slack for AWS services (rds, elasticsearch, redis)
- Plugged into LogTrail (fluentD)



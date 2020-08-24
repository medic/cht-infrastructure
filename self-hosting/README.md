# HOSTING THE CHT APP

The community health toolkit core framework has been packaged into a docker container to make it portable and easy to install. It is available from [dockerhub](https://hub.docker.com/r/medicmobile/medic-os). To learn more how to work with docker you could follow the tutorial [here](https://docker-curriculum.com/#getting-started) and the cheat sheet [here](https://www.docker.com/sites/default/files/d8/2019-09/docker-cheat-sheet.pdf).  

## Installing Docker Prerequisites

This Ideally depends on which operating system you are running. You need to first install these on your box before you can run the CHT docker containers.

### 64-bit Linux

Depending on which distro you run, install the docker packages from [here](https://docs.docker.com/engine/install/). We have however, historically run most of our containers in Ubuntu.

#### 64-bit Ubuntu

- [Docker CE](https://docs.docker.com/engine/install/ubuntu/)  

- [Docker-compose](https://docs.docker.com/compose/install/)

### Windows 

The CHT docker image was built in Ubuntu so for it to work on windows you need to install The Windows Subsystem for Linux (WSL) in addition to docker desktop.

- [WSL2](https://docs.microsoft.com/en-us/windows/wsl/install-win10)

- [Docker for Windows here](https://download.docker.com/win/stable/Docker%20for%20Windows%20Installer.exe)  and [here](https://docs.docker.com/docker-for-windows/install/)

Note: If you have Hyper-V Capability, please ensure it is enabled in order to run Linux Containers on Windows. If you are running your Windows Server in cloud services, please ensure it is running on [bare-metal](https://en.wikipedia.org/wiki/Bare_machine). You will not be able to run Linux Containers in Windows if the previous comments are not adhered due to nested virtualization.

If you do not have Hyper-V capability, but your server still supports virtualization, ensure that is enabled in your BiOS, and install the following package: [Docker Toolbox using VirtualBox](https://github.com/docker/toolbox/releases)

### Mac OSX:

- [Docker for Mac](https://download.docker.com/mac/stable/Docker.dmg)

## Installing with a compose file

The CHT containers are installed using [docker compose](https://docs.docker.com/compose/reference/overview/) so that you can run multiple containers  as a single service.

Start by choosing the location where you would like to save your compose configuration file.  Then create your docker compose file (`docker-compose.yml`) with contents as listed below.

```yaml
version: '3.7'

services:
  medic-os:
    container_name: medic-os
    image: medicmobile/medic-os:cht-3.9.0-rc.2
    volumes:
      - medic-data:/srv
    ports:
     - 80:80
     - 443:443
    working_dir: /srv
    depends_on:
      - haproxy
    networks:
      - medic-net
    environment:
      - DOCKER_NETWORK_NAME=haproxy
      - DOCKER_COUCHDB_ADMIN_PASSWORD=$DOCKER_COUCHDB_ADMIN_PASSWORD

  haproxy:
    container_name: haproxy
    image: medicmobile/haproxy:rc-1.17
    volumes:
      - medic-data:/srv
    environment:
      - COUCHDB_HOST=medic-os
      - HA_PASSWORD=$DOCKER_COUCHDB_ADMIN_PASSWORD
    networks:
      - medic-net

volumes:
  medic-data:
    name: medic-data

networks:
  medic-net:
    name: medic-net

```

The install requires an admin password that it will configure in the database. You need to provide this externally as an environment variable. before you run the compose file, you need to export this variable as shown below.

`export DOCKER_COUCHDB_ADMIN_PASSWORD=myAwesomeCHTAdminPassword`

You can then run docker-compose in the folder where you put your compose configuration yaml file as shown below.

```bash
## run compose inside the coconfigulation folder as root 

$ sudo docker-compose up 

## In detached mode 

$ sudo docker-compose up  -d 

##  Outside the config folder 

$ sudo docker-compose -f /path/to/docker-compose.yml up -d

```

Note In certain shells, docker-compose may not interpolate the admin password that was exported above. In that case, your admin user had a password automatically generated. Note the New CouchDB Administrative User and New CouchDB Administrative Password in the output terminal. You can retrieve these via running `docker logs medic-os` and searching the terminal.

Once containers are setup, please run the following command from your host terminal:

```bash

$ docker exec -it medic-os /bin/bash -c "sed -i 's/--install=3.9.0/--complete-install/g' /srv/scripts/horticulturalist/postrun/horticulturalist"
$ docker exec -it medic-os /bin/bash -c "/boot/svc-disable medic-core openssh && /boot/svc-disable medic-rdbms && /boot/svc-disable medic-couch2pg"

```

The first command fixes a postrun script for horticulturalist to prevent unique scenarios of re-install. The second command removes extra services that you will not need.

### Visit your project

Open a browser to: https://localhost

You will have to click to through the SSL Security warning. Click Advanced -> Continue to site.


### Clean up an re-install

You could have missed some of the instructions above and end with a bricked setup.  You can use the commands below to clean up and start afresh.

Stop containers:

- `docker-compose down or docker stop medic-os && docker stop haproxy`
Remove containers:

- `docker-compose rm or docker rm medic-os && docker rm haproxy`
Clean data volume:

- `docker volume rm medic-data`

Prune system:

- `docker system prune`

After following the above commands, you can re-run docker-compose up and create a fresh install (no previous data present)


### Port Conflicts

In case you are already running services on HTTP(80) and HTTPS(443), you will have to map new ports to the medic-os container.

Turn off and remove all existing containers that were started:

- `docker-compose down && docker-compose rm`
To find out which service is using a conflicting port: On Linux:

`sudo netstat -plnt | grep ':<port>'`
On Mac (10.10 and above):

`sudo lsof -iTCP -sTCP:LISTEN -n -P | grep ':<port>'` 

You can either kill the service which is occupying HTTP/HTTPS ports, or run the container with forwarded ports that are free. In your compose file, change the ports under medic-os:

```yaml

services:
  medic-os:
    container_name: medic-os
    image: medicmobile/medic-os:cht-3.7.0-rc.1
    volumes:
      - medic-data:/srv
    ports:
     - 8080:80
     - 444:443

```

Note: You can  substitute 8080, 444 with whichever ports are free on your host. You would now visit https://localhost:444 to visit your project.

### Helpful Docker Commands

#### Get  into a container and view specific service logs 

`docker exec -it medic-os /bin/bash`

##### Once inside container

- view couchdb logs:
`#less /srv/storage/medic-core/couchdb/logs/startup.log`
- view medic-api logs:
`#less /srv/storage/medic-api/logs/medic-api.log`
- view medic-sentinel logs:
`#less /srv/storage/medic-sentinel/logs/medic-sentinel.log`

#### View container stderr/stdout log

`# docker logs medic-os`
`# docker logs haproxy`

#### Other handy commands

- list running containers `#docker ps`

- list all available docker containers with their status `# docker ps -a`

- stop container `# docker stop <container_id>`

- start container `docker start <container_id>`

- list all stoped containers `docker ps -f "status=exited"`

## SSL Certificate Installation

Once your application is up,  you can install your ssl certificates by following the steps below.

- First you need to have your ssl certificate files handy. Both the key file (`ssl.key`) that you sued to generate the certificate and the certificate file (`ssl.crt`) issued by certification authority e.g. letsencrypt. 

### Copy certificates into the medic-os container

```bash
$sudo docker ps
$sudo docker cp /path/to/ssl.crt medic-os:/srv/settings/medic-core/nginx/private/ssl.crt
$docker cp /path/to/ssl.key medic-os:/srv/settings/medic-core/nginx/private/ssl.key
```

### Edit the nginx configuration file

```bash
$docker exec -it medic-os /bin/bash
sed -i "s|default.crt|ssl.crt|" /srv/settings/medic-core/nginx/nginx.conf
sed -i "s|default.key|ssl.key|" /srv/settings/medic-core/nginx/nginx.conf

```

### Restart services

```bash
# enter medic-os container:
$docker exec -it medic-os /bin/bash
 /boot/svc-restart medic-core nginx

```

### View Nginx Logs

```bash
# enter medic-os container:
$docker exec -it medic-os /bin/bash
cd /srv/storage/medic-core/nginx/logs/ 
ls
access.log error-ssl.log error.log startup.og
```

## Data storage & persistence

Docker containers are [stateless](https://www.redhat.com/en/topics/cloud-native-apps/stateful-vs-stateless) by design.  In order to persist your data when a container restarts you need to specify  the volumes that the container can use to store data. The CHT app stores all it's data in the `/srv` folder.  This is the folder that you need to map to your volume before you spin up your containers. 

Ideally you should map this folder to a volume that is backed up regulaly by your cloud hosting provider.

The exmaple below shows how to map this folder in ubuntu

```bash
# create the /srv folder 
$sudo mkdir  /srv 

## mount your volume to this folder 
$sudo mount /dev/xvdg /srv # the attached volume number varries find your volume by running lsblk
```

Update your compose file  so that the containers store data to this folder

```yaml

services:
  medic-os:
    container_name: medic-os
    image: medicmobile/medic-os:cht-3.9.0-rc.2
    volumes:
      - /srv:/srv

 ----
 haproxy:
    container_name: haproxy
    image: medicmobile/haproxy:rc-1.17
    volumes:
      - /srv:/srv 

```

Alternatively  you can create the /srv folder on any drive with anough space that is regularly backed up. You then just map the path to the folder in the compose file like this.

```yaml
volumes:
      - /path/to/srv:/srv
```

Be sure to check the available storage space regularly and expand your volume when needed









1. Mount the attached EBS volume to the instance.  Mount it to /srv
2. Make an entry in `/etc/fstab` so that the volume is always mounted on every boot. (https://help.ubuntu.com/community/Fstab)
3. Run the `prepare.sh` command from within the `prepare-system/ubuntu` folder
4. See if things are running by doing a `sudo docker ps`
5. You can connect to the running container using `sudo docker exec -it medic-os /bin/bash`
6.  You can check supervisorctl by doing `sudo supervisorctl`.  It should show you that medic is `RUNNING`
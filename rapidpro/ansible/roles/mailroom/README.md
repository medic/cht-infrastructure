onaio - Mailroom [![Build Status](https://travis-ci.org/onaio/ansible-mailroom.svg?branch=master)](https://travis-ci.org/onaio/ansible-mailroom)
=========

Installs and configures [Mailroom](https://github.com/nyaruka/mailroom).

Requirements
------------



Role Variables
--------------
Check the [defaults/main.yml](./defaults/main.yml) file for the full list of default variables.

```yml
# System architecture for the host. Possible value are:
#   - linux_amd64
#   - darwin_amd64
mailroom_system_architecture: "linux_amd64"
# The package repository to download Mailroom tarballs from
mailroom_download_url: "https://github.com/nyaruka/mailroom/releases/download/v{{ mailroom_version }}/mailroom_{{ mailroom_version }}_{{ mailroom_system_architecture }}.tar.gz"
# The root directory Mailroom versioned directories are created
mailroom_package_directory_root: "{{ mailroom_system_home }}/app-versioned"
# The name to give the directory the Mailroom binary is copied to
mailroom_package_directory_name: "{{ mailroom_version }}"
```

Dependencies
------------

Example Playbook
----------------

```yml
- hosts: all
  roles:
    - role: ansible-mailroom
      mailroom_version: "0.0.195"
```

License
-------

Apache v2.0

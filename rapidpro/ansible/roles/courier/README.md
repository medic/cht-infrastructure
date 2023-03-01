onaio - Courier [![Build Status](https://travis-ci.org/onaio/ansible-courier.svg?branch=master)](https://travis-ci.org/onaio/ansible-courier)
=========

Installs and configures [Courier](https://github.com/nyaruka/courier).

Requirements
------------

Courier needs to point to instances of Redis and PostgreSQL for it to run as expected.

Role Variables
--------------
Check the [defaults/main.yml](./defaults/main.yml) file for the full list of default variables.

```yml
# The package repository to download Courier tarballs from
`courier_package_repository_url`: "https://github.com/nyaruka/courier/releases/download"

# System architecture for the host. Possible value are:
#   - linux_amd64
#   - windows_amd64
#   - darwin_amd64
`courier_system_architecture`: "linux_amd64"

# The download URL for the Courier tarball
courier_download_url: "{{ courier_package_repository_url }}/v{{ courier_version }}/courier_{{ courier_version }}_{{ courier_system_architecture }}.tar.gz"

# The root directory Courier versioned directories are created
courier_package_directory_root: "{{ courier_system_home }}/app-versioned"

# The name to give the directory the Courier binary is copied to
courier_package_directory_name: "{{ courier_version }}"

# Path to the symbolic link pointing to the current active Courier
# binary
courier_active_package_symlink: "{{ courier_system_home }}/app"

# Courier environment variables to be set. Check
# https://github.com/nyaruka/courier#rapidpro-configuration
# for the full list of variables
courier_environment_vars:
  COURIER_DOMAIN: "example.com"
  COURIER_SPOOL_DIR: "{{ courier_system_home }}/spool"
```

Dependencies
------------

Example Playbook
----------------

```yml
- hosts: all
  roles:
    - role: ansible-courier
      courier_version: "1.2.148"
```

License
-------

Apache v2.0

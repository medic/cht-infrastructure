onaio - RapidPro Indexer [![Build Status](https://travis-ci.org/onaio/ansible-rapidpro-indexer.svg?branch=master)](https://travis-ci.org/onaio/ansible-rapidpro-indexer)
=========

Installs and configures [RapidPro Indexer](https://github.com/nyaruka/rp-indexer).

Requirements
------------

RapidPro Indexer needs to point to instances of Elasticsearch and PostgreSQL for it to run as expected.

Role Variables
--------------
Check the [defaults/main.yml](./defaults/main.yml) file for the full list of default variables.

```yml
# System architecture for the host. Possible value are:
#   - linux_amd64
#   - darwin_amd64
rapidpro_indexer_system_architecture: "linux_amd64"

# The package repository to download RapidPro Indexer tarballs from
rapidpro_indexer_download_url: "https://github.com/nyaruka/rp-indexer/releases/download/v{{ rapidpro_indexer_version }}/rp-indexer_{{ rapidpro_indexer_version }}_{{ rapidpro_indexer_system_architecture }}.tar.gz"

# The root directory RapidPro Indexer versioned directories are created
rapidpro_indexer_package_directory_root: "{{ rapidpro_indexer_system_home }}/app-versioned"

# The name to give the directory the RapidPro Indexer binary is copied to
rapidpro_indexer_package_directory_name: "{{ rapidpro_indexer_version }}"

# Whether to rebuild the index before starting the service
rapidpro_indexer_rebuild: false

# Whether to clean old indexes when index is rebuilt
rapidpro_indexer_cleanup: true
```

Dependencies
------------

Example Playbook
----------------

```yml
- hosts: all
  roles:
    - role: postgresql
    - role: elasticsearch
    - role: ansible-rapidpro-indexer
      rapidpro_indexer_version: "1.0.26"
```

License
-------

Apache v2.0

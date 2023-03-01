import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_rapidpro_indexer_service(host):
    rapidpro_indexer = host.service("rapidpro-indexer")

    assert rapidpro_indexer.is_running
    assert rapidpro_indexer.is_enabled


def test_rapidpro_indexer_app_files(host):
    appDir = host.file("/home/rapidpro-indexer/app")
    assert appDir.exists
    assert appDir.user == "rapidpro-indexer"
    assert appDir.group == "rapidpro-indexer"
    assert appDir.is_symlink
    assert appDir.linked_to == "/home/rapidpro-indexer/app-versioned/1.0.26"

    appVersionedDir = host.file("/home/rapidpro-indexer/app-versioned/1.0.26")
    assert appVersionedDir.exists
    assert appVersionedDir.user == "rapidpro-indexer"
    assert appVersionedDir.group == "rapidpro-indexer"
    assert appVersionedDir.is_directory
    assert oct(appVersionedDir.mode) == "0o755"

    configFile = host.file("/home/rapidpro-indexer/app/indexer.toml")
    assert configFile.exists
    assert configFile.user == "rapidpro-indexer"
    assert configFile.group == "rapidpro-indexer"
    assert configFile.is_file
    assert oct(configFile.mode) == "0o750"

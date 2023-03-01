import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_courier_service(host):
    courier = host.service("courier")

    assert courier.is_running
    assert courier.is_enabled


def test_courier_app_files(host):
    appDir = host.file("/home/courier/app")
    assert appDir.exists
    assert appDir.user == "courier"
    assert appDir.group == "courier"
    assert appDir.is_symlink
    assert appDir.linked_to == "/home/courier/app-versioned/1.2.148"

    appVersionedDir = host.file("/home/courier/app-versioned/1.2.148")
    assert appVersionedDir.exists
    assert appVersionedDir.user == "courier"
    assert appVersionedDir.group == "courier"
    assert appVersionedDir.is_directory
    assert oct(appVersionedDir.mode) == "0o755"

    envFile = host.file("/home/courier/app/environment")
    assert envFile.exists
    assert envFile.user == "courier"
    assert envFile.group == "courier"
    assert envFile.is_file
    assert oct(envFile.mode) == "0o750"

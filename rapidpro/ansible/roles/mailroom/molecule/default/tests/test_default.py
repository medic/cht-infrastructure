import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_mailroom_service(host):
    mailroom = host.service("mailroom")

    assert mailroom.is_running
    assert mailroom.is_enabled


def test_mailroom_app_files(host):
    appDir = host.file("/home/mailroom/app")
    assert appDir.exists
    assert appDir.user == "mailroom"
    assert appDir.group == "mailroom"
    assert appDir.is_symlink
    assert appDir.linked_to == "/home/mailroom/app-versioned/0.0.195"

    appVersionedDir = host.file("/home/mailroom/app-versioned/0.0.195")
    assert appVersionedDir.exists
    assert appVersionedDir.user == "mailroom"
    assert appVersionedDir.group == "mailroom"
    assert appVersionedDir.is_directory
    assert oct(appVersionedDir.mode) == "0o755"

    envFile = host.file("/home/mailroom/app/environment")
    assert envFile.exists
    assert envFile.user == "mailroom"
    assert envFile.group == "mailroom"
    assert envFile.is_file
    assert oct(envFile.mode) == "0o750"

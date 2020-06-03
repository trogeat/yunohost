import glob
import os
import pytest
import shutil
import requests

from conftest import message, raiseYunohostError

from moulinette import m18n
from moulinette.utils.filesystem import mkdir

from yunohost.domain import _get_maindomain, domain_add, domain_remove, domain_list
from yunohost.utils.error import YunohostError
from yunohost.regenconf import manually_modified_files, regen_conf, _get_conf_hashes, _force_clear_hashes

TEST_DOMAIN = "secondarydomain.test"
TEST_DOMAIN_NGINX_CONFIG = "/etc/nginx/conf.d/secondarydomain.test.conf"
SSHD_CONFIG = "/etc/ssh/sshd_config"

def setup_function(function):

    _force_clear_hashes([TEST_DOMAIN_NGINX_CONFIG])
    clean()

def teardown_function(function):

    clean()
    _force_clear_hashes([TEST_DOMAIN_NGINX_CONFIG])

def clean():

    assert os.system("pgrep slapd >/dev/null") == 0
    assert os.system("pgrep nginx >/dev/null") == 0

    if TEST_DOMAIN in domain_list()["domains"]:
        domain_remove(TEST_DOMAIN)
        assert not os.path.exists(TEST_DOMAIN_NGINX_CONFIG)

    os.system("rm -f %s" % TEST_DOMAIN_NGINX_CONFIG)

    assert os.system("nginx -t 2>/dev/null") == 0

    assert not os.path.exists(TEST_DOMAIN_NGINX_CONFIG)
    assert TEST_DOMAIN_NGINX_CONFIG not in _get_conf_hashes("nginx")
    assert TEST_DOMAIN_NGINX_CONFIG not in manually_modified_files()

    regen_conf(['ssh'], force=True)


def test_add_domain():

    domain_add(TEST_DOMAIN)

    assert TEST_DOMAIN in domain_list()["domains"]

    assert os.path.exists(TEST_DOMAIN_NGINX_CONFIG)

    assert TEST_DOMAIN_NGINX_CONFIG in _get_conf_hashes("nginx")
    assert TEST_DOMAIN_NGINX_CONFIG not in manually_modified_files()


def test_add_and_edit_domain_conf():

    domain_add(TEST_DOMAIN)

    assert os.path.exists(TEST_DOMAIN_NGINX_CONFIG)
    assert TEST_DOMAIN_NGINX_CONFIG in _get_conf_hashes("nginx")
    assert TEST_DOMAIN_NGINX_CONFIG not in manually_modified_files()

    os.system("echo ' ' >> %s" % TEST_DOMAIN_NGINX_CONFIG)

    assert TEST_DOMAIN_NGINX_CONFIG in manually_modified_files()


def test_add_domain_conf_already_exists():

    os.system("echo ' ' >> %s" % TEST_DOMAIN_NGINX_CONFIG)

    domain_add(TEST_DOMAIN)

    assert os.path.exists(TEST_DOMAIN_NGINX_CONFIG)
    assert TEST_DOMAIN_NGINX_CONFIG in _get_conf_hashes("nginx")
    assert TEST_DOMAIN_NGINX_CONFIG not in manually_modified_files()


def test_ssh_conf_unmanaged():

    _force_clear_hashes([SSHD_CONFIG])

    assert SSHD_CONFIG not in _get_conf_hashes("ssh")

    regen_conf()

    assert SSHD_CONFIG in _get_conf_hashes("ssh")


def test_ssh_conf_unmanaged_and_manually_modified(mocker):

    _force_clear_hashes([SSHD_CONFIG])
    os.system("echo ' ' >> %s" % SSHD_CONFIG)

    assert SSHD_CONFIG not in _get_conf_hashes("ssh")

    regen_conf()

    assert SSHD_CONFIG in _get_conf_hashes("ssh")
    assert SSHD_CONFIG in manually_modified_files()

    with message(mocker, "regenconf_need_to_explicitly_specify_ssh"):
        regen_conf(force=True)

    assert SSHD_CONFIG in _get_conf_hashes("ssh")
    assert SSHD_CONFIG in manually_modified_files()

    regen_conf(['ssh'], force=True)

    assert SSHD_CONFIG in _get_conf_hashes("ssh")
    assert SSHD_CONFIG not in manually_modified_files()

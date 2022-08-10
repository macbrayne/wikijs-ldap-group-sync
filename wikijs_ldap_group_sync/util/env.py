import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger("ldap-group-sync:env")

class Env:
    WIKIJS_URL: str = os.environ.get("WIKIJS_URL")
    WIKIJS_TOKEN: str = os.environ.get("WIKIJS_TOKEN")

    LDAP_URL: str = os.environ.get("LDAP_URL")
    ADMIN_BIND_DN: str = os.environ.get("ADMIN_BIND_DN")
    ADMIN_BIND_CRED: str = os.environ.get("ADMIN_BIND_CRED")

    GROUPS_SEARCH_BASE: str = os.environ.get("GROUPS_SEARCH_BASE")
    GROUPS_SEARCH_FILTER: str = os.environ.get("GROUPS_SEARCH_FILTER")

    USER_SEARCH_BASE: str = os.environ.get("USER_SEARCH_BASE")
    USER_SEARCH_FILTER: str = os.environ.get("USER_SEARCH_FILTER")

    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", default="INFO")

    LDAP_TLS_VERIFICATION: bool = os.environ.get("LDAP_TLS_VERIFICATION")
    LDAP_TLS_CERT_FILE: str = os.environ.get("LDAP_TLS_CERT_PATH")


def check_config():
    do_exit = False
    if Env.WIKIJS_URL is None:
        logger.error("WIKIJS_URL is not set")
        do_exit = True
    if Env.WIKIJS_TOKEN is None:
        logger.error("WIKIJS_TOKEN is not set")
        do_exit = True
    if Env.LDAP_URL is None:
        logger.error("LDAP_URL is not set")
        do_exit = True
    if Env.ADMIN_BIND_DN is None:
        logger.warning("ADMIN_BIND_DN is not set")
    if Env.ADMIN_BIND_CRED is None:
        logger.warning("ADMIN_BIND_CRED is not set")
    if Env.GROUPS_SEARCH_BASE is None:
        logger.error("GROUPS_SEARCH_BASE is not set")
        do_exit = True
    if Env.GROUPS_SEARCH_FILTER is None:
        logger.warning("GROUPS_SEARCH_FILTER is not set")
    if Env.USER_SEARCH_BASE is None:
        logger.error("USER_SEARCH_BASE is not set")
        do_exit = True
    if Env.USER_SEARCH_FILTER is None:
        logger.warning("USER_SEARCH_FILTER is not set")
    if Env.LDAP_TLS_VERIFICATION is not None and Env.LDAP_TLS_CERT_FILE is None:
        logger.warning("LDAP_TLS_VERIFICATION set but LDAP_TLS_CERT_FILE is not set")

    if do_exit:
        logger.error("Configuration errors found, exiting")
        exit(1)

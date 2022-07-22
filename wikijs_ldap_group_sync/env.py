import os
from dotenv import load_dotenv
load_dotenv()

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

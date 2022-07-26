from env import *
from classes import *
import ldap
import logging

logger = logging.getLogger("ldap-group-sync:ldap_utils")

def get_ldap_groups(ldap_connection):
    # Retrieving groups from LDAP
    logger.info("Retrieving list group from ldap")
    search = ldap_connection.search_s(base=Env.GROUPS_SEARCH_BASE, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=Env.GROUPS_SEARCH_FILTER, attrlist=['cn', 'memberUid'])
    groups = []

    for result in search:
        result = result[1]
        cn = result['cn'][0].decode("utf-8")
        member_uids = []
        raw_member_uids = result.get('memberUid', [])
        for raw_member_uid in raw_member_uids:
            member_uids.append(raw_member_uid.decode("utf-8"))
        groups.append(Group(cn=cn, member_uids=member_uids))
    return groups

def get_ldap_users(ldap_connection):
    search = ldap_connection.search_s(base=Env.USER_SEARCH_BASE, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=Env.USER_SEARCH_FILTER, attrlist=['uid', 'cn', 'mail'])

    ldap_users = []
    for result in search:
        uid = result[0]
        cn = result[1]['uid'][0].decode("utf-8")
        if "mail" not in result[1]:
            continue
        email = result[1]['mail'][0].decode("utf-8")
        ldap_users.append(LDAPUser(uid=uid, cn=cn, email=email))
    return ldap_users
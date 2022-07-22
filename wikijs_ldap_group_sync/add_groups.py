
from graphqlclient import GraphQLClient
import ldap
import logging
from env import *


import util
from classes import *



# ---------------------------
### SETUP
# ---------------------------
# LDAP Connection
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
try:
    logging.info("Attempting LDAP connection to ", Env.LDAP_URL)
    ldap_connection = ldap.initialize(Env.LDAP_URL)
    ldap_connection.simple_bind_s(Env.ADMIN_BIND_DN, Env.ADMIN_BIND_CRED)
except ldap.SERVER_DOWN as error:
    logging.error(error)
    exit(1)

# WikiJS client
client = GraphQLClient(Env.WIKIJS_URL)
client.inject_token(Env.WIKIJS_TOKEN)
# ---------------------------

# Retrieving groups from LDAP
search = ldap_connection.search_s(base=Env.GROUPS_SEARCH_BASE, scope=ldap.SCOPE_SUBTREE, filterstr="(objectClass=posixGroup)", attrlist=['cn', 'memberUid'])
groups = []
print(search)

for result in search:
    uid = result[0]
    result = result[1]
    cn = result['cn'][0].decode("utf-8")
    member_uids = []
    raw_member_uids = result.get('memberUid', [])
    for raw_member_uid in raw_member_uids:
        member_uids.append(raw_member_uid.decode("utf-8"))
    groups.append(Group(cn=cn, member_uids=member_uids))


search = ldap_connection.search_s(base=Env.USER_SEARCH_BASE, scope=ldap.SCOPE_SUBTREE, filterstr=Env.USER_SEARCH_FILTER, attrlist=['cn', 'mail'])

ldap_users = []
for result in search:
    uid = result[0]
    cn = result[1]['cn'][0].decode("utf-8")
    if "mail" not in result[1]:
        continue
    email = result[1]['mail'][0].decode("utf-8")
    ldap_users.append(LDAPUser(uid=uid, cn=cn, email=email))

raw_users = util.retrieve_users(client)
wiki_users = []
for user in raw_users:
    wiki_users.append(WikiUser(id=user["id"], email=user["email"]))



util.assign_user(client, 37, 12)

for group in groups:
    group_id = util.create_group(client, group.cn)
    util.sync_users(client, group.cn, group.member_uids)
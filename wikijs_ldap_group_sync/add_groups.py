from graphqlclient import GraphQLClient
import ldap
import logging
from env import *


import wikijs_utils
import ldap_utils
from classes import *


# ---------------------------
### SETUP
# ---------------------------
# LDAP Connection
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
ldap_connection = None
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

groups = ldap_utils.get_groups_from_ldap(ldap_connection)
ldap_users = ldap_utils.get_users_from_ldap(ldap_connection)

wiki_users = wikijs_utils.get_wikijs_users(client)
wiki_groups = wikijs_utils.get_wikijs_groups(client)

for ldap_user in ldap_users:
    for wiki_user in wiki_users:
        if ldap_user.email == wiki_user.email:
            ldap_user.wiki_user = wiki_user


for group in groups:
    for wiki_group in wiki_groups:
        if group.cn == wiki_group["name"]:
            group.id = wiki_group["id"]

    if group.id is None:
        group.id = wikijs_utils.create_wikijs_group(client, group.cn)

    wikijs_utils.sync_group_membership(client, group.id, group.member_uids, ldap_users)

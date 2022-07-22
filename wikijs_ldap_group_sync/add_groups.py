import logging

import ldap
from graphqlclient import GraphQLClient

import ldap_utils
import wikijs_utils
from env import *

# ---------------------------
### SETUP
# ---------------------------
# LDAP Connection
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
ldap_connection = None
try:
    logging.info("Attempting LDAP connection to", Env.LDAP_URL)
    ldap_connection = ldap.initialize(Env.LDAP_URL)
    ldap_connection.simple_bind_s(Env.ADMIN_BIND_DN, Env.ADMIN_BIND_CRED)
except ldap.SERVER_DOWN as error:
    logging.error(error)
    exit(1)

# WikiJS client
logging.info("Setting up WikiJS Client at", Env.WIKIJS_URL)
wikijs_connection = GraphQLClient(Env.WIKIJS_URL)
wikijs_connection.inject_token(Env.WIKIJS_TOKEN)
# ---------------------------

ldap_groups = ldap_utils.get_ldap_groups(ldap_connection)
ldap_users = ldap_utils.get_ldap_users(ldap_connection)

wiki_users = wikijs_utils.get_wikijs_users(wikijs_connection)
wiki_groups = wikijs_utils.get_wikijs_groups(wikijs_connection)

for ldap_user in ldap_users:
    for wiki_user in wiki_users:
        if ldap_user.email == wiki_user.email:
            ldap_user.wiki_user = wiki_user


for ldap_group in ldap_groups:
    for wiki_group in wiki_groups:
        if ldap_group.cn == wiki_group["name"]:
            ldap_group.id = wiki_group["id"]

    if ldap_group.id is None:
        logging.debug("Attempting to create group", ldap_group.cn)
        ldap_group.id = wikijs_utils.create_wikijs_group(wikijs_connection, ldap_group.cn)

    wikijs_utils.sync_group_membership(wikijs_connection, ldap_group.id, ldap_group.member_uids, ldap_users)

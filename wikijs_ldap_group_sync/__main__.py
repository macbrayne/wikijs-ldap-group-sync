import logging
import ldap

import wikijs_ldap_group_sync.util.env as env

from graphqlclient import GraphQLClient
from wikijs_ldap_group_sync.util import ldap_utils, wikijs_utils
from wikijs_ldap_group_sync.util.env import Env


def main():
    # ---------------------------
    ### SETUP
    # ---------------------------

    # Logging
    logging.basicConfig(level=Env.LOG_LEVEL)
    logger = logging.getLogger("ldap-group-sync:main")

    # Check Configuration
    env.check_config()

    # LDAP Connection
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    ldap_connection = None
    try:
        logger.info("Attempting LDAP connection to %s", Env.LDAP_URL)
        ldap_connection = ldap.initialize(Env.LDAP_URL)
        ldap_connection.simple_bind_s(Env.ADMIN_BIND_DN, Env.ADMIN_BIND_CRED)
    except ldap.SERVER_DOWN as error:
        logger.error(error)
        exit(1)

    # WikiJS client
    logger.info("Setting up WikiJS Client at %s", Env.WIKIJS_URL)
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
            logger.warning("Attempting to create group %s", ldap_group.cn)
            ldap_group.id = wikijs_utils.create_wikijs_group(wikijs_connection, ldap_group.cn)

        wikijs_utils.sync_group_membership(wikijs_connection, ldap_group.id, ldap_group.member_uids, ldap_users)


if __name__ == '__main__':
    main()

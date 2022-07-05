from dotenv import load_dotenv
from graphqlclient import GraphQLClient
import os
import json
import ldap

load_dotenv()


# Retrieving groups from LDAP
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
ldap_connection = ldap.initialize(os.environ.get("LDAP_URL"))

#try:
#    ldap_connection.start_tls_s()
#except ldap.LDAPError as err:
#    print("TLS Error: {0}", format(err))
#    exit()
ldap_connection.simple_bind_s(os.environ.get("ADMIN_BIND_DN"), os.environ.get("ADMIN_BIND_CRED"))

# Adding groups to WikiJS
client = GraphQLClient(os.environ.get("WIKIJS_URL"))
client.inject_token(os.environ.get("WIKIJS_TOKEN"))


def create_group(name: str):
    result = client.execute('''
    {
      groups {
        list { name }
      }
    }
    ''')
    if name in result:
        return
    # result = json.loads(result)
    # result["groups"]["list"]
    #print(type(result))

    # TODO: Implement error checks
    print(client.execute('''
    mutation Group($name: String!) {
      groups {
         create(name: $name) {
          responseResult {
            succeeded,
            errorCode,
            slug,
            message
          },
          group {
            id
            createdAt
            name
          }
        }
      }
    }
    ''', variables={'name': name}))


# create_group("tes4t")
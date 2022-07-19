from dotenv import load_dotenv
from graphqlclient import GraphQLClient
import os
import json
import ldap

load_dotenv()

class Group:
    cn: str
    gid_number: str
    member_uids: list

    def __init__(self, cn: str, gid_number: str, member_uids: list):
        self.cn = cn
        self.gid_number = gid_number
        self.member_uids = member_uids


# Retrieving groups from LDAP
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
ldap_connection = ldap.initialize(os.environ.get("LDAP_URL"))
ldap_connection.simple_bind_s(os.environ.get("ADMIN_BIND_DN"), os.environ.get("ADMIN_BIND_CRED"))
search = ldap_connection.search_s(base=os.environ.get("SEARCH_BASE"), scope=ldap.SCOPE_SUBTREE, filterstr="(objectClass=posixGroup)", attrlist=['cn', 'memberUid', 'gidNumber'])
groups = []

print(search)
for result in search:
    result = result[1]
    cn = result['cn'][0].decode("utf-8")
    gid_number = result['gidNumber'][0].decode("utf-8")
    member_uids = []
    raw_member_uids = result.get('memberUid', [])
    for raw_member_uid in raw_member_uids:
        member_uids.append(raw_member_uid.decode("utf-8"))
    groups.append(Group(cn=cn, gid_number=gid_number, member_uids=member_uids))

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

def sync_users(name: str, users: list):
    # TODO: Sync users
    yield

for group in groups:
    create_group(group.cn)
    sync_users(group.cn, group.member_uids)

# create_group("tes4t")
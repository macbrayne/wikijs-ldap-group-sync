from dotenv import load_dotenv
from graphqlclient import GraphQLClient
import os
import json
import ldap

load_dotenv()

class Group:
    cn: str
    member_uids: list

    def __init__(self, cn: str, member_uids: list):
        self.cn = cn
        self.member_uids = member_uids


# Retrieving groups from LDAP
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
ldap_connection = ldap.initialize(os.environ.get("LDAP_URL"))
ldap_connection.simple_bind_s(os.environ.get("ADMIN_BIND_DN"), os.environ.get("ADMIN_BIND_CRED"))
search = ldap_connection.search_s(base=os.environ.get("GROUPS_SEARCH_BASE"), scope=ldap.SCOPE_SUBTREE, filterstr="(objectClass=posixGroup)", attrlist=['cn', 'memberUid'])
groups = []

print(search)
for result in search:
    result = result[1]
    cn = result['cn'][0].decode("utf-8")
    member_uids = []
    raw_member_uids = result.get('memberUid', [])
    for raw_member_uid in raw_member_uids:
        member_uids.append(raw_member_uid.decode("utf-8"))
    groups.append(Group(cn=cn, member_uids=member_uids))

search = ldap_connection.search_s(base=os.environ.get("USER_SEARCH_BASE"), scope=ldap.SCOPE_SUBTREE, filterstr="(objectClass=organizationalPerson)", attrlist=['uid', 'mail'])

print(search)

# Adding groups to WikiJS
client = GraphQLClient(os.environ.get("WIKIJS_URL"))
client.inject_token(os.environ.get("WIKIJS_TOKEN"))


def create_group(name: str):
    _result = client.execute('''
    {
      groups {
        list { name }
      }
    }
    ''')
    if name in _result:
        return
    # result = json.loads(result)
    # result["groups"]["list"]
    #print(type(result))

    # TODO: Implement error checks
    _result = client.execute('''
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
    ''', variables={'name': name})
    print(_result)
    return _result["data"]["groups"]["create"]["group"]["id"]

def sync_users(name: str, users: list):
    # TODO: Sync users
    yield

def assign_user(group_id: int, user_id: int):
    _result = client.execute('''
        mutation AssignUser($groupId: Int!, $userId: Int!) {
            groups {
                assignUser(groupId: $groupId, userId: $userId) {
                responseResult {
                succeeded,
                errorCode,
                slug,
                message
              }
            }
          }
    }''', variables={'groupId': group_id, 'userId': user_id})
    print(_result)

assign_user(37, 12)

for group in groups:
    group_id = create_group(group.cn)
    sync_users(group.cn, group.member_uids)


# create_group("tes4t")
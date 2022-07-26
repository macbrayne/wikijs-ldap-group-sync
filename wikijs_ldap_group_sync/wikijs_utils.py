from graphqlclient import GraphQLClient

import json
import logging

from wikijs_ldap_group_sync.classes import WikiUser


def create_wikijs_group(client: GraphQLClient, name: str):
    _result = client.execute('''
    {
      groups {
        list { name }
      }
    }
    ''')
    if name in _result:
        return

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
    return _result["data"]["groups"]["create"]["group"]["id"]

def sync_group_membership(client: GraphQLClient, group_id: int, users: list, ldap_users: list):
    logging.info(f"Attempting to assign group id {group_id} to the following users: {users}")
    for user in users:
        for ldap_user in ldap_users:
            if user == ldap_user.cn and ldap_user.wiki_user is not None:
                assign_wikijs_user_to_group(client, group_id, ldap_user.wiki_user.id)


def assign_wikijs_user_to_group(client: GraphQLClient, group_id: int, user_id: int):
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
    logging.debug(_result)

def get_wikijs_users(client: GraphQLClient):
    _result = client.execute('''
    {
        users {
            list {
                id
                email
            }
        }
    }''')
    _result = json.loads(_result)

    wiki_users = []
    for user in _result["data"]["users"]["list"]:
        wiki_users.append(WikiUser(id=user["id"], email=user["email"]))
    return wiki_users


def get_wikijs_groups(client: GraphQLClient):
    _result = client.execute('''
    {
        groups {
            list {
                id
                name
            }
        }
    }
    ''')
    _result = json.loads(_result)
    return _result["data"]["groups"]["list"]
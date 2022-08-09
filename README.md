# WikiJS LDAP Group Sync
WikiJS only [plans on integrating](https://js.wiki/feedback/p/group-mapping) syncing
groups from authentication providers to WikiJS in its 3.0 release making this custom Python script necessary.

## Architecture

This script relies on the WikiJS GraphQL server to work which unfortunately doesn't provide ways to list users
together with their ids and group memberships.
That's why this script has to send as many requests as there are users times the amount of groups.

Roughly speaking the script does the following:

1. Connect to LDAP
2. Retrieve user information, group names and group membership from LDAP
3. Retrieve user information (id, email) and group information (id, name) from WikiJS
4. Add group to WikiJS if group doesn't already exist
5. Compare data and map group ownership to users
6. Tell WikiJS to assign groups to users

Because the script has no way of knowing which user is assigned to which group without making individual requests (or batching) to the WikiJS GraphQL API the majority of runtime is going to be spent on the last step.

## Installing

### Docker

```bash
docker build -t wikijs-ldap-group-sync .
docker run wikijs-ldap-group-sync
```

### Poetry

After cloning the project and installing poetry simply execute `poetry run sync` to run the script.

## Configuration

By default, WikiJS LDAP Group Sync uses environment variables however you can also provide a `.env` file in the main execution directory.

| Environment Variable | Example                                                                                       | Meaning                                          |
|----------------------|-----------------------------------------------------------------------------------------------|--------------------------------------------------|
| WIKIJS_URL           | "https://wiki.example.com/graphql"                                                            | URL of the WikiJS GraphQL endpoint               |
| WIKIJS_TOKEN         | "Bearer rVcMvDUsAAv4abPxcIEg"                                                                 | Used for authenticating to GraphQL [[1]](#note1) |
| LDAP_URL             | "ldaps://ldap.example.com:636"                                                                | URL of the LDAP Server [[2]](#note2)             |
| ADMIN_BIND_DN        | "UID=admin,CN=Users,DC=example,DC=com"                                                        | DN used for authenticating to LDAP               |
| ADMIN_BIND_CRED      | "supersecretpassword"                                                                         | Password used for authenticating to LDAP         |
| GROUPS_SEARCH_BASE   | "CN=Groups,DC=example,DC=com"                                                                 | LDAP base groups will be searched for under      |
| GROUPS_SEARCH_FILTER | "(objectClass=posixGroup)"                                                                    | LDAP group search filter                         |
| USER_SEARCH_BASE     | "CN=Users,DC=example,DC=com"                                                                  | LDAP base users will be searched for under       |
| USER_SEARCH_FILTER   | "(&(objectClass=organizationalPerson)(memberof=CN=Domain Users,CN=Groups,DC=example,DC=com))" | LDAP user search filter                          |

<a name="note1">1</a>: Authentication tokens can be generated in the WikiJS Admin Panel under "API Access" 

<a name="note2">2</a>: Note that there is currently no support for providing a certificate
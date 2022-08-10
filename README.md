# WikiJS LDAP Group Sync

WikiJS currently lacks the ability to sync groups from authentication providers to WikiJS.
They plan to provide a feature like that [in its 3.0 release](https://js.wiki/feedback/p/group-mapping), until then this Python script can help.

## Architecture

This script relies on the WikiJS GraphQL server to get group membership information which unfortunately doesn't provide ways to list users
together with their ids and group memberships.
Due to that this script has to send as many requests as there are users times the amount of groups.

Roughly speaking the script does the following:

1. Connect to LDAP
2. Retrieve user information, group names and group membership from LDAP
3. Retrieve user information (id, email) and group information (id, name) from WikiJS
4. Add group to WikiJS if group doesn't already exist
5. Compare data and map group ownership to users
6. Tell WikiJS to assign groups to users

Because we have no way of knowing which user is assigned to which group without making individual requests to the WikiJS GraphQL API (or batching them) the majority of runtime is going to be spent on the last step.

## Installing

### Docker

Pull from GitHub Container registry:
```bash
docker pull ghcr.io/macbrayne/wikijs-ldap-group-sync:main
```
Pull from Docker Hub:
```bash
docker pull macbrayne/wikijs-ldap-group-sync
 ```

Alternatively you can build it yourself:
```bash
docker build -t macbrayne/wikijs-ldap-group-sync 'https://github.com/macbrayne/wikijs-ldap-group-sync.git#main'
docker run macbrayne/wikijs-ldap-group-sync
```

### Poetry

Depending on your distribution you might have to install additional dependencies before being able to use the script.
In case of Debian based distributions these dependencies might be:
```bash
apt-get install --no-install-recommends build-essential libsasl2-dev libldap2-dev
```
Then, after installing poetry simply execute `poetry run sync` to run the script.

## Configuration

By default, WikiJS LDAP Group Sync uses environment variables however you can also provide a `.env` file in the main execution directory.

| Environment Variable | Example                                                                                       | Meaning                                     |
|----------------------|-----------------------------------------------------------------------------------------------|---------------------------------------------|
| WIKIJS_URL           | "https://wiki.example.com/graphql"                                                            | URL of the WikiJS GraphQL endpoint          |
| WIKIJS_TOKEN         | "Bearer rVcMvDUsAAv4abPxcIEg"                                                                 | Used for authenticating to GraphQL [^1]     |
| LDAP_URL             | "ldaps://ldap.example.com:636"                                                                | URL of the LDAP Server [^2]                 |
| ADMIN_BIND_DN        | "UID=admin,CN=Users,DC=example,DC=com"                                                        | DN used for authenticating to LDAP          |
| ADMIN_BIND_CRED      | "supersecretpassword"                                                                         | Password used for authenticating to LDAP    |
| GROUPS_SEARCH_BASE   | "CN=Groups,DC=example,DC=com"                                                                 | LDAP base groups will be searched for under |
| GROUPS_SEARCH_FILTER | "(objectClass=posixGroup)"                                                                    | LDAP group search filter                    |
| USER_SEARCH_BASE     | "CN=Users,DC=example,DC=com"                                                                  | LDAP base users will be searched for under  |
| USER_SEARCH_FILTER   | "(&(objectClass=organizationalPerson)(memberof=CN=Domain Users,CN=Groups,DC=example,DC=com))" | LDAP user search filter                     |
 | (optional) LOG_LEVEL | (default) "INFO"                                                                              | Log level to be used [^3]                   |

[^1]: Authentication tokens can be generated in the WikiJS Admin Panel under "API Access" 

[^2]: Note that there is currently no way of providing a certificate

[^3]: Server down at "ERROR", group creation at "WARNING", general program flow at "INFO", the results of group assignments at "DEBUG"
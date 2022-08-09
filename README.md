# WikiJS LDAP Group Sync
As WikiJS only [plans on integrating](https://js.wiki/feedback/p/group-mapping) syncing
groups from authentication providers to WikiJS in its 3.0 release.

## Architecture

This script relies on the WikiJS GraphQL server to work which unfortunately doesn't provide ways to list users
together with their ids and group memberships.
That's why im steps this script has to send as many requests as there are users times the amount of groups!

Roughly speaking the script does the following:

1. Connect to LDAP
2. Retrieve user information, group names and group membership from LDAP
3. Retrieve user information (id, email) and group information (id, name) from WikiJS
4. Add group to WikiJS if group doesn't already exist
5. Compare data and map group ownership to users
6. Tell WikiJS to assign groups to users

Because the script has no way of knowing which user is assigned to which group without making individual requests (or batching) the WikiJS GraphQL API the majority of runtime is going to be spent on the last step.
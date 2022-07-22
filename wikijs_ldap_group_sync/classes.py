class Group:
    uid: str
    cn: str
    member_uids: list

    def __init__(self, cn: str, member_uids: list):
        self.cn = cn
        self.member_uids = member_uids

class User:
    email: str
    def __init__(self, email: str):
        self.email = email

class LDAPUser(User):
    uid: str
    cn: str
    def __init__(self, email: str, cn: str, uid: str):
        super().__init__(email)
        self.uid = uid
        self.cn = cn

class WikiUser(User):
    id: int
    def __init__(self, email: str, id: int):
        super().__init__(email)
        self.id = id
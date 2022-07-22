from __future__ import annotations

class Group:
    uid: str
    cn: str
    member_uids: list
    id: int

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
    wiki_user: WikiUser = None
    def __init__(self, email: str, cn: str, uid: str):
        super().__init__(email)
        self.uid = uid
        self.cn = cn

    def __str__(self) -> str:
        return f"LDAPUser:{{ uid: {self.uid}, cn: {self.cn}, email: {self.email}, wiki_user: {self.wiki_user}}}"


class WikiUser(User):
    id: int
    def __init__(self, email: str, id: int):
        super().__init__(email)
        self.id = id
    def __str__(self) -> str:
        return f"WikiUser:{{ id: {self.id}, email: {self.email}}}"
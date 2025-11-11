class Account:
    _accounts = []

    def __init__(self, name):
        self.id = len(Account._accounts) + 1
        self.name = name

    def save(self):
        Account._accounts.append(self)

    @classmethod
    def all(cls):
        return cls._accounts

    def serialize(self):
        return {"id": self.id, "name": self.name}

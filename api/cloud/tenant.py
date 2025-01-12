from hashlib import sha256

class Tenant:
    def __init__(self, id : str, name : str):
        self.id = id
        self.name = name

    def __hash__(self)->int:
        return hash(self.id) + hash(self.name)
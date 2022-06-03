class Special:
    s: int
    p: int
    e: int
    c: int
    i: int
    a: int
    l: int

    def __init__(self, special: dict):
        self.s = special.get('s', 1)
        self.p = special.get('p', 1)
        self.e = special.get('e', 1)
        self.c = special.get('c', 1)
        self.i = special.get('i', 1)
        self.a = special.get('a', 1)
        self.l = special.get('l', 1)

    def to_dict(self) -> dict:
        return {
            's': self.s,
            'p': self.p,
            'e': self.e,
            'c': self.c,
            'i': self.i,
            'a': self.a,
            'l': self.l,
        }

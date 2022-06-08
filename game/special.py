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

    def stealth(self) -> int:
        return int(25 + self.a + int(self.l / 3))

    def detection(self) -> int:
        return int(30 + self.p + int(self.l / 2))

    def reaction(self) -> int:
        return int(2 * self.p + 2 * self.a)

    def max_weight(self) -> int:
        return 30 + int(pow(30, ((self.s - 1) / 5)))

    def max_action_points(self) -> int:
        return int(self.a / 3)

    def max_hp(self) -> int:
        return int(pow(100, (1 + (self.e / 30))) / 2 + self.s)

    def heal_points(self) -> int:
        return int(self.e / 3)

    def max_stamina(self) -> int:
        return int(self.e * 20)

    def stamina_points(self) -> int:
        return int(self.e * 2)

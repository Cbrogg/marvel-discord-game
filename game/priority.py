class Priority:
    id: int
    value: int

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def __iadd__(self, other):
        return Priority(self.id, self.value+other)

    def __isub__(self, other):
        return Priority(self.id, self.value - other)

    def __cmp__(self, other):
        return self.value - other.value

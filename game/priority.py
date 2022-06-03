class Priority:
    id: int
    value: int

    def __init__(self, id, value=0):
        self.id = id
        self.value = value

    def __iadd__(self, other):
        return Priority(self.id, self.value + other)

    def __isub__(self, other):
        return Priority(self.id, self.value - other)

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return f"id: {self.id}; value: {self.value}"
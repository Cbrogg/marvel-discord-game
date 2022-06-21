class Priority:
    p_id: int
    value: int

    def __init__(self, p_id, value=0):
        self.p_id = p_id
        self.value = value

    def __add__(self, other):
        return Priority(self.p_id, self.value + other)

    def __sub__(self, other):
        return Priority(self.p_id, self.value - other)

    def __iadd__(self, other):
        return Priority(self.p_id, self.value + other)

    def __isub__(self, other):
        return Priority(self.p_id, self.value - other)

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value and self.p_id == other.p_id

    def __str__(self):
        return f"id: {self.p_id}; value: {self.value}"

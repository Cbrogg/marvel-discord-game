from enum import Enum


class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'


class EnemyHealthStatus(Enum):
    HEALTH = 'здоров'
    DAM20 = 'замедлен'
    DAM40 = 'получил заметные повреждения'
    DAM60 = 'получил обширные повреждения'
    DAM80 = 'на последнем издыхании'
    DEAD = 'мертв'


class EnemyCombatStatus(Enum):
    IDLE = 'idle'
    COMBAT = 'combat'
    MILLE = 'mille_combat'
    RANGE = 'range_combat'
    MAGIC = 'magic_combat'
    CHASE = 'chase'


class PlayerHealthStatus(Enum):
    HEALTH = 'здоров'
    DAM10 = 'легкое ранение'
    DAM20 = 'среднее ранение'
    DAM60 = 'тяжелое ранение'
    DAM80 = 'критическое состояние'
    DEAD = 'без сознания'




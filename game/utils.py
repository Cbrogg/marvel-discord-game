from .consts import flags


def parse_message(message: str) -> dict:
    d = {}
    for flag in flags.keys():
        p = message.find(flag) >= 0
        if p >= 0:
            d[flag] = p
    return d


def is_message_valid(content: str) -> bool:
    for key in flags.keys():
        content = content.replace(key, "", -1)
    content = content.replace("  ", " ", -1)
    if len(content) < 30:
        return False
    else:
        return True


def special_mapper(attr: int) -> str:
    if attr <= 1:
        return "отвратительный"
    elif 1 < attr <= 3:
        return "низкий"
    elif attr == 4:
        return "ниже среднего"
    elif attr == 5:
        return "средний"
    elif attr == 6:
        return "выше среднего"
    elif 6 < attr <= 8:
        return "высокий"
    else:
        return "исключительный"
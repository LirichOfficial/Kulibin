import random


def get_word(topic):
    list = ["Гарри Поттер", "Гермиона Грейнджер", "Рон Уизли", "Драко Малфой", "Невилл Долгопупс"]
    return list[random.randint(0, len(list) - 1)]


def get_answer(word, quest):
    z = random.randint(0, 1)
    if z == 1:
        return True
    else:
        return False


def is_equal(word1, word2):
    if word1 == word2:
        return True
    else:
        return False

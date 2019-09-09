class Message:
    WINMESSAGE = (0, "Вы победили!")            # Сообщение при победе
    LOSEMESSAGE = (1, "Вы проиграли!")          # ...при поражении
    DRAWMESSAGE = (2, "Ничья")                  # ...при ничьей
    STEPMESSAGE = (3, "Вы сделали свой ход")    # ...на каждом шаге
    COLLISIONMESSAGE = (4, "Вы поставили в занятую клетку")                 # ...при установке в занятую клетку
    OTHERCOLLIDEDMESSAGE = (5, "Кто-то поставил фишку в занятую клетку")    # ...если кто-то другой поставил фишку в занятую клетку


class Map:
    def __init__(self, size: tuple, numerate: bool = False):
        self.size = size
        self.len = size[0] * size[1]
        self.__map = list(range(self.len)) if numerate else [-1 for _ in range(self.len)]

    def __repr__(self):
        return f"<Map{self.size}>"

    def __str__(self):
        return '\n'.join([(" ".join([f"{self.get(position=(x, y)):3}" for y in range(self.size[1])])) for x in range(self.size[0])])

    @property
    def state(self):
        return tuple(self.__map)

    def set(self, value: int = -1, number: int = None, position: tuple = None):
        """ Установить значение клетке, если возможно (если занято, возвращает False) """
        if number is None and position is not None:
            number = self.convert(position)
        if self.get(number) == -1 and value >= 0:
            self.__map[number] = value
            return True
        return False

    def get(self, number: int = None, position: tuple = None):
        """ Получить значение клетки """
        if number is None and position is not None:
            number = self.convert(position)
        return self.__map[number]

    def convert(self, position: tuple):
        """ Перевод из формата (x, y) в номер позиции """
        return position[0] * self.size[1] + position[1]

    def get_row(self, number: int = None, position: tuple = None, row: int = None):
        """ Получить ряд """
        if row is None:
            if number is not None:
                row = number // self.size[1]
            elif position is not None:
                row = position[0]
        return self.__map[self.size[1] * row:self.size[1] * (row + 1)]

    def get_column(self, number: int = None, position: tuple = None, column: int = None):
        """ Получить колонку """
        if column is None:
            if number is not None:
                column = number % self.size[1]
            elif position is not None:
                column = position[1]
        return self.__map[column::self.size[1]]

    def get_diag(self, number: int = None, position: tuple = None, counter=False):
        """ Получить диагонально расположенные элементы"""
        step = 1 if counter else -1

        if number is not None:
            x = number // self.size[1]
            y = number % self.size[1]
        elif position is not None:
            x, y = position

        start = 0
        while x >= 0 and self.size[1] > y >= 0:
            # Найти границу поля, находящуюся на одной диагонали с полученной клеткой
            start = (x, y)
            x -= 1
            y += step

        # Какая дигональ нужна:
        if counter:
            # Справа налево "/"
            return self.__map[self.convert(start):self.convert(start) + ((start[1] * self.size[1]) or 1):self.size[1] - 1]
        else:
            # Слева направо "\"
            return self.__map[self.convert(start)::self.size[1] + 1]

    def is_filled(self):
        return -1 not in self.__map


class Game:
    WINREWARD = 10              # Награда при победе
    LOSEREWARD = -10            # ...при поражении
    DRAWREWARD = 0              # ...при ничьей
    STEPREWARD = -1             # ...на каждом шаге
    COLLISIONREWARD = -100      # ...при установке в занятую клетку
    OTHERCOLLIDEDREWARD = 0     # ...при установке кем-то другим в занятую клетку

    def __init__(self, players=2, size=(3, 3), in_a_row=3):
        """ Создание новой игры """
        # Базовые правила:
        # количество игроков не может быть отрицательным, равным нулю или одному
        assert players > 1
        # игровое поле двумерное и количество клеток больше 0
        assert len(size) == 2 and size[0] * size[1] > 0
        # для победы нельзя иметь одну фишку, ноль или отрицательное число
        assert in_a_row > 1

        self.players = players      # Количество игроков
        self.size = size            # Размер поля (h, w)
        self.in_a_row = in_a_row    # Количество фишек вряд для победы

        self.game_map = Map(self.size)  # Игровое поле
        self.current_player = 0         # Какой игрок ходит
        self.done = False               # Была ли закончена партия
        self.winner = -1                # Номер победившего игрока
                                        # (-2 - кто-то поставил в занятую клетку, -1 - ничья или партия продолжается)

    def reset(self):
        """ Сброс игры, начать новую партию """
        self.game_map = Map(self.size)
        self.current_player = 0
        self.done = False
        self.winner = -1
        return self.game_map

    def action(self, action):
        """ Совершить действие (номер действия - позиция на поле) """
        if self.done:
            # Если партия уже закончена
            if self.winner == -1:
                # Ничья
                reward = self.DRAWREWARD
                msg = Message.DRAWMESSAGE
            elif self.winner == -2:
                # Кто-то поставил фишку в занятую клетку
                reward = self.OTHERCOLLIDEDREWARD
                msg = Message.OTHERCOLLIDEDMESSAGE
            elif self.current_player != self.winner:
                # Проигравший
                reward = self.LOSEREWARD
                msg = Message.LOSEMESSAGE
            elif self.current_player == self.winner:
                # Победитель
                reward = self.WINREWARD
                msg = Message.WINMESSAGE

            self.next_player()
            return self.game_map, reward, True, msg

        if not self.game_map.set(self.current_player, action):
            # Если игрок пытается поставить фишку на занятую клетку
            self.done = True
            self.winner = -2
            self.next_player()
            return self.game_map, self.COLLISIONREWARD, True, Message.COLLISIONMESSAGE

        if self.find_in_a_row(action):
            # Найден победитель
            self.done = True
            self.winner = self.current_player
            self.next_player()
            return self.game_map, self.WINREWARD, True, Message.WINMESSAGE

        if self.game_map.is_filled():
            # Поле было заполнено
            self.done = True
            self.winner = -1
            self.next_player()
            return self.game_map, self.DRAWREWARD, True, Message.DRAWMESSAGE

        # Партия продолжается
        self.next_player()
        return self.game_map, self.STEPREWARD, False, Message.STEPMESSAGE

    def find_in_a_row(self, last_action):
        """ Определение победителя: стоят ли фишки в ряд (в количестве in_a_row) """
        def same(lst: list, in_a_row):
            if len(lst) >= in_a_row:
                for i in range(len(lst) - in_a_row + 1):
                    if len(set(lst[i:i + in_a_row])) == 1 and lst[i] != -1:
                        return True
            return False
        # В строке
        row = self.game_map.get_row(last_action)
        if same(row, self.in_a_row):
            return True
        # В колонке
        column = self.game_map.get_column(last_action)
        if same(column, self.in_a_row):
            return True
        # Первая диагональ
        diagonal = self.game_map.get_diag(last_action)
        if same(diagonal, self.in_a_row):
            return True
        # Вторая диагональ
        diagonal = self.game_map.get_diag(last_action, counter=True)
        if same(diagonal, self.in_a_row):
            return True

        # Не найдено победителя
        return False

    def next_player(self):
        # Перейти к следующему игроку
        self.current_player += 1
        if self.current_player >= self.players:
            self.current_player = 0


if __name__ == "__main__":
    env = Game(2, (3, 3))
    print(env.game_map)
    print(env.action(0))
    print(env.action(1))
    print(env.action(2))
    print(env.action(3))
    print(env.action(4))
    print(env.action(8))
    print(env.action(7))
    print(env.action(6))
    print(env.action(5))
    print(env.action(4))
    print(env.game_map)

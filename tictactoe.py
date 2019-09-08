import numpy as np


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
        print(x, y)
        start = 0
        while x >= 0 and self.size[1] > y >= 0:
            # Найти границу поля, находящуюся на одной диагонали с полученной клеткой
            start = (x, y)
            x -= 1
            y += step
        print(start, step)
        if counter:
            return self.__map[self.convert(start):self.convert(start) + ((start[1] * self.size[1]) or 1):self.size[1] - 1]
        else:
            return self.__map[self.convert(start)::self.size[1] + 1]

    def is_filled(self):
        return len(set(self.__map)) == 1


class Game:
    WINREWARD = 10              # Награда при победе
    LOSEREWARD = -10            # ...при поражении
    STEPREWARD = -1             # ...на каждом шаге
    COLLISIONREWARD = -100      # ...при установке в занятую клетку

    def __init__(self, players=2, size=(3, 3), in_a_row=3):
        self.players = players
        self.size = size
        self.in_a_row = in_a_row

        self.game_map = Map(self.size)
        self.current_player = 0
        self.done = False
        self.winner = -1
        # 1 + len (size * size) + len * (len - 1) + len * (len - 1) * (len - 2)

    def reset(self):
        self.game_map = Map(self.size)
        self.current_player = 0
        self.done = False
        self.winner = -1

    def action(self, action):
        if self.done:
            # Если партия уже закончена
            if self.winner == -1:
                # Кто-то поставил фишку в занятую клетку
                reward = self.STEPREWARD
            elif self.current_player != self.winner:
                # Проигравший
                reward = self.LOSEREWARD
            elif self.current_player == self.winner:
                # Победитель
                reward = self.WINREWARD

            self.next_player()
            return self.game_map, reward, True, None

        if not self.game_map.set(self.current_player, action):
            # Если игрок пытается поставить фишку на занятую клетку
            self.done = True
            self.next_player()
            return self.game_map, self.COLLISIONREWARD, True, None

        if self.find_in_a_row(action):
            # Найден победитель
            self.done = True
            self.winner = self.current_player
            self.next_player()
            return self.game_map, self.WINREWARD, True, None

        self.next_player()
        return self.game_map, self.STEPREWARD, False, None

    def find_in_a_row(self, last_action):
        def same(lst: list, in_a_row=3):
            if len(lst) >= in_a_row:
                for i in range(len(lst) - in_a_row + 1):
                    print(set(lst[i:i + in_a_row]), lst[i:i + in_a_row])
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
    env = Game(2, (3, 4))
    print(env.game_map)
    print(env.action(0))
    print(env.action(5))
    print(env.action(1))
    print(env.action(6))
    print(env.action(2))
    print(env.action(4))
    print(env.game_map)

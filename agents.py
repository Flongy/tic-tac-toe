import numpy as np
import pickle


class Agent:
    """ Базовые класс для взаимодействия с игрой """
    def __init__(self, size: tuple = (3, 3), *args):
        self.size = size
        self.len = size[0] * size[1]

    def action(self, state: tuple):
        """ Выполнить действие при данном состоянии """
        pass

    def fit(self, state: tuple, new_state: tuple, action: int, reward: float):
        """ Корректировать внутренние значения (например, q-таблицу) """
        pass

    def save(self, filename: str):
        """ Сохранить внутренние значения на диск """
        pass

    @staticmethod
    def load(filename: str, size: tuple = (3, 3), *args):
        """ Загрузить внутренние значения """
        return Agent(size)

    def decay(self, episode: int):
        """ Преобразования в конце эпизода """
        pass


class QAgent(Agent):
    """ Компьютер, реализующий алгоритм Q-Learning """
    def __init__(self, size=(3, 3), use_epsilon: bool = True, episodes: int = 10_000):
        super().__init__(size)

        self.LEARNING_RATE = 0.1
        self.DISCOUNT = 0.95

        self.use_epsilon = use_epsilon
        if use_epsilon:
            # epsilon - вероятность выбора случайного действия
            self.epsilon = 0.5
            self.START_EPSILON_DECAYING = episodes // 5
            self.END_EPSILON_DECAYING = episodes // 2
            self.epsilon_decay = self.epsilon / (self.END_EPSILON_DECAYING - self.START_EPSILON_DECAYING)

        self.q_table = {}

    def action(self, state: tuple):
        """ Выбор действия по Q-таблице """
        if not self.use_epsilon or np.random.random() >= self.epsilon:
            return np.argmax(self.get(state))
        return self.random_action(state)

    def random_action(self, state: tuple):
        """ Случайное действие """
        ch = np.where(np.array(state) == -1)[0]
        if ch.any():
            return np.random.choice(ch)
        else:
            return 0

    def get(self, state: tuple):
        """ Получить строчку Q-таблицы для данного состояния игры """
        if state not in self.q_table:
            self.q_table[state] = np.random.random(self.len).astype(np.float32)
            self.q_table[state][np.array(state) > -1] = np.finfo(np.float32).min
        return self.q_table[state]

    def fit(self, state, new_state, action, reward):
        """ Преобразовать Q-таблицу """
        max_future_q = max(self.get(new_state))
        current_q = self.get(state)[action]

        new_q = (1 - self.LEARNING_RATE) * current_q + self.LEARNING_RATE * (reward + self.DISCOUNT * max_future_q)
        self.q_table[state][action] = new_q

    def save(self, filename):
        """ Сохранить Q-таблицу на диск """
        with open(filename, "wb") as f:
            pickle.dump(self.q_table, f)

    @staticmethod
    def load(filename, size=(3, 3), use_epsilon=True, episodes: int = 10_000):
        """ Загрузить Q-таблицу с диска """
        qagent = QAgent(size, use_epsilon, episodes)
        with open(filename, 'rb') as f:
            qagent.q_table = pickle.load(f)
        return qagent

    def decay(self, episode):
        """ Изменить epsilon """
        if self.use_epsilon:
            if self.END_EPSILON_DECAYING >= episode >= self.START_EPSILON_DECAYING:
                self.epsilon -= self.epsilon_decay
        else:
            pass


class RAgent(Agent):
    """ Компьютер, выбирающий случайные действия """
    def __init__(self, size: tuple = (3, 3), *args):
        super().__init__(size, *args)

    def action(self, state: tuple, **kwargs):
        """ Случайное действие """
        ch = np.where(np.array(state) == -1)[0]
        if ch.any():
            return np.random.choice(ch)
        else:
            return 0


class UIAgent(Agent):
    """ Взаимодействие с пользователем """
    def __init__(self, size: tuple = (3, 3), *args):
        super().__init__(size, *args)

    def action(self, state: tuple):
        """ Пользовательский ввод """
        self.show_map(state)
        return int(input("Выберите, куда поставить фишку: "))

    def show_map(self, state: tuple):
        """ Показать текущее """
        print("\n".join([" ".join(f"{y:3}" for y in state[x * self.size[1]:(x + 1) * self.size[1]]) for x in range(self.size[0])]))

    def decay(self, episode: int):
        """ Вызывается в конце эпизода """
        print("-"*15)
        print("Партия окончена")
        print("-"*15)

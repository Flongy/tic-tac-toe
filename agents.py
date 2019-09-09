import numpy as np
import pickle


class Agent:
    """ Базовые класс для взаимодействия с игрой """
    def __init__(self, size: tuple = (3, 3), *args):
        self.size = size
        self.len = size[0] * size[1]

    def action(self, state: tuple):
        pass

    def fit(self, state: tuple, new_state: tuple, action: int, reward: float):
        pass

    def dump(self, filename: str):
        pass

    @staticmethod
    def load(filename: str, size: tuple = (3, 3), *args):
        return Agent(size)

    def decay(self, episode: int):
        pass


class QAgent(Agent):
    """ Компьютер, реализующий алгоритм Q-Learning """
    def __init__(self, size=(3, 3), use_epsilon: bool = True):
        super().__init__(size)

        self.LEARNING_RATE = 0.1
        self.DISCOUNT = 0.95

        self.use_epsilon = use_epsilon
        self.epsilon = 0.5
        self.START_EPSILON_DECAYING = 5_000
        self.END_EPSILON_DECAYING = EPISODES // 2
        self.epsilon_decay = self.epsilon / (self.END_EPSILON_DECAYING - self.START_EPSILON_DECAYING)

        self.q_table = {}

    def action(self, state: tuple):
        if not self.use_epsilon or np.random.random() >= self.epsilon:
            return np.argmax(self.get(state))
        return np.random.randint(0, self.len)

    def get(self, state: tuple):
        if state not in self.q_table:
            self.q_table[state] = np.random.random(self.len)
        return self.q_table[state]

    def fit(self, state, new_state, action, reward):
        max_future_q = max(self.get(new_state))
        current_q = self.get(state)[action]

        new_q = (1 - self.LEARNING_RATE) * current_q + self.LEARNING_RATE * (reward + self.DISCOUNT * max_future_q)
        self.q_table[state][action] = new_q

    def dump(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self.q_table, f)

    @staticmethod
    def load(filename, size=(3, 3), use_epsilon=True):
        qagent = QAgent(size, use_epsilon)
        with open(filename, 'rb') as f:
            qagent.q_table = pickle.load(f)
        return qagent

    def decay(self, episode):
        if self.END_EPSILON_DECAYING >= episode >= self.START_EPSILON_DECAYING:
            self.epsilon -= self.epsilon_decay


class RAgent(Agent):
    """ Компьютер, выбирающий случайные действия """
    def __init__(self, size: tuple = (3, 3), *args):
        super().__init__(size, *args)

    def action(self, state: tuple, **kwargs):
        ch = np.where(np.array(state) == -1)[0]
        if ch.any():
            return np.random.choice(ch)
        else:
            return np.random.randint(self.len)

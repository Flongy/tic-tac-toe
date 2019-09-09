import pickle
import time
import numpy as np
from tictactoe import Game, Message


EPISODES = 5_000_000


class QAgent:
    LEARNING_RATE = 0.1
    DISCOUNT = 0.95

    def __init__(self, size=(3, 3)):
        self.size = size
        self.len = size[0] * size[1]
        self.q_table = {}

    def action(self, state: tuple):
        return np.argmax(self.get(state))

    def get(self, state: tuple):
        if state not in self.q_table:
            self.q_table[state] = np.random.random(self.len)
        return self.q_table[state]

    def fit(self, state, new_state, action, reward):
        max_future_q = max(self.get(new_state))
        current_q = self.get(state)[action]

        new_q = (1 - self.LEARNING_RATE) * current_q + self.LEARNING_RATE * (reward + self.DISCOUNT * max_future_q)
        self.q_table[state][action] = new_q


if __name__ == "__main__":
    players = 3
    size = (8, 8)
    in_a_row = 4
    env = Game(players, size, in_a_row)

    wins = [0] * players
    loses = [0] * players
    draws = 0

    qagents = [QAgent(size) for _ in range(players)]
    for i in range(EPISODES):
        done = [False] * players
        msgs = [None] * players
        state = env.reset().state
        while not min(done):
            for j, ag in enumerate(qagents):
                if not done[j]:
                    action = ag.action(state)
                    new_map, reward, done[j], msgs[j] = env.action(action)
                    new_state = new_map.state
                    ag.fit(state, new_state, action, reward)
                    state = new_state
        else:
            if Message.DRAWMESSAGE in msgs:
                draws += 1
            else:
                for j, m in enumerate(msgs):
                    if m == Message.WINMESSAGE:
                        wins[j] += 1
                    elif m == Message.LOSEMESSAGE:
                        loses[j] += 1
            if i % 10_000 == 0:
                print(f"Игра №{i}")
                for j in range(players):
                    print(f"\tИгрок {j}. Побед: {wins[j]}. Поражений: {loses[j]}")
                print(f"\tНичьей: {draws}")

            if i % 20_000 == 0 and Message.WINMESSAGE in msgs:
                print(env.game_map)

            if i % 50_000 == 0 and i:
                for j in range(players):
                    with open(f"dumps/Player{j}-{size[0]}x{size[1]}-{players}-{in_a_row}-{i}eps-{int(time.time())}.pickle", "wb") as f:
                        pickle.dump(qagents[j].q_table, f)

from tictactoe import Game, Message
from agents import QAgent, RAgent


def train(players, size, in_a_row, agents, episodes):
    env = Game(players, size, in_a_row)

    wins = [0] * players
    loses = [0] * players
    draws = 0

    for episode in range(1, episodes + 1):
        done = [False] * players
        msgs = [None] * players
        state = env.reset().state
        while not min(done):
            for j, ag in enumerate(agents):
                if not done[j]:
                    action = ag.action(state)
                    new_map, reward, done[j], msgs[j] = env.action(action)
                    new_state = new_map.state
                    ag.fit(state, new_state, action, reward)
                    state = new_state
        else:
            for ag in agents:
                ag.decay(episode)

            if Message.DRAWMESSAGE in msgs:
                draws += 1
            else:
                for j, m in enumerate(msgs):
                    if m == Message.WINMESSAGE:
                        wins[j] += 1
                    elif m == Message.LOSEMESSAGE:
                        loses[j] += 1

            if episode % 10_000 == 0:
                print(f"Игра №{episode}")
                for j in range(players):
                    print(f"\tИгрок {j}. Побед: {wins[j]}. Поражений: {loses[j]}")
                print(f"\tНичьих: {draws}")

            if episode % 20_000 == 0 and (Message.WINMESSAGE in msgs or Message.DRAWMESSAGE in msgs):
                print(env.game_map)

            if episode % 100_000 == 0 and episode:
                for j, ag in enumerate(agents):
                    # ag.dump(f"dumps/Player{j}-{players}-{size[0]}x{size[1]}-{in_a_row}-{episode}eps-{int(time.time())}.pickle")
                    ag.dump(f"dumps/Player{j}-{players}-{size[0]}x{size[1]}-{in_a_row}-last.pickle")


if __name__ == "__main__":
    # Настройки игры
    players = 2
    size = (4, 4)
    in_a_row = 4

    # Компьютеры, участвующие в игре
    # agents = [QAgent(size) for _ in range(players)]
    # agents = [RAgent(size), QAgent(size)]
    # agents = [QAgent.load("dumps/name.pickle", size, False),
    #           QAgent.load("dumps/name.pickle", size, False)]
    agents = [RAgent(size), QAgent.load("dumps/Player1-2-4x4-4-last.pickle", size, False)]

    # Запуск цикла тренировки
    train(players, size, in_a_row, agents, 1_000_000)

from tictactoe import Game, Message
from agents import QAgent, RAgent, UIAgent


def train(players, size, in_a_row, agents, episodes):
    """ Сыграть несколько партий с agents """
    env = Game(players, size, in_a_row)

    wins = [0] * players
    loses = [0] * players
    draws = 0

    for episode in range(1, episodes + 1):
        done = [False] * players
        msgs = [None] * players
        state = env.reset().state
        while not min(done):
            # Пройти по всем пользователям, пока для всех не закончится партия
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
                # Посчитать победы
                for j, m in enumerate(msgs):
                    if m == Message.WINMESSAGE:
                        wins[j] += 1
                    elif m == Message.LOSEMESSAGE:
                        loses[j] += 1

            if episode % 10_000 == 0:
                # Отобразить статистику
                print(f"Игра №{episode}")
                for j in range(players):
                    print(f"\tИгрок {j}. Побед: {wins[j]}. Поражений: {loses[j]}")
                print(f"\tНичьих: {draws}")

            if episode % 20_000 == 0 and (Message.WINMESSAGE in msgs or Message.DRAWMESSAGE in msgs):
                # Отобразить поле в конце партии
                if Message.DRAWMESSAGE in msgs:
                    print(Message.DRAWMESSAGE[1])
                else:
                    print(f"Игрок №{msgs.index(Message.WINMESSAGE)} выиграл")
                print(env.game_map)

            if episode % 200_000 == 0 and episode:
                # Сохранить Q-таблицы
                for j, ag in enumerate(agents):
                    # ag.save(f"dumps/Player{j}-{players}-{size[0]}x{size[1]}-{in_a_row}-{episode}eps-{int(time.time())}.pickle")
                    ag.save(f"dumps/Player{j}-{players}-{size[0]}x{size[1]}-{in_a_row}-last.pickle")
                print("Q-таблицы сохранены")


if __name__ == "__main__":
    # Настройки игры
    players = 2
    size = (4, 4)
    in_a_row = 4
    episodes = 1_000_000

    # Компьютеры, участвующие в игре
    # agents = [QAgent(size) for _ in range(players)]
    agents = [RAgent(size), QAgent(size, episodes=episodes)]
    # agents = [QAgent.load("dumps/Player0-2-4x4-4-last.pickle", size, False),
    #           QAgent.load("dumps/Player1-2-4x4-4-last.pickle", size, False)]
    # agents = [RAgent(size), QAgent.load("dumps/Player1-2-4x4-4-last.pickle", size, True, episodes)]
    # agents = [QAgent.load("dumps/Player0-2-4x4-4-last.pickle", size, False), RAgent(size)]
    # agents = [RAgent(size), UIAgent(size)]

    # Запуск цикла тренировки
    train(players, size, in_a_row, agents, episodes)

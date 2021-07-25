import asyncio

from avalon.avalon import Game
from avalon.player import PlayerList
from shell_gameplay.shell_game import ShellPlayer


class User:
    def __init__(self, _id: int, name: str):
        self.id = _id
        self.name = name


# set game
names = ["Alice", "Cairo", "LongHorn", "Duke", "Green"]
players = PlayerList()
users = []
for i, name in enumerate(names):
    acc = User(i, name)
    users.append(acc)
    players[acc] = ShellPlayer(acc=acc)
game = Game(players=players)


async def last_quest_success():
    level = 4
    game.quest_no = level
    game.quest_results = ["success", "success", "failure", "failure", ""]
    [game.players.update_leader() for _ in range(level)]

    # start game
    await asyncio.sleep(1)
    game.event_next_round.set()
    # select players
    await asyncio.sleep(1)
    game.players[users[level]].get_msg([users[i].name for i in range(3)])
    # accept team
    await asyncio.sleep(1)
    for player in game.players:
        player.get_msg(["accept"])
    # quest vote
    await asyncio.sleep(1)
    for i in range(3):
        game.players[users[i]].get_msg(["success"])
    # finds merlin
    await asyncio.sleep(1)
    game.players.assassin.get_msg([game.players.merlin.name])

    print(f"{game.result=}")


async def main():
    asyncio.create_task(game.start())
    await last_quest_success()


asyncio.run(main())
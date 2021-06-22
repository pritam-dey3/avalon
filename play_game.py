import asyncio
from shell_gameplay.commands import MyCLI
from game.avalon import Account, Player, Game

names = ["Alice", "Cairo", "LongHorn", "Duke", "Green"]
players = [Account(id=i, name=name) for i, name in enumerate(names)]
players = [Player(acc=acc) for acc in players]
game = Game(players=players)

# game.assign_characters()
# morgana = next(filter(lambda x: x.character == "morgana", game.players))
# morgana.vote_for_quest()

asyncio.get_event_loop().run_until_complete(MyCLI().run())
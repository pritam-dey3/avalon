from game.avalon import Player, Game

names = ["Alice", "Cairo", "LongHorn", "Duke", "Green"]
players = [Player(id=i, name=name) for i, name in enumerate(names)]
game = Game(players=players)

# game.assign_characters()
# morgana = next(filter(lambda x: x.character == "morgana", game.players))
# morgana.vote_for_quest()

game.start()

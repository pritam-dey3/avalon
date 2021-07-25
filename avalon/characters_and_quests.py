from dataclasses import dataclass
from random import sample
from typing import List


@dataclass
class Character:
    name: str
    type: str
    knows_characters_of: List[str]
    character_reveal_prefix: str


merlin = Character(
    name="merlin",
    type="good",
    knows_characters_of=["assassin", "morgana"],
    character_reveal_prefix="Assassin and Morgana are ",
)

percival = Character(
    name="percival",
    type="good",
    knows_characters_of=["merlin", "morgana"],
    character_reveal_prefix="Merlin is one of ",
)

loyal_servant = Character(
    name="loyal_servant",
    type="good",
    knows_characters_of=[],
    character_reveal_prefix="",
)

assassin = Character(
    name="assassin",
    type="evil",
    knows_characters_of=["morgana", "minion"],
    character_reveal_prefix="Minions of Mordred are ",
)

morgana = Character(
    name="morgana",
    type="evil",
    knows_characters_of=["assassin", "minion"],
    character_reveal_prefix="Minions of Mordred are ",
)

minion = Character(
    name="minion",
    type="evil",
    knows_characters_of=["assassin", "morgana", "minion"],
    character_reveal_prefix="Minions of Mordred are ",
)

oberon = Character(
    name="oberon", type="evil", knows_characters_of=[], character_reveal_prefix=" "
)


def get_characters(n_players):
    player_distribution = {
        5: (3, 2),
        6: (4, 2),
        7: (4, 3),
        8: (5, 3),
        9: (6, 3),
        10: (6, 4),
    }
    n_good, n_bad = player_distribution[n_players]

    good_cards = [loyal_servant for _ in range(4)]
    evil_cards = [minion for _ in range(3)] + [oberon]

    good_list = [merlin, percival] + sample(good_cards, k=n_good - 2)
    evil_list = [assassin, morgana] + sample(evil_cards, k=n_bad - 2)

    return good_list + evil_list


quest_table = [
    [(2, 1), (2, 1), (2, 1), (3, 1), (3, 1), (3, 1)],
    [(3, 1), (3, 1), (3, 1), (4, 1), (4, 1), (4, 1)],
    [(2, 1), (4, 1), (3, 1), (4, 1), (4, 1), (4, 1)],
    [(3, 1), (3, 1), (4, 2), (5, 2), (5, 2), (5, 2)],
    [(3, 1), (4, 1), (4, 1), (5, 1), (5, 1), (5, 1)],
]

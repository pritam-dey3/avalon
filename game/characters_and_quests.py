from random import sample

merlin = {
    "character": "merlin",
    "type": "good",
    "knows_characters_of": ["assassin", "morgana"],
    "character_reveal_sentence": "Assassin and Morgana are "
}

percival = {
    "character": "percival",
    "type": "good",
    "knows_characters_of": ["merlin", "morgana"],
    "character_reveal_sentence": "Merlin is one of "
}

loyal_servant = {
    "character": "loyal_servant",
    "type": "good",
    "knows_characters_of": [],
    "character_reveal_sentence": ""
}

assassin = {
    "character": "assassin",
    "type": "evil",
    "knows_characters_of": ["morgana", "minion"],
    "character_reveal_sentence": "Minions of Mordred are "
}

morgana = {
    "character": "morgana",
    "type": "evil",
    "knows_characters_of": ["assassin", "minion"],
    "character_reveal_sentence": "Minions of Mordred are "
}

minion = {
    "character": "minion",
    "type": "evil",
    "knows_characters_of": ["assassin", "morgana", "minion"],
    "character_reveal_sentence": "Minions of Mordred are "
}

oberon = {
    "character": "oberon",
    "type": "evil",
    "knows_characters_of": [],
    "character_reveal_sentence": " "
}


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


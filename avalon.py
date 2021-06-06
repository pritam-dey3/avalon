from __future__ import annotations
from random import sample
from typing import List, Union

from characters_and_quests import get_characters, quest_table


def get_id_name(players: List[Player]):
    player_list = [(player.id, player.name) for player in players]
    return player_list


class Player:
    def __init__(self, id=0, name=""):
        self.id = id
        self.name = name
        self.character = ""
        self.type = ""
        self.knows_characters_of = []
        self.character_reveal_sentence = " "
        self.voting_options = []

    def reveal_characters(self, players: List[Player]):
        revealed_characters = ""
        for player in players:
            if player.character in self.knows_characters_of:
                revealed_characters += player.name + ", "
        self.message(self.character_reveal_sentence + revealed_characters[:-2])

    def select_players_for_quest(self, n_members, players: List[Player]):
        players = get_id_name(players)
        player_id_msg = ""
        options = []
        for id, name in players:
            player_id_msg += str(id) + ":\t" + name + "\n"
            options.append(id)
        msg = "Select players for the quest..." + "\n" + player_id_msg

        while True:
            try:
                selected_player_ids = self.message(
                    msg, need_response=True, options=options
                )
                members = [int(id) for id in selected_player_ids.split()]

                assert (
                    len(members) == n_members
                ), f"You have to select {n_members} players for this quest."

                assert all(
                    id < len(players) and id >= 0 for id in members
                ), "Invalid ids."

            except (ValueError, AssertionError) as e:
                self.message(str(e))
                continue
            else:
                break
        return members

    def vote(self):
        while True:
            try:
                vote = self.message(
                    "Do you approve the selected players for the quest?",
                    need_response=True,
                )
            except AssertionError:
                self.message("Your vote is not valid")
                continue
            else:
                break
        return vote in ["Approve", "approve", "A", "a"]

    def message(self, msg, need_response: Union[bool, int] = False, options=[]):
        options = [str(option) for option in options]

        print(f"Private message to {self.name}...")
        print(msg)
        if need_response:
            response = input()
            return response

    def set_player(self, id, name):
        self.id = id
        self.name = name

    def set_character(self, character_dict: dict):
        self.__dict__.update(character_dict)


class Game:
    def __init__(self, players):
        self.players: List[Player] = players
        self.leader = 0
        self.vote_track = 0
        self.quest_results = ["" for i in range(5)]
        self.result = ""
        self.n_players = len(self.players)
        self.quest_no = 0

    def assign_characters(self):
        characters = get_characters(self.n_players)
        players = sample(self.players, k=len(self.players))
        for player, character in zip(players, characters):
            player.set_character(character)

    def reveal_characters(self):
        for player in self.players:
            player.reveal_characters()

    def start(self):
        self.assign_characters()
        self.reveal_characters()
        self.loop()
        self.end()

    def loop(self):
        while True:
            quest_members = self.players[self.leader].select_players_for_quest(
                quest_table[self.quest_no][self.n_players - 5], self.players
            )
            self.quest(quest_members)
            self.leader = (self.leader + 1) % self.n_players

    def end(self):
        pass

    def broadcast(self, msg):
        print("Announcement...")
        print(msg)

    def quest(self, members):
        quest_player_names = [self.players[id].name for id in members]
        self.broadcast(
            f"{self.players[self.leader].name} has chosen the following players.\n"
            + ", ".join(quest_player_names)
        )
        result = self.vote()
        if (result <= 0):
            self.vote_track += 1
            return
        

    def vote(self):
        votes = [player.vote() for player in self.players]
        return 2*sum(votes) - self.n_players

    def game_is_finished(self):
        success_count = self.quest_results.count("success")
        failure_count = self.quest_results.count("failure")
        if success_count == 3:
            self.result = "good"
            return True
        elif failure_count == 3:
            self.result = "evil"
            return True
        elif self.vote_track == 5:
            self.result = "evil"
            return True
        else:
            return False

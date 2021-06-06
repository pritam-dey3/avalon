from __future__ import annotations
from typing import List, Union

from functools import partial
from random import sample

from characters_and_quests import get_characters, quest_table


class Message:
    def send_msg(self, id:int=-1, name:str='',
                text:str="", guide:str="", 
                options:list=[], m=1):
        if id == -1:
            print("Announcement...")
        else:
            print(f"Private message to {name}...")

        if not options:
            print(text)
            return 0
        
        options = [str(opt) for opt in options]
        if not guide:
            guide = "You only have the options\n" + ", ".join(options)
        
        while True:
            print(text)
            print(guide)
            responses = input().split()
            if len(responses) != m:
                print(f"You have to enter {m} valid answers separated by spaces.")
            elif not all(entry in options for entry in responses):
                print("Incorrect entries.")
            else:
                if m == 1:
                    return responses[0]
                else:
                    return responses


class Player:
    def __init__(self, msg:Message, id=0, name=""):
        self.id = id
        self.name = name
        self.msg = msg
        self.send_msg = partial(msg.send_msg, id=self.id, name=self.name)
        self.character = ""
        self.type = ""
        self.knows_characters_of = []
        self.character_reveal_sentence = " "
        self.voting_options = []
    
    @staticmethod
    def get_id_name(players: List[Player]):
        player_list = [(player.id, player.name) for player in players]
        return player_list

    def reveal_characters(self, players: List[Player]):
        revealed_characters = ""
        for player in players:
            if player.character in self.knows_characters_of:
                revealed_characters += player.name + ", "
        self.send_msg(self.character_reveal_sentence + revealed_characters[:-2])

    def select_players_for_quest(self, n_members, players: List[Player]):
        players = Player.get_id_name(players)
        player_id_msg = ""
        options = []
        for id, name in players:
            player_id_msg += str(id) + ":\t" + name + "\n"
            options.append(id)
        msg = "Select players for the quest..."
        members = self.send_msg(text = msg, guide=player_id_msg, options=options, m=n_members)
        members = [int(id) for id in members]
        return members

    def vote_to_accept_team(self):
        text = "Do you approve the current team for this quest?"
        options = ["a", "r"]
        guide = "a:\taccept team\nr:\treject team"
        vote = self.send_msg(text=text, options=options, guide=guide)
        return vote == "a"

    def set_player(self, id, name):
        self.id = id
        self.name = name

    def set_character(self, character_dict: dict):
        self.__dict__.update(character_dict)

    def __repr__(self):
        return f"{self.id}: {self.name}, {self.character}"


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


if __name__ == "__main__":
    msg = Message()
    players = [Player(msg, id=i, name=str(i)) for i in range(5)]
    game = Game(players)
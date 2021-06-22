from __future__ import annotations
import asyncio
from typing import List, Union, Dict, Any

from functools import partial
from random import sample, shuffle

from game.characters_and_quests import get_characters, quest_table, Character


class Inquisitor:
    def __init__(self, question: str = None, players: List[Player] = None):
        self.question = question
        self.targets = players
        self.answers = dict()
        self.event = asyncio.Event()

    def ask(self):
        asyncio.gather(
            *[self.send_msg(player, self.question) for player in self.targets]
        )
        self.event.clear()

    async def send_msg(self, player: Player, q: str):
        await player.send_msg(q)

    def get_answer(self, player: Player, answer):
        self.answers[player] = answer
        print(f"got {answer} from player-{player.acc.id}")
        if len(self.answers.keys()) == len(self.targets):
            self.event.set()

    async def result(self):
        self.ask()
        await self.event.wait()
        return self.answers

class Account:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Player:
    def __init__(self, acc:Account=None, character: Character = None):
        self.acc = acc
        self.character = character

    @staticmethod
    def get_id_name(players: List[Player]):
        player_list = [(player.acc.id, player.acc.name) for player in players]
        return player_list

    def reveal_characters(self, players: List[Player]):
        revealed_characters = ""
        for player in players:
            if player.character.name in self.character.knows_characters_of:
                revealed_characters += player.acc.name + ", "
        self.send_msg(text=self.character.character_reveal_sentence + revealed_characters[:-2])

    def select_players_for_quest(self, n_members: int, players: List[Player]):
        player_id_msg = ""
        for option, player in enumerate(players):
            player_id_msg += str(option + 1) + ":\t" + player.acc.name + "\n"
        msg = f"Select players for the quest...({n_members})"
        options = range(1, len(players) + 1)
        choices = self.send_msg(
            text=msg,
            guide=player_id_msg,
            options=options,
            m=n_members,
        )
        members = [players[int(c) - 1] for c in choices]
        return members

    def vote_for_team(self):
        text = "Do you approve the current team for this quest?"
        options = ["a", "r"]
        guide = "a:\taccept team\nr:\treject team"
        vote = self.send_msg(text=text, options=options, guide=guide)
        return vote == "a"

    def vote_for_quest(self):
        text = "Do you want this mission to be a success or failure?"
        options = ["s"] + (["f"] if self.character.type == "evil" else [])
        guide = "s:\tSuccess\nf:\tFail" + ("(x)" if self.character.type == "good" else "")
        vote = self.send_msg(text=text, options=options, guide=guide)
        return vote == "s"

    def find_merlin(self, players: List[Player]):
        text = "Find Merlin to win the game."
        options = range(1, len(players) + 1)
        player_id_msg = ""
        for option, player in enumerate(players):
            player_id_msg += str(option + 1) + ":\t" + player.acc.name + "\n"
        suspect = self.send_msg(text=text, guide=player_id_msg, options=options, m=1)
        return players[int(suspect) - 1].character == "merlin"

    def set_player(self, acc:Account):
        self.acc = acc

    def set_character(self, character: Character):
        self.character = character
        self.send_msg(text=f"You are {self.character.name}!")

    def send_msg(
        self,
        text: str = "",
        guide: str = "",
        options: list = [],
        m=1,
    ):

        print(f"Private message to {self.acc.name}...")

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

    def __repr__(self):
        return f"{self.acc.id}: {self.acc.name}, {self.character}"

    def __eq__(self, other: Player) -> bool:
        return self.acc.id == other.acc.id


class Game:
    def __init__(self, players): #, inq:Inquisitor
        self.players: List[Player] = players
        self.leader = 0
        self.vote_track = 0
        self.quest_results = ["" for _ in range(5)]
        self.result = ""
        self.n_players = len(self.players)
        self.quest_no = 0

    async def start(self):
        self.assign_characters()
        self.reveal_characters()
        self.loop()
        self.end()

    def assign_characters(self):
        characters = get_characters(self.n_players)
        players = sample(self.players, k=len(self.players))
        for player, character in zip(players, characters):
            player.set_character(character)

    def reveal_characters(self):
        for player in self.players:
            player.reveal_characters(self.players)

    def loop(self):
        while True:
            quest_members = self.players[self.leader].select_players_for_quest(
                quest_table[self.quest_no][self.n_players - 5][0], self.players
            )
            self.quest(quest_members)
            self.leader = (self.leader + 1) % self.n_players
            if self.game_is_finished():
                break

    def end(self):
        if self.result == "evil":
            self.send_msg(text="Minions of the Mordred wins!")
            return
        assassin = next(filter(lambda p: p.character == "assassin", self.players))
        merlin_found = assassin.find_merlin(self.players)
        if merlin_found:
            self.send_msg(text="Minions of the Mordred wins!")
            return
        else:
            self.send_msg(text="The loyal servants of Arthur wins")
            return

    def quest(self, members: List[Player]):
        quest_player_names = [player.acc.name for player in members]
        self.send_msg(
            text=f"{self.players[self.leader].acc.name} has chosen the following players.\n"
            + ", ".join(quest_player_names)
        )

        # Team selection vote
        team_vote_result = self.vote_for_team()
        if team_vote_result <= 0:
            self.vote_track += 1
            return

        self.quest_no += 1
        # Quest vote
        fail_count = self.vote_for_quest(members)

        if fail_count >= quest_table[self.quest_no][self.n_players - 5][1]:
            self.quest_results.append("failure")
            self.send_msg(text="Quest failed.")
            return
        else:
            self.quest_results.append("success")
            self.send_msg(text="Successful quest!")
            return

    def vote_for_team(self):
        votes = [player.vote_for_team() for player in self.players]
        return 2 * sum(votes) - self.n_players

    def vote_for_quest(self, members: List[Player]):
        votes = [player.vote_for_quest() for player in members]
        shuffle(votes)
        votes_msg = ["Success" if vote else "Fail" for vote in votes]
        self.send_msg(text="Votes for this quest\n" + ", ".join(votes_msg))
        return len(members) - sum(votes)

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

    def send_msg(self, text: str = ""):
        print(f"Announcement...")
        print(text)

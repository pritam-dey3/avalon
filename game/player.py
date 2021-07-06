from __future__ import annotations
from typing import List, TYPE_CHECKING, Protocol, Any
import asyncio

from game.characters_and_quests import Character

if TYPE_CHECKING:
    from game.interaction import Inquisitor


class Account(Protocol):
    id: Any
    name: str


class Player:
    def __init__(self, acc: Account, character: Character = None):
        self.acc = acc
        self.character = character
        self.name = acc.name
        self.id = acc.id
        self.current_inq: Inquisitor = None

    @staticmethod
    def get_id_name(players: List[Player]):
        player_list = [(player.id, player.name) for player in players]
        return player_list

    def reveal_characters(self, players: List[Player]):
        revealed_characters = ""
        for player in players:
            if player.character.name in self.character.knows_characters_of:
                revealed_characters += player.name + ", "
        self.send_msg(
            text=self.character.character_reveal_sentence + revealed_characters[:-2]
        )

    # def select_players_for_quest(self, n_members: int, players: List[Player]):
    #     player_id_msg = ""
    #     for option, player in enumerate(players):
    #         player_id_msg += str(option + 1) + ":\t" + player.name + "\n"
    #     msg = f"Select players for the quest...({n_members})"
    #     options = range(1, len(players) + 1)
    #     choices = self.send_msg(
    #         text=msg,
    #         guide=player_id_msg,
    #         options=list(options),
    #         m=n_members,
    #     )
    #     members = [players[int(c) - 1] for c in choices]
    #     return members

    def vote_for_team(self):
        text = "Do you approve the current team for this quest?"
        options = ["a", "r"]
        guide = "a:\taccept team\nr:\treject team"
        vote = self.send_msg(text=text, options=options, guide=guide)
        return vote == "a"

    def vote_for_quest(self):
        text = "Do you want this mission to be a success or failure?"
        options = ["s"] + (["f"] if self.character.type == "evil" else [])
        guide = "s:\tSuccess\nf:\tFail" + (
            "(x)" if self.character.type == "good" else ""
        )
        vote = self.send_msg(text=text, options=options, guide=guide)
        return vote == "s"

    # def find_merlin(self, players: List[Player]):
    #     text = "Find Merlin to win the game."
    #     options = range(1, len(players) + 1)
    #     player_id_msg = ""
    #     for option, player in enumerate(players):
    #         player_id_msg += str(option + 1) + ":\t" + player.name + "\n"
    #     suspect = self.send_msg(
    #         text=text, guide=player_id_msg, options=list(options), m=1
    #     )
    #     return players[int(suspect) - 1].character == "merlin"

    def set_player(self, acc: Account):
        self.acc = acc

    def set_character(self, character: Character, silent=False):
        self.character = character
        if not silent:
            self.send_msg(text=f"You are {self.character.name}!")

    def send_msg(self, text: str = ""):
        """Sends `text` to the player

        Args:
            text (str, optional): Text message to send. Defaults to "".
        """
        raise NotImplementedError
        # print(f"Private message to {self.acc.name}...")
        # print(text)
        

    def get_msg(self, args: List[str]):
        """Called when the player answers to some question.

        This function should ensure 1. The values in `args` are one of
        the options provided by the `Inquisitor`. 2. `self.current_inq is not None`

        Finally this function calls current inquisitor with `self.current_inq(self, args)`

        Args:
            args (List[str]): List of arguments passed while answering
        """
        raise NotImplementedError
        # if not isinstance(args, list):
        #     args = [args]
        # if self.current_inq is None:
        #     self.send_msg("You don't have any questions")
        #     return 0

        # q = self.current_inq.questions[self]
        # options = q.options
        # # print(options.keys(), args, sep="\n")
        # if all(arg in options.keys() for arg in args) and len(args) == q.m:
        #     self.current_inq.get_answer(self, args)
        # else:
        #     self.send_msg(f"Invalid answer(s). Choose {q.m} answers from the options")

    def __repr__(self):
        return f"{self.acc.id}: {self.acc.name}, {self.character.name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return False
        return self.acc.id == other.acc.id

    def __hash__(self) -> int:
        return hash(self.id)

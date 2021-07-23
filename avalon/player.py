from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING, Protocol, Any
from itertools import cycle
from random import sample

from avalon.characters_and_quests import Character, get_characters

if TYPE_CHECKING:
    from avalon.interaction import Inquisitor


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

    def reveal_characters(self, players: List[Player]):
        revealed_characters = ""
        for player in players:
            if player.character.name in self.character.knows_characters_of:
                revealed_characters += player.name + ", "
        self.send_msg(
            text=self.character.character_reveal_sentence + revealed_characters[:-2]
        )

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

    def get_msg(self, args: List[str]):
        """Called when the player answers to some question.

        This function should ensure 1. The values in `args` are one of
        the options provided by the `Inquisitor`. 2. `self.current_inq is not None`

        Finally this function calls current inquisitor with
        `self.current_inq(self, args)`

        Args:
            args (List[str]): List of arguments passed while answering
        """
        raise NotImplementedError

    def __repr__(self):
        return f"{self.acc.id}: {self.acc.name}, {self.character.name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return False
        return self.acc.id == other.acc.id

    def __hash__(self) -> int:
        return hash(self.id)


class PlayerList:
    def __init__(
        self,
    ):
        self.leader: Player = None
        self._store: Dict[Account, Player] = {}
        self._n_players = 0
        self.leader_cycle = cycle(self.store.values())

    @property
    def store(self):
        return self._store

    @store.setter
    def store(self, val):
        self._store = val
        self.leader_cycle = cycle(self._store.values())

    @property
    def n_players(self):
        if self.store:
            return len(self.store)
        else:
            return 0

    @n_players.setter
    def n_players(self, value: int):
        self._n_players = value

    def set_characters(self, silent=False):
        characters = get_characters(self.n_players)
        players: List[Player] = sample(list(self.store.values()), k=self.n_players)
        for player, character in zip(players, characters):
            player.set_character(character, silent)
            self.__dict__[character.name] = player
            # print(character.name, player)    # debug

    def update_leader(self):
        self.leader = next(self.leader_cycle)

    def __getitem__(self, key: Account):
        return self.store[key]

    def __setitem__(self, key: Account, value: Player):
        self.store[key] = value
        self.n_players += 1

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store.values())

    def __len__(self):
        return len(self.store)

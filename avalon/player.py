from __future__ import annotations

import asyncio
from itertools import cycle
from random import sample
from typing import TYPE_CHECKING, Any, Dict, List, Protocol, Union

from avalon.characters_and_quests import Character, get_characters

if TYPE_CHECKING:
    from avalon.interaction import Inquisitor, Question


class Account(Protocol):
    id: Any
    name: str


class Player:
    def __init__(self, acc: Account, character: Character = None):
        self.acc = acc
        self.character = character
        self.current_inq: Inquisitor = None
        self.name = getattr(acc, "name", repr(acc))
        self.id = getattr(acc, "id", 0)

    async def reveal_characters(self, players: List[Player]):
        revealed_characters = ""
        for player in players:
            if player.character.name in self.character.knows_characters_of:
                revealed_characters += player.name + ", "
        await self.send_msg(
            msg=self.character.character_reveal_sentence + revealed_characters[:-2]
        )

    async def set_character(self, character: Character, silent=False):
        self.character = character
        if not silent:
            await self.send_msg(msg=f"You are {self.character.name}!")

    async def send_msg(self, msg: Union[str, Question] = ""):
        """Sends `text` to the player

        Args:
            text (str, optional): Text message to send. Defaults to "".
        """
        raise NotImplementedError

    async def get_msg(self, args: List[str]):
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
        return f"{self.id}: {self.name}, {self.character.name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return False
        return self.id == other.acc.id

    def __hash__(self) -> int:
        return hash(self.id)


class PlayerList:
    def __init__(self, store: Dict[Account, Player] = {}):
        self.leader: Player = None
        self._store: Dict[Account, Player] = store
        self.n_players = 0
        self._leader_cycle = None

    @property
    def store(self):
        return self._store

    @store.setter
    def store(self, val):
        self._store = val
        self.n_players = len(self._store)

    @property
    def leader_cycle(self):
        if self._leader_cycle is None:
            self._leader_cycle = cycle(self._store.values())
        return self._leader_cycle

    def set_characters(self, silent=False):
        characters = get_characters(self.n_players)
        players: List[Player] = sample(list(self._store.values()), k=self.n_players)
        coros = []
        for player, character in zip(players, characters):
            coros.append(player.set_character(character, silent))
            self.__dict__[character.name] = player
            # print(character.name, player)    # debug
        asyncio.gather(*coros)

    def update_leader(self):
        self.leader = next(self.leader_cycle)

    def __getitem__(self, key: Account):
        return self._store[key]

    def __setitem__(self, key: Account, value: Player):
        self._store[key] = value
        self.n_players += 1

    def __delitem__(self, key):
        del self._store[key]
        self.n_players -= 1

    def __iter__(self):
        return iter(self._store.values())

    def __len__(self):
        return len(self._store)

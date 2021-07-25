from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, List, Mapping

if TYPE_CHECKING:
    from avalon.player import Player, PlayerList


class AnsweredWithoutQuestion(Exception):
    pass


class Question:
    def __init__(
        self,
        target: Player = None,
        question: str = None,
        options: Mapping[str, object] = None,
        m: int = 1,
    ) -> None:
        self.target = target
        self.question = question
        self.options = options
        self.m = m
        self.event_answered = asyncio.Event()
        self.answers: Any = None

    async def ask(self):
        self.target.current_q = self
        await self.target.send_msg(self)
        self.event_answered.clear()

    def reply(self, answers: List[str]):
        """Convert valid player answers(str) to expected objects"""
        assert (
            len(answers) == self.m
        ), f"{self.target.name} has not given expected number of answers"

        self.answers = [self.options[a] for a in answers]
        self.target.current_q = None
        # print(f"got {answer} from player-{self.target.name}") # debug
        self.event_answered.set()

    async def answer(self) -> Any:
        await self.ask()
        await self.event_answered.wait()
        return self.answers


class SelectTeam(Question):
    def __init__(self, leader: Player, options: PlayerList, n_members: int) -> None:
        msg = f"Select players for the next quest...({n_members})"
        ops = {p.name: p for p in options}
        super().__init__(target=leader, question=msg, options=ops, m=n_members)

    # result(self) -> List[Player]


class TeamVote(Question):
    def __init__(self, voter: Player):
        msg = "Do you approve the current team for this quest?"
        ops = {"accept": True, "reject": False}
        super().__init__(target=voter, question=msg, options=ops, m=1)

    async def answer(self) -> bool:
        await self.ask()
        await self.event_answered.wait()
        return self.answers[0]


class QuestVote(Question):
    def __init__(self, voter: Player):
        msg = "Do you want this mission to be a success or failure?"
        ops = {"success": True}
        if voter.character.type == "evil":
            ops["fail"] = False
        super().__init__(target=voter, question=msg, options=ops, m=1)

    async def answer(self) -> bool:
        await self.ask()
        await self.event_answered.wait()
        return self.answers[0]


class FindMerlin(Question):
    def __init__(self, assassin: Player, players: List[Player]):
        msg = "Find Merlin to win the game."
        ops = {p.name: p.character.name for p in players}
        super().__init__(target=assassin, question=msg, options=ops, m=1)

    async def answer(self) -> bool:
        await self.ask()
        await self.event_answered.wait()
        return self.answers[0] == "merlin"

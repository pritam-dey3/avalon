from typing import List, Dict, Mapping
from dataclasses import dataclass
import asyncio

from avalon.player import Player, PlayerList


class AnsweredWithoutQuestion(Exception):
    pass


@dataclass
class Question:
    question: str = None
    options: Mapping[str, object] = None
    m: int = 1


class SelectTeam(Question):
    def __init__(self, options: PlayerList, n_members: int):
        msg = f"Select players for the next quest...({n_members})"
        ops = {p.name: p for p in options}
        super().__init__(question=msg, options=ops, m=n_members)


class TeamVote(Question):
    def __init__(self):
        msg = "Do you approve the current team for this quest?"
        ops = {"accept": True, "reject": False}
        super().__init__(question=msg, options=ops, m=1)


class QuestVote(Question):
    def __init__(self, player: Player):
        msg = "Do you want this mission to be a success or failure?"
        ops = {"success": True}
        if player.character.type == "evil":
            ops["fail"] = False
        super().__init__(question=msg, options=ops, m=1)


class FindMerlin(Question):
    def __init__(self, players: List[Player]):
        msg = "Find Merlin to win the game."
        ops = {p.name: p.character.name for p in players}
        super().__init__(question=msg, options=ops, m=1)


class Inquisitor:
    def __init__(
        self,
        questions: Dict[Player, Question] = None,
    ):
        self.questions = questions
        self.answers: Dict[Player, List] = dict()
        self.event = asyncio.Event()
        self.debug = False

    def ask(self):
        for player in self.questions.keys():
            print(player.name)
            player.current_inq = self
        asyncio.gather(
            *[
                self.send_msg(player, question)
                for player, question in self.questions.items()
            ]
        )
        self.event.clear()

    async def send_msg(self, player: Player, q: Question):
        raise NotImplementedError

    def get_answer(self, player: Player, answer: List[str]):
        """Convert valid player answers(str) to objects"""
        assert len(answer) == self.questions[player].m
        try:
            question = self.questions[player]
        except KeyError:
            raise AnsweredWithoutQuestion(
                f"{player.name} answered, but no question was asked."
            )

        self.answers[player] = [question.options[a] for a in answer]
        player.current_inq = None
        if self.debug:
            print(f"got {answer} from player-{player.acc.id}")
        if len(self.answers) == len(self.questions):
            self.event.set()

    async def result(self):
        self.ask()
        await self.event.wait()
        return self.answers

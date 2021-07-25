from typing import Union

from avalon.avalon import Player
from avalon.characters_and_quests import Character
from avalon.interaction import Question


class User:
    def __init__(self, _id: int, name: str):
        self.id = _id
        self.name = name


class ShellPlayer(Player):
    def __init__(self, acc: User, character: Character = None):
        super().__init__(acc, character=character)
        self.name = acc.name
        self.id = acc.id

    async def send_msg(self, msg: Union[str, Question] = ""):
        print(f"Private message to {self.acc.name}...")
        if isinstance(msg, Question):
            text = (
                msg.question
                + "\n"
                + "\n".join(f"{i}:\t {op}" for i, op in enumerate(msg.options))
            )
        elif isinstance(msg, str):
            text = msg
        else:
            raise ValueError("`msg` argument is not `str` or `Question`")
        print(text)

    def get_msg(self, args):
        """Process player input for given question"""
        if not isinstance(args, list):
            args = [args]
        if self.current_inq is None:
            self.send_msg("You don't have any questions")
            return 0

        q = self.current_inq.questions[self]
        options = q.options
        if all(arg in options.keys() for arg in args) and len(args) == q.m:
            self.current_inq.get_answer(self, args)
        else:
            self.send_msg(f"Invalid answer(s). Choose {q.m} answer(s) from the options")

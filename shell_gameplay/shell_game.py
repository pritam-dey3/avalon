import asyncio

from avalon.avalon import Player
from avalon.interaction import Inquisitor, Question


class ShellInquisitor(Inquisitor):
    async def send_msg(self, player: Player, q: Question):
        print(f"Question to {player.name}...")
        await asyncio.sleep(0.3)
        # process options
        print(q.question)
        options = "\n".join(f"{i}:\t {op}" for i, op in enumerate(q.options))
        await asyncio.sleep(0.3)
        print(options, flush=True)
        return


class ShellPlayer(Player):
    def send_msg(self, text: str = ""):
        print(f"Private message to {self.acc.name}...")
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

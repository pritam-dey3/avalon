import traceback
import os
import pickle

import asyncio
from aiocmd import aiocmd
from aiocmd.aiocmd import ExitPromptException

from game.avalon import Game

from shell_gameplay.shell_game import ShellInquisitor, ShellPlayer


class User:
    def __init__(self, _id: int, name: str):
        self.id = _id
        self.name = name


class MyCLI(aiocmd.PromptToolkitCmd):
    def __init__(self, *args, **kwargs):
        super().__init__(aiocmd.PromptToolkitCmd, *args, **kwargs)
        self.players = None
        self.game = None

    async def _run_single_command(self, command, args):
        command_real_args, command_real_kwargs = self._get_command_args(command)
        if len(args) < len(command_real_args):
            print(
                "Bad command args. Usage: %s"
                % self._get_command_usage(
                    command, command_real_args, command_real_kwargs
                )
            )
            return
        elif len(args) > (n := (len(command_real_args) + len(command_real_kwargs))):
            extra_args = args[n - 1 :]
            args = args[: n - 1]
            args.append(extra_args)

        try:
            com_func = self._get_command(command)
            if asyncio.iscoroutinefunction(com_func):
                await com_func(*args)
            else:
                com_func(*args)
            return
        except (ExitPromptException, asyncio.CancelledError):
            raise
        except Exception as ex:
            print("Command failed: ", ex)
            traceback.print_exc()

    def do_my_action(self):
        """This will appear in help text"""
        print("You ran my action!")

    def do_add(self, x, y):
        print(int(x) + int(y))

    async def do_start_game(self):
        names = ["Alice", "Cairo", "LongHorn", "Duke", "Green"]
        players = [User(_id=i, name=name) for i, name in enumerate(names)]
        players = [ShellPlayer(acc=acc) for acc in players]
        self.game = Game(players=players, inq=ShellInquisitor)
        self.game_task = asyncio.create_task(self.game.start())

    async def do_answer(self, player_id: int, *args):
        self.game.players[int(player_id)].get_msg(args[0])

    async def do_next_round(self):
        self.game.next_round.set()
        
    # async def do_debug(self):
    #     self.game.inq.debug = not self.game.inq.d

    async def do_load(self, name: str):
        if self.game:
            self.game.send_msg("Cancelling current game...")
            self.game_task.cancel()
        with open(f"saved_games/{name}.pickle", "rb") as f:
            state = pickle.load(f)
        self.game = Game.load(state)
        # self.players = self.game.players  # have to update the players also!!??
        try:
            self.game_task = asyncio.create_task(self.game.start(from_save=True))
        except asyncio.CancelledError as ex:
            print("cancel")
            print(ex)
            raise
        except:
            traceback.print_exc()
            return False

    def do_eval(self, *args):
        args = args[0]
        if not isinstance(args, list):
            args = [args]
        args = " ".join(args)
        print(eval(args))

    def do_clear(self):
        os.system("clear")


async def background_task():
    print("doing background job")
    await asyncio.sleep(5)
    print("job done")

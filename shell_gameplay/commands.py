import asyncio
from aiocmd import aiocmd
from aiocmd.aiocmd import ExitPromptException

from game.avalon import Player, Game, Account

class MyCLI(aiocmd.PromptToolkitCmd):
    
    async def _run_single_command(self, command, args):
        command_real_args, command_real_kwargs = self._get_command_args(command)
        if len(args) < len(command_real_args):
            print("Bad command args. Usage: %s" % self._get_command_usage(command, command_real_args,
                                                                          command_real_kwargs))
            return
        elif len(args) > (n:=(len(command_real_args) + len(command_real_kwargs))):
            extra_args = args[n-1:]
            args = args[:n-1]
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

    def do_my_action(self):
        """This will appear in help text"""
        print("You ran my action!")
        
    def do_add(self, x, y):
        print(int(x) + int(y))

    async def do_start_game(self):
        names = ["Alice", "Cairo", "LongHorn", "Duke", "Green"]
        players = [Account(id=i, name=name) for i, name in enumerate(names)]
        players = [Player(acc=acc) for acc in players]
        game = Game(players=players)
        asyncio.create_task(game.start())

    async def do_input(self, player_id:int, args):
        print(type(player_id), args)

    async def do_sleep(self, sleep_time=1):
        await asyncio.sleep(int(sleep_time))
        print("now sleeping in the background")
        asyncio.create_task(background_task())

async def background_task():
    print("doing background job")
    await asyncio.sleep(5)
    print("job done")
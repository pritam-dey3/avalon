import asyncio
from shell_gameplay.commands import MyCLI, User


asyncio.get_event_loop().run_until_complete(MyCLI().run())
import asyncio
from shell_gameplay.commands import MyCLI


asyncio.get_event_loop().run_until_complete(MyCLI().run())

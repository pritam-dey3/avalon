import logging
import os
from datetime import datetime
import asyncio

from aiogram import Bot, Dispatcher, types

from game.player import PlayerList
from telegram_bot.credentials import test_accounts, TELEGRAM_BOT_TOKEN


filename = "telegram_bot/logs/" + datetime.now().strftime("%b%d - %H.%M") + ".log"
os.makedirs(os.path.dirname(filename), exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=filename)
logger = logging.getLogger(__name__)


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def start(message: types.Message) -> None:
    """Send a message when the command /start is issued."""
    await message.reply("Hi!\nI'm Kib0!\nPowered by aiogram.")


class JoinGame:
    def __init__(self):
        self.chat: types.Chat
        self.game_joining = asyncio.Event()
        self.players: PlayerList = PlayerList([])

    async def join(self, message: types.Message):
        pass

    async def start_game(self, message: types.Message):
        await message.reply(
            "Starting a new game, type `join` in the chat to join the game."
        )
        asyncio.create_task(
            set_countdown_for(ev=self.game_joining, t=3000, msg="", chat=self.chat)
        )
        await self.game_joining.wait()
        print("woo hoo.. The game is starting with")


async def set_countdown_for(ev: asyncio.Event, t: int, chat: types.Chat, msg: str = ""):
    await asyncio.sleep(t)
    if not ev.is_set():
        bot.send_message(chat_id=chat.id, text="Time over!\n" + msg)
        ev.set()

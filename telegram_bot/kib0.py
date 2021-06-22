import logging
import os
from typing import List
from datetime import datetime
from collections.abc import Sequence

from telegram import User, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, ForceReply
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
)

from telegram_bot.credentials import test_accounts, TELEGRAM_BOT_TOKEN
from game.avalon import Game, Player


filename = "telegram_bot/logs/" + datetime.now().strftime("%b%d - %H.%M") + ".log"
os.makedirs(os.path.dirname(filename), exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=filename)
logger = logging.getLogger(__name__)

updater = Updater(TELEGRAM_BOT_TOKEN)
dp = updater.dispatcher

class PlayerList:
    _instance = None

    def __new__(self):
        if self._instance is None:
            print("Creating the player list")
            self._instance = super(PlayerList, self).__new__(self)
            # Put any initialization here.
            self.player_list: List[User] = []
        else:
            self.just_created = False
            return self._instance

    def add(self, player):
        self.player_list.append(player)

    def __getitem__(self, i):
        return self.player_list[i]

    def __repr__(self):
        return f"{self.player_list}"

    def __len__(self):
        return len(self.player_list)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr"Hi {user.mention_markdown_v2()}\!",
        reply_markup=ForceReply(selective=True),
    )

dp.add_handler(CommandHandler("start", start, run_async=True))


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")

dp.add_handler(CommandHandler("help", help_command, run_async=True))


def start_game(update: Update, _):
    """ starts a game """

    players: PlayerList = PlayerList() if update.message.text == "/start_game" else None
    if update.message.text == "/start_game" and players is None:
        update.message.reply_text(
            "Game will start soon. Type `/join` to join the game."
        )
    elif update.message.text == "/join" and players is not None:
        players.add(update.message.from_user)
        print(players)
    elif (
        (update.message.text == "/done")
        # and (len(players) >= 5)
        and (players is not None)
    ):

        names = [player.username for player in players.player_list]
        update.message.reply_text("Game started with players " + ", ".join(names))
        
dp.add_handler(CommandHandler(["start_game", "join", "done"], start_game, run_async=True))


def choose_option(user: User):
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ],
        [InlineKeyboardButton("Option 3", callback_data='3')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    user.send_message(text='Please choose:', reply_markup=reply_markup)


def button(update: Update, _) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Selected option: {query.data}")
    print(query.data)

dp.add_handler(CallbackQueryHandler(button))


def choice(update: Update, _):
    choose_option(update.message.from_user)

dp.add_handler(CommandHandler('choice', choice))



def start_test(update: Update, _):
    test_players = test_accounts 

     

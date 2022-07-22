import nextcord
from nextcord.ext import commands as cmds
from colorama import Fore
from dpyConsole import Console

from config import *

intents = nextcord.Intents.all()


class Bot(cmds.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=cmds.when_mentioned_or(prefix), case_insensitive=True, intents=intents, help_command=None)

if __name__ == "__main__":
    """
    for filename in os.listdir(f"{path}commands"):
        if filename.endswith(".py"):
            bot.load_extension(f"commands.{filename[:-3]}", extras={"prefix": prefix, "in_row": in_row, "currency": currency}) """
    bot = Bot()
    cmd = Console(bot)
    cmd.load_extension(f'console')
    cmd.start()
    print(f'\n{Fore.RED}[>>>]Please, wait a bit...{Fore.RESET}')
    bot.load_extension(f"commands.event_handl", extras={"prefix": prefix, "in_row": in_row})

    #bot.run(token)
    bot.run(debug_token)
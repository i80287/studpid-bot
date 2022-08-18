"""activate_this = '/home/bot/python/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})"""

from nextcord import Intents
from nextcord.ext import commands as cmds
from colorama import Fore
from dpyConsole import Console

from os import listdir

from config import path_to, prefix, debug_token, token

class Bot(cmds.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=cmds.when_mentioned_or(prefix), case_insensitive=True, intents=Intents.all(), help_command=None)

    # just because if i put handler only in the cog i get an error message in the cmd every time
    async def on_application_command_error(*args):
        return

if __name__ == "__main__":
    
    bot = Bot()

    for filename in listdir(f"{path_to}/commands"):
        if filename.endswith(".py"):
            bot.load_extension(f"commands.{filename[:-3]}")
    
    cmd = Console(bot)
    cmd.load_extension("console")
    cmd.start()

    print(f"\n{Fore.RED}[>>>]Please, wait a bit...{Fore.RESET}")

    #bot.run(token)
    bot.run(debug_token)
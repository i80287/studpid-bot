from nextcord import Intents
from nextcord.ext import commands as cmds
from colorama import Fore
from dpyConsole import Console

from config import *

class Bot(cmds.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=cmds.when_mentioned_or(prefix), case_insensitive=True, intents=Intents.all(), help_command=None)

    # just because if i put handler only in the cog i get an error message in the cmd every time
    async def on_application_command_error(*args):
        pass

if __name__ == "__main__":
    """
    for filename in os.listdir(f"{path}commands"):
        if filename.endswith(".py"):
            bot.load_extension(f"commands.{filename[:-3]}")"""
    bot = Bot()
    
    cmd = Console(bot)
    cmd.load_extension(f'console')
    cmd.start()

    print(f'\n{Fore.RED}[>>>]Please, wait a bit...{Fore.RESET}')
    bot.load_extension(f"commands.event_handl")

    """ bot.load_extension(f"commands.polls")
    bot.load_extension(f"commands.m_commands")
    bot.load_extension(f"commands.basic")
    bot.load_extension(f"commands.slash_shop") """

    #bot.run(token)
    bot.run(debug_token)
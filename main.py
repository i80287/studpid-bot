"""activate_this = '/home/bot/python/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})"""

from nextcord import Intents
from nextcord.ext.commands import Bot, when_mentioned_or

from config import prefix, DEBUG_TOKEN, TOKEN, DEBUG

class StoreBot(Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=when_mentioned_or(prefix), 
            case_insensitive=True, 
            intents=Intents.all(), 
            help_command=None
        )

    # just because if i put handler only in the cog i get an error message in the cmd every time
    async def on_application_command_error(*args):
        return

if __name__ == "__main__":
    bot = StoreBot()
    bot.load_extensions_from_module("Commands")

    if DEBUG:
        from colorama import Fore
        from dpyConsole import Console
        
        cmd = Console(bot)
        cmd.load_extension("console")
        cmd.start()

        print(f"\n{Fore.RED}[>>>]Please, wait a bit...{Fore.RESET}")

        bot.run(DEBUG_TOKEN)
    else:
        bot.run(TOKEN)
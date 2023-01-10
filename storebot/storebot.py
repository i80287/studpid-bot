from time import time

from nextcord import Intents, Member
from nextcord.ext.commands import Bot, when_mentioned_or

from config import prefix, DEBUG_TOKEN, TOKEN, DEBUG, FEEDBACK_CHANNEL

class StoreBot(Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=when_mentioned_or(prefix), 
            case_insensitive=True, 
            intents=Intents.all(), 
            help_command=None
        )
        self.bot_feedback_channel: int = FEEDBACK_CHANNEL
        self.current_polls: int = 0
        self.startup_time: int = int(time())
        # guild_id: member_id: Member
        self.members_in_voice: dict[int, dict[int, Member]] = {}
        # guild_is: {channel_id}
        self.ignored_channels: dict[int, set[int]] = {}

    # just because if i put handler only in the cog i get an error message in the cmd every time
    async def on_application_command_error(*args) -> None:
        return

if __name__ == "__main__":
    bot: StoreBot = StoreBot()
    bot.load_extensions_from_module("Commands")

    if DEBUG:
        from colorama import Fore
        from dpyConsole import Console
        
        cmd: Console = Console(bot)
        cmd.load_extension("console")
        cmd.start()

        print(f"\n{Fore.RED}[>>>]Please, wait a bit...{Fore.RESET}")

        bot.run(DEBUG_TOKEN)
    else:
        bot.run(TOKEN)

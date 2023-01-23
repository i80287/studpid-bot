from asyncio import Lock
from time import time
from typing import (
    List,
    Dict,
    Set
)

from nextcord import Intents, Member
from nextcord.ext.commands import Bot, when_mentioned_or

from Commands import polls
from config import prefix, DEBUG_TOKEN, TOKEN, DEBUG, FEEDBACK_CHANNEL

class StoreBot(Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=when_mentioned_or(prefix), 
            case_insensitive=True, 
            intents=Intents.all(), 
            help_command=None
        )
        
        self.statistic_lock: Lock = Lock()
        self.bot_feedback_channel: int = FEEDBACK_CHANNEL
        self.current_polls: List[polls.Poll] = []
        
        self.text_lock: Lock = Lock()
        # guild_id: {text_channel_id}
        self.ignored_text_channels: Dict[int, Set[int]] = {}

        self.voice_lock: Lock = Lock()
        self.startup_time: int = int(time())
        # guild_id: member_id: Member
        self.members_in_voice: Dict[int, Dict[int, Member]] = {}
        # guild_id: {voice_channel_id}
        self.ignored_voice_channels: Dict[int, Set[int]] = {}
    
    # Dummy listener.
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

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Cogs.polls_cog import Poll

    from nextcord import Member

from asyncio import Lock
from time import time

from nextcord import Intents
from nextcord.ext import commands

try:
    from .config import prefix, FEEDBACK_CHANNEL
except:
    from .config_example import prefix, FEEDBACK_CHANNEL

class StoreBot(commands.Bot):
    def __init__(self) -> None:
        intents: Intents = Intents.all()
        intents.presences = False
        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix),
            case_insensitive=True,
            intents=intents,
            help_command=None
        )
        
        self.statistic_lock: Lock = Lock()
        self.bot_feedback_channel: int = FEEDBACK_CHANNEL
        self.current_polls: list[Poll] = []
        
        self.text_lock: Lock = Lock()
        # guild_id: {text_channel_id}
        self.ignored_text_channels: dict[int, set[int]] = {}

        self.voice_lock: Lock = Lock()
        self.startup_time: int = int(time())
        # guild_id: member_id: Member
        self.members_in_voice: dict[int, dict[int, Member]] = {}
        # guild_id: {voice_channel_id}
        self.ignored_voice_channels: dict[int, set[int]] = {}
    
    # Dummy listener.
    async def on_application_command_error(*args) -> None:
        return

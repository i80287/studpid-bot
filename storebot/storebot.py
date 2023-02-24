from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from storebot.Commands.polls import Poll

from asyncio import Lock
from time import time

from nextcord import Intents, Member
from nextcord.ext.commands import Bot, when_mentioned_or

from storebot.config import prefix, FEEDBACK_CHANNEL

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

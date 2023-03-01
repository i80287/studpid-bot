from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import NoReturn

    from nextcord import (
        VoiceState,
        Member,
        Guild
    )
    
    from ..storebot import StoreBot

import asyncio
from time import time

from nextcord import (
    VoiceChannel,
    StageChannel,
    TextChannel,
    Embed
)
from nextcord.ext import tasks
from nextcord.ext.commands import Cog

from ..Tools import db_commands
from ..Tools.logger import Logger


class VoiceHandlerCog(Cog):
    voice_handler_text: dict[int, dict[int, str]] = {
        0: {
            0: "**`Member`** <@{}> **`joined voice channel`** <#{}>",
            1: "**`Member`** <@{}> **`left voice channel`** <#{}> **`and gained {}`** {}"
        },
        1: {
            0: "**`Участник`** <@{}> **`присоединился к голосовому каналу`** <#{}>",
            1: "**`Участник`** <@{}> **`покинул голосовой канал`** <#{}> **`и заработал {}`** {}",
        }
    }

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot
        self.voice_queue: asyncio.Queue[tuple[Member, VoiceState, VoiceState, int]] = asyncio.Queue()
        self.voice_processor.start()

    @Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState) -> None:
        if member.bot:
            return
        
        await self.voice_queue.put((member, before, after, int(time())))
    
    @tasks.loop()
    async def voice_processor(self) -> NoReturn:
        await Logger.write_one_log_async(filename="common_logs.log", report="[voice processor started]")
        while True:
            member, before, after, timestamp = await self.voice_queue.get()

            guild: Guild = member.guild
            guild_id: int = guild.id
            async with self.bot.voice_lock:
                if guild_id not in self.bot.ignored_voice_channels:
                    self.bot.ignored_voice_channels[guild_id] = set()

            before_channel: VoiceChannel | StageChannel | None = before.channel
            after_channel: VoiceChannel | StageChannel | None = after.channel
            before_channel_is_voice: bool = isinstance(before_channel, VoiceChannel)
            after_channel_is_voice: bool = isinstance(after_channel, VoiceChannel)

            if not (before_channel_is_voice or after_channel_is_voice):
                continue

            money_for_voice: int = db_commands.get_server_info_value(guild_id=guild_id, key_name="mn_for_voice")       
            member_id: int = member.id

            if before_channel_is_voice and after_channel_is_voice:
                after_channel_id: int = after_channel.id
                before_channel_id: int = before_channel.id
                if after_channel_id == before_channel_id:
                    continue
                
                await self.process_left_member(
                    member_id=member_id,
                    guild=guild,
                    money_for_voice=money_for_voice,
                    channel_id=before_channel_id,
                    channel_name=before_channel.name,
                    voice_left_time=timestamp
                )
                await self.process_joined_member(
                    member_id=member_id,
                    member=member,
                    guild=guild,
                    money_for_voice=money_for_voice,
                    channel_id=after_channel_id,
                    channel_name=after_channel.name,
                    voice_join_time=timestamp
                )

                continue

            if before_channel_is_voice:
                await self.process_left_member(
                    member_id=member_id,
                    guild=guild,
                    money_for_voice=money_for_voice,
                    channel_id=before_channel.id,
                    channel_name=before_channel.name,
                    voice_left_time=timestamp
                )

                continue

            if after_channel_is_voice:
                await self.process_joined_member(
                    member_id=member_id,
                    member=member,
                    guild=guild,
                    money_for_voice=money_for_voice,
                    channel_id=after_channel.id,
                    channel_name=after_channel.name,
                    voice_join_time=timestamp
                )

                continue

    @voice_processor.before_loop
    async def before_voice_processor(self) -> None:
        await self.bot.wait_until_ready()

    async def process_left_member(self, member_id: int, guild: Guild, money_for_voice: int, channel_id: int, channel_name: str, voice_left_time: int) -> None:
        guild_id: int = guild.id
        async with self.bot.voice_lock:
            if guild_id in self.bot.members_in_voice:
                if member_id in self.bot.members_in_voice[guild_id]:
                    member_name: str = self.bot.members_in_voice[guild_id].pop(member_id).name
                    voice_join_time: int = 0
                    was_in_dict: bool = True
                else:
                    # If member joined voice channel before the bot startup.
                    member_name: str = "not in dict;"
                    voice_join_time: int = self.bot.startup_time
                    was_in_dict: bool = False
            else:
                # If member left in time bot startuped
                self.bot.members_in_voice[guild_id] = {}
                member_name: str = "guild not in dict;"
                voice_join_time: int = self.bot.startup_time
                was_in_dict: bool = False

            if channel_id in self.bot.ignored_voice_channels[guild_id]:
                await Logger.write_guild_log_async(
                    filename="voice_logs.log",
                    guild_id=guild_id,
                    report=f"[member {member_id}:{member_name} left ignored channel {channel_id}:{channel_name}] [guild {guild_id}:{guild.name}] [money_for_voice: {money_for_voice}] [join time: {voice_join_time}] [left time: {voice_left_time}]"
                )
                money_for_voice = 0
        
        if was_in_dict:
            income, voice_join_time = await db_commands.register_user_voice_channel_left(
                guild_id=guild_id,
                member_id=member_id,
                money_for_voice=money_for_voice,
                time_left=voice_left_time
            )
        else:
            income: int = await db_commands.register_user_voice_channel_left_with_join_time(
                guild_id=guild_id,
                member_id=member_id,
                money_for_voice=money_for_voice,
                time_join=voice_join_time,
                time_left=voice_left_time
            )

        if not money_for_voice:
            return
        
        await Logger.write_guild_log_async(
            filename="voice_logs.log",
            guild_id=guild_id,
            report=f"[member {member_id}:{member_name} left channel {channel_id}:{channel_name}] [guild {guild_id}:{guild.name}] [income: {income}] [join time: {voice_join_time}] [left time: {voice_left_time}] [money_for_voice: {money_for_voice}]"
        )

        log_channel_id: int = await db_commands.get_server_info_value_async(guild_id=guild_id, key_name="log_c") 
        if log_channel_id and isinstance(log_channel := guild.get_channel(log_channel_id), TextChannel):
            server_lng: int = await db_commands.get_server_info_value_async(guild_id=guild_id, key_name="lang")
            currency: str = await db_commands.get_server_currency_async(guild_id=guild_id)
            await log_channel.send(embed=Embed(
                description=self.voice_handler_text[server_lng][1].format(member_id, channel_id, income, currency)
            ))
    
    async def process_joined_member(self, member_id: int, member: Member, guild: Guild, money_for_voice: int, channel_id: int, channel_name: str, voice_join_time: int) -> None:
        guild_id: int = guild.id
        async with self.bot.voice_lock:
            if guild_id in self.bot.members_in_voice:
                self.bot.members_in_voice[guild_id][member_id] = member
            else:
                self.bot.members_in_voice[guild_id] = {member_id: member}

        await db_commands.register_user_voice_channel_join(
            guild_id=guild_id,
            member_id=member_id,
            time_join=voice_join_time
        )

        async with self.bot.voice_lock:
            if channel_id in self.bot.ignored_voice_channels[guild_id]:
                await Logger.write_guild_log_async(
                    filename="voice_logs.log",
                    guild_id=guild_id,
                    report=f"[member {member_id}:{member.name}] [joined ignored channel {channel_id}:{channel_name}] [guild {guild_id}:{guild.name}; money_for_voice: {money_for_voice}] [join time: {voice_join_time}]"
                )
                return

        await Logger.write_guild_log_async(
            filename="voice_logs.log",
            guild_id=guild_id,
            report=f"[member {member_id}:{member.name}] [joined channel {channel_id}:{channel_name}] [guild {guild_id}:{guild.name}; money_for_voice: {money_for_voice}] [join time: {voice_join_time}]"
        )

        if not money_for_voice:
            return

        log_channel_id: int = await db_commands.get_server_info_value_async(guild_id=guild_id, key_name="log_c") 
        if log_channel_id and (log_channel := guild.get_channel(log_channel_id)) and isinstance(log_channel, TextChannel):
            server_lng: int = await db_commands.get_server_info_value_async(guild_id=guild_id, key_name="lang")
            await log_channel.send(embed=Embed(
                description=self.voice_handler_text[server_lng][0].format(member_id, channel_id)
            ))

    async def process_member_on_bot_shutdown(self, guild: Guild, member_id: int, member: Member) -> None:
        if not member.voice:
            return

        current_channel: VoiceChannel | StageChannel | None = member.voice.channel
        if not isinstance(current_channel, VoiceChannel):
            return

        channel_id: int = current_channel.id
        guild_id: int = guild.id
        
        # self.bot.voice_lock is already locked.
        if channel_id not in self.bot.ignored_voice_channels[guild_id]:
            money_for_voice: int = await db_commands.get_server_info_value_async(guild_id=guild_id, key_name="mn_for_voice")
        else:
            money_for_voice = 0
        
        voice_left_time: int = int(time())
        income, voice_join_time = await db_commands.register_user_voice_channel_left(
            guild_id=guild_id,
            member_id=member_id,
            money_for_voice=money_for_voice,
            time_left=voice_left_time
        )

        await Logger.write_guild_log_async(
            filename="voice_logs.log",
            guild_id=guild_id,
            report=f"[member {member_id}:{member.name} processed as left from channel {channel_id}:{current_channel.name}] [guild: {guild_id}:{guild.name}] [income: {income}] [join time: {voice_join_time}] [left time: {voice_left_time}] [money_for_voice: {money_for_voice}]"
        )


def setup(bot: StoreBot) -> None:
    bot.add_cog(VoiceHandlerCog(bot))
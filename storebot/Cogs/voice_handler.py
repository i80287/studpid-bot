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

from ..Tools.db_commands import (
    get_money_and_xp_async,
    get_server_log_info_async,
    get_server_currency_async,
    register_user_voice_channel_join,
    register_user_voice_channel_left,
    register_user_voice_channel_left_with_join_time
)
from ..Tools.logger import (
    write_one_log_async,
    write_guild_log_async
)

class VoiceHandlerCog(Cog):
    voice_handler_text: tuple[tuple[str, str], tuple[str, str]] = (
        (
            "**`Member`** <@{}> **`joined voice channel`** <#{}>",
            "**`Member`** <@{}> **`left voice channel`** <#{}> **`and gained {} xp and {}`** {}"
        ),
        (
            "**`Участник`** <@{}> **`присоединился к голосовому каналу`** <#{}>",
            "**`Участник`** <@{}> **`покинул голосовой канал`** <#{}> **`и заработал {} опыта и {}`** {}"
        )
    )

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot
        self.voice_queue: asyncio.Queue[tuple[Member, VoiceState, VoiceState, int]] = asyncio.Queue()
        self.voice_processor.start()

    @Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState) -> None:
        if member.bot:
            return

        await write_one_log_async(
            "observations.log",
            f"[member: {member.id}:{member.name}] [guild: {member.guild.id}:{member.guild.name}]"
        )
        await self.voice_queue.put((member, before, after, int(time())))
    
    @tasks.loop()
    async def voice_processor(self) -> NoReturn:
        await write_one_log_async("common_logs.log", "[voice processor started]")
        bot: StoreBot = self.bot
        next_voise_state_update_coro = self.voice_queue.get
        process_left_member_coro = self.process_left_member
        process_joined_member_coro = self.process_joined_member
        from .event_handler import EventsHandlerCog
        process_new_lvl_coro = EventsHandlerCog.process_new_lvl

        while True:
            try:
                member, before, after, timestamp = await next_voise_state_update_coro()

                before_channel: VoiceChannel | StageChannel | None = before.channel
                after_channel: VoiceChannel | StageChannel | None = after.channel

                if before_channel is None and after_channel is None:
                    continue

                before_channel_id: int | None = before_channel.id if before_channel is not None else None
                after_channel_id: int | None = after_channel.id if after_channel is not None else None

                if before_channel_id is after_channel_id or before_channel_id == after_channel_id:
                    await write_one_log_async(
                        "observations.log",
                        f"[continuation on line 87] [member: {member.id}] [guild: {member.guild.id}]"
                    )
                    continue

                guild: Guild = member.guild
                guild_id: int = guild.id
                async with bot.voice_lock:
                    if guild_id not in bot.ignored_voice_channels:
                        bot.ignored_voice_channels[guild_id] = set()

                money_for_voice, xp_for_voice = await get_money_and_xp_async(guild_id)
                member_id: int = member.id

                if before_channel is not None:
                    assert before_channel_id is not None
                    new_level = await process_left_member_coro(
                        member_id,
                        guild,
                        money_for_voice,
                        xp_for_voice,
                        before_channel_id,
                        before_channel.name,
                        timestamp
                    )
                    if new_level:
                        await process_new_lvl_coro(guild, member, new_level, bot)

                if after_channel is not None:
                    assert after_channel_id is not None
                    await process_joined_member_coro(
                        member_id,
                        member,
                        guild,
                        money_for_voice,
                        xp_for_voice,
                        after_channel_id,
                        after_channel.name,
                        timestamp
                    )
            except Exception as ex:
                await write_one_log_async(
                    "error.log",
                    f"[FATAL] [ERROR] [voice_processor global loop] [{ex}:{ex!r}]"
                )

    @voice_processor.before_loop
    async def before_voice_processor(self) -> None:
        await self.bot.wait_until_ready()

    async def process_left_member(
            self,
            member_id: int,
            guild: Guild,
            money_for_voice: int,
            xp_for_voice: int,
            channel_id: int,
            channel_name: str,
            voice_left_time: int) -> int:
        await write_one_log_async("observations.log", f"[member left] [member: {member_id}] [guild: {guild.name}]")
        guild_id: int = guild.id
        bot: StoreBot = self.bot
        was_in_dict: bool = True
        async with bot.voice_lock:
            members_in_voice: dict[int, dict[int, Member]] = bot.members_in_voice
            if guild_id in members_in_voice:
                if (member := members_in_voice[guild_id].pop(member_id, None)) is not None:
                    member_name: str = member.name
                    voice_join_time: int = 0
                else:
                    # If member joined voice channel before the bot startup.
                    member_name: str = "not in dict;"
                    time_now = int(time())
                    voice_join_time: int = (time_now - (time_now >> 2)) + (bot.startup_time >> 2)
                    was_in_dict = False
            else:
                # If member left in time bot startuped
                members_in_voice[guild_id] = {}
                member_name: str = "guild not in dict;"
                voice_join_time: int = int(time())
                was_in_dict = False

            if channel_id in bot.ignored_voice_channels[guild_id]:
                await write_guild_log_async(
                    "voice_logs.log",
                    guild_id,
                    f"[member {member_id}:{member_name} left ignored channel {channel_id}:{channel_name}] [guild {guild_id}:{guild.name}] [money_for_voice: {money_for_voice}] [join time: {voice_join_time}] [left time: {voice_left_time}]"
                )
                money_for_voice = 0
                xp_for_voice = 0

        if was_in_dict:
            income, xp_income, voice_join_time, new_level = await register_user_voice_channel_left(
                guild_id,
                member_id,
                money_for_voice,
                xp_for_voice,
                voice_left_time
            )
        else:
            income, xp_income, new_level = await register_user_voice_channel_left_with_join_time(
                guild_id,
                member_id,
                money_for_voice,
                xp_for_voice,
                voice_join_time,
                voice_left_time
            )

        if not money_for_voice and not xp_for_voice:
            return 0

        await write_guild_log_async(
            "voice_logs.log",
            guild_id,
            f"[member {member_id}:{member_name} left channel {channel_id}:{channel_name}] [guild {guild_id}:{guild.name}] [income: {income}] [xp_income: {xp_income}] [join time: {voice_join_time}] [left time: {voice_left_time}] [money_for_voice: {money_for_voice}]"
        )

        log_channel_id, server_lng = await get_server_log_info_async(guild_id)
        if log_channel_id and isinstance(log_channel := guild.get_channel(log_channel_id), TextChannel):
            currency: str = await get_server_currency_async(guild_id)
            try:
                await log_channel.send(embed=Embed(
                    description=self.voice_handler_text[server_lng][1].format(member_id, channel_id, xp_income, income, currency)
                ))
            except:
                pass

        return new_level
    
    async def process_joined_member(
            self, member_id: int,
            member: Member,
            guild: Guild,
            money_for_voice: int,
            xp_for_voice: int,
            channel_id: int,
            channel_name: str,
            voice_join_time: int) -> None:
        await write_one_log_async("observations.log", f"[member join] [member: {member_id}] [guild: {guild.name}]")        
        guild_id: int = guild.id
        bot: StoreBot = self.bot
        async with bot.voice_lock:
            members_in_voice: dict[int, dict[int, Member]] = bot.members_in_voice
            if (guild_members_in_voice := members_in_voice.get(guild_id, None)) is not None:
                guild_members_in_voice[member_id] = member
            else:
                members_in_voice[guild_id] = {member_id: member}

        await register_user_voice_channel_join(
            guild_id=guild_id,
            member_id=member_id,
            time_join=voice_join_time
        )

        async with bot.voice_lock:
            if channel_id in bot.ignored_voice_channels[guild_id]:
                await write_guild_log_async(
                    "voice_logs.log",
                    guild_id,
                    f"[member {member_id}:{member.name}] [joined ignored channel {channel_id}:{channel_name}] [guild {guild_id}:{guild.name}; money_for_voice: {money_for_voice}; xp_for_voice: {xp_for_voice}] [join time: {voice_join_time}]"
                )
                return

        await write_guild_log_async(
            "voice_logs.log",
            guild_id,
            f"[member {member_id}:{member.name}] [joined channel {channel_id}:{channel_name}] [guild {guild_id}:{guild.name}; money_for_voice: {money_for_voice}; xp_for_voice: {xp_for_voice}] [join time: {voice_join_time}]"
        )

        if not money_for_voice and not xp_for_voice:
            return

        log_channel_id, server_lng = await get_server_log_info_async(guild_id)
        if log_channel_id and isinstance(log_channel := guild.get_channel(log_channel_id), TextChannel):
            try:
                await log_channel.send(embed=Embed(
                    description=self.voice_handler_text[server_lng][0].format(member_id, channel_id)
                ))
            except:
                pass

    async def process_member_on_bot_shutdown(self, guild: Guild, members_dict: dict[int, Member]) -> None:
        guild_id: int = guild.id
        guild_name: str = guild.name
        ignored_voice_channels = self.bot.ignored_voice_channels
        from .event_handler import EventsHandlerCog
        process_new_lvl_coro = EventsHandlerCog.process_new_lvl

        for member_id, member in members_dict.items():
            if not member.voice:
                continue

            current_channel: VoiceChannel | StageChannel | None = member.voice.channel
            if not isinstance(current_channel, VoiceChannel):
                continue

            channel_id: int = current_channel.id
            # self.bot.voice_lock is already locked.
            money_for_voice, xp_for_voice = \
                await get_money_and_xp_async(guild_id) \
                if channel_id not in ignored_voice_channels[guild_id] else (0, 0)

            voice_left_time: int = int(time())
            income, xp_income, voice_join_time, new_level = await register_user_voice_channel_left(
                guild_id,
                member_id,
                money_for_voice,
                xp_for_voice,
                voice_left_time
            )

            await write_guild_log_async(
                "voice_logs.log",
                guild_id,
                f"[member {member_id}:{member.name} processed as left from channel {channel_id}:{current_channel.name}] [guild: {guild_id}:{guild_name}] [income: {income}] [xp_income: {xp_income}] [join time: {voice_join_time}] [left time: {voice_left_time}] [money_for_voice: {money_for_voice}]"
            )

            if not new_level:
                continue

            await process_new_lvl_coro(guild, member, new_level, self.bot)

def setup(bot: StoreBot) -> None:
    bot.add_cog(VoiceHandlerCog(bot))

from nextcord import VoiceState, VoiceChannel, \
    StageChannel, TextChannel, Member, Guild, Embed
from nextcord.ext.commands import Cog

from storebot import StoreBot
from Tools import db_commands


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

    @Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState) -> None:
        guild: Guild = member.guild
        guild_id: int = guild.id
        async with self.bot.lock:
            if guild_id not in self.bot.ignored_voice_channels:
                self.bot.ignored_voice_channels[guild_id] = set()

        before_channel: VoiceChannel | StageChannel | None = before.channel
        after_channel:  VoiceChannel | StageChannel | None = after.channel
        before_channel_is_voice: bool = isinstance(before_channel, VoiceChannel)
        after_channel_is_voice: bool = isinstance(after_channel, VoiceChannel)

        if not (before_channel_is_voice or after_channel_is_voice):
            return

        money_for_voice: int = db_commands.get_server_info_value(guild_id=guild_id, key_name="mn_for_voice")
        if not money_for_voice:
            return

        member_id: int = member.id
        if before_channel_is_voice:
            async with self.bot.lock:
                if before_channel.id not in self.bot.ignored_voice_channels[guild_id]:
                    is_continue: bool = True
                else:
                    is_continue: bool = False

            if is_continue:
                await self.process_left_member(
                    member_id=member_id,
                    guild=guild,
                    money_for_voice=money_for_voice,
                    channel_id=before_channel.id
                )

        if after_channel_is_voice:
            async with self.bot.lock:
                if after_channel.id in self.bot.ignored_voice_channels[guild_id]:
                    return

            await self.process_joined_member(
                member_id=member_id,
                member=member,
                guild=guild,
                channel_id=after_channel.id
            ) 

    async def process_left_member(self, member_id: int, guild: Guild, money_for_voice: int, channel_id: int) -> None:
        guild_id: int = guild.id
        async with self.bot.lock:
            if member_id not in self.bot.members_in_voice[guild_id]:
                # If member joined voice channel before the bot startup.
                income: int = await db_commands.register_user_voice_channel_left_with_join_time(
                    guild_id=guild_id,
                    member_id=member_id,
                    money_for_voice=money_for_voice,
                    time_join=self.bot.startup_time
                )
            else:
                self.bot.members_in_voice[guild_id].pop(member_id)
                income: int = await db_commands.register_user_voice_channel_left(
                    guild_id=guild_id,
                    member_id=member_id,
                    money_for_voice=money_for_voice
                )
        
        log_channel_id: int = db_commands.get_server_info_value(guild_id=guild_id, key_name="log_c")
        if log_channel_id and isinstance(log_channel := guild.get_channel(log_channel_id), TextChannel):
            server_lng: int = db_commands.get_server_info_value(guild_id=guild_id, key_name="lang")
            currency: str = db_commands.get_server_currency(guild_id=guild_id)
            await log_channel.send(embed=Embed(
                description=self.voice_handler_text[server_lng][1].format(member_id, channel_id, income, currency)
            ))
    
    async def process_joined_member(self, member_id: int, member: Member, guild: Guild, channel_id: int) -> None:
        # members_in_voice_now will be pointer to the same dict
        guild_id: int = guild.id
        async with self.bot.lock:
            self.bot.members_in_voice[guild_id][member_id] = member
        await db_commands.register_user_voice_channel_join(
            guild_id=guild_id,
            member_id=member_id
        )

        log_channel_id: int = db_commands.get_server_info_value(guild_id=guild_id, key_name="log_c") 
        if log_channel_id and (log_channel := guild.get_channel(log_channel_id)) and isinstance(log_channel, TextChannel):
            server_lng: int = db_commands.get_server_info_value(guild_id=guild_id, key_name="lang")
            await log_channel.send(embed=Embed(
                description=self.voice_handler_text[server_lng][0].format(member_id, channel_id)
            ))


    async def process_member_on_bot_shutdown(self, guild: Guild, member_id: int, member: Member) -> None:
        if not member.voice:
            return

        money_for_voice: int = db_commands.get_server_info_value(guild_id=guild.id, key_name="mn_for_voice")
        if not money_for_voice:
            return

        current_channel: VoiceChannel | StageChannel | None = member.voice.channel
        channel_is_voice: bool = isinstance(current_channel, VoiceChannel)
        if not channel_is_voice:
            return
        
        await db_commands.register_user_voice_channel_left(
            guild_id=guild.id,
            member_id=member_id,
            money_for_voice=money_for_voice
        )


def setup(bot: StoreBot) -> None:
    bot.add_cog(VoiceHandlerCog(bot))

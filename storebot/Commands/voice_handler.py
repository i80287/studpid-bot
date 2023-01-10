from nextcord import VoiceChannel, TextChannel, Member, Guild, Embed
from nextcord.ext.commands import Cog
from nextcord.abc import GuildChannel

from storebot import StoreBot
from Tools import db_commands


class VoiceHandlerCog(Cog):
    voice_handler_text: dict[int, dict[int, str]] = {
        0: {
            0: "**`Member <@{}> joined voice channel <#{}>`**",
            1: "**`Member <@{}> left voice channel <#{}> and gained {}`** {}"
        },
        1: {
            0: "**`Участник <@{}> присоединился к голосовому каналу <#{}>`**",
            1: "**`Участник <@{}> покинул голосовой канал <#{}> и заработал {}`** {}",
        }
    }

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot

    @Cog.listener()
    async def on_guild_channel_update(self, before: GuildChannel, after: GuildChannel) -> None:
        if not (isinstance(before, VoiceChannel) and isinstance(after, VoiceChannel)):
            return
        
        guild: Guild = after.guild
        channel_id: int = after.id
        money_for_voice: int = db_commands.get_server_info_value(guild_id=guild.id, key_name="mn_for_voice")
        if not money_for_voice:
            return

        before_members_ids: frozenset[int] = frozenset(member.id for member in before.members)
        after_members_ids: frozenset[int] = frozenset(member.id for member in after.members)
        
        left_members_ids: frozenset[int] = before_members_ids.__sub__(after_members_ids)
        if left_members_ids:
            await self.process_left_members(
                left_members_ids=left_members_ids,
                guild=guild,
                channel_id=channel_id
            )

        joined_members_ids: frozenset[int] = after_members_ids.__sub__(before_members_ids)
        if joined_members_ids:
            await self.process_joined_members(
                joined_members_ids=joined_members_ids,
                guild=guild,
                channel_id=channel_id
            )

    async def process_left_members(self, left_members_ids: frozenset[int], guild: Guild, money_for_voice: int, channel_id: int) -> None:
        # members_in_voice_now will be pointer to the same dict
        members_in_voice_now: dict[int, Member] = self.bot.members_in_voice
        guild_id: int = guild.id
        log_channel_id: int = db_commands.get_server_info_value(guild_id=guild_id, key_name="log_c")
        if not(log_channel_id and (log_channel := guild.get_channel(log_channel_id)) and isinstance(log_channel, TextChannel)):
            log_channel = None
            server_lng: int = 0
            currency: str = ""
        else:
            server_lng: int = db_commands.get_server_info_value(guild_id=guild_id, key_name="lang")
            currency: str = db_commands.get_server_currency(guild_id=guild_id)
        for member_id in left_members_ids:
            if member_id not in members_in_voice_now:
                # If member joined voice channel before bot startup.
                member: Member | None = guild.get_member(member_id)
                if not member:
                    # If member left server during the method execution.
                    continue
                income: int = db_commands.register_user_voice_channel_left_with_join_time(
                    guild_id=guild_id,
                    member_id=member_id,
                    money_for_voice=money_for_voice,
                    time_join=self.bot.startup_time
                )
            else:
                member: Member = members_in_voice_now.pop(member_id)
                income: int = db_commands.register_user_voice_channel_left(
                    guild_id=guild_id,
                    member_id=member_id,
                    money_for_voice=money_for_voice
                )
            if log_channel:
                await log_channel.send(embed=Embed(
                    description=self.voice_handler_text[server_lng][1].format(member_id, channel_id, income, currency)
                ))
    
    async def process_joined_members(self, joined_members_ids: frozenset[int], guild: Guild, channel_id: int) -> None:
        # members_in_voice_now will be pointer to the same dict
        guild_id: int = guild.id
        members_in_voice_now: dict[int, Member] = self.bot.members_in_voice
        log_channel_id: int = db_commands.get_server_info_value(guild_id=guild_id, key_name="log_c")
        if not(log_channel_id and (log_channel := guild.get_channel(log_channel_id)) and isinstance(log_channel, TextChannel)):
            log_channel = None
            server_lng: int = 0
        else:
            server_lng: int = db_commands.get_server_info_value(guild_id=guild_id, key_name="lang")
        for member_id in joined_members_ids:
            member: Member | None = guild.get_member(member_id)
            if not member:
                # if member accidentally left guild during the method execution. 
                if member_id in members_in_voice_now:
                    members_in_voice_now.pop(member_id)
                continue
            members_in_voice_now[member_id] = member
            db_commands.register_user_voice_channel_join(
                guild_id=guild_id,
                member_id=member_id
            )
            if log_channel:
                await log_channel.send(embed=Embed(
                    description=self.voice_handler_text[server_lng][0].format(member_id, channel_id)
                ))


def setup(bot: StoreBot) -> None:
    bot.add_cog(VoiceHandlerCog(bot))

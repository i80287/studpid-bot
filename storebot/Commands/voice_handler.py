from nextcord import VoiceChannel, Member, Guild
from nextcord.ext.commands import Cog
from nextcord.abc import GuildChannel

from storebot import StoreBot
from Tools import db_commands


class VoiceHandlerCog(Cog):
    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot

    @Cog.listener()
    async def on_guild_channel_update(self, before: GuildChannel, after: GuildChannel) -> None:
        if not (isinstance(before, VoiceChannel) and isinstance(after, VoiceChannel)):
            return
        
        guild: Guild = after.guild
        before_members_ids: frozenset[int] = frozenset(member.id for member in before.members)
        after_members_ids: frozenset[int] = frozenset(member.id for member in after.members)
        
        left_members_ids: frozenset[int] = before_members_ids.__sub__(after_members_ids)
        if left_members_ids:
            self.process_left_members(left_members_ids=left_members_ids, guild_id=guild.id)

        joined_members_ids: frozenset[int] = after_members_ids.__sub__(before_members_ids)
        if joined_members_ids:
            self.process_joined_members(joined_members_ids=joined_members_ids, guild=guild)

    def process_left_members(self, left_members_ids: frozenset[int], guild_id: int) -> None:
        # members_in_voice_now will be pointer to the same dict
        members_in_voice_now: dict[int, Member] = self.bot.members_in_voice
        for member_id in left_members_ids:
            if member_id not in members_in_voice_now:
                continue
            members_in_voice_now.pop(member_id)
            db_commands.register_user_voice_channel_left(guild_id=guild_id, member_id=member_id)
    
    def process_joined_members(self, joined_members_ids: frozenset[int], guild: Guild) -> None:
        # members_in_voice_now will be pointer to the same dict
        guild_id: int = guild.id
        members_in_voice_now: dict[int, Member] = self.bot.members_in_voice
        for member_id in joined_members_ids:
            member: Member | None = guild.get_member(member_id)
            if not member:
                # if member accidentally left guild during the method execution. 
                if member_id in members_in_voice_now:
                    members_in_voice_now.pop(member_id)
                continue
            members_in_voice_now[member_id] = member
            db_commands.register_user_voice_channel_join(guild_id=guild_id, member_id=member_id)


def setup(bot: StoreBot) -> None:
    bot.add_cog(VoiceHandlerCog(bot))

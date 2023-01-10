from nextcord import VoiceChannel, Member, Guild
from nextcord.ext.commands import Cog
from nextcord.abc import GuildChannel

from storebot import StoreBot
from Variables.vars import path_to
from config import DEBUG


class VoiceHandlerCog(Cog):
    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot
        self._backup.start()

    @Cog.listener()
    async def on_guild_channel_update(self, before: GuildChannel, after: GuildChannel):
        if not (isinstance(before, VoiceChannel) and isinstance(after, VoiceChannel)):
            return
        
        before_members_ids = {member.id for member in before.members}
        after_members_ids = {member.id for member in after.members}

        left_members_ids = before_members_ids - after_members_ids
        joined_members_ids = after_members_ids - before_members_ids
        for member_id in left_members_ids:
            # TODO: check whether member_id is in the dict
            member: Member = self.bot.members_in_voice.pop(member_id)
            # TODO: calculate user's voice activity length
        guild: Guild = after.guild
        for member_id in joined_members_ids:
            # TODO: check whether member_id isn't in the dict
            self.bot.members_in_voice["member_id"] = guild.get_member(member_id)
            # TODO: add user join to the database


def setup(bot: StoreBot) -> None:
    bot.add_cog(VoiceHandlerCog(bot))

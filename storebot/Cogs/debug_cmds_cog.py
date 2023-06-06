from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nextcord import Guild

    from ..storebot import StoreBot

from asyncio import sleep
from os import path

from nextcord import (
    Embed,
    Game,
    Status,
    TextChannel
)
from nextcord.ext.commands import command, is_owner, Cog, Context

from ..constants import CWD_PATH

class DebugCommandsCog(Cog):
    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot

    @command(name="lst") # type: ignore
    @is_owner()
    async def lst(self, ctx: Context) -> None:
        await ctx.reply(
            embed=Embed(description="`fb_channel` `text channel`\n"
                                    "`load` `extension`\n"
                                    "`unload` `extension`\n"
                                    "`reload` `extension`\n"
                                    "`statistics`\n"
                                    "`update_status` [`any text` | `default`]\n"
                                    "`shutdown`\n"
                                    "`guild_info` `guild_id`\n"
                                    "`guild_member_info` `guild_id` `member_id`\n"
                                    "`check_db` `guild_id`"),
            mention_author=False
        )

    @command(name="fb_channel") # type: ignore
    @is_owner()
    async def fb_channel(self, ctx: Context, channel: TextChannel) -> None:
        channel_id: int = channel.id
        self.bot.bot_feedback_channel = channel_id
        await ctx.reply(
            embed=Embed(description=f"New feedback channel is <#{channel_id}>"),
            mention_author=False,
            delete_after=10.0
        )

    @command(name="load") # type: ignore
    @is_owner()
    async def load(self, ctx: Context, extension) -> None:
        if path.exists(CWD_PATH + f"/Cogs/{extension}.py"):
            bot = self.bot
            async with bot.text_lock:
                async with bot.voice_lock:
                    async with bot.statistic_lock:
                        async with bot.bot_added_roles_lock:
                            async with bot.bot_removed_roles_lock:
                                self.bot.load_extension(f"storebot.Cogs.{extension}")
            await sleep(1.0)
            await bot.sync_all_application_commands()
            await sleep(1.0)
            emb: Embed = Embed(description=f"**Loaded `{extension}`**")
        else:
            emb: Embed = Embed(description=f"**`{extension}` not found**")

        await ctx.reply(embed=emb, mention_author=False, delete_after=10.0)
    
    @command(name="unload") # type: ignore
    @is_owner()
    async def unload(self, ctx: Context, extension) -> None:
        if path.exists(CWD_PATH + f"/Cogs/{extension}.py"):
            bot = self.bot
            async with bot.text_lock:
                async with bot.voice_lock:
                    async with bot.statistic_lock:
                        async with bot.bot_added_roles_lock:
                            async with bot.bot_removed_roles_lock:
                                bot.unload_extension(f"storebot.Cogs.{extension}")

            await sleep(1.0)
            await bot.sync_all_application_commands()
            await sleep(1.0)
            emb: Embed = Embed(description=f"**`Unloaded {extension}`**")
        else:
            emb: Embed = Embed(description=f"**`{extension} not found`**")

        await ctx.reply(embed=emb, mention_author=False, delete_after=10.0)

    @command(name="reload") # type: ignore
    @is_owner()
    async def reload(self, ctx: Context, extension) -> None:
        if path.exists(CWD_PATH + f"/Cogs/{extension}.py"):
            bot = self.bot
            await ctx.reply(embed=Embed(description="**`Started reloading`**"), mention_author=False, delete_after=10.0)
            
            async with bot.text_lock:
                async with bot.voice_lock:
                    async with bot.statistic_lock:
                        async with bot.bot_added_roles_lock:
                            async with bot.bot_removed_roles_lock:
                                bot.unload_extension(f"storebot.Cogs.{extension}")
                                bot.load_extension(f"storebot.Cogs.{extension}")
            
            await sleep(1.0)
            await bot.sync_all_application_commands()
            await sleep(1.0)
            emb: Embed = Embed(description=f"**`Reloaded {extension}`**")
        else:
            emb: Embed = Embed(description=f"**`{extension}` not found**")

        await ctx.reply(embed=emb, mention_author=False, delete_after=10.0)

    @command(aliases=["statistics"]) # type: ignore
    @is_owner()
    async def statistic(self, ctx: Context) -> None:
        guilds: list[Guild] = self.bot.guilds.copy()
        lines: list[str] = ["```guild - id - member_count```"]
        members_count: int = 0
        async with self.bot.statistic_lock:
            for guild in guilds:
                if member_count := guild.member_count:
                    members_count += member_count
                lines.append(fr"{{{guild.name} }}-{{{guild.id}}}-{{{member_count}}}-{{{guild.owner_id}}}")

            lines.extend((
                f"\n**`Total guilds: {len(guilds)}`**",
                f"\n**`Currently active polls: {len(self.bot.current_polls)}`**",
                f"\n**`Members count: {members_count}`**",
            ))

        half_size = len(lines) >> 1
        quat_size = half_size >> 1
        await ctx.reply(
            embed=Embed(description='\n'.join(lines[:quat_size])),
            mention_author=False,
            delete_after=30.0
        )
        await sleep(0.5)

        await ctx.reply(
            embed=Embed(description='\n'.join(lines[quat_size:half_size])),
            mention_author=False,
            delete_after=30.0
        )
        await sleep(0.5)

        quat_size += half_size
        await ctx.reply(
            embed=Embed(description='\n'.join(lines[half_size:quat_size])),
            mention_author=False,
            delete_after=30.0
        )
        await sleep(0.5)

        await ctx.reply(
            embed=Embed(description='\n'.join(lines[quat_size:])),
            mention_author=False,
            delete_after=30.0
        )

    @command(name="update_status") # type: ignore
    @is_owner()
    async def update_status(self, ctx: Context, *text) -> None:
        if not text or text[0] == "default":
            await self.bot.change_presence(activity=Game(f"/help on {len(self.bot.guilds)} servers"), status=Status.online)
        else:
            await self.bot.change_presence(activity=Game(' '.join(text)), status=Status.dnd)
        await ctx.reply(embed=Embed(description=f"**`Changed status to {' '.join(text)}`**"), mention_author=False)

    @command(name="shutdown") # type: ignore
    @is_owner()
    async def shutdown(self, ctx: Context) -> None:
        cog: Cog | None = self.bot.cogs.get("VoiceHandlerCog")

        from storebot.Cogs.voice_handler import VoiceHandlerCog
        if not isinstance(cog, VoiceHandlerCog):
            return

        invoice_members_count: int = 0
        bot = self.bot
        async with bot.voice_lock:
            members_in_voice = bot.members_in_voice
            for guild_id, members_dict in members_in_voice.items():
                if (guild := bot.get_guild(guild_id)) is not None:
                    await cog.process_member_on_bot_shutdown(guild, members_dict)
                    invoice_members_count += len(members_dict)
                    members_in_voice[guild_id] = {}

        await ctx.reply(embed=Embed(description=f"**`Processed {invoice_members_count} members`**"), mention_author=False)

    @command(name="guild_info") # type: ignore
    @is_owner()
    async def guild_info(self, ctx: Context, guild_id: int) -> None:
        if (guild := self.bot.get_guild(guild_id)) is None:
            await ctx.reply(embed=Embed(description="**`Guild not found`**"), mention_author=False)
            return

        report: list[str] = [f"**`Got guild: {guild_id}:" + guild.name + f"`**\n**`Members count: {guild.member_count}`**"]
        if (owner := guild.owner) is not None:
            report.append(f"**`Owner: {owner.id}:" + owner.name+ "`**")

        bot = self.bot
        async with bot.voice_lock:
            if (guild_dict := bot.members_in_voice.get(guild_id)) is not None:
                if guild_dict:
                    report.append("**`Guild members in voice:`**")
                    report.extend(f"**`{member.id}:{member.name}`**" for member in guild_dict.values())
                else:
                    report.append("**`No guild members are in voice now`**")

        if (lines_count := len(report)) <= 64:
            await ctx.reply(embed=Embed(description='\n'.join(report)), mention_author=False)
            return

        half_lines = lines_count >> 1
        await ctx.reply(embed=Embed(description='\n'.join(report[:half_lines])), mention_author=False)
        await ctx.reply(embed=Embed(description='\n'.join(report[half_lines:])), mention_author=False)

    @command(name="guild_member_info") # type: ignore
    @is_owner()
    async def guild_member_info(self, ctx: Context, guild_id: int, member_id: int) -> None:
        if (guild := self.bot.get_guild(guild_id)) is None:
            await ctx.reply(embed=Embed(description="**`Guild not found`**"), mention_author=False)
            return

        if (member := guild.get_member(member_id)) is None:
            await ctx.reply(embed=Embed(description="**`Member not found`**"), mention_author=False)
            return

        report: list[str] = [
            f"**`Got guild: {guild_id}:" + guild.name + "`**",
            f"**`Got member: {member_id}:" + member.name + "`**"
        ]
        if (owner := guild.owner) is not None:
            report.append(f"**`Guild owner: {owner.id}:" + owner.name + "`**")
        
        report.append("**`Member roles:`**")
        report.extend(map(lambda role: f"**`{role.id}:" + role.name + "`**", member.roles))

        await ctx.reply(embed=Embed(description='\n'.join(report)), mention_author=False)

    @command(name="check_db") # type: ignore
    @is_owner()
    async def check_db_command(self, ctx: Context, guild_id: int) -> None:
        try:
            from ..Tools.db_commands import check_db
            from os import mkdir

            str_guild_id = str(guild_id)
            db_path: str = CWD_PATH + f"/bases/bases_{str_guild_id}/"
            if not path.exists(db_path):
                mkdir(db_path)

            logs_path: str = CWD_PATH + f"/logs/logs_{str_guild_id}/"
            if not path.exists(logs_path):
                mkdir(logs_path)

            check_db(guild_id, None)
            await ctx.reply(embed=Embed(description=f"**`Updated info for the guild {guild_id}`**"), mention_author=False)
        except Exception as ex:
            await ctx.reply(embed=Embed(description=f"Exception occured: {ex} : {ex!r}"), mention_author=False)

def setup(bot: StoreBot) -> None:
    bot.add_cog(DebugCommandsCog(bot))

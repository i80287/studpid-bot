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

    @command(name="fb_channel") # type: ignore
    @is_owner()
    async def fb_channel(self, ctx: Context, chnl: TextChannel) -> None:
        self.bot.bot_feedback_channel = chnl.id
        await ctx.reply(embed=Embed(description=f"New feedback channel is <#{chnl.id}>"), mention_author=False, delete_after=10.0)

    @command(name="load") # type: ignore
    @is_owner()
    async def load(self, ctx: Context, extension) -> None:
        if path.exists(CWD_PATH + f"storebot/Cogs/{extension}.py"):
            async with self.bot.text_lock:
                async with self.bot.voice_lock:
                    async with self.bot.statistic_lock:
                        self.bot.load_extension(f"storebot.Cogs.{extension}")
            await sleep(1.0)
            await self.bot.sync_all_application_commands()
            await sleep(1.0)
            emb: Embed = Embed(description=f"**Loaded `{extension}`**")
        else:
            emb: Embed = Embed(description=f"**`{extension}` not found**")
        await ctx.reply(embed=emb, mention_author=False, delete_after=10.0)
    
    @command(name="unload") # type: ignore
    @is_owner()
    async def unload(self, ctx: Context, extension) -> None:
        if path.exists(CWD_PATH + f"storebot/Cogs/{extension}.py"):
            async with self.bot.text_lock:
                async with self.bot.voice_lock:
                    async with self.bot.statistic_lock:
                        self.bot.unload_extension(f"storebot.Cogs.{extension}")
            await sleep(1.0)
            await self.bot.sync_all_application_commands()
            await sleep(1.0)
            emb: Embed = Embed(description=f"**`Unloaded {extension}`**")
        else:
            emb: Embed = Embed(description=f"**`{extension} not found`**")
        await ctx.reply(embed=emb, mention_author=False, delete_after=10.0)

    @command(name="reload") # type: ignore
    @is_owner()
    async def reload(self, ctx: Context, extension) -> None:
        if path.exists(CWD_PATH + f"storebot/Cogs/{extension}.py"):
            await ctx.reply(embed=Embed(description="**`Started reloading`**"), mention_author=False, delete_after=10.0)
            async with self.bot.text_lock:
                async with self.bot.voice_lock:
                    async with self.bot.statistic_lock:
                        self.bot.unload_extension(f"storebot.Cogs.{extension}")
                        self.bot.load_extension(f"storebot.Cogs.{extension}")
            await sleep(1.0)
            await self.bot.sync_all_application_commands()
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
        
        half_size: int = len(lines) >> 1

        emb1: Embed = Embed(description='\n'.join(lines[:half_size]))
        emb2: Embed = Embed(description='\n'.join(lines[half_size:]))
        await ctx.reply(embed=emb1, mention_author=False, delete_after=20.0)
        await ctx.reply(embed=emb2, mention_author=False, delete_after=20.0)

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
        
        k: int = 0
        async with self.bot.voice_lock:
            for guild_id, members_dict in self.bot.members_in_voice.items():
                guild: Guild | None = self.bot.get_guild(guild_id)
                if not guild:
                    continue
                for member_id, member in members_dict.items():
                    await cog.process_member_on_bot_shutdown(
                        guild=guild,
                        member_id=member_id,
                        member=member
                    )
                    k += 1
                self.bot.members_in_voice[guild_id] = {}

        await ctx.reply(embed=Embed(description=f"**`Processed {k} members`**"), mention_author=False)

def setup(bot: StoreBot) -> None:
    bot.add_cog(DebugCommandsCog(bot))

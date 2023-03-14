from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import (
        Callable,
        Literal,
    )

    from nextcord import (
        Role,
        Guild,
        Message
    )
    from nextcord.ext.commands import Context

    from ..storebot import StoreBot

import re
from sqlite3 import connect
from contextlib import closing
from os import path, mkdir
from asyncio import sleep

from nextcord import (
    Game,
    Embed,
    Member,
    TextChannel,
    Interaction
)
from nextcord.errors import ApplicationCheckFailure
from nextcord.ext.commands import Cog
from nextcord.ext import tasks

from .text_cmds_cog import TextComandsCog
from ..Tools.logger import Logger
from ..Tools.db_commands import (
    check_db,
    make_backup,
    process_salary_roles,
    check_member_level_async,
)
from ..constants import CWD_PATH, DB_PATH


command_match: Callable[[str, int, int], re.Match[str] | None] = re.compile(r"^(!work)|(!collect)", re.RegexFlag.IGNORECASE).match

class EventsHandlerCog(Cog):
    event_handl_text: dict[int, dict[int, str]] = {
        0: {
            0: "**`Sorry, but you don't have enough permissions to use this command`**",
        },
        1: {
            0: "**`Извините, но у Вас недостаточно прав для использования этой команды`**",
        },
    }
    greetings: tuple[str, str] = (
        "Thanks for adding bot!\nUse **`/guide`** to see guide about bot's system\n**`/settings`** to manage bot\nand **`/help`** to see available commands",
        "Благодарим за добавление бота!\nИспользуйте **`/guide`** для просмотра гайда о системе бота\n**`/settings`** для управления ботом\nи **`/help`** для просмотра доступных команд",
    )
    new_level_text: dict[int, dict[int, str]] = {
        0: {
            0: "New level!",
            1: "{}, you raised level to **{}**!",
        },
        1: {
            0: "Новый уровень!",
            1: "{}, Вы подняли уровень до **{}**!",
        }
    }

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot
        self.salary_roles_task.start()
        self.backup_task.start()

    @classmethod
    async def send_first_message(cls, guild: Guild, embed: Embed) -> list[Exception]:
        exceptions: list[Exception] = []
        guild_me: Member = guild.me
        for channel in guild.text_channels:
            permission: bool = False
            try:
                permission = channel.permissions_for(guild_me).send_messages
            except Exception as ex:
                exceptions.append(PermissionError("Error while seeking permissions"))
                exceptions.append(ex)
                continue
            if permission:
                try:
                    await channel.send(embed=embed)
                    return exceptions
                except Exception as ex:
                    exceptions.append(ex)
                    continue
        
        return exceptions

    @Cog.listener()
    async def on_connect(self) -> None:
        await Logger.write_log_async("common_logs.log", "on_connect")
    
    @Cog.listener()
    async def on_ready(self) -> None:
        if not path.exists(CWD_PATH + "/bases/"):
            mkdir(CWD_PATH + "/bases/")
        if not path.exists(CWD_PATH + "/logs/"):
            mkdir(CWD_PATH + "/logs/")

        guilds: list[Guild] = self.bot.guilds.copy()
        for guild in guilds:
            guild_id: int = guild.id
            str_guild_id: str = str(guild_id)
            
            if not path.exists(f"{CWD_PATH}/bases/bases_{str_guild_id}/"):
                mkdir(f"{CWD_PATH}/bases/bases_{str_guild_id}/")
            if not path.exists(f"{CWD_PATH}/logs/logs_{str_guild_id}/"):
                mkdir(f"{CWD_PATH}/logs/logs_{str_guild_id}/")

            db_ignored_channels_data: list[tuple[int, int, int]] = check_db(guild_id, guild.preferred_locale)
            async with self.bot.voice_lock:
                self.bot.members_in_voice[guild_id] = {}
                self.bot.ignored_voice_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[2]}
            async with self.bot.text_lock:
                self.bot.ignored_text_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[1]}

            await Logger.write_log_async("common_logs.log", "correct_db func", str_guild_id, guild.name)

        from ..config import DEBUG
        if DEBUG:
            print("[>>>]Logged into Discord as {0.user}".format(self.bot))

        guilds_len_str: str = str(len(guilds))
        await self.bot.change_presence(activity=Game(f"/help on {guilds_len_str} servers"))
        await Logger.write_log_async("common_logs.log", "on_ready", f"total {guilds_len_str} guilds")

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        guild_id: int = guild.id
        
        # discord abusers
        if guild_id in {260978723455631373, 1068135541360578590}:
            await guild.leave()
            return

        str_guild_id: str = str(guild_id)
        if not path.exists(CWD_PATH + "/bases/bases_{0}/".format(str_guild_id)):
            mkdir(CWD_PATH + "/bases/bases_{0}/".format(str_guild_id))
        if not path.exists(CWD_PATH + "/logs/logs_{0}/".format(str_guild_id)):
            mkdir(CWD_PATH + "/logs/logs_{0}/".format(str_guild_id))

        guild_locale: str | None = guild.preferred_locale
        db_ignored_channels_data: list[tuple[int, int, int]] = check_db(guild_id, guild_locale)
        guild_name: str = guild.name
        await Logger.write_log_async("common_logs.log", "correct_db func", str_guild_id, guild_name)
        async with self.bot.voice_lock:
            self.bot.members_in_voice[guild_id] = {}
            self.bot.ignored_voice_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[2]}
        async with self.bot.text_lock:
            self.bot.ignored_text_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[1]}
        
        exceptions: list[Exception]
        try:
            exceptions = await self.send_first_message(
                guild,
                Embed(description=self.greetings[1 if guild_locale and "ru" in guild_locale else 0])
            )
        except Exception as ex:
            exceptions = [ex]
        
        for ex in exceptions:
            await Logger.write_one_log_async(
                filename="error.log",
                report=f"[FATAL] [ERROR] [send_first_message] [guild: {str_guild_id}:{guild_name}] [{str(ex)}:{ex:!r}]\n"
            )

        await Logger.write_log_async("guild.log", "guild_join", str_guild_id, guild_name)
        await Logger.write_log_async("common_logs.log", "guild_join", str_guild_id, guild_name)
        await Logger.write_guild_log_async(
            filename="guild.log",
            guild_id=guild_id,
            report=f"[guild_join] [guild: {str_guild_id}:{guild_name}]"
        )

        await self.bot.change_presence(activity=Game(f"/help on {len(self.bot.guilds)} servers"))

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        guild_id: int = guild.id

        # discord abusers
        if guild_id in {260978723455631373, 1068135541360578590}:
            return

        await Logger.write_log_async("guild", "guild_remove", str(guild_id), str(guild.name))
        await Logger.write_log_async("common_logs", "guild_remove", str(guild_id), str(guild.name))
        
        await self.bot.change_presence(activity=Game(f"/help on {len(self.bot.guilds)} servers"))
        async with self.bot.voice_lock:
            del self.bot.members_in_voice[guild_id]
            del self.bot.ignored_voice_channels[guild_id]
        async with self.bot.text_lock:
            del self.bot.ignored_text_channels[guild_id]
    
    @tasks.loop(seconds=180.0)
    async def salary_roles_task(self) -> None:
        for guild in self.bot.guilds.copy():
            await process_salary_roles(guild.id)
            await sleep(1.0)
    
    @salary_roles_task.before_loop
    async def before_timer(self) -> None:
        await self.bot.wait_until_ready()

    @tasks.loop(hours=2.0)
    async def backup_task(self) -> None:
        for guild in self.bot.guilds.copy():
            await make_backup(guild.id)
            await sleep(1.0)

    @backup_task.before_loop
    async def before_timer_backup(self) -> None:
        await self.bot.wait_until_ready()

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        #or message.type is MessageType.chat_input_command
        if not isinstance(member := message.author, Member) or member.bot:
            return

        assert message.guild is not None
        guild: Guild = message.guild
        g_id: int = guild.id

        if g_id in {1058854571239280721, 1057747986349821984, 750708076029673493, 863462268402532363} \
            and command_match(message.content, 0, 8) is not None:
            await TextComandsCog.work_command(await self.bot.get_context(message))
            return

        async with self.bot.text_lock:
            ignored_text_channels: dict[int, set[int]] = self.bot.ignored_text_channels
            if g_id in ignored_text_channels:
                if message.channel.id in ignored_text_channels[g_id]:
                    return
            else:
                ignored_text_channels[g_id] = set()

        new_level: int = await check_member_level_async(guild_id=g_id, member_id=member.id)
        if not new_level:
            return

        with closing(connect(DB_PATH.format(g_id))) as base:
            with closing(base.cursor()) as cur:
                channel_id: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lvl_c';").fetchone()[0]
                if channel_id and isinstance(channel := guild.get_channel(channel_id), TextChannel):
                    lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang';").fetchone()[0]
                    emb: Embed = Embed(title=self.new_level_text[lng][0], description=self.new_level_text[lng][1].format(member.mention, new_level))
                    await channel.send(embed=emb)

                db_lvl_rls: list[tuple[int, int]] | list = cur.execute("SELECT level, role_id FROM rank_roles ORDER BY level").fetchall()
                
        if not db_lvl_rls:
            return

        lvl_rls: dict[int, int] = {k: v for k, v in db_lvl_rls}
        if new_level in lvl_rls:
            levels: list[int] = [tup[0] for tup in db_lvl_rls]
            del db_lvl_rls

            guild_roles: dict[int, Role] = guild._roles.copy()
            memb_roles: set[int] = {role_id for role_id in member._roles if role_id in guild_roles}

            new_level_role_id: int = lvl_rls[new_level]
            if new_level_role_id not in memb_roles and (role := guild_roles.get(new_level_role_id)):
                try: 
                    await member.add_roles(role, reason=f"Member gained new level {new_level}")
                except: 
                    pass

            # Bin search, realized in Python, will be slower here, as predicted ~ len(new_level_index) < 32 (very small)
            new_level_index: int = levels.index(new_level)
            if new_level_index and ((old_role_id := lvl_rls[levels[new_level_index-1]]) in memb_roles) and (role := guild_roles.get(old_role_id)):
                try: 
                    await member.remove_roles(role, reason=f"Member gained new level {new_level}")
                except: 
                    pass

    @Cog.listener()
    async def on_application_command_error(self, interaction: Interaction, exception) -> None:
        if isinstance(exception, ApplicationCheckFailure):
            assert interaction.locale is not None
            lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=self.event_handl_text[lng][0]), ephemeral=True)
            return

        guild_report: str = f"[{guild.id}] [{guild.name}] " if (guild := interaction.guild) else ""
        command_report: str = f"[{interaction.application_command.name}] " if interaction.application_command else ""
        report: str = f"[ERROR] [slash_command] {command_report}{guild_report}[{str(exception)}]"
        await Logger.write_one_log_async(filename="error.log", report=report)

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error) -> None:
        lines: list[str] = ["[ERROR]"]
        if (member := ctx.author):
            lines.append(f"[member: {member.id}:{member.name}]")
        if (guild := ctx.guild):
            lines.append(f"[guild: {guild.id}:{guild.name}]")
        lines.append('[' + str(error) + ']')
        
        await Logger.write_one_log_async(filename="error.log", report=' '.join(lines))


def setup(bot: StoreBot) -> None:
    bot.add_cog(EventsHandlerCog(bot))

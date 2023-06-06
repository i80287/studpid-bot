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
from ..Tools.logger import (
    write_guild_log_async,
    write_log_async,
    write_one_log_async
)
from ..Tools.db_commands import (
    check_db,
    make_backup,
    process_salary_roles,
    check_member_level_async,
    get_server_info_value_async,
    get_server_lvllog_info_async,
    add_member_role_async,
    remove_member_role_async
)
from ..constants import CWD_PATH, DB_PATH


_command_match: Callable[[str, int, int], re.Match[str] | None] = re.compile(r"^(!work)|(!collect)", re.RegexFlag.IGNORECASE).match

class EventsHandlerCog(Cog):
    event_handl_text: tuple[str, str] = (
        "**`Sorry, but you don't have enough permissions to use this command`**",
        "**`Извините, но у Вас недостаточно прав для использования этой команды`**",
    )
    greetings: tuple[str, str] = (
        "Thanks for adding bot!\nUse **`/guide`** to see guide about bot's system\n**`/settings`** to manage bot\nand **`/help`** to see available commands",
        "Благодарим за добавление бота!\nИспользуйте **`/guide`** для просмотра гайда о системе бота\n**`/settings`** для управления ботом\nи **`/help`** для просмотра доступных команд",
    )
    new_level_text: tuple[tuple[str, str], tuple[str, str]] = (
        (
            "New level!",
            "{}, you raised level to **{}**!",
        ),
        (
            "Новый уровень!",
            "{}, Вы подняли уровень до **{}**!",
        )
    )

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
        await write_log_async("common_logs.log", "on_connect")

    @staticmethod
    async def _process_guilds(bot: StoreBot, guilds: list[Guild]) -> None:
        for guild in guilds:
            guild_id: int = guild.id
            str_guild_id: str = str(guild_id)

            db_path: str = CWD_PATH + f"/bases/bases_{str_guild_id}/"
            if not path.exists(db_path):
                mkdir(db_path)

            logs_path: str = CWD_PATH + f"/logs/logs_{str_guild_id}/"
            if not path.exists(logs_path):
                mkdir(logs_path)

            db_ignored_channels_data: list[tuple[int, int, int]] = check_db(guild_id, guild.preferred_locale)
            async with bot.voice_lock:
                bot.members_in_voice[guild_id] = {}
                bot.ignored_voice_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[2]}
            async with bot.text_lock:
                bot.ignored_text_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[1]}

            # Does not cached when set to 0
            if (member_join_remove_channel_id := await get_server_info_value_async(guild_id, "memb_join_rem_chnl")):
                async with bot.member_join_remove_lock:
                    bot.join_remove_message_channels[guild_id] = member_join_remove_channel_id

            await write_log_async("common_logs.log", "correct_db func", str_guild_id, guild.name)

    @Cog.listener()
    async def on_ready(self) -> None:
        db_path: str = CWD_PATH + "/bases/"
        if not path.exists(db_path):
            mkdir(db_path)

        logs_path: str = CWD_PATH + "/logs/"
        if not path.exists(logs_path):
            mkdir(logs_path)

        bot: StoreBot = self.bot
        bot_guilds: list[Guild] = bot.guilds
        guilds: list[Guild] = bot_guilds.copy()
        await self._process_guilds(bot, guilds)
        if len(guilds) != len(bot_guilds):
            await self._process_guilds(bot, bot_guilds.copy())
            await write_one_log_async(
                filename="error.log",
                report=f"[WARNING] [guilds count changed during the on_ready execution]"
            )

        from ..config import DEBUG
        if DEBUG:
            print("[>>>]Logged into Discord as {0.user}".format(bot))

        guilds_len_str: str = str(len(guilds))
        await bot.change_presence(activity=Game(f"/help on {guilds_len_str} servers"))
        await write_log_async("common_logs.log", "on_ready", f"total {guilds_len_str} guilds; startup time: {bot.startup_time}")

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        guild_id: int = guild.id

        # discord abusers
        if guild_id in {260978723455631373, 1068135541360578590}:
            await guild.leave()
            return

        str_guild_id: str = str(guild_id)
        db_path: str = CWD_PATH + f"/bases/bases_{str_guild_id}"
        if not path.exists(db_path):
            mkdir(db_path)
        del db_path

        logs_path: str = CWD_PATH + f"/logs/logs_{str_guild_id}/"
        if not path.exists(logs_path):
            mkdir(logs_path)
        del logs_path

        guild_locale: str | None = guild.preferred_locale
        db_ignored_channels_data: list[tuple[int, int, int]] = check_db(guild_id, guild_locale)
        guild_name: str = guild.name
        await write_log_async("common_logs.log", "correct_db func", str_guild_id, guild_name)
        bot: StoreBot = self.bot
        async with bot.voice_lock:
            bot.members_in_voice[guild_id] = {}
            bot.ignored_voice_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[2]}
        async with bot.text_lock:
            bot.ignored_text_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[1]}

        # Does not cached when set to 0
        if (member_join_remove_channel_id := await get_server_info_value_async(guild_id, "memb_join_rem_chnl")):
            async with bot.member_join_remove_lock:
                bot.join_remove_message_channels[guild_id] = member_join_remove_channel_id

        exceptions: list[Exception]
        try:
            exceptions = await self.send_first_message(
                guild,
                Embed(description=self.greetings[1 if guild_locale and "ru" in guild_locale else 0])
            )
        except Exception as ex:
            exceptions = [ex]

        for ex in exceptions:
            await write_one_log_async(
                filename="error.log",
                report=f"[FATAL] [ERROR] [send_first_message] [guild: {str_guild_id}:{guild_name}] [{ex} : {ex!r}]"
            )

        await write_log_async("guild.log", "guild_join", str_guild_id, guild_name)
        await write_log_async("common_logs.log", "guild_join", str_guild_id, guild_name)
        await write_guild_log_async(
            "guild.log",
            guild_id,
            f"[guild_join] [guild: {str_guild_id}:{guild_name}]"
        )

        await bot.change_presence(activity=Game(f"/help on {len(bot.guilds)} servers"))

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        guild_id: int = guild.id

        # discord abusers
        if guild_id in {260978723455631373, 1068135541360578590}:
            return

        await write_log_async("guild.log", "guild_remove", str(guild_id), str(guild.name))
        await write_log_async("common_logs.log", "guild_remove", str(guild_id), str(guild.name))

        bot: StoreBot = self.bot
        await bot.change_presence(activity=Game(f"/help on {len(bot.guilds)} servers"))
        async with bot.voice_lock:
            if guild_id in bot.members_in_voice:
                del bot.members_in_voice[guild_id]
            if guild_id in bot.ignored_voice_channels:
                del bot.ignored_voice_channels[guild_id]
        async with bot.text_lock:
            if guild_id in bot.ignored_text_channels:
                del bot.ignored_text_channels[guild_id]
        
        async with bot.member_join_remove_lock:
            if guild_id in bot.join_remove_message_channels:
                del bot.join_remove_message_channels[guild_id]

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
        bot = self.bot

        if g_id in {1058854571239280721, 1057747986349821984, 750708076029673493, 863462268402532363} \
            and _command_match(message.content, 0, 8) is not None:
            await TextComandsCog.work_command(await bot.get_context(message))
            return

        async with bot.text_lock:
            ignored_text_channels = bot.ignored_text_channels
            if g_id in ignored_text_channels:
                if message.channel.id in ignored_text_channels[g_id]:
                    return
            else:
                ignored_text_channels[g_id] = set()

        new_level: int = await check_member_level_async(g_id, member.id)
        if not new_level:
            return

        await self.process_new_lvl(guild, member, new_level, bot)

    @classmethod
    async def process_new_lvl(cls, guild: Guild, member: Member, new_level: int, bot: StoreBot) -> None:
        assert isinstance(new_level, int) and new_level != 0
        guild_id = guild.id
        res: tuple[list[tuple[int, int]], int, int] | list[tuple[int, int]] = await get_server_lvllog_info_async(guild_id)
        if isinstance(res, tuple):
            db_lvl_rls, channel_id, server_lng = res
            if isinstance(channel := guild.get_channel(channel_id), TextChannel):
                new_lvl_text: tuple[str, str] = cls.new_level_text[server_lng]
                assert len(new_lvl_text) >= 2
                emb: Embed = Embed(title=new_lvl_text[0], description=new_lvl_text[1].format(member.mention, new_level))
                try:
                    await channel.send(embed=emb)
                except Exception as ex:
                    await write_one_log_async(
                        "error.log",
                        f"[WARNING] [guild: {guild_id}:{guild.name}] [was not able to send new level message in on_message] [{ex} : {ex!r}]"
                    )
        else:
            db_lvl_rls = res

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
                async with bot.bot_added_roles_lock:
                    bot.bot_added_roles_queue.put_nowait(new_level_role_id)
                try: 
                    await member.add_roles(role, reason=f"Member gained new level {new_level}")
                    await add_member_role_async(guild_id, member.id, new_level_role_id)
                except:
                    pass

            # Bin search, realized in Python, will be slower here, as predicted ~ len(new_level_index) < 32 (very small)
            new_level_index: int = levels.index(new_level)
            if new_level_index and ((old_role_id := lvl_rls[levels[new_level_index-1]]) in memb_roles) and (role := guild_roles.get(old_role_id)):
                async with bot.bot_removed_roles_lock:
                    bot.bot_removed_roles_queue.put_nowait(old_role_id)
                try: 
                    await member.remove_roles(role, reason=f"Member gained new level {new_level}")
                    await remove_member_role_async(guild_id, member.id, old_role_id)
                except:
                    pass

    @Cog.listener()
    async def on_application_command_error(self, interaction: Interaction, exception) -> None:
        if isinstance(exception, ApplicationCheckFailure):
            assert interaction.locale is not None
            lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=self.event_handl_text[lng]), ephemeral=True)
            return

        report: list[str] = ["[ERROR] [slash_command]"]
        if guild := interaction.guild:
            report.append(f"[{guild.id}] [{guild.name}]")
        if app_cmd := interaction.application_command:
            report.append('[' + str(app_cmd.name) + ']')
        report.append('[' + str(exception) + ']')

        await write_one_log_async("error.log", ' '.join(report))

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error) -> None:
        lines: list[str] = ["[ERROR] [on_command_error]"]
        if (member := ctx.author):
            lines.append(f"[member: {member.id}:{member.name}]")
        if (guild := ctx.guild):
            lines.append(f"[guild: {guild.id}:{guild.name}]")
        lines.append('[' + str(error) + ']')
        
        await write_one_log_async("error.log", ' '.join(lines))


def setup(bot: StoreBot) -> None:
    bot.add_cog(EventsHandlerCog(bot))

from sqlite3 import connect
from datetime import datetime, timedelta
from contextlib import closing
from os import path, mkdir
from typing import Literal
from asyncio import sleep
from time import time

from nextcord import (
    Game,
    Message,
    Embed,
    Guild,
    Interaction,
    Role,
    TextChannel,
    Member
)
from nextcord.errors import ApplicationCheckFailure
from nextcord.ext.commands import Cog, Context
from nextcord.ext import tasks

from storebot import StoreBot
from Tools import db_commands
from Tools.logger import Logger
from Variables.vars import CWD_PATH
from config import DEBUG


class EventsHandlerCog(Cog):
    event_handl_text: dict[int, dict[int, str]] = {
        0: {
            0: "**`Sorry, but you don't have enough permissions to use this command`**",
        },
        1: {
            0: "**`Извините, но у Вас недостаточно прав для использования этой команды`**",
        },
    }
    greetings: dict[int, str] = {
        0: "Thanks for adding bot!\n\
            Use **`/guide`** to see guide about bot's system\n\
            *`/settings`** to manage bot\n\
            and **`/help`** to see available commands",
        1: "Благодарим за добавление бота!\n\
            Используйте **`/guide`** для просмотра гайда о системе бота\n\
            **`/settings`** для управления ботом\n\
            и **`/help`** для просмотра доступных команд",
    }
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
        self.salary_roles.start()
        self._backup.start()
        
    
    @classmethod
    async def send_first_message(cls, guild: Guild, lng: int) -> None:
        channel_to_send_greet: TextChannel | None = None
        system_channel: TextChannel | None = guild.system_channel
        guild_me: Member = guild.me
        if system_channel and system_channel.permissions_for(guild_me).send_messages:
            channel_to_send_greet = system_channel
        else:
            for channel in guild.text_channels:
                if channel.permissions_for(guild_me).send_messages:
                    channel_to_send_greet = channel
                    break
        if channel_to_send_greet:
            await channel_to_send_greet.send(embed=Embed(description=cls.greetings[lng]))

    @Cog.listener()
    async def on_connect(self) -> None:
        await Logger.write_log_async("common_logs.log", "on_connect")
    
    @Cog.listener()
    async def on_ready(self) -> None:
        if not path.exists(f"{CWD_PATH}/bases/"):
            mkdir(f"{CWD_PATH}/bases/")
        if not path.exists(f"{CWD_PATH}/logs/"):
            mkdir(f"{CWD_PATH}/logs/")

        guilds: list[Guild] = self.bot.guilds.copy()
        for guild in guilds:
            guild_id: int = guild.id
            
            if not path.exists(f"{CWD_PATH}/bases/bases_{guild_id}/"):
                mkdir(f"{CWD_PATH}/bases/bases_{guild_id}/")
            if not path.exists(f"{CWD_PATH}/logs/logs_{guild_id}/"):
                mkdir(f"{CWD_PATH}/logs/logs_{guild_id}/")

            db_ignored_channels_data: list[tuple[int, int, int]] = db_commands.check_db(guild_id=guild_id, guild_locale=guild.preferred_locale)
            async with self.bot.voice_lock:
                self.bot.members_in_voice[guild_id] = {}
                self.bot.ignored_voice_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[2]}
            async with self.bot.text_lock:
                self.bot.ignored_text_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[1]}

            await Logger.write_log_async("guild.log", "correct_db func", str(guild_id), str(guild.name))

        if DEBUG:
            from colorama import Fore
            print(f'{Fore.CYAN}[>>>]Logged into Discord as {self.bot.user}\n')
            opt=f'\n{Fore.YELLOW}[>>>]Available commands:{Fore.RESET}\n' \
                f'\n{Fore.GREEN}1) setup guild_id lng - creates and setups new database for selected server.\n' \
                f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n'\
                f'{Fore.RED}\n[>>>]Enter command:'
            print(opt, end=' ')

        guilds_len: int = len(guilds)
        await self.bot.change_presence(activity=Game(f"/help on {guilds_len} servers"))
        await Logger.write_log_async("common_logs.log", "on_ready", f"total {guilds_len} guilds")

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        guild_id: int = guild.id
        
        if not path.exists(f"{CWD_PATH}/bases/bases_{guild_id}/"):
            mkdir(f"{CWD_PATH}/bases/bases_{guild_id}/")
        if not path.exists(f"{CWD_PATH}/logs/logs_{guild_id}/"):
                mkdir(f"{CWD_PATH}/logs/logs_{guild_id}/")

        guild_locale: str = str(guild.preferred_locale)
        db_ignored_channels_data: list[tuple[int, int, int]] =  db_commands.check_db(guild_id=guild_id, guild_locale=guild.preferred_locale)
        async with self.bot.voice_lock:
            self.bot.members_in_voice[guild_id] = {}
            self.bot.ignored_voice_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[2]}
        async with self.bot.text_lock:
            self.bot.ignored_text_channels[guild_id] = {tup[0] for tup in db_ignored_channels_data if tup[1]}
        
        lng: int = 1 if "ru" in guild_locale else 0
        try:
            await self.send_first_message(guild=guild, lng=lng)
        except Exception as ex:
            await Logger.write_one_log_async(
                filename="error.log",
                report=f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [FATAL] [ERROR] [send_first_message] [guild: {guild_id}:{guild.name}] [{str(ex)}]\n"
            )

        await Logger.write_log_async("guild.log", "guild_join", str(guild_id), str(guild.name))
        await Logger.write_log_async("common_logs.log", "guild_join", str(guild_id), str(guild.name))
        await Logger.write_guild_log_async(
            filename="guild.log",
            guild_id=guild_id,
            report=f"[guild_join] [guild: {guild_id}:{guild.name}]"
        )

        await self.bot.change_presence(activity=Game(f"/help on {len(self.bot.guilds)} servers"))

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        guild_id: int = guild.id

        await Logger.write_log_async("guild", "guild_remove", str(guild_id), str(guild.name))
        await Logger.write_log_async("common_logs", "guild_remove", str(guild_id), str(guild.name))
        
        await self.bot.change_presence(activity=Game(f"/help on {len(self.bot.guilds)} servers"))
        async with self.bot.voice_lock:
            del self.bot.members_in_voice[guild_id]
            del self.bot.ignored_voice_channels[guild_id]
        async with self.bot.text_lock:
            del self.bot.ignored_text_channels[guild_id]
    
    @tasks.loop(seconds=60)
    async def salary_roles(self) -> None:
        guild_ids: list[int] = [guild.id for guild in self.bot.guilds.copy()]
        for guild_id in guild_ids: 
            with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    r: list[tuple[int, str, int, int, int]] | list = \
                        cur.execute(
                            "SELECT role_id, members, salary, salary_cooldown, last_time FROM salary_roles"
                        ).fetchall()
                    if r:
                        time_now: int = int(time())
                        for role, role_owners, salary, t, last_time in r:
                            if not last_time or time_now - last_time >= t:
                                cur.execute("UPDATE salary_roles SET last_time = ? WHERE role_id = ?", (time_now, role))
                                base.commit()
                                member_ids: set[int] = {int(member_id) for member_id in role_owners.split("#") if member_id}
                                for member_id in member_ids:
                                    cur.execute("UPDATE users SET money = money + ? WHERE memb_id = ?", (salary, member_id))
                                    base.commit()
            await sleep(0.5)

    
    @salary_roles.before_loop
    async def before_timer(self) -> None:
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=30)
    async def _backup(self) -> None:
        guild_ids: frozenset[int] = frozenset(guild.id for guild in self.bot.guilds.copy())
        for guild_id in guild_ids:
            with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as src:
                with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}_backup.db")) as bck:
                    src.backup(bck)
            await sleep(0.5)        

    @_backup.before_loop
    async def before_timer_backup(self) -> None:
        await self.bot.wait_until_ready()

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        #or message.type is MessageType.chat_input_command
        if (member := message.author).bot or not isinstance(member, Member) or not (guild := message.guild):
            return
        
        g_id: int = guild.id
        async with self.bot.text_lock:
            if g_id not in self.bot.ignored_text_channels:
                self.bot.ignored_text_channels[g_id] = set()
            elif message.channel.id in self.bot.ignored_text_channels[g_id]:
                return

        new_level: int = await db_commands.check_member_level_async(guild_id=g_id, member_id=member.id)
        if not new_level:
            return

        with closing(connect(f"{CWD_PATH}/bases/bases_{g_id}/{g_id}.db")) as base:
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
        del db_lvl_rls
        if new_level in lvl_rls:
            guild_roles: dict[int, Role] = guild._roles
            memb_roles: set[int] = {role_id for role_id in member._roles if role_id in guild_roles}
            new_level_role_id: int = lvl_rls[new_level]
            if new_level_role_id not in memb_roles and (role := guild_roles.get(new_level_role_id)):
                try: 
                    await member.add_roles(role, reason=f"Member gained new level {new_level}")
                except: 
                    pass
            levels: list[int] = sorted(lvl_rls.keys())
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
        guild_report: str = f"[{guild.id}] [{guild.name}" if (guild := ctx.guild) else ""
        await Logger.write_log_async("error.log", ctx.author.id, guild_report, str(error))
    
def setup(bot: StoreBot) -> None:
    bot.add_cog(EventsHandlerCog(bot))

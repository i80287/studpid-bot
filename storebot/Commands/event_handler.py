from sqlite3 import connect, Connection, Cursor
from datetime import datetime, timedelta
from contextlib import closing
from os import path, mkdir
from typing import Literal
from asyncio import sleep
from time import time

from nextcord import Game, Message, User, Embed, \
    Guild, Interaction, Role, TextChannel, Member
from nextcord.errors import ApplicationCheckFailure
from nextcord.ext.commands import Cog
from nextcord.ext import tasks
from nextcord.abc import GuildChannel

from storebot import StoreBot
from Tools import db_commands
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
        
    @staticmethod
    def log_event(filename: str = "common_logs", report: list[str] = [""]) -> None:
        with open(file=filename+".log", mode="a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] {' '.join([f'[{s}]' for s in report])}\n")

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
        self.log_event(report=["on_connect"])
    
    @Cog.listener()
    async def on_ready(self) -> None:
        if not path.exists(f"{CWD_PATH}/bases/"):
            mkdir(f"{CWD_PATH}/bases/")
        for guild in self.bot.guilds:
            guild_id: int = guild.id
            if not path.exists(f"{CWD_PATH}/bases/bases_{guild_id}/"):
                mkdir(f"{CWD_PATH}/bases/bases_{guild_id}/")
            self.bot.members_in_voice[guild_id] = {}
            self.bot.ignored_channels[guild_id] = db_commands.check_db(guild_id=guild_id, guild_locale=guild.preferred_locale)
            self.log_event(report=["correct_db func", str(guild_id), str(guild.name)])

        if DEBUG:
            from colorama import Fore
            print(f'{Fore.CYAN}[>>>]Logged into Discord as {self.bot.user}\n')
            opt=f'\n{Fore.YELLOW}[>>>]Available commands:{Fore.RESET}\n' \
                f'\n{Fore.GREEN}1) setup guild_id lng - creates and setups new database for selected server.\n' \
                f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n'\
                f'{Fore.RED}\n[>>>]Enter command:'
            print(opt, end=' ')

        guilds_len: int = len(self.bot.guilds)
        await self.bot.change_presence(activity=Game(f"/help on {guilds_len} servers"))
        self.log_event(report=["on_ready", f"total {guilds_len} guilds"])

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        guild_id: int = guild.id
        if not path.exists(f"{CWD_PATH}/bases/bases_{guild_id}/"):
            mkdir(f"{CWD_PATH}/bases/bases_{guild_id}/")
        guild_locale: str = str(guild.preferred_locale)
        lng: int = 1 if "ru" in guild_locale else 0
        db_commands.check_db(guild_id=guild_id, guild_locale=guild_locale)
        
        if guild.me:
            await self.send_first_message(guild=guild, lng=lng)
        else:
            g: Guild | None = self.bot.get_guild(guild.id)
            if g and g.me:
                await self.send_first_message(guild=g, lng=lng)
            else:
                with open("error.log", "a+", encoding="utf-8") as f:
                    f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [FATAL] [ERROR] [send_first_message] [{guild.me}] [{g.me}]\n")
    
        report_args: list[str] = ["guild_join", str(guild_id), str(guild.name)]
        self.log_event(filename="guild", report=report_args)
        self.log_event(report=report_args)

        await self.bot.change_presence(activity=Game(f"/help on {len(self.bot.guilds)} servers"))

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        report_args: list[str] = ["guild_remove", str(guild.id), str(guild.name)]
        self.log_event(filename="guild", report=report_args)
        self.log_event(filename="common_logs", report=report_args)
        await self.bot.change_presence(activity=Game(f"/help on {len(self.bot.guilds)} servers"))   
    
    @tasks.loop(seconds=60)
    async def salary_roles(self) -> None:
        guild_ids: frozenset[int] = frozenset(guild.id for guild in self.bot.guilds.copy())
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

    @staticmethod
    def check_user(base: Connection, cur: Cursor, memb_id: int, xp_b: int, mn_m: int, xp_m: int) -> int:
        member: tuple[int] | None = cur.execute(
            "SELECT xp FROM users WHERE memb_id = ?",
            (memb_id,)
        ).fetchone()
        if member:
            cur.execute("UPDATE users SET money = money + ?, xp = xp + ? WHERE memb_id = ?", (mn_m, xp_m, memb_id))
            base.commit()
            old_level: int = (member[0] - 1) // xp_b + 1
            new_level: int = (member[0] + xp_m - 1) // xp_b + 1
            if old_level == new_level:                
                return 0
            return new_level
        else:
            cur.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, ?, ?, ?, ?, ?)",
                (memb_id, mn_m, "", 0, xp_m, 0)
            )
            base.commit()
            return 1

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        user: User | Member = message.author

        #or message.type is MessageType.chat_input_command
        if user.bot or not isinstance(user, Member):
            return
        
        g_id: int = message.guild.id
        if g_id not in self.bot.ignored_channels:
            self.bot.ignored_channels[g_id] = set()
        elif message.channel.id in self.bot.ignored_channels[g_id]:
            return

        with closing(connect(f"{CWD_PATH}/bases/bases_{g_id}/{g_id}.db")) as base:
            with closing(base.cursor()) as cur:                    
                xp_b: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border';").fetchone()[0]
                xp_p_m: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_per_msg';").fetchone()[0]
                mn_p_m: int = cur.execute("SELECT value FROM server_info WHERE settings = 'mn_per_msg';").fetchone()[0]
                new_level: int = self.check_user(base=base, cur=cur, memb_id=user.id, xp_b=xp_b, mn_m=mn_p_m, xp_m=xp_p_m)
                if new_level:
                    channel_id: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lvl_c';").fetchone()[0]
                    if channel_id:
                        channel: GuildChannel | None = message.guild.get_channel(channel_id)
                        if channel and isinstance(channel, TextChannel):
                            lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang';").fetchone()[0]
                            emb: Embed = Embed(title=self.new_level_text[lng][0], description=self.new_level_text[lng][1].format(user.mention, new_level))
                            await channel.send(embed=emb)

                    db_lvl_rls: list[tuple[int, int]] | list = \
                        cur.execute("SELECT level, role_id FROM rank_roles ORDER BY level").fetchall()
                    if not db_lvl_rls:
                        return

                    lvl_rls: dict[int, int] = {k: v for k, v in db_lvl_rls}  
                    del db_lvl_rls              
                    if new_level in lvl_rls:
                        memb_roles: set[int] = {role.id for role in user.roles}
                        new_level_role_id: int = lvl_rls[new_level]
                        if new_level_role_id not in memb_roles:
                            role: Role | None = user.guild.get_role(new_level_role_id)
                            if role:
                                try: 
                                    await user.add_roles(role, reason=f"Member gained new level {new_level}")
                                except: 
                                    pass
                        levels: list[int] = sorted(lvl_rls.keys())
                        i: int = levels.index(new_level)
                        if i and (old_role_id := lvl_rls[levels[i-1]]) in memb_roles:                                
                            role: Role | None = user.guild.get_role(old_role_id)
                            if role:
                                try: 
                                    await user.remove_roles(role, reason=f"Member gained new level {new_level}")
                                except: 
                                    pass

    @Cog.listener()
    async def on_application_command_error(self, interaction: Interaction, exception) -> None:
        if isinstance(exception, ApplicationCheckFailure):
            lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
            await interaction.response.send_message(embed=Embed(description=self.event_handl_text[lng][0]), ephemeral=True)
            return

        guild_report: str = f" [{guild.id}] [{guild.name}]" if (guild := interaction.guild) else ""
        with open("error.log", "a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [slash_command] [{interaction.application_command.name}]{guild_report} [{str(exception)}]\n")


def setup(bot: StoreBot) -> None:
    bot.add_cog(EventsHandlerCog(bot))

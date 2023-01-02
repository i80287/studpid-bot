from sqlite3 import connect, Connection, Cursor
from datetime import datetime, timedelta
from contextlib import closing
from os import path, mkdir
from typing import Literal
from asyncio import sleep
from time import time

from nextcord import Game, Message, ChannelType,\
    Embed, Guild, Interaction, Role, TextChannel
from nextcord.errors import ApplicationCheckFailure
from nextcord.ext.commands import Bot, Cog
from nextcord.ext import tasks

from Variables.vars import path_to, bot_guilds, ignored_channels
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
    greetings: dict[int, list[str]] = {
        0: [
            "Thanks for adding bot!",
            "Use **`/guide`** to see guide about bot's system",
            "**`/settings`** to manage bot",
            "and **`/help`** to see available commands",
        ],
        1: [
            "Благодарим за добавление бота!",
            "Используйте **`/guide`** для просмотра гайда о системе бота",
            "**`/settings`** для управления ботом",
            "и **`/help`** для просмотра доступных команд",
        ]
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

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self.salary_roles.start()
        self._backup.start()
        
    @classmethod
    def correct_db(cls, guild: Guild) -> None:
        with closing(connect(f"{path_to}/bases/bases_{guild.id}/{guild.id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.executescript("""\
                CREATE TABLE IF NOT EXISTS users (
                    memb_id INTEGER PRIMARY KEY,
                    money INTEGER NOT NULL DEFAULT 0,
                    owned_roles TEXT NOT NULL DEFAULT '',
                    work_date INTEGER NOT NULL DEFAULT 0,
                    xp INTEGER NOT NULL DEFAULT 0,
                    pending_requests INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS sale_requests (
                    request_id INTEGER PRIMARY KEY,
                    seller_id INTEGER NOT NULL DEFAULT 0,
                    target_id INTEGER NOT NULL DEFAULT 0,
                    role_id INTEGER NOT NULL DEFAULT 0,
                    price INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS server_roles (
                    role_id INTEGER PRIMARY KEY,
                    price INTEGER NOT NULL DEFAULT 0,
                    salary INTEGER NOT NULL DEFAULT 0,
                    salary_cooldown INTEGER NOT NULL DEFAULT 0,
                    type INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS store (
                    role_number INTEGER PRIMARY KEY,
                    role_id INTEGER NOT NULL DEFAULT 0,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    price INTEGER NOT NULL DEFAULT 0,
                    last_date INTEGER NOT NULL DEFAULT 0,
                    salary INTEGER NOT NULL DEFAULT 0,
                    salary_cooldown INTEGER NOT NULL DEFAULT 0,
                    type INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS salary_roles (
                    role_id INTEGER PRIMARY KEY,
                    members TEXT NOT NULL DEFAULT '',
                    salary INTEGER NOT NULL DEFAULT 0,
                    salary_cooldown INTEGER NOT NULL DEFAULT 0,
                    last_time INTEGER NOT NULL DEFAULT 0,
                    additional_salary INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS server_info (
                    settings TEXT PRIMARY KEY,
                    value INTEGER NOT NULL DEFAULT 0,
                    str_value TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS rank_roles (
                    level INTEGER PRIMARY KEY,
                    role_id INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS ic (
                    chnl_id INTEGER PRIMARY KEY
                );
                CREATE TABLE IF NOT EXISTS mod_roles (
                    role_id INTEGER PRIMARY KEY
                );""")
                base.commit()
                
                db_guild_language: tuple[int] | None = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()
                if db_guild_language: 
                    lng: Literal[1, 0] = db_guild_language[0]
                else: 
                    lng: Literal[1, 0] = 1 if "ru" in str(guild.preferred_locale) else 0
                
                settings_params: list[tuple[str, int, str]] = [
                    ('lang', lng, ""),
                    ('tz', 0, ""),
                    ('xp_border', 100, ""),
                    ('xp_per_msg', 1, ""),
                    ('mn_per_msg', 1, ""),
                    ('w_cd', 14400, ""),
                    ('sal_l', 1, ""),
                    ('sal_r', 250, ""),
                    ('lvl_c', 0, ""),
                    ('log_c', 0, ""),
                    ('poll_v_c', 0, ""),
                    ('poll_c', 0, ""),
                    ('economy_enabled', 1, ""),
                    ('ranking_enabled', 1, ""),
                    ('currency', 0, ":coin:"),
                    ('sale_price_perc', 100, ""),
                ]
                cur.executemany("INSERT OR IGNORE INTO server_info (settings, value, str_value) VALUES(?, ?, ?)", settings_params)
                base.commit()

                ignored_channels[guild.id] = {r[0] for r in cur.execute("SELECT chnl_id FROM ic").fetchall()}

        bot_guilds.add(guild.id)
        cls.log_event(report=["correct_db func", str(guild.id), str(guild.name)])

    @staticmethod
    def log_event(filename: str = "common_logs", report: list[str] = [""]) -> None:
        with open(file=filename+".log", mode="a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] {' '.join([f'[{s}]' for s in report])}\n")

    @classmethod
    async def send_first_message(cls, guild: Guild, lng: int) -> None:
        channel_to_send_greet: TextChannel | None = None
        if guild.system_channel.permissions_for(guild.me).send_messages:
            channel_to_send_greet = guild.system_channel
        else:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    channel_to_send_greet = channel
                    break
        if channel_to_send_greet:
            await channel_to_send_greet.send(embed=Embed(description="\n".join(cls.greetings[lng])))

    @Cog.listener()
    async def on_connect(self) -> None:
        self.log_event(report=["on_connect"])
    
    @Cog.listener()
    async def on_ready(self) -> None:
        setattr(self.bot, "current_polls", 0)
        if not path.exists(f"{path_to}/bases/"):
            mkdir(f"{path_to}/bases/")
        for guild in self.bot.guilds:
            if not path.exists(f"{path_to}/bases/bases_{guild.id}/"):
                mkdir(f"{path_to}/bases/bases_{guild.id}/")
            self.correct_db(guild=guild)

        if DEBUG:
            from colorama import Fore
            print(f'{Fore.CYAN}[>>>]Logged into Discord as {self.bot.user}\n')
            opt=f'\n{Fore.YELLOW}[>>>]Available commands:{Fore.RESET}\n' \
                f'\n{Fore.GREEN}1) setup guild_id lng - creates and setups new database for selected server.\n' \
                f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n'\
                f'{Fore.RED}\n[>>>]Enter command:'
            print(opt, end=' ')

        await self.bot.change_presence(activity=Game(f"/help on {len(bot_guilds)} servers"))

        self.log_event(report=["on_ready", f"total {len(bot_guilds)} guilds"])

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        if not path.exists(f"{path_to}/bases/bases_{guild.id}/"):
            mkdir(f"{path_to}/bases/bases_{guild.id}/")
        self.correct_db(guild=guild)
        guild_locale: str | None = guild.preferred_locale
        lng: int = 1 if guild_locale and "ru" in guild_locale else 0
        
        if guild.me:
            await self.send_first_message(guild=guild, lng=lng)
        else:
            g: Guild | None = self.bot.get_guild(guild.id)
            if g and g.me:
                await self.send_first_message(guild=g, lng=lng)
            else:
                with open("error.log", "a+", encoding="utf-8") as f:
                    f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [FATAL] [ERROR] [send_first_message] [{guild.me}] [{g.me}]\n")
    
        self.log_event(filename="guild", report=["guild_join", str(guild.id), str(guild.name)])
        self.log_event(report=["guild_join", str(guild.id), str(guild.name)])

        await self.bot.change_presence(activity=Game(f"/help on {len(bot_guilds)} servers"))

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        g_id: int = guild.id
        if g_id in bot_guilds:
            bot_guilds.remove(g_id)
        self.log_event(filename="guild", report=["guild_remove", str(guild.id), str(guild.name)])
        self.log_event(filename="common_logs", report=["guild_remove", str(guild.id), str(guild.name)])
        await self.bot.change_presence(activity=Game(f"/help on {len(bot_guilds)} servers"))
        
    
    @tasks.loop(seconds=60)
    async def salary_roles(self) -> None:
        for g in bot_guilds: 
            with closing(connect(f"{path_to}/bases/bases_{g}/{g}.db")) as base:
                with closing(base.cursor()) as cur:
                    r: list[tuple[int, str, int, int, int]] | list = \
                        cur.execute(
                            "SELECT role_id, members, salary, salary_cooldown, last_time FROM salary_roles"
                        ).fetchall()
                    if r:
                        t_n: int = int(time())
                        for role, members, salary, t, last_time in r:
                            if not last_time or t_n - last_time >= t:
                                cur.execute("UPDATE salary_roles SET last_time = ? WHERE role_id = ?", (t_n, role))
                                base.commit()
                                for member in members.split("#"):
                                    if member:
                                        cur.execute("UPDATE users SET money = money + ? WHERE memb_id = ?", (salary, int(member)))
                                        base.commit()
            await sleep(0.5)

    
    @salary_roles.before_loop
    async def before_timer(self) -> None:
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=30)
    async def _backup(self) -> None:
        for guild_id in bot_guilds:
            with closing(connect(f"{path_to}/bases/bases_{guild_id}/{guild_id}.db")) as src:
                with closing(connect(f"{path_to}/bases/bases_{guild_id}/{guild_id}_backup.db")) as bck:
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
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, pending_requests) VALUES (?, ?, ?, ?, ?, ?)",
                (memb_id, mn_m, "", 0, xp_m, 0)
            )
            base.commit()
            return 1

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        user = message.author

        #or message.type is MessageType.chat_input_command
        if user.bot or message.channel.type is ChannelType.private:
            return
        
        g_id: int = message.guild.id
        if g_id not in ignored_channels:
            ignored_channels[g_id] = set()
        elif message.channel.id in ignored_channels[g_id]:
            return

        with closing(connect(f"{path_to}/bases/bases_{g_id}/{g_id}.db")) as base:
            with closing(base.cursor()) as cur:                    
                xp_b: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border';").fetchone()[0]
                xp_p_m: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_per_msg';").fetchone()[0]
                mn_p_m: int = cur.execute("SELECT value FROM server_info WHERE settings = 'mn_per_msg';").fetchone()[0]
                new_level: int = self.check_user(base=base, cur=cur, memb_id=user.id, xp_b=xp_b, mn_m=mn_p_m, xp_m=xp_p_m)
                if new_level:
                    channel_id: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lvl_c';").fetchone()[0]
                    
                    if channel_id:
                        channel = message.guild.get_channel(channel_id)
                        if channel:
                            lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang';").fetchone()[0]
                            emb: Embed = Embed(title=self.new_level_text[lng][0], description=self.new_level_text[lng][1].format(user.mention, new_level))
                            await channel.send(embed=emb)

                    lvl_rls: list = cur.execute("SELECT * FROM rank_roles ORDER BY level").fetchall()
                    if not lvl_rls:
                        return

                    lvl_rls: dict[int, int] = {k: v for k, v in lvl_rls}                
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
                        if i and lvl_rls[levels[i-1]] in memb_roles:                                
                            role: Role | None = user.guild.get_role(lvl_rls[levels[i-1]])
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

        with open("error.log", "a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [slash_command] [{interaction.application_command.name}] [{interaction.guild_id}] [{interaction.guild.name}] [{str(exception)}]\n")


def setup(bot: Bot) -> None:
    bot.add_cog(EventsHandlerCog(bot))

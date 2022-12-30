from sqlite3 import connect, Connection, Cursor
from datetime import datetime, timedelta
from contextlib import closing
from os import path, mkdir
from asyncio import sleep
from time import time

from nextcord import Game, Message, ChannelType, Embed, Guild, Interaction
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

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.salary_roles.start()
        self._backup.start()
        
    @classmethod
    def correct_db(cls, guild: Guild):
        with closing(connect(f"{path_to}/bases/bases_{guild.id}/{guild.id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.executescript("""
                    CREATE TABLE IF NOT EXISTS users(memb_id INTEGER PRIMARY KEY, money INTEGER, owned_roles TEXT, work_date INTEGER, xp INTEGER);
                    CREATE TABLE IF NOT EXISTS server_roles(role_id INTEGER PRIMARY KEY, price INTEGER, salary INTEGER, salary_cooldown INTEGER, type INTEGER);
                    CREATE TABLE IF NOT EXISTS store (role_number INTEGER PRIMARY KEY, 
                        role_id INTEGER NOT NULL DEFAULT 0, 
                        quantity INTEGER NOT NULL DEFAULT 0, 
                        price INTEGER NOT NULL DEFAULT 0, 
                        last_date INTEGER NOT NULL DEFAULT 0, 
                        salary INTEGER NOT NULL DEFAULT 0, 
                        salary_cooldown INTEGER NOT NULL DEFAULT 0, 
                        type INTEGER NOT NULL DEFAULT 0
                    );
                    CREATE TABLE IF NOT EXISTS salary_roles(role_id INTEGER PRIMARY KEY, members TEXT, salary INTEGER NOT NULL, salary_cooldown INTEGER, last_time INTEGER);
                    CREATE TABLE IF NOT EXISTS server_info(settings TEXT PRIMARY KEY, value INTEGER);
                    CREATE TABLE IF NOT EXISTS rank_roles(level INTEGER PRIMARY KEY, role_id INTEGER);
                    CREATE TABLE IF NOT EXISTS ic(chnl_id INTEGER PRIMARY KEY);
                    CREATE TABLE IF NOT EXISTS mod_roles(role_id INTEGER PRIMARY KEY);
                """)
                
                # Fixing legacy.
                TABLE_NAME: str = "store"
                columns_count = len(cur.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall())
                if columns_count != 8:
                    roles = cur.execute(f"SELECT * FROM {TABLE_NAME} ORDER BY last_date DESC").fetchall()

                    store_backup = connect(f"{path_to}/bases/bases_{guild.id}/{TABLE_NAME}_backup.db")
                    store_cur = store_backup.cursor()
                    store_cur.executescript(f"""
                    DROP TABLE IF EXISTS {TABLE_NAME};
                    CREATE TABLE {TABLE_NAME} (role_id INTEGER, quantity INTEGER, price INTEGER, last_date INTEGER, salary INTEGER, salary_cooldown INTEGER, type INTEGER);
                    """)
                    store_backup.executemany("""INSERT INTO 
                    store (role_id, quantity, price, last_date, salary, salary_cooldown, type) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, roles)
                    store_backup.commit()
                    store_backup.close()
                    
                    cur.executescript(f"""
                        DROP TABLE IF EXISTS {TABLE_NAME};
                        CREATE TABLE {TABLE_NAME} (role_number INTEGER PRIMARY KEY, 
                            role_id INTEGER NOT NULL DEFAULT 0, 
                            quantity INTEGER NOT NULL DEFAULT 0, 
                            price INTEGER NOT NULL DEFAULT 0, 
                            last_date INTEGER NOT NULL DEFAULT 0, 
                            salary INTEGER NOT NULL DEFAULT 0, 
                            salary_cooldown INTEGER NOT NULL DEFAULT 0, 
                            type INTEGER NOT NULL DEFAULT 0
                        );
                    """)
                    new_roles = [(i + 1, *r) for i, r in enumerate(roles)]
                    cur.executemany(f"""INSERT INTO 
                    {TABLE_NAME} (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, new_roles)
                    base.commit()

                base.commit()
                
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()
                if lng: lng = lng[0]
                else: lng = 1 if "ru" in guild.preferred_locale else 0
                    
                r = (
                    ('lang', lng), ('tz', 0), 
                    ('xp_border', 100), ('xp_per_msg', 1), ('mn_per_msg', 1), 
                    ('w_cd', 14400), ('sal_l', 1), ('sal_r', 250),
                    ('lvl_c', 0), ('log_c', 0), ('poll_v_c', 0), ('poll_c', 0),
                    ('economy_enabled', 1), ('ranking_enabled', 1), ('currency', ":coin:")
                )
                cur.executemany("INSERT OR IGNORE INTO server_info(settings, value) VALUES(?, ?)", r)
                base.commit()

                ignored_channels[guild.id] = {r[0] for r in cur.execute("SELECT chnl_id FROM ic").fetchall()}

        bot_guilds.add(guild.id)
        cls.log_event(report=["correct_db func", str(guild.id), str(guild.name)])

    @staticmethod
    def log_event(filename: str = "common_logs", report: list[str] = [""]):
        with open(file=filename+".log", mode="a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] {' '.join([f'[{s}]' for s in report])}\n")

    @classmethod
    async def send_first_message(cls, guild: Guild, lng: int):
        channel_to_send_greet = None
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
    async def on_connect(self):
        self.log_event(report=["on_connect"])
    
    @Cog.listener()
    async def on_ready(self):
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
    async def on_guild_join(self, guild: Guild):
        if not path.exists(f"{path_to}/bases/bases_{guild.id}/"):
            mkdir(f"{path_to}/bases/bases_{guild.id}/")
        self.correct_db(guild=guild)
        guild_locale = guild.preferred_locale
        lng: int = 1 if guild_locale and "ru" in guild_locale else 0
        
        if guild.me:
            await self.send_first_message(guild=guild, lng=lng)
        else:
            g = self.bot.get_guild(guild.id)
            if g.me:
                await self.send_first_message(guild=g, lng=lng)
            else:
                with open("error.log", "a+", encoding="utf-8") as f:
                    f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [FATAL] [ERROR] [send_first_message] [{[m.id for m in guild]}] [{[memb.id for memb in g]}] [{guild.me}] [{g.me}]\n")
    
        self.log_event(filename="guild", report=["guild_join", str(guild.id), str(guild.name)])
        self.log_event(report=["guild_join", str(guild.id), str(guild.name)])

        await self.bot.change_presence(activity=Game(f"/help on {len(bot_guilds)} servers"))

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        g_id = guild.id
        if g_id in bot_guilds:
            bot_guilds.remove(g_id)
        self.log_event(filename="guild", report=["guild_remove", str(guild.id), str(guild.name)])
        self.log_event(filename="common_logs", report=["guild_remove", str(guild.id), str(guild.name)])
        await self.bot.change_presence(activity=Game(f"/help on {len(bot_guilds)} servers"))
        
    
    @tasks.loop(seconds=60)
    async def salary_roles(self):
        for g in bot_guilds: 
            with closing(connect(f"{path_to}/bases/bases_{g}/{g}.db")) as base:
                with closing(base.cursor()) as cur:
                    r = cur.execute("SELECT * FROM salary_roles").fetchall()
                    if r:
                        t_n = int(time())
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
    async def before_timer(self):
        await self.bot.wait_until_ready()


    @tasks.loop(minutes=30)
    async def _backup(self):
        for guild_id in bot_guilds:
            with closing(connect(f"{path_to}/bases/bases_{guild_id}/{guild_id}.db")) as src:
                with closing(connect(f"{path_to}/bases/bases_{guild_id}/{guild_id}_backup.db")) as bck:
                    src.backup(bck)
            await sleep(0.5)
        

    @_backup.before_loop
    async def before_timer_backup(self):
        await self.bot.wait_until_ready()


    @staticmethod
    def check_user(base: Connection, cur: Cursor, memb_id: int, xp_b: int, mn_m: int, xp_m: int) -> int:
        member = cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()
        if not member:
            cur.execute('INSERT INTO users(memb_id, money, owned_roles, work_date, xp) VALUES(?, ?, ?, ?, ?)', (memb_id, mn_m, "", 0, xp_m))
            base.commit()
            return 1
        else:
            cur.execute('UPDATE users SET money = money + ?, xp = xp + ? WHERE memb_id = ?', (mn_m, xp_m, memb_id))
            base.commit()
            old_level = (member[4] - 1) // xp_b + 1
            new_level = (member[4] + xp_m - 1) // xp_b + 1
            if old_level != new_level:
                return new_level
            return 0


    @Cog.listener()
    async def on_message(self, message: Message):
        user = message.author

        #or message.type is MessageType.chat_input_command
        if user.bot or message.channel.type is ChannelType.private:
            return
        
        g_id = message.guild.id
        if g_id not in ignored_channels:
            ignored_channels[g_id] = set()
        elif message.channel.id in ignored_channels[g_id]:
            return

        with closing(connect(f"{path_to}/bases/bases_{g_id}/{g_id}.db")) as base:
            with closing(base.cursor()) as cur:                    
                xp_b = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border';").fetchone()[0]
                xp_p_m = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_per_msg';").fetchone()[0]
                mn_p_m = cur.execute("SELECT value FROM server_info WHERE settings = 'mn_per_msg';").fetchone()[0]
                
                new_level = self.check_user(base=base, cur=cur, memb_id=user.id, xp_b=xp_b, mn_m=mn_p_m, xp_m=xp_p_m)

                if new_level:
                    channel_id = cur.execute("SELECT value FROM server_info WHERE settings = 'lvl_c';").fetchone()[0]
                    
                    if channel_id:
                        channel = message.guild.get_channel(channel_id)
                        if channel:
                            lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang';").fetchone()[0]
                            emb = Embed(title=self.new_level_text[lng][0], description=self.new_level_text[lng][1].format(user.mention, new_level))
                            await channel.send(embed=emb)

                    lvl_rls: list = cur.execute("SELECT * FROM rank_roles ORDER BY level").fetchall()
                    if not lvl_rls:
                        return

                    lvl_rls: dict[int, int] = {k: v for k, v in lvl_rls}                
                    if new_level in lvl_rls:
                        memb_roles = {role.id for role in user.roles}
                        new_level_role_id = lvl_rls[new_level]
                        if new_level_role_id not in memb_roles:
                            role = user.guild.get_role(new_level_role_id)
                            if role:
                                try: 
                                    await user.add_roles(role, reason=f"Member gained new level {new_level}")
                                finally: 
                                    pass
                        levels = list(lvl_rls.keys())
                        i = levels.index(new_level)
                        if i and lvl_rls[levels[i-1]] in memb_roles:                                
                            role = user.guild.get_role(lvl_rls[levels[i-1]])
                            if role:
                                try: 
                                    await user.remove_roles(role, reason=f"Member gained new level {new_level}")
                                finally: 
                                    pass

    @Cog.listener()
    async def on_application_command_error(self, interaction: Interaction, exception):
        if isinstance(exception, ApplicationCheckFailure):
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=self.event_handl_text[lng][0]), ephemeral=True)
            return

        with open("error.log", "a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [slash_command] [{interaction.application_command.name}] [{interaction.guild_id}] [{interaction.guild.name}] [{str(exception)}]\n")


def setup(bot: Bot):
    bot.add_cog(EventsHandlerCog(bot))

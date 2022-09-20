from os import path, mkdir
from contextlib import closing
from sqlite3 import connect, Connection, Cursor
from datetime import datetime, timedelta
from time import time
from asyncio import sleep

from colorama import Fore
from nextcord import Game, Message, ChannelType, Embed, Guild, Interaction
from nextcord.ext import commands, tasks
from nextcord.errors import ApplicationCheckFailure

from config import path_to 

# event_handl_text = {
#     0 : {
#         0 : "**Sorry, but you don't have enough permissions to use this command**",
#     },
#     1 : {
#         0 : "**Извините, но у Вас недостаточно прав для использования этой командыы**",
#     }
# }


class msg_h(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        global bot_guilds
        bot_guilds = set()
        
        global tx
        tx = {
            0 : {
                0 : "New level!",
                1 : "{}, you raised level to **{}**!"
            },
            1 : {
                0 : "Новый уровень!",
                1 : "{}, Вы подняли уровень до **{}**!"
            }
        }
        global greetings
        greetings = {
            0 : [
                "Thanks for adding bot!",
                "Use **`/guide`** to see guide about bot's system",
                "**`/settings`** to manage bot",
                "and **`/help`** to see available commands"
            ],
            1 : [
                "Благодарим за добавление бота!",
                "Используйте **`/guide`** для просмотра гайда о системе бота",
                "**`/settings`** для управления ботом",
                "и **`/help`** для просмотра доступных команд"
            ]
        }
        self.salary_roles.start()
        self._backup.start()
        
    
    def correct_db(self, guild: Guild) -> None:
        with closing(connect(f'{path_to}/bases/bases_{guild.id}/{guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                cur.executescript("""
                    CREATE TABLE IF NOT EXISTS users(memb_id INTEGER PRIMARY KEY, money INTEGER, owned_roles TEXT, work_date INTEGER, xp INTEGER);
                    CREATE TABLE IF NOT EXISTS server_roles(role_id INTEGER PRIMARY KEY, price INTEGER, salary INTEGER, salary_cooldown INTEGER, type INTEGER);
                    CREATE TABLE IF NOT EXISTS store(role_id INTEGER, quantity INTEGER, price INTEGER, last_date INTEGER, salary INTEGER, salary_cooldown INTEGER, type INTEGER);
                    CREATE TABLE IF NOT EXISTS salary_roles(role_id INTEGER PRIMARY KEY, members TEXT, salary INTEGER NOT NULL, salary_cooldown INTEGER, last_time INTEGER);
                    CREATE TABLE IF NOT EXISTS server_info(settings TEXT PRIMARY KEY, value INTEGER);
                    CREATE TABLE IF NOT EXISTS rank_roles(level INTEGER PRIMARY KEY, role_id INTEGER);
                    CREATE TABLE IF NOT EXISTS ic(chnl_id INTEGER PRIMARY KEY);
                    CREATE TABLE IF NOT EXISTS mod_roles(role_id INTEGER PRIMARY KEY);
                """)
                base.commit()
                
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()
                if not lng:
                    lng = 1 if "ru" in guild.preferred_locale else 0
                else:
                    lng = lng[0]
                    
                r = [
                    ('lang', lng), ('tz', 0), 
                    ('xp_border', 100), ('xp_per_msg', 1), ('mn_per_msg', 1), 
                    ('w_cd', 14400), ('sal_l', 1), ('sal_r', 250),
                    ('lvl_c', 0), ('log_c', 0), ('poll_v_c', 0), ('poll_c', 0),
                    ('economy_enabled', 1), ('ranking_enabled', 1), ('currency', ":coin:")
                ]
                    
                cur.executemany("INSERT OR IGNORE INTO server_info(settings, value) VALUES(?, ?)", r)
                base.commit()

        bot_guilds.add(guild.id)

    @commands.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "current_polls", 0)
        if not path.exists(f"{path_to}/bases/"):
            mkdir(f"{path_to}/bases/")
        for guild in self.bot.guilds:
            if not path.exists(f"{path_to}/bases/bases_{guild.id}/"):
                mkdir(f"{path_to}/bases/bases_{guild.id}/")
            self.correct_db(guild=guild)

        print(f'{Fore.CYAN}[>>>]Logged into Discord as {self.bot.user}\n')

        opt=f'\n{Fore.YELLOW}[>>>]Available commands:{Fore.RESET}\n' \
            f'\n{Fore.GREEN}1) setup guild_id lng - creates and setups new database for selected server.\n' \
            f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n'\
            f'{Fore.RED}\n[>>>]Enter command:'

        print(opt, end=' ')
        await self.bot.change_presence(activity=Game(f"/help on {len(bot_guilds)} servers"))


    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:

        if not path.exists(f"{path_to}/bases/bases_{guild.id}/"):
            mkdir(f"{path_to}/bases/bases_{guild.id}/")
        self.correct_db(guild=guild)
        try:
            lng = 1 if "ru" in guild.preferred_locale else 0
        except:
            lng = 0
        
        if guild.system_channel.permissions_for(guild.me).send_messages:
            await guild.system_channel.send(embed=Embed(description="\n".join(greetings[lng])))
        else:
            for c in guild.text_channels:
                if c.permissions_for(guild.me).send_messages:
                    await c.send(embed=Embed(description="\n".join(greetings[lng])))
                    break
        await self.bot.change_presence(activity=Game(f"/help on {len(bot_guilds)} servers"))

        with open("guild.log", "a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [guild_join] [{guild.id}] [{guild.name}]\n")
            

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        g_id = guild.id
        if g_id in bot_guilds:
            bot_guilds.remove(g_id)
        await self.bot.change_presence(activity=Game(f"/help on {len(bot_guilds)} servers"))
        with open("guild.log", "a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [guild_remove] [{g_id}] [{guild.name}]\n")

    
    @tasks.loop(seconds=60)
    async def salary_roles(self):
        for g in bot_guilds: 
            with closing(connect(f"{path_to}/bases/bases_{g}/{g}.db")) as base:
                with closing(base.cursor()) as cur:
                    r = cur.execute("SELECT * FROM salary_roles").fetchall()
                    if r:
                        t_n = int(time())
                        for role, members, salary, t, last_time in r:
                            flag: bool = False

                            if not last_time:
                                flag = True
                            elif t_n - last_time >= t:
                                flag = True

                            if flag:
                                cur.execute("UPDATE salary_roles SET last_time = ? WHERE role_id = ?", (t_n, role))
                                base.commit()
                                for member in members.split("#"):
                                    if member != "":
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


    def check_user(self, base: Connection, cur: Cursor, memb_id: int, xp_b: int, mn_m: int, xp_m: int) -> int:
        member = cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()
        if not member:
            cur.execute('INSERT INTO users(memb_id, money, owned_roles, work_date, xp) VALUES(?, ?, ?, ?, ?)', (memb_id, mn_m, "", 0, xp_m))
            base.commit()
            return 1
        else:
            cur.execute('UPDATE users SET money = money + ?, xp = xp + ? WHERE memb_id = ?', (mn_m, xp_m, memb_id))
            base.commit()
            n_l = (member[4] + xp_m - 1) // xp_b
            if (member[4] - 1) // xp_b != n_l:
                return n_l
            return 0


    @commands.Cog.listener()
    async def on_message(self, message: Message):
        user = message.author

        #or message.type is MessageType.chat_input_command
        if user.bot or message.channel.type is ChannelType.private:
            return

        with closing(connect(f"{path_to}/bases/bases_{message.guild.id}/{message.guild.id}.db")) as base:
            with closing(base.cursor()) as cur:
                
                if cur.execute("SELECT count() FROM ic WHERE chnl_id = ?", (message.channel.id,)).fetchone()[0]:
                    return
                    
                xp_b = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border';").fetchone()[0]
                xp_p_m = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_per_msg';").fetchone()[0]
                mn_p_m = cur.execute("SELECT value FROM server_info WHERE settings = 'mn_per_msg';").fetchone()[0]
                
                lvl = self.check_user(base=base, cur=cur, memb_id=user.id, xp_b=xp_b, mn_m=mn_p_m, xp_m=xp_p_m)

                if lvl:
                    chnl = cur.execute("SELECT value FROM server_info WHERE settings = 'lvl_c';").fetchone()[0]
                    
                    if chnl != 0:
                        ch = message.guild.get_channel(chnl)
                        if ch:
                            lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang';").fetchone()[0]
                            emb = Embed(title=tx[lng][0], description=tx[lng][1].format(user.mention, lvl))
                            await ch.send(embed=emb)

                    lvl_rls = sorted(cur.execute("SELECT * FROM rank_roles").fetchall(), key=lambda tup: tup[0])
                    
                    if not lvl_rls:
                        return

                    lvl_rls = {k: v for k, v in lvl_rls}
                    lvls = [k for k in lvl_rls.keys()]

                    if lvl in lvl_rls:
                        memb_rls = {role.id for role in user.roles}

                        if not lvl_rls[lvl] in memb_rls:
                            role = user.guild.get_role(lvl_rls[lvl])
                            await user.add_roles(role, reason=f"Member gained new level {lvl}")

                        i = lvls.index(lvl)
                        if i != 0 and lvl_rls[lvls[i-1]] in memb_rls:                                
                            role = user.guild.get_role(lvl_rls[lvls[i-1]])
                            await user.remove_roles(role, reason=f"Member gained new level {lvl}")


    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: Interaction, exception) -> None:
        if isinstance(exception, ApplicationCheckFailure):
            if "ru" in interaction.locale:
                await interaction.response.send_message(embed=Embed(description="**`Извините, но у Вас недостаточно прав для использования этой команды`**"), ephemeral=True)
            else:
                await interaction.response.send_message(embed=Embed(description="**`Sorry, but you don't have enough permissions to use this command`**"), ephemeral=True)
            return
        with open("error.log", "a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [slash_command] [{interaction.application_command.name}] [{interaction.guild_id}] [{interaction.guild.name}] [{str(exception)}]\n")


def setup(bot: commands.Bot):
    bot.add_cog(msg_h(bot))

from os import path, mkdir
from asyncio import sleep
from contextlib import closing
from sqlite3 import connect
from datetime import datetime, timedelta

from colorama import Fore
from nextcord import Game, Message, ChannelType, MessageType, Embed
from nextcord.ext import commands
from nextcord.errors import ApplicationCheckFailure
from nextcord.ext.commands import CheckFailure, CommandError

from config import path_to, bot_guilds_e, bot_guilds_r, bot_guilds, prefix, in_row

event_handl_text = {
    0 : {
        0 : "**Sorry, but you don't have enough permissions to use this command**",
    },
    1 : {
        0 : "**Извините, но у Вас недостаточно прав для использования этой командыы**",
    }
}


class msg_h(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        global bot_guilds_e
        global bot_guilds_r

    
    """src = connect(f'{path_to}/bases/bases_{guild_id}/{guild_id}.db')
            bck = connect(f'{path_to}/bases/bases_{guild_id}/{guild_id}_shop_rec_1.db')
            src.backup(bck)
            src.close()
            bck.close()
            copy2(f'{path_to}/bases/bases_{guild_id}/{guild_id}.db', f'{path_to}/bases/bases_{guild_id}/{guild_id}_shop_rec_2.db')
            print(f'{Fore.CYAN}Created a backup for {guild_id}{Fore.RED}\n')"""

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            if not path.exists(f'{path_to}/bases/bases_{guild.id}'):
                mkdir(f'{path_to}/bases/bases_{guild.id}/')
            try:
                with closing(connect(f'{path_to}/bases/bases_{guild.id}/{guild.id}.db')) as base:
                    with closing(base.cursor()) as cur:
                        cur.executescript("""
                            CREATE TABLE IF NOT EXISTS users(memb_id INTEGER PRIMARY KEY, money INTEGER, owned_roles TEXT, work_date INTEGER);
                            CREATE TABLE IF NOT EXISTS server_roles(role_id INTEGER PRIMARY KEY, price INTEGER, salary INTEGER, salary_cooldown INTEGER, type INTEGER);
                            CREATE TABLE IF NOT EXISTS store(item_id INTEGER PRIMARY KEY, role_id INTEGER, quantity INTEGER, price INTEGER, last_date INTEGER, salary INTEGER, salary_cooldown INTEGER, type INTEGER);
                            CREATE TABLE IF NOT EXISTS salary_roles(role_id INTEGER PRIMARY KEY, members TEXT, salary INTEGER NOT NULL, salary_cooldown INTEGER, last_time INTEGER);
                            CREATE TABLE IF NOT EXISTS server_info(settings TEXT PRIMARY KEY, value INTEGER);
                            CREATE TABLE IF NOT EXISTS rank_roles(level INTEGER PRIMARY KEY, role_id INTEGER);
                            CREATE TABLE IF NOT EXISTS rank(memb_id INTEGER PRIMARY KEY, xp INTEGER);
                            CREATE TABLE IF NOT EXISTS ic(chn_id INTEGER PRIMARY KEY);
                            CREATE TABLE IF NOT EXISTS mod_roles(role_id INTEGER PRIMARY KEY);
                        """)
                        base.commit()
                        
                        lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()
                        if lng == None:
                            lng = 1 if "ru" in guild.preferred_locale else 0
                        else:
                            lng = lng[0]
                            
                        r = [
                            ('lang', lng), ('tz', 0), 
                            ('xp_border', 100), ('xp_per_msg', 1), ('mn_per_msg', 1), 
                            ('w_cd', 14400), ('sal_l', 1), ('sal_r', 250),
                            ('lvl_c', 0), ('log_c', 0), ('poll_v_c', 0), ('poll_c', 0)
                        ]
                            
                        cur.executemany("INSERT OR IGNORE INTO server_info(settings, value) VALUES(?, ?)", r)
                        base.commit()

                        if lng == 1:
                            bot_guilds_r.add(guild.id)
                        else:
                            bot_guilds_e.add(guild.id)
                        bot_guilds.add(guild.id)

            except Exception:
                base.rollback()
                with open("d.log", "a+", encoding="utf-8") as f:
                    f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [on_ready] [{guild.id}] [{guild.name}] [{str(Exception)}]\n")
    
        self.bot.load_extension(f"commands.m_commands")
        self.bot.load_extension(f"commands.basic", extras={"prefix": prefix, "in_row": in_row})
        self.bot.load_extension(f"commands.slash_shop", extras={"prefix": prefix, "in_row": in_row})

        await sleep(2)
        await self.bot.sync_all_application_commands()
        await sleep(1)
        print(bot_guilds_e, bot_guilds_r)

        print(f'{Fore.CYAN}[>>>]Logged into Discord as {self.bot.user}\n')

        opt=f'\n{Fore.YELLOW}[>>>]Available commands:{Fore.RESET}\n' \
            f'\n{Fore.GREEN}1) setup guild_id lng - creates and setups new database for selected server.\n' \
            f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n'\
            f'{Fore.RED}\n[>>>]Enter command:'

        print(opt, end=' ')
        await self.bot.change_presence(activity=Game("/help"))

    
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        user = message.author
        if user.bot or message.channel.type is ChannelType.private \
            or message.type is MessageType.chat_input_command:
            return
        

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction, exception):
        if isinstance(exception, ApplicationCheckFailure):
            await interaction.response.send_message(embed=Embed(description="Sorry, but you don't have enough permissions"), ephemeral=True)
            return 0
        with open("d.log", "a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [slash command] [{interaction.guild.id}] [{interaction.guild.name}] [{str(exception)}]\n")

def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(msg_h(bot, **kwargs))
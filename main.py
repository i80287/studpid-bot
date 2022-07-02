import nextcord, os, sqlite3
from datetime import datetime, timedelta
from nextcord.ext import commands
#from nextcord.abc import GuildChannel
from contextlib import closing
from config import *
from colorama import Fore
from dpyConsole import Console

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), case_insensitive=True, intents=intents, help_command=None)
cmd = Console(bot)

@bot.event
async def on_ready():
    global bot_guilds
    for guild in bot.guilds:
        if not os.path.exists(f'{path}bases_{guild.id}'):
            os.mkdir(f'{path}bases_{guild.id}/')
            with closing(sqlite3.connect(f'{path}bases_{guild.id}/{guild.id}_store.db')) as base:
                with closing(base.cursor()) as cur:
                    cur.execute('CREATE TABLE IF NOT EXISTS users(memb_id INTEGER PRIMARY KEY, money INTEGER, owned_roles TEXT, work_date INTEGER)')
                    base.commit()
                    cur.execute('CREATE TABLE IF NOT EXISTS server_roles(role_id INTEGER PRIMARY KEY, price INTEGER, special INTEGER)')
                    base.commit()
                    cur.execute('CREATE TABLE IF NOT EXISTS outer_store(item_id INTEGER PRIMARY KEY, role_id INTEGER, quantity INTEGER, price INTEGER, last_date INTEGER, special INTEGER)')
                    base.commit()
                    cur.execute('CREATE TABLE IF NOT EXISTS money_roles(role_id INTEGER NOT NULL PRIMARY KEY, members TEXT, salary INTEGER NOT NULL, last_time INTEGER)')
                    base.commit()
                    cur.execute("CREATE TABLE IF NOT EXISTS server_info(settings TEXT PRIMARY KEY, value INTEGER)")
                    base.commit()
            
                    r = [
                        ('lang', 0), ('log_channel', 0), ('error_log', 0), 
                        ('mod_role', 0), ('tz', 0), ('time_r', 14400), 
                        ('sal_l', 1), ('sal_r', 250), ('uniq_timer', 14400)
                    ]
                    cur.executemany("INSERT INTO server_info(settings, value) VALUES(?, ?)", r)
                    base.commit()
        bot_guilds.append(guild.id)
                
    print(f'{Fore.CYAN}[>>>]Logged into Discord as {bot.user}\n')

    opt=f'\n{Fore.YELLOW}[>>>]Available commands:{Fore.RESET}\n' \
        f'\n{Fore.GREEN} 1) recover <guild_id> - recovers database for selected server from restore file (guild_id_shop_res.db)\n' \
        f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n' \
        f'\n{Fore.GREEN} 2) backup <guild_id> - creates a copy of database for selected server (guild_id_shop_res.db)\n' \
        f'\n 3) setup <guild_id> - creates and setups new database for selected server.\n' \
        f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n'\
        f'{Fore.RED}\n[>>>]Enter command:'

    print(opt, end=' ')
    #status=nextcord.Status.dnd,
    await bot.change_presence(activity=nextcord.Game("/help"))


if __name__ == "__main__":
    for filename in os.listdir(f"{path}commands"):
        if filename.endswith(".py"):
            bot.load_extension(f"commands.{filename[:-3]}", extras={"prefix": prefix, "in_row": in_row, "currency": currency})
    cmd.load_extension(f'console')
    cmd.start()
    print(f'\n{Fore.RED}[>>>]Please, wait a bit...{Fore.RESET}')
    bot.run(token)
    #bot.run(debug_token)

from os import mkdir, path
from sqlite3 import connect
from contextlib import closing

from colorama import Fore
from dpyConsole import console, Cog, Console
from config import path_to


class ConsoleCog(Cog):
    def __init__(self, console: Console):
        super(ConsoleCog, self).__init__()
        self.console = console
    
    @console.command()
    async def setup(self, guild_id, lng = "0"):
        if not path.exists(f"{path_to}/bases/"):
            try:
                mkdir(f"{path_to}/bases/")
            except:
                print(f"Can't create {path_to}/bases folder")

        if not path.exists(f"{path_to}/bases/bases_{guild_id}/"):
            try:
                mkdir(f"{path_to}/bases/bases_{guild_id}/")
            except:
                print(f"{Fore.YELLOW}Can't create path to the database in the {path_to}/bases/ folder!{Fore.RED}\n")


        with closing(connect(f'{path_to}/bases/bases_{guild_id}/{guild_id}.db')) as base:
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
                
                try:
                    lng = int(lng)
                except:
                    lng = 0
                    
                r = [
                    ('lang', lng), ('tz', 0),
                    ('xp_border', 100), ('xp_per_msg', 1), ('mn_per_msg', 1),
                    ('w_cd', 14400), ('sal_l', 1), ('sal_r', 250),
                    ('lvl_c', 0), ('log_c', 0), ('poll_v_c', 0), ('poll_c', 0)
                ]
                    
                cur.executemany("INSERT OR IGNORE INTO server_info(settings, value) VALUES(?, ?)", r)
                base.commit()


        print(f'{Fore.CYAN}[>>>]created and setuped database for {guild_id}{Fore.RED}')

        opt=f'\n{Fore.YELLOW}[>>>]Available commands:{Fore.RESET}\n' \
            f'\n{Fore.GREEN} 1) recover <guild_id> - recovers database for selected server from restore file (guild_id_store_res.db)\n' \
            f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n' \
            f'\n{Fore.GREEN} 2) backup <guild_id> - creates a copy of database for selected server (guild_id_store_res.db)\n' \
            f'\n 3) setup <guild_id> - creates and setups new database for selected server.\n' \
            f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n\n[>>>]Enter command:'
        
        print(opt, end=' ')

def setup(console):
    console.add_console_cog(ConsoleCog(console))
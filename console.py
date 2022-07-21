
import os
from shutil import copy2
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
    async def recover(self, guild_id):
        try:
            copy2(f'{path_to}/bases/bases_{guild_id}/{guild_id}_shop_rec_2.db', f'{path_to}/bases/bases_{guild_id}/{guild_id}.db')
            print(f'{Fore.CYAN}Recovered database for {guild_id}{Fore.RED}')
        except:
            print(f"{Fore.YELLOW}Can't recover database!{Fore.RED}\n")

        opt =   f'\n{Fore.YELLOW}[>>>]Available commands:{Fore.RESET}\n' \
            f'\n{Fore.GREEN} 1) recover <guild_id> - recovers database for selected server from restore file (guild_id_shop_res.db)\n' \
            f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n' \
            f'\n{Fore.GREEN} 2) backup <guild_id> - creates a copy of database for selected server (guild_id_shop_res.db)\n' \
            f'\n 3) setup <guild_id> - creates and setups new database for selected server.\n' \
            f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n\n[>>>]Enter command:'
        
        print(opt, end=' ')

    @console.command()
    async def backup(self, guild_id):
        try:
            src = connect(f'{path_to}/bases/bases_{guild_id}/{guild_id}.db')
            bck = connect(f'{path_to}/bases/bases_{guild_id}/{guild_id}_shop_rec_1.db')
            src.backup(bck)
            src.close()
            bck.close()
            copy2(f'{path_to}/bases/bases_{guild_id}/{guild_id}.db', f'{path_to}/bases/bases_{guild_id}/{guild_id}_shop_rec_2.db')
            print(f'{Fore.CYAN}Created a backup for {guild_id}{Fore.RED}\n')
        except:
            print(f"{Fore.YELLOW}Can't create a backup for the {guild_id}{Fore.RED}")

        opt =   f'\n{Fore.YELLOW}[>>>]Available commands:{Fore.RESET}\n' \
            f'\n{Fore.GREEN} 1) recover <guild_id> - recovers database for selected server from restore file (guild_id_shop_res.db)\n' \
            f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n' \
            f'\n{Fore.GREEN} 2) backup <guild_id> - creates a copy of database for selected server (guild_id_shop_res.db)\n' \
            f'\n 3) setup <guild_id> - creates and setups new database for selected server.\n' \
            f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n\n[>>>]Enter command:'
        
        print(opt, end=' ')
    
    @console.command()
    async def setup(self, guild_id, lng):
        if not os.path.exists(f"{path_to}/bases/"):
            try:
                os.mkdir(f"{path_to}/bases/")
            except:
                print(f"Can't create {path_to}/bases folder")

        if not os.path.exists(f"{path_to}/bases/bases_{guild_id}/"):
            try:
                os.mkdir(f"{path_to}/bases/bases_{guild_id}/")
            except:
                print(f"{Fore.YELLOW}Can't create path to the database in the {path_to}/bases/ folder!{Fore.RED}\n")
        
        """
        elif os.path.exists(f"{path}/bases/bases_{guild_id}/{guild_id}.db"):
            try:
                os.remove(f"{path}/bases/bases_{guild_id}/{guild_id}.db")
            except:
                print(f"{Fore.YELLOW}Can't delete old database!{Fore.RED}\n") """

        with closing(connect(f'{path_to}/bases//bases_{guild_id}/{guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                cur.execute('CREATE TABLE IF NOT EXISTS users(memb_id INTEGER PRIMARY KEY, money INTEGER, owned_roles TEXT, work_date INTEGER)')
                base.commit()
                cur.execute('CREATE TABLE IF NOT EXISTS server_roles(role_id INTEGER PRIMARY KEY, price INTEGER, salary INTEGER, type INTEGER)')
                base.commit()
                cur.execute('CREATE TABLE IF NOT EXISTS store(item_id INTEGER PRIMARY KEY, role_id INTEGER, quantity INTEGER, price INTEGER, last_date INTEGER, salary INTEGER, type INTEGER)')
                base.commit()
                cur.execute('CREATE TABLE IF NOT EXISTS salary_roles(role_id INTEGER PRIMARY KEY, members TEXT, salary INTEGER NOT NULL, last_time INTEGER)')
                base.commit()
                cur.execute("CREATE TABLE IF NOT EXISTS server_info(settings TEXT PRIMARY KEY, value INTEGER)")
                base.commit()
                cur.execute("CREATE TABLE IF NOT EXISTS rank_roles(level INTEGER PRIMARY KEY, role_id INTEGER)")
                base.commit()
                cur.execute("CREATE TABLE IF NOT EXISTS rank(memb_id INTEGER PRIMARY KEY, xp INTEGER, c_xp INTEGER)")
                base.commit()
                cur.execute("CREATE TABLE IF NOT EXISTS ic(chn_id INTEGER PRIMARY KEY)")
                base.commit()
                cur.execute("CREATE TABLE IF NOT EXISTS mod_roles(role_id INTEGER PRIMARY KEY)")
                base.commit()
                try:
                    lng = int(lng)
                except:
                    lng = 0
                    
                r = [
                    ('lang', lng), ("0>>", -1), ('xp_step', 1), ('tz', 0), 
                    ('w_cd', 14400), ('sal_t', 0), ('sal_l', 1), ('sal_r', 250),
                    ('lvl_c', 0), ('log_c', 0), ('poll_v_c', 0), ('poll_c', 0)
                ]
                    
                cur.executemany("INSERT INTO server_info(settings, value) VALUES(?, ?)", r)
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
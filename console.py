from colorama import Fore
from dpyConsole import console, Cog
import shutil, sqlite3, os, dpyConsole
from contextlib import closing

class ConsoleCog(Cog):
    def __init__(self, console: dpyConsole.Console):
        super(ConsoleCog, self).__init__()
        self.console = console

    @console.command()
    async def recover(self, guild_id):
        try:
            shutil.copy2(f'./bases_{guild_id}/{guild_id}_shop_rec_2.db', f'./bases_{guild_id}/{guild_id}_shop.db')
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
            src = sqlite3.connect(f'./bases_{guild_id}/{guild_id}_shop.db')
            bck = sqlite3.connect(f'./bases_{guild_id}/{guild_id}_shop_rec_1.db')
            src.backup(bck)
            src.close()
            bck.close()
            shutil.copy2(f'./bases_{guild_id}/{guild_id}_shop.db', f'./bases_{guild_id}/{guild_id}_shop_rec_2.db')
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
    async def setup(self, guild_id):
        if os.path.exists(f'./bases_{guild_id}/{guild_id}_shop.db'):
            os.remove(f'./bases_{guild_id}/{guild_id}_shop.db')
        else:
            if not os.path.exists(f'./bases_{guild_id}'):
                try:
                    os.mkdir(f'./bases_{guild_id}/')
                except:
                    print(f"{Fore.YELLOW}Can't create database!{Fore.RED}\n")
        
        with closing(sqlite3.connect(f'./bases_{guild_id}/{guild_id}_shop.db')) as base:
            with closing(base.cursor()) as cur:

                cur.execute('CREATE TABLE IF NOT EXISTS users(memb_id INTEGER PRIMARY KEY, money INTEGER, owned_roles TEXT, work_date INTEGER)')
                base.commit()
                cur.execute('CREATE TABLE IF NOT EXISTS server_roles(role_id INTEGER PRIMARY KEY, price INTEGER, special INTEGER)')
                base.commit()
                cur.execute('CREATE TABLE IF NOT EXISTS outer_shop(item_id INTEGER PRIMARY KEY, role_id INTEGER, quantity INTEGER, price INTEGER, last_date INTEGER, special INTEGER)')
                base.commit()
                cur.execute('CREATE TABLE IF NOT EXISTS money_roles(role_id INTEGER NOT NULL PRIMARY KEY, members TEXT, salary INTEGER NOT NULL, last_time INTEGER)')
                base.commit()
                cur.execute("CREATE TABLE IF NOT EXISTS server_info(settings TEXT PRIMARY KEY, value INTEGER)")
                base.commit()
           
                cur.execute("INSERT INTO server_info(settings, value) VALUES('lang', 0)")
                base.commit()           
                cur.execute("INSERT INTO server_info(settings, value) VALUES('log_channel', 0)")
                base.commit()           
                cur.execute("INSERT INTO server_info(settings, value) VALUES('error_log', 0)")
                base.commit()          
                cur.execute("INSERT INTO server_info(settings, value) VALUES('mod_role', 0)")
                base.commit()
                cur.execute("INSERT INTO server_info(settings, value) VALUES('tz', 0)")
                base.commit()
                
        print(f'{Fore.CYAN}[>>>]created and setuped database for {guild_id}{Fore.RED}')

        opt=f'\n{Fore.YELLOW}[>>>]Available commands:{Fore.RESET}\n' \
            f'\n{Fore.GREEN} 1) recover <guild_id> - recovers database for selected server from restore file (guild_id_shop_res.db)\n' \
            f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n' \
            f'\n{Fore.GREEN} 2) backup <guild_id> - creates a copy of database for selected server (guild_id_shop_res.db)\n' \
            f'\n 3) setup <guild_id> - creates and setups new database for selected server.\n' \
            f'{Fore.RED}   Warning: if old database exists, it will be restored to default and all infromation will be lost.\n\n[>>>]Enter command:'
        
        print(opt, end=' ')

def setup(console):
    console.add_console_cog(ConsoleCog(console))
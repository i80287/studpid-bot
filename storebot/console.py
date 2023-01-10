from os import mkdir, path

from dpyConsole import console, Cog, Console
from colorama import Fore

from Tools import db_commands
from Variables.vars import CWD_PATH


class ConsoleCog(Cog):
    def __init__(self, console: Console):
        super(ConsoleCog, self).__init__()
        self.console = console
    
    @console.command()
    async def setup(self, guild_id, str_lng = "1"):
        if not guild_id.isdigit() or (g_id := int(guild_id)) <= 0:
            print("first param (guild id) should be integer > 0")
            return
        if not path.exists(f"{CWD_PATH}/bases/"):
            try:
                mkdir(f"{CWD_PATH}/bases/")
            except:
                print(f"Can't create {CWD_PATH}/bases folder")
                return

        if not path.exists(f"{CWD_PATH}/bases/bases_{guild_id}/"):
            try:
                mkdir(f"{CWD_PATH}/bases/bases_{guild_id}/")
            except:
                print(f"{Fore.YELLOW}Can't create path to the database in the {CWD_PATH}/bases/ folder!{Fore.RED}\n")
                return
        
        db_commands.check_db(guild_id=g_id, guild_locale="ru" if str_lng == "1" else "en-US")

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
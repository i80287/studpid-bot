import nextcord, os
from nextcord.ext import commands
#from nextcord.abc import GuildChannel
from config import token, prefix, in_row, currency, debug_token
from colorama import Fore
from dpyConsole import Console

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), case_insensitive=True, intents=intents, help_command=None)
cmd = Console(bot)

@bot.event
async def on_ready():
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
    await bot.change_presence(activity=nextcord.Game("/shop"))

if __name__ == "__main__":

    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            bot.load_extension(f"commands.{filename[:-3]}", extras={"prefix": prefix, "in_row": in_row, "currency": currency})
            #pass

    cmd.load_extension(f'console')
    cmd.start()
    print(f'\n{Fore.RED}[>>>]Please, wait a bit...{Fore.RESET}')
    bot.run(token)
    #bot.run(debug_token)
import asyncio
import os
from nextcord.ext.commands import Cog

from Variables.vars import CWD_PATH
from dummy_variables import GUILD_ID, dummy_guild, dummy_roles, dummy_interaction
from Commands.slash_shop import SlashCommandsCog
from storebot import StoreBot

from Tools import db_commands

async def main() -> None:
    guild_id: int = GUILD_ID
    if not os.path.exists(f"{CWD_PATH}/bases/bases_{guild_id}/"):
        os.mkdir(f"{CWD_PATH}/bases/bases_{guild_id}/")
    db_commands.check_db(guild_id=guild_id, guild_locale=dummy_guild.preferred_locale)

    test_bot: StoreBot = StoreBot()
    test_bot.load_extensions_from_module("Commands")
    cog: SlashCommandsCog | Cog | None = test_bot.get_cog("SlashCommandsCog")
    if not Cog:
        return

    await cog.bet(interaction=dummy_interaction, amount=42)

    os.remove(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")
    
if __name__ == "__main__":
    asyncio.run(main())

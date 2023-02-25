from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any

    from nextcord import Guild, User, Role

    from .dummy_variables import DummyInteraction

import asyncio
import os

from nextcord import Colour, Member

from storebot.constants import CWD_PATH, DB_PATH
from storebot.Commands.slash_shop import SlashCommandsCog
from storebot.storebot import StoreBot
from storebot.Tools import db_commands

from tests.builder import build_interaction, get_guild, get_test_role, get_bot

async def main() -> None:
    guild: Guild = get_guild()
    guild_id: int = guild.id
    
    dir_path: str = f"{CWD_PATH}/bases/bases_{guild_id}/"
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    
    db_commands.check_db(guild_id=guild_id, guild_locale=guild.preferred_locale)

    test_bot: StoreBot = get_bot()
    test_bot.load_extensions_from_module("storebot.Commands")
    
    cog: SlashCommandsCog | None = test_bot.get_cog("SlashCommandsCog") # type: ignore
    if not cog:
        raise Exception("SlashCommandsCog not found")

    await test_slash_cog(cog)

    os.remove(DB_PATH.format(guild_id))
    os.rmdir(dir_path)

async def test_slash_cog(cog: SlashCommandsCog) -> None:
    interaction: DummyInteraction = build_interaction()
    await cog.bet(interaction=interaction, amount=42)
    
    payload: dict[str, Any] = interaction.payload
    assert "embeds" in payload
    embeds: list[dict[str, Any]] = payload["embeds"]
    assert isinstance(embeds, list)
    assert len(embeds) == 1
    embed_payload: dict[str, Any] = embeds[0]
    assert "color" in embed_payload
    color: int = embed_payload["color"]
    assert isinstance(color, int)
    assert Colour(color) == Colour.dark_grey()
    assert "description" in embed_payload
    description: str = embed_payload["description"]
    assert isinstance(description, str)
    assert description == "**`You can't make a bet, because you need 42`** :coin: **`more`**"
    
    interaction = build_interaction()
    interaction.locale = "ru"
    await cog.bet(interaction=interaction, amount=42)

    payload = interaction.payload
    assert "embeds" in payload
    embeds = payload["embeds"]
    assert isinstance(embeds, list)
    assert len(embeds) == 1
    embed_payload = embeds[0]
    assert "color" in embed_payload
    color = embed_payload["color"]
    assert isinstance(color, int)
    assert Colour(color) == Colour.dark_grey()
    assert "description" in embed_payload
    description = embed_payload["description"]
    assert isinstance(description, str)
    assert description == "**`Вы не можете сделать ставку, так как Вам не хватает 42`** :coin:"

    interaction = build_interaction()
    member: User | Member | None = interaction.user
    assert isinstance(member, Member)
    
    role: Role = get_test_role(False)
    await cog.buy(interaction=interaction, role=role)
    
if __name__ == "__main__":
    asyncio.run(main())

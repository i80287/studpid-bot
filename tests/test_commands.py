from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any

    from nextcord import Guild, Role

    from .dummy_variables import DummyInteraction

import asyncio
import os

from nextcord import Colour, Member
from nextcord.ui.view import View

from storebot.constants import CWD_PATH, DB_PATH
from storebot.Commands.slash_shop import SlashCommandsCog
from storebot.storebot import StoreBot
from storebot.Tools import db_commands
from storebot.Tools.db_commands import RoleInfo
from storebot.CustomComponents.custom_button import CustomButton
from storebot.CustomComponents.view_base import ViewBase

from tests.builder import (
    build_interaction,
    get_guild,
    get_test_role,
    get_bot,
    add_role,
    get_member,
    remove_role,
    add_role_to_db,
    get_connection,
    get_view
)

test_bot: StoreBot = get_bot()
guild: Guild = get_guild()
guild_id: int = guild.id
conn_state = get_connection()

async def main() -> None:
    dir_path: str = f"{CWD_PATH}/bases/bases_{guild_id}/"
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    
    db_path: str = DB_PATH.format(guild_id)
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db_commands.check_db(guild_id=guild_id, guild_locale=guild.preferred_locale)
    
    test_bot.load_extensions_from_module("storebot.Commands")
    
    cog: SlashCommandsCog | None = test_bot.get_cog("SlashCommandsCog") # type: ignore
    if not cog:
        raise Exception("SlashCommandsCog not found")

    try:
        await test_slash_cog(cog)
    except:
        raise
    finally:
        try:
            session = get_connection().http.__session
            if session:
                await session.close()
        except:
            pass
        os.remove(db_path)
        os.rmdir(dir_path)

async def test_slash_cog(cog: SlashCommandsCog) -> None:
    interaction: DummyInteraction = build_interaction()
    await cog.bet(interaction=interaction, amount=42)
    check_embed(interaction.payload, "**`You can't make a bet, because you need 42`** :coin: **`more`**")
    
    interaction = build_interaction()
    interaction.locale = "ru"
    await cog.bet(interaction=interaction, amount=42)
    check_embed(interaction.payload, "**`Вы не можете сделать ставку, так как Вам не хватает 42`** :coin:")

    role = get_test_role()

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role)
    check_embed(interaction.payload, "**`I don't have permission to manage this role. My role should be higher than this role`**")
    
    bot_member: Member = guild.me
    max_guild_role: Role = max(guild.roles)
    add_role(bot_member, max_guild_role)

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role)
    check_embed(interaction.payload, "**`This item not found. Please, check if you selected right role`**")

    member: Member = get_member()

    ROLE_PRICE: int = 100
    role_info: RoleInfo = RoleInfo(role_id=role.id, price=ROLE_PRICE, salary=100, salary_cooldown=86400, role_type=1, additional_salary=42)
    await add_role_to_db(guild_id, role_info, {member.id})

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role)
    check_embed(interaction.payload, "**`You already have this role`**")

    role: Role = get_test_role(False)

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role)
    check_embed(interaction.payload, "**`This item not found. Please, check if you selected right role`**")

    role_info = RoleInfo(role_id=role.id, price=ROLE_PRICE, salary=100, salary_cooldown=86400, role_type=1, additional_salary=42)
    await add_role_to_db(guild_id, role_info)

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role)
    check_embed(interaction.payload, f"**`For purchasing this role you need {ROLE_PRICE} `:coin:` more`**")

    await db_commands.update_member_cash_async(guild_id, member.id, ROLE_PRICE - 1)

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role)
    check_embed(interaction.payload, "**`For purchasing this role you need 1 `:coin:` more`**")

    await db_commands.update_member_cash_async(guild_id, member.id, ROLE_PRICE << 1)

    interaction = build_interaction()

    task: asyncio.Task[None] = asyncio.create_task(cog.buy(interaction=interaction, role=role))
    view: View = await get_view()
    
    assert isinstance(view, ViewBase)
    items = view.children
    assert isinstance(items, list)
    assert len(items) == 2
    button1 = items[0]
    button2 = items[1]
    assert isinstance(button1, CustomButton)
    assert isinstance(button2, CustomButton)
    await button1.callback(build_interaction())
    
    await asyncio.sleep(1.0)
    if task.cancelled() is False:
        task.cancel()

    check_embed(interaction.edit_payload, "**`If your DM are open, then purchase confirmation will be messaged you`**", False)

def check_embed(payload: dict[str, Any], description_text: str, check_color: bool = True):
    assert "embeds" in payload
    embeds = payload["embeds"]
    assert isinstance(embeds, list)
    assert len(embeds) == 1
    embed_payload = embeds[0]
    
    assert "description" in embed_payload
    description = embed_payload["description"]
    assert isinstance(description, str)
    assert description == description_text

    if check_color:
        assert "color" in embed_payload
        color = embed_payload["color"]
        assert isinstance(color, int)
        assert Colour(color) == Colour.dark_grey()

if __name__ == "__main__":
    asyncio.run(main())

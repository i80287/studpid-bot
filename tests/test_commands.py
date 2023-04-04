from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Iterator, Literal

    from nextcord import Guild, Role
    from nextcord.state import ConnectionState

    from .dummy_variables import DummyInteraction

import os
import asyncio
from datetime import datetime, timedelta, timezone

from nextcord import Colour, Member
from nextcord.ui.view import View

from storebot.constants import CWD_PATH, DB_PATH
from storebot.Cogs.slash_cmds_cog import SlashCommandsCog, text_slash as slash_commands_text
from storebot.Cogs.add_cmds_cog import AdditionalCommandsCog
from storebot.storebot import StoreBot
from storebot.Tools import db_commands
from storebot.Tools.db_commands import RoleInfo
from storebot.Components.custom_button import CustomButton
from storebot.Components.view_base import ViewBase

from tests.builder import (
    get_emoji_assets,
    build_interaction,
    get_guild,
    get_test_role,
    get_bot,
    add_role,
    get_member,
    remove_role,
    add_role_to_db,
    get_connection,
    get_view,
    MISSING
)

test_bot: StoreBot = get_bot()
guild: Guild = get_guild()
guild_id: int = guild.id
conn_state: ConnectionState = get_connection()

async def main() -> None:
    exceptions: list[Exception] = []
    dir_path: str | None = None
    db_path: str | None = None
    
    try:
        db_bases_path: str = CWD_PATH + "/bases/"
        if not os.path.exists(db_bases_path):
            os.mkdir(db_bases_path)
        dir_path = CWD_PATH + f"/bases/bases_{guild_id}/"
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        
        db_path = DB_PATH.format(guild_id)
        if os.path.exists(db_path):
            os.remove(db_path)
        
        db_commands.check_db(guild_id=guild_id, guild_locale=guild.preferred_locale)
        
        test_bot.load_extensions_from_module("storebot.Cogs")
        await test_slash_cog()
        print("SlashCommandsCog tests passed")
        await test_add_cmds_cog()
        print("AdditionalCommandsCog tests passed")
    except Exception as ex:
        exceptions.append(ex)
    finally:
        if (session := conn_state.http.__session) is not MISSING:
            try:
                await session.close()
            except Exception as ex:
                exceptions.append(ex)
        if db_path:
            try:
                os.remove(db_path)
            except Exception as ex:
                exceptions.append(ex)
        if dir_path:
            try:
                os.rmdir(dir_path)
            except Exception as ex:
                exceptions.append(ex)
    
    if exceptions:
        print(*exceptions, sep='\n')
        raise exceptions[0]
    else:
        print("All tests passed")

async def test_slash_cog() -> None:
    cog: SlashCommandsCog | None = test_bot.get_cog("SlashCommandsCog") # type: ignore
    if cog is None:
        raise Exception("SlashCommandsCog not found")

    interaction: DummyInteraction = build_interaction()
    await cog.duel(interaction=interaction, amount=42)
    check_embed(interaction, "**`You can't make a bet, because you need 42`** :coin: **`more`**")
    
    interaction = build_interaction()
    interaction.locale = "ru"
    await cog.duel(interaction=interaction, amount=42)
    check_embed(interaction, "**`Вы не можете сделать ставку, так как Вам не хватает 42`** :coin:")

    role = get_test_role()

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role)
    check_embed(interaction, "**`I don't have permission to manage this role. My role should be higher than this role`**")
    
    bot_member: Member = guild.me
    max_guild_role: Role = max(guild.roles)
    add_role(bot_member, max_guild_role)

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role)
    check_embed(interaction, "**`This item not found. Please, check if you selected right role`**")

    member: Member = get_member()
    member_id: int = member.id

    ROLE_PRICE: int = 100
    role_id_member_has: int = role.id
    role_info_member_has: RoleInfo = RoleInfo(role_id=role_id_member_has, price=ROLE_PRICE, salary=100, salary_cooldown=86400, role_type=1, additional_salary=42)
    time_added: int = await add_role_to_db(guild_id, role_info_member_has, {member_id})
    interaction = build_interaction()
    task = asyncio.create_task(cog.store(interaction=interaction))
    view = await get_view()

    assert isinstance(view, ViewBase)
    await asyncio.sleep(1.0)
    view.stop()
    if not task.cancelled():
        task.cancel()
    
    check_store_embed(interaction.payload, role_info_member_has, time_added)

    member_info: tuple[int, int, str, int, int, int] = await db_commands.get_member_async(guild_id, member_id)
    assert member_id == member_info[0]
    assert "#{0}".format(role_id_member_has) == member_info[2]

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role)
    check_embed(interaction, "**`You already have this role`**")

    role_member_does_not_have: Role = get_test_role(False)
    role_id_to_add: int = role_member_does_not_have.id
    assert not member._roles.has(role_id_to_add)

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role_member_does_not_have)
    check_embed(interaction, "**`This item not found. Please, check if you selected right role`**")

    role_info: RoleInfo = RoleInfo(role_id=role_id_to_add, price=ROLE_PRICE, salary=100, salary_cooldown=86400, role_type=1, additional_salary=42)
    await add_role_to_db(guild_id, role_info)

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role_member_does_not_have)
    check_embed(interaction, f"**`For purchasing this role you need {ROLE_PRICE} `:coin:` more`**")

    await db_commands.update_member_cash_async(guild_id, member_id, ROLE_PRICE - 1)

    interaction = build_interaction()
    await cog.buy(interaction=interaction, role=role_member_does_not_have)
    check_embed(interaction, "**`For purchasing this role you need 1 `:coin:` more`**")

    MEMBER_INIT_CASH: int = ROLE_PRICE << 1
    await db_commands.update_member_cash_async(guild_id, member_id, MEMBER_INIT_CASH)

    interaction = build_interaction()
    task: asyncio.Task[None] = asyncio.create_task(cog.buy(interaction=interaction, role=role_member_does_not_have))
    view: View | ViewBase = await get_view()
    
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
    view.stop()
    if not task.cancelled():
        task.cancel()

    check_embed(interaction.edit_payload, slash_commands_text[0][11], False)
    assert await db_commands.get_member_cash_nocheck_async(guild_id, member_id) == MEMBER_INIT_CASH - ROLE_PRICE
    assert member._roles.has(role_id_to_add)

    interaction = build_interaction()
    interaction.locale = "ru"
    await cog.buy(interaction=interaction, role=role_member_does_not_have)
    check_embed(interaction, slash_commands_text[1][5])

    await add_role_to_db(guild_id, role_info)

    interaction = build_interaction()
    interaction.locale = "ru"
    await cog.buy(interaction=interaction, role=role_member_does_not_have)
    check_embed(interaction, slash_commands_text[1][4])
    member._roles.remove(role_id_to_add)
    await db_commands.remove_member_role_async(guild_id, member_id, role_id_to_add)

    interaction = build_interaction()
    interaction.locale = "ru"
    task = asyncio.create_task(cog.buy(interaction=interaction, role=role_member_does_not_have))
    view = await get_view()

    assert isinstance(view, ViewBase)
    items = view.children
    assert isinstance(items, list)
    assert len(items) == 2
    button1 = items[0]
    button2 = items[1]
    assert isinstance(button1, CustomButton)
    assert isinstance(button2, CustomButton)
    button_interaction: DummyInteraction = build_interaction()
    button_interaction.locale = "ru"
    await button1.callback(button_interaction)
    
    await asyncio.sleep(1.0)
    view.stop()
    if not task.cancelled():
        task.cancel()

    check_embed(interaction.edit_payload, slash_commands_text[1][11], False)
    assert await db_commands.get_member_cash_nocheck_async(guild_id, member_id) == MEMBER_INIT_CASH - 2 * ROLE_PRICE
    assert member._roles.has(role_id_to_add)
    member_info = await db_commands.get_member_async(guild_id, member_id)
    assert member_id == member_info[0]
    assert "#{0}#{1}".format(role_id_member_has, role_id_to_add) == member_info[2]

    await db_commands.update_member_cash_async(guild_id, member_id, 0)
    currency: str = await db_commands.get_server_currency_async(guild_id)

    interaction = build_interaction()
    await cog.sell(interaction, role_member_does_not_have)
    check_embed(interaction, slash_commands_text[0][19].format(role_id_to_add, ROLE_PRICE, currency), False)
    member_info = await db_commands.get_member_async(guild_id, member_id)
    assert member_id == member_info[0]
    assert member_info[1] == ROLE_PRICE
    assert "#{0}".format(role_id_member_has) == member_info[2]

    await db_commands.add_member_role_async(guild_id, member_id, role_id_to_add)
    member._roles.add(role_id_to_add)

    interaction = build_interaction()
    interaction.locale = "ru"
    await cog.sell(interaction, role_member_does_not_have)
    check_embed(interaction, slash_commands_text[1][19].format(role_id_to_add, ROLE_PRICE, currency), False)

    member_cash: int = 308
    CONST_CASH = 38
    bot_id: int = bot_member.id
    await db_commands.update_member_cash_async(guild_id, member_id, member_cash)
    assert await db_commands.get_member_cash_nocheck_async(guild_id, member_id) == member_cash
    assert await db_commands.get_member_cash_async(guild_id, member_id) == member_cash
    
    interaction = build_interaction()
    await cog.transfer(interaction, member_cash + CONST_CASH, bot_member)
    check_embed(interaction, slash_commands_text[0][39].format(CONST_CASH, currency))

    interaction = build_interaction()
    interaction.locale = "ru"
    await cog.transfer(interaction, member_cash + CONST_CASH, bot_member)
    check_embed(interaction, slash_commands_text[1][39].format(CONST_CASH, currency))
    
    interaction = build_interaction()
    await cog.transfer(interaction, CONST_CASH, bot_member)
    check_embed(interaction, slash_commands_text[0][41].format(CONST_CASH, currency, bot_id), False)

    interaction = build_interaction()
    interaction.locale = "ru"
    await cog.transfer(interaction, CONST_CASH, bot_member)
    check_embed(interaction, slash_commands_text[1][41].format(CONST_CASH, currency, bot_id), False)


async def test_add_cmds_cog():
    cog: AdditionalCommandsCog | None = test_bot.get_cog("AdditionalCommandsCog") # type: ignore
    if cog is None:
        raise Exception("SlashCommandsCog not found")

    (emoji_id, full_name) = get_emoji_assets()
    description_text: str = f"""**`Emoji:`** {full_name}\n\
**`Raw string:`** \\{full_name}\n\
**`Emoji id:`** {emoji_id}\n\
**`Created at:`** 01/01/2015, 00:00:00\n\
**`URL:`** https://cdn.discordapp.com/emojis/{emoji_id}.png?quality=lossless"""

    interaction: DummyInteraction = build_interaction()   
    await cog.emoji(interaction, emoji_str=str(emoji_id))
    check_embed(interaction, description_text, False)

    interaction = build_interaction()
    await cog.emoji(interaction, emoji_str=full_name)
    check_embed(interaction, description_text, False)

    interaction = build_interaction()
    await cog.emoji(interaction, emoji_str=":black_large_square:")
    check_embed(interaction, "**`Default Discord emoji: `**:black_large_square:", False)

    interaction = build_interaction()
    await cog.server(interaction)
    check_server_ember(interaction)

    interaction = build_interaction()
    interaction.locale = "ru"
    await cog.server(interaction)
    check_server_ember(interaction, 1)

def check_embed(interaction: DummyInteraction | dict[str, Any], description_text: str, check_color: bool = True) -> None:
    payload: dict[str, Any] = \
        interaction \
        if isinstance(interaction, dict) else \
        interaction.payload

    assert "embeds" in payload
    embeds: list[dict[str, Any]] = payload["embeds"]
    assert isinstance(embeds, list)
    assert len(embeds) == 1
    embed_payload: dict[str, Any] = embeds[0]
    
    assert isinstance(embed_payload, dict)
    assert "description" in embed_payload
    description: str = embed_payload["description"]
    assert isinstance(description, str)
    assert description == description_text

    if check_color:
        assert "color" in embed_payload
        color = embed_payload["color"]
        assert isinstance(color, int)
        assert Colour(color) == Colour.dark_grey()

def check_store_embed(payload: dict[str, Any], role_info: RoleInfo, time_added: int, lng: int = 0) -> None:
    assert "embeds" in payload
    embeds: list[dict[str, Any]] = payload["embeds"]
    assert isinstance(embeds, list)
    assert len(embeds) == 1
    embed_payload: dict[str, Any] = embeds[0]
    
    assert isinstance(embed_payload, dict)
    
    assert "description" in embed_payload
    description: str = embed_payload["description"]
    assert isinstance(description, str)
    lines: list[str] = description.split('\n')

    if (role_salary := role_info.salary):
        assert len(lines) == 7
        salary_cooldown: int = role_info.salary_cooldown
        assert salary_cooldown != 0
        salary_per_week: int = 604800 * role_salary // salary_cooldown
        assert lines[5] == \
            (f"`Average passive salary per week` - `{salary_per_week:0,}` :coin:" \
            if not lng else \
            f"`Средний пассивный доход за неделю` - `{salary_per_week:0,}` :coin:")
    else:
        assert len(lines) == 6
    # Last line in lines must be empty
    assert not lines[-1]

    role_id: int = role_info.role_id
    assert lines[0] == f"1 **\u2022** <@&{role_id}>"

    price: int = role_info.price
    assert lines[1] == \
        (f"`Price` - `{price:0,}` :coin:" \
        if not lng else \
        f"`Цена` - `{price:0,}` :coin:")

    assert lines[2] == \
        ("`Left` - `1`" \
        if not lng else \
        "`Осталось` - `1`")

    assert lines[3] == \
        ("`Listed for sale:`" \
         if not lng else \
        "`Выставленa на продажу:`")

    tzinfo: timezone = timezone(timedelta(hours=0))
    date: str = datetime.fromtimestamp(time_added, tz=tzinfo).strftime("%H:%M %d-%m-%Y")
    assert lines[4] == f"*{date}*"
    
    assert "footer" in embed_payload
    footer: dict[str, Any] = embed_payload["footer"]
    assert isinstance(footer, dict)
    assert "text" in footer
    text: str = footer["text"]
    assert isinstance(text, str)
    assert text == ("Page 1 from 1" if not lng else "Страница 1 из 1")

    assert "components" in payload
    components: list[dict[str, Any]] = payload["components"]
    assert len(components) == 3
    
    buttons_action_row: dict[str, Any] = components[0]
    assert "type" in buttons_action_row
    assert buttons_action_row["type"] == 1
    assert "components" in buttons_action_row
    
    buttons: list[dict[str, Any]] = buttons_action_row["components"]
    assert isinstance(buttons, list)
    assert len(buttons) == 4
    for button in buttons:
        assert "type" in button
        assert button["type"] == 2
        assert button["style"] == 2
        assert button["label"] == None
        assert button["disabled"] == False
        assert "emoji" in button
        assert "name" in button["emoji"]
    
    sorting_selects_action_row: dict[str, Any] = components[1]
    assert "type" in sorting_selects_action_row
    assert sorting_selects_action_row["type"] == 1
    assert "components" in sorting_selects_action_row

    select_components: list[dict[str, Any]] = sorting_selects_action_row["components"]
    assert isinstance(select_components, list)
    assert len(select_components) == 1
    
    select_menu: dict[str, Any] = select_components[0]
    assert "type" in select_menu
    assert select_menu["type"] == 3
    assert "options" in select_menu
    
    select_options: list[dict[str, Any]] = select_menu["options"]
    assert isinstance(select_options, list)
    assert len(select_options) == 2
    
    check_option(
        select_options[0],
        "Sort by price" if not lng else "Сортировать по цене",
        "0",
        True
    )
    check_option(
        select_options[1],
        "Sort by date" if not lng else "Сортировать по дате",
        "1",
        False
    )

    assert "placeholder" in select_menu
    assert select_menu["placeholder"] == \
        ("Sort by..." \
        if not lng else \
        "Сортировать по...")

    sorting_types_selects_action_row: dict[str, Any] = components[2]
    assert "type" in sorting_types_selects_action_row
    assert sorting_types_selects_action_row["type"] == 1
    assert "components" in sorting_types_selects_action_row

    select_types_components: list[dict[str, Any]] = sorting_types_selects_action_row["components"]
    assert isinstance(select_types_components, list)
    assert len(select_types_components) == 1
    
    select_menu: dict[str, Any] = select_types_components[0]
    assert "type" in select_menu
    assert select_menu["type"] == 3
    assert "options" in select_menu
    
    select_options: list[dict[str, Any]] = select_menu["options"]
    assert isinstance(select_options, list)
    assert len(select_options) == 2
    
    check_option(
        select_options[0],
        "From the lower price / newer role" if not lng else "От меньшей цены / более свежого товара",
        "0",
        True
    )
    check_option(
        select_options[1],
        "From the higher price / older role" if not lng else "От большей цены / более старого товара",
        "1",
        False
    )

    assert "placeholder" in select_menu
    assert select_menu["placeholder"] == \
        ("Sort from..." \
        if not lng else \
        "Сортировать от...")

def check_server_ember(interaction: DummyInteraction, lng: int = 0) -> None:
    payload: dict[str, Any] = interaction.payload
    assert "embeds" in payload
    embeds: list[dict[str, Any]] = payload["embeds"]
    assert isinstance(embeds, list)
    assert len(embeds) == 1
    embed_payload: dict[str, Any] = embeds[0]

    assert "footer" in embed_payload
    footer: dict[str, Any] = embed_payload["footer"]
    assert "text" in footer
    assert footer["text"] == f"{AdditionalCommandsCog.text_slash[lng][14]}{interaction.guild_id}"

    assert "fields" in embed_payload
    fields: list[dict[str, Any]] = embed_payload["fields"]
    assert isinstance(fields, list)
    assert len(fields) == 8

    index_iter: Iterator[Literal[0, 12, 4, 8, 17, 18, 19, 20]] = iter((0, 12, 4, 8, 17, 18, 19, 20))
    info_text: dict[int, str] = AdditionalCommandsCog.server_info_text[lng]
    for field in fields:
        assert "inline" in field and isinstance(is_inline := field["inline"], bool) and is_inline
        assert "name" in field and isinstance(name := field["name"], str)
        assert name == info_text[next(index_iter)]

def check_option(option: dict[str, Any], label: str, value: str, is_default: bool) -> None:
    assert "label" in option
    option_label: str = option["label"]
    assert isinstance(option_label, str)
    assert option_label == label

    assert "value" in option
    option_value: str = option["value"]
    assert isinstance(option_value, str)
    assert option_value == value

    assert "default" in option
    option_is_default: bool = option["default"]
    assert isinstance(option_is_default, bool)
    assert option_is_default == is_default

    assert "emoji" in option
    assert "name" in option["emoji"]

if __name__ == "__main__":
    asyncio.run(main())

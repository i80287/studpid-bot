from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nextcord.member import Member

from time import time

from storebot.Tools import db_commands
from storebot.Tools.db_commands import RoleInfo
from storebot.constants import DB_PATH
from storebot.Modals.custom_modals import RoleEditModal

from tests.dummy_variables import *

def get_guild() -> Guild:
    return guild

def get_bot() -> StoreBot:
    return bot

def get_test_role(member_has: bool = True) -> Role:
    return GUILD_ROLES[1] if member_has else GUILD_ROLES[GUILD_MEMBER_ROLES_COUNT + 1]

def build_interaction() -> DummyInteraction:
    dummy_interaction_payloads: InteractionPayLoads = build_interaction_payloads()
    return DummyInteraction(data=dummy_interaction_payloads, state=conn_state)

def add_role(member: Member, role: Role) -> Member:
    member._roles.add(role.id)
    return member

def remove_role(member: Member, role: Role) -> Member:
    roles = member._roles
    role_id = role.id
    if roles.has(role_id):
        roles.remove(role.id)
        return member
    
    raise Exception(f"{member!r} does not have {role!r}")

def get_member(bot: bool = False) -> Member:
    return guild.members[0] if bot is False else guild.members[-1]

async def add_role_to_db(guild_id: int, role_info: RoleInfo, members_id_with_role: set[int] = set(), amount: int = 1) -> int:
    await db_commands.add_role_async(guild_id=guild_id, role_info=role_info, members_id_with_role=members_id_with_role)

    # TODO: update bot db layer
    from sqlite3 import connect
    from contextlib import closing
    with closing(connect(DB_PATH.format(guild_id))) as base:
        with closing(base.cursor()) as cur:
            time_added: int = int(time())
            RoleEditModal.update_store(base, cur, role_info.role_id, role_info.price, role_info.salary, role_info.salary_cooldown, role_info.role_type, amount, 0)
    
    return time_added

def get_connection() -> ConnectionState:
    return conn_state

async def get_view() -> View:
    return await views_queue.get()

def get_emoji_assets() -> tuple[int, str]:
    assert isinstance(emoji_id := emoji_payload["id"], int)
    assert (emoji_name := emoji_payload["name"]) is not None
    full_name: str = emoji_name + ':' + str(emoji_id) + '>'
    assert "animated" in emoji_payload
    full_name = "<:a:" + full_name if emoji_payload["animated"] else "<:" + full_name
    return (emoji_id, full_name)

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import (
        Literal,
        LiteralString,
        Callable
    )
    from collections.abc import Iterable, Generator
    from sqlite3 import Cursor, Row

from enum import IntEnum
from random import Random
from time import time
from dataclasses import dataclass
from sqlite3 import connect
from aiosqlite import connect as connect_async
from contextlib import closing
from itertools import pairwise

from .logger import write_one_log_async
from ..constants import CWD_PATH, DB_PATH

_rnd: Random = Random()

class CommandId(IntEnum):
    # 0 is reserved
    STORE = 1
    BUY = 2
    SELL = 3
    SELL_TO = 4
    PROFILE = 5
    ACCEPT_REQUEST = 6
    DECLINE_REQUEST = 7
    WORK = 8
    DUEL = 9
    TRANSFER = 10
    LEADERS = 11
    SLOTS = 12
    ROULETTE = 13

@dataclass(frozen=True, match_args=False)
class RoleInfo:
    role_id: int
    price: int
    salary: int
    salary_cooldown: int
    role_type: int
    additional_salary: int

    @property
    def all_items(self) -> tuple[int, int, int, int, int, int]:
        return (self.role_id, self.price, self.salary, self.salary_cooldown, self.role_type, self.additional_salary)


@dataclass(frozen=True, match_args=False)
class PartialRoleInfo:
    role_id: int
    salary: int
    salary_cooldown: int


@dataclass(frozen=True, match_args=False)
class PartialRoleStoreInfo:
    role_id: int
    price: int
    salary: int
    quantity: int
    role_type: int

async def get_mod_roles_async(guild_id: int) -> list[tuple[int]] | list:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        return await base.execute_fetchall("SELECT * FROM mod_roles;") # type: ignore

async def update_server_info_table_async(guild_id: int, key_name: str, new_value: int) -> None:
    assert isinstance(key_name, str)
    async with connect_async(DB_PATH.format(guild_id)) as base:
        await base.execute("UPDATE server_info SET value = " + str(new_value) + " WHERE settings = '" + key_name + "';")
        await base.commit()

async def update_server_info_table_uncheck_async(guild_id: int, key_name: str, new_value: str) -> None:
    assert isinstance(key_name, str) and isinstance(new_value, str) and new_value.isdecimal()
    async with connect_async(DB_PATH.format(guild_id)) as base:
        await base.execute("UPDATE server_info SET value = " + new_value + " WHERE settings = '" + key_name + "';")
        await base.commit()

async def get_server_info_value_async(guild_id: int, key_name: str) -> int:
    assert isinstance(key_name, str)
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute("SELECT value FROM server_info WHERE settings = '" + key_name + "';") as cur:
            return (await cur.fetchone())[0] # type: ignore

async def get_money_and_xp_async(guild_id: int) -> tuple[int, int]:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute("SELECT value FROM server_info WHERE settings = 'mn_for_voice';") as cur:
            if res := await cur.fetchone():
                money_for_voice: int = res[0]
            else:
                await write_one_log_async(
                    "error.log",
                    f"[FATAL] [ERROR] [empty 'mn_for_voice' fetch result in get_money_and_xp_async line 101] [res: {res}] [guild_id: {guild_id}]"
                )
                money_for_voice = 6

        async with base.execute("SELECT value FROM server_info WHERE settings = 'xp_for_voice';") as cur:
            if res := await cur.fetchone():
                # xp_for_voice: int = res[0]
                return (money_for_voice, res[0])
            else:
                await write_one_log_async(
                    "error.log",
                    f"[FATAL] [ERROR] [empty 'xp_for_voice' fetch result in get_money_and_xp_async line 112] [res: {res}] [guild_id: {guild_id}]"
                )
                # xp_for_voice = 6
                return (money_for_voice, 6)

async def get_server_log_info_async(guild_id: int) -> tuple[int, int]:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute("SELECT value FROM server_info WHERE settings = 'log_c';") as cur:
            log_channel_id: int = (await cur.fetchone())[0] # type: ignore

        if log_channel_id:
            async with base.execute("SELECT value FROM server_info WHERE settings = 'lang';") as cur:
                lng: int = (await cur.fetchone())[0] # type: ignore
            return (log_channel_id, lng)

        return (0, 0)

async def get_server_lvllog_info_async(guild_id: int) -> tuple[list[tuple[int, int]], int, int] | list[tuple[int, int]]:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        db_lvl_rls: list[tuple[int, int]] = await base.execute_fetchall("SELECT level, role_id FROM rank_roles ORDER BY level;") # type: ignore

        async with base.execute("SELECT value FROM server_info WHERE settings = 'lvl_c';") as cur:
            lvl_log_channel_id: int = (await cur.fetchone())[0] # type: ignore

        if lvl_log_channel_id:
            async with base.execute("SELECT value FROM server_info WHERE settings = 'lang';") as cur:
                lng: int = (await cur.fetchone())[0] # type: ignore
            return (db_lvl_rls, lvl_log_channel_id, lng)

        return db_lvl_rls

async def get_server_currency_async(guild_id: int) -> str:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute("SELECT str_value FROM server_info WHERE settings = 'currency';") as cur:
            return (await cur.fetchone())[0] # type: ignore

async def get_member_async(guild_id: int, member_id: int) -> tuple[int, int, str, int, int, int]:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute(
            "SELECT memb_id, money, owned_roles, work_date, xp, voice_join_time FROM users WHERE memb_id = " + str(member_id)
        ) as cur:
            result = await cur.fetchone()
        assert result is None or isinstance(result, tuple)

        if result is not None:
            return tuple(result)

        await base.execute(
            "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, 0, ?, 0, 0, 0)",
            (member_id, "")
        )
        await base.commit()

        return (member_id, 0, "", 0, 0, 0)

async def check_member_async(guild_id: int, member_id: int) -> None:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute("SELECT rowid FROM users WHERE memb_id = ?", (member_id,)) as cur:
            result = await cur.fetchone()
        assert result is None or isinstance(result, tuple)

        if result is None:
            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, 0, ?, 0, 0, 0)",
                (member_id, "")
            )
            await base.commit()

async def get_member_nocheck_async(guild_id: int, member_id: int) -> tuple[int, int, str, int, int, int]:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute("SELECT memb_id, money, owned_roles, work_date, xp, voice_join_time FROM users WHERE memb_id = " + str(member_id)) as cur:
            return tuple(await cur.fetchone()) # type: ignore

async def get_member_cash_async(guild_id: int, member_id: int) -> int:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute("SELECT money FROM users WHERE memb_id = " + str(member_id)) as cur:
            res = await cur.fetchone()
            if res:
                return res[0]
            
            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, 0, ?, 0, 0, 0)",
                (member_id, "")
            )
            await base.commit()
            return 0

async def get_member_cash_nocheck_async(guild_id: int, member_id: int) -> int:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute("SELECT money FROM users WHERE memb_id = " + str(member_id)) as cur:
            return (await cur.fetchone())[0] # type: ignore

async def update_member_cash_async(guild_id: int, member_id: int, cash: int) -> None:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        await base.execute("UPDATE users SET money = ? WHERE memb_id = ?", (cash, member_id))
        await base.commit()

async def check_member_level_async(guild_id: int, member_id: int) -> int:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        xp_b: int = (await (await base.execute("SELECT value FROM server_info WHERE settings = 'xp_border';")).fetchone())[0] # type: ignore
        mn_p_m: int = (await (await base.execute("SELECT value FROM server_info WHERE settings = 'mn_per_msg';")).fetchone())[0] # type: ignore
        xp_p_m: int = (await (await base.execute("SELECT value FROM server_info WHERE settings = 'xp_per_msg';")).fetchone())[0] # type: ignore 
        member_row = await (await base.execute("SELECT xp FROM users WHERE memb_id = ?", (member_id,))).fetchone() # type: ignore
        assert member_row is None or isinstance(member_row, tuple)

        if member_row:
            await base.execute("UPDATE users SET money = money + ?, xp = xp + ? WHERE memb_id = ?", (mn_p_m, xp_p_m, member_id))
            await base.commit()
            xp = member_row[0]
            assert isinstance(xp, int)
            old_level: int = (xp - 1) // xp_b + 1
            new_level: int = (xp + xp_p_m - 1) // xp_b + 1
            if old_level == new_level:
                return 0
            return new_level
        else:
            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, ?, ?, 0, ?, 0)",
                (member_id, mn_p_m, "", xp_p_m)
            )
            await base.commit()
            return 1

async def register_user_voice_channel_join(guild_id: int, member_id: int, time_join: int) -> None:
    str_member_id = str(member_id)
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute("SELECT rowid FROM users WHERE memb_id = " + str_member_id) as cur:
            result = await cur.fetchone()
        assert result is None or isinstance(result, tuple)

        if result is not None:
            await base.execute(
                "UPDATE users SET voice_join_time = ? WHERE memb_id = " + str_member_id,
                (time_join,)
            )
        else:
            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, 0, ?, 0, 0, ?)",
                (member_id, "", time_join)
            )
            
        await base.commit()

async def register_user_voice_channel_left(
        guild_id: int,
        member_id: int,
        money_for_voice: int,
        xp_for_voice: int,
        time_left: int) -> tuple[int, int, int, int]:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute("SELECT xp, voice_join_time FROM users WHERE memb_id = " + str(member_id)) as cur:
            result = await cur.fetchone()
        assert result is None or (isinstance(result, tuple) and len(result) == 2)

        if result is not None:    
            if not (voice_join_time := result[1]):
                return (0, 0, 0, 0)

            xp = result[0]
        else:
            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, 0, ?, 0, 0, 0)",
                (member_id, "")
            )
            await base.commit()
            return (0, 0, 0, 1)

        time_delta = time_left - voice_join_time
        money_for_voice = (time_delta * money_for_voice) // 600
        xp_for_voice = (time_delta * xp_for_voice) // 600
        await base.execute(
            "UPDATE users SET money = money + ?, xp = xp + ?, voice_join_time = 0 WHERE memb_id = ?",
            (money_for_voice, xp_for_voice, member_id)
        )
        await base.commit()

        xp_border: int = (await (await base.execute("SELECT value FROM server_info WHERE settings = 'xp_border';")).fetchone())[0] # type: ignore
        old_level: int = (xp - 1) // xp_border + 1
        new_level: int = (xp + xp_for_voice - 1) // xp_border + 1

    return (money_for_voice, xp_for_voice, voice_join_time, (0 if old_level == new_level else new_level))

async def register_user_voice_channel_left_with_join_time(
        guild_id: int,
        member_id: int,
        money_for_voice: int,
        xp_for_voice: int,
        time_join: int,
        time_left: int) -> tuple[int, int, int]:
    time_delta: int = time_left - time_join
    money_for_voice = (time_delta * money_for_voice) // 600
    xp_for_voice = (time_delta * xp_for_voice) // 600

    async with connect_async(DB_PATH.format(guild_id)) as base:
        await base.execute(
            "INSERT INTO users(memb_id,money,owned_roles,work_date,xp,voice_join_time)"
            f"VALUES({member_id},{money_for_voice},'',0,{xp_for_voice},0)"
            "ON CONFLICT(memb_id) DO UPDATE SET"
            " money=money+excluded.money,"
            " xp=xp+excluded.xp,"
            " voice_join_time=0;"
        )
        await base.commit()

        xp: int = (await (await base.execute("SELECT xp FROM users WHERE memb_id = " + str(member_id))).fetchone())[0] # type: ignore
        xp_border: int = (await (await base.execute("SELECT value FROM server_info WHERE settings = 'xp_border';")).fetchone())[0] # type: ignore
        old_level: int = (xp - 1) // xp_border + 1
        new_level: int = (xp + xp_for_voice - 1) // xp_border + 1

    return (money_for_voice, xp_for_voice, (0 if old_level == new_level else new_level))

async def add_role_async(guild_id: int, role_info: RoleInfo, members_id_with_role: set[int]) -> None:
    role_id: int = role_info.role_id
    salary: int = role_info.salary
    async with connect_async(DB_PATH.format(guild_id)) as base:
        await base.execute(
            "INSERT OR IGNORE INTO server_roles (role_id, price, salary, salary_cooldown, type, additional_salary) VALUES(?, ?, ?, ?, ?, ?)", 
            role_info.all_items
        )    
        await base.commit()

        str_role_id: str = str(role_id)
        if members_id_with_role:
            for member_id in members_id_with_role:
                async with base.execute("SELECT owned_roles FROM users WHERE memb_id = ?", (member_id,)) as cur:
                    result = await cur.fetchone()
                assert result is None or isinstance(result, tuple)

                if result is not None:
                    owned_roles: str = result[0]
                    if str_role_id not in owned_roles:
                        owned_roles += ('#' + str_role_id)
                        await base.execute("UPDATE users SET owned_roles = ? WHERE memb_id = ?", (owned_roles, member_id))
                else:
                    await base.execute(
                        "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, 0, ?, 0, 0, 0)",
                        (member_id, '#' + str_role_id)
                    )

            await base.commit()

        if salary:
            async with base.execute("SELECT members FROM salary_roles WHERE role_id = " + str_role_id) as cur:
                result = await cur.fetchone()
            assert result is None or isinstance(result, tuple)

            if result is None:
                salary_cooldown: int = role_info.salary_cooldown
                role_owners: str = '#' + '#'.join(map(str, members_id_with_role)) if members_id_with_role else ""
                await base.execute(
                    "INSERT OR IGNORE INTO salary_roles (role_id, members, salary, salary_cooldown, last_time) VALUES(?, ?, ?, ?, 0)", 
                    (role_id, role_owners, salary, salary_cooldown)
                )
            else:
                role_owners: str = result[0]
                owners_ids_in_db: set[int] = {int(owner_id) for owner_id in role_owners.split('#') if owner_id.isdecimal()}
                owners_ids_in_db |= members_id_with_role
                role_owners: str = '#' + '#'.join(map(str, owners_ids_in_db)) if owners_ids_in_db else ""
                await base.execute(
                    "UPDATE salary_roles SET members = ? WHERE role_id = ?",
                    (role_owners, role_id)
                )

            await base.commit()

async def verify_role_members_async(guild_id: int, role_info: PartialRoleInfo, members_id_with_role: set[int]) -> None:
    role_id: int = role_info.role_id
    salary: int = role_info.salary
    str_role_id: str = str(role_id)
    add_str_role_id: str = '#' + str_role_id
    async with connect_async(DB_PATH.format(guild_id)) as base:
        for member_id in members_id_with_role:
            async with base.execute("SELECT owned_roles FROM users WHERE memb_id = ?", (member_id,)) as cur:
                result = await cur.fetchone()
            assert result is None or isinstance(result, tuple)

            if result is None:
                await base.execute(
                    "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, 0, ?, 0, 0, 0)",
                    (member_id, add_str_role_id)
                )
            else:
                owned_roles: str = result[0]
                if add_str_role_id not in owned_roles:
                    owned_roles += add_str_role_id
                    await base.execute("UPDATE users SET owned_roles = ? WHERE memb_id = ?", (owned_roles, member_id))
        await base.commit()

        if not salary:
            return

        async with base.execute("SELECT members FROM salary_roles WHERE role_id = " + str_role_id) as cur:
            result = await cur.fetchone()
        assert result is None or isinstance(result, tuple)

        if result is None:
            role_owners: str = '#' + '#'.join(map(str, members_id_with_role)) if members_id_with_role else ""
            await base.execute(
                "INSERT OR IGNORE INTO salary_roles (role_id, members, salary, salary_cooldown, last_time) VALUES(?, ?, ?, ?, 0)", 
                (role_id, role_owners, salary, role_info.salary_cooldown)
            )
        else:
            role_owners: str = result[0]
            owners_ids_in_db: set[int] = {int(owner_id) for owner_id in role_owners.split('#') if owner_id.isdecimal()}
            owners_ids_in_db |= members_id_with_role
            role_owners: str = '#' + '#'.join(map(str, owners_ids_in_db)) if owners_ids_in_db else ""
            await base.execute("UPDATE salary_roles SET members = '" + role_owners + "' WHERE role_id = " + str_role_id)

        await base.commit()

async def add_member_role_async(guild_id: int, member_id: int, role_id: int) -> bool:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        str_role_id: str = str(role_id)
        async with base.execute("SELECT salary, salary_cooldown FROM server_roles WHERE role_id = " + str_role_id) as cur:
            role_info_row = await cur.fetchone()
        assert role_info_row is None or isinstance(role_info_row, tuple)
        
        if not role_info_row:
            return False
        
        str_member_id: str = str(member_id)
        # Update member's roles in users table.
        async with base.execute("SELECT owned_roles FROM users WHERE memb_id = " + str_member_id) as cur:
            result = await cur.fetchone()
        assert result is None or isinstance(result, tuple)

        is_added: bool = False
        if result is None:
            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, 0, ?, 0, 0, 0)",
                (member_id, '#' + str_role_id)
            )
            await base.commit()
            is_added = True
        else:
            str_member_roles_ids: str = result[0]
            if str_role_id not in str_member_roles_ids:
                await base.execute("UPDATE users SET owned_roles = '" + str_member_roles_ids + '#' + str_role_id + "' WHERE memb_id = " + str_member_id)
                await base.commit()
                is_added = True
            del str_member_roles_ids
        del result
        
        salary: int = role_info_row[0]
        if not salary:
            return is_added
        
        # If role has salary.
        async with base.execute("SELECT members FROM salary_roles WHERE role_id = " + str_role_id) as cur:
            result = await cur.fetchone()
        assert result is None or isinstance(result, tuple)

        if result is None:
            await base.execute(
                "INSERT INTO salary_roles (role_id, members, salary, salary_cooldown, last_time) VALUES (?, ?, ?, ?, 0)",
                (role_id, '#' + str_member_id, salary, role_info_row[1])
            )
            await base.commit()
        else:        
            str_role_owners_ids: str = result[0]
            if str_member_id not in str_role_owners_ids:
                await base.execute("UPDATE salary_roles SET members = '" + str_role_owners_ids + '#' + str_member_id + "' WHERE role_id = " + str_role_id)
                await base.commit()
            
        return is_added

async def remove_member_role_async(guild_id: int, member_id: int, role_id: int) -> bool:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        str_role_id: str = str(role_id)
        async with base.execute("SELECT salary FROM server_roles WHERE role_id = " + str_role_id) as cur:
            role_info_row = await cur.fetchone()
        assert role_info_row is None or isinstance(role_info_row, tuple)
        
        if not role_info_row:
            return False
        
        str_member_id: str = str(member_id)
        # Update member's roles in users table.
        async with base.execute("SELECT owned_roles FROM users WHERE memb_id = " + str_member_id) as cur:
            result = await cur.fetchone()
        assert result is None or isinstance(result, tuple)

        is_removed: bool = False
        if result is None:
            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, 0, ?, 0, 0, 0)",
                (member_id, "")
            )
            await base.commit()
            is_removed = True
        else:
            str_member_roles_ids: str = result[0]
            if str_role_id in str_member_roles_ids:
                await base.execute("UPDATE users SET owned_roles = '" + str_member_roles_ids.replace('#' + str_role_id, "") + "' WHERE memb_id = " + str_member_id)
                await base.commit()
                is_removed = True
            del str_member_roles_ids
        del result

        salary: int = role_info_row[0]
        if not salary:
            return is_removed
        
        # If role has salary.
        async with base.execute("SELECT members FROM salary_roles WHERE role_id = " + str_role_id) as cur:
            result = await cur.fetchone()
        assert result is None or isinstance(result, tuple)

        if result is None:
            return is_removed
        
        str_role_owners_ids: str = result[0]
        if str_member_id in str_role_owners_ids:
            str_role_owners_ids = str_role_owners_ids.replace('#' + str_member_id, "")
            # if str_role_owners_ids:
            await base.execute("UPDATE salary_roles SET members = '" + str_role_owners_ids + "' WHERE role_id = " + str_role_id)
            # else:
            #     await base.execute("DELETE FROM salary_roles WHERE role_id = " + str_role_id)
            await base.commit()
        
        return is_removed

async def process_bought_role(guild_id: int, member_id: int, buyer_member_roles: str, role_info: PartialRoleStoreInfo) -> None:
    role_id: int = role_info.role_id
    price: int = role_info.price
    role_type: int = role_info.role_type
    salary: int = role_info.salary
    str_role_id: str = str(role_id)

    async with connect_async(DB_PATH.format(guild_id)) as base:
        await base.execute(
            "UPDATE users SET money = money - ?, owned_roles = ? WHERE memb_id = ?;",
            (price, buyer_member_roles + '#' + str_role_id, member_id)
        )
            
        if role_type == 1:
            query: str = "SELECT rowid FROM store WHERE role_id = " + str_role_id + " ORDER BY last_date;"
            rowid_to_delete: int = (await (await base.execute(query)).fetchone())[0] # type: ignore
            await base.execute("DELETE FROM store WHERE rowid = " + str(rowid_to_delete))
        elif role_type == 2:
            if role_info.quantity > 1:
                await base.execute("UPDATE store SET quantity = quantity - 1 WHERE role_id = " + str_role_id)
            else:
                await base.execute("DELETE FROM store WHERE role_id = " + str_role_id)

        await base.commit()

        if salary:
            role_members = (await (await base.execute("SELECT members FROM salary_roles WHERE role_id = " + str_role_id)).fetchone())
            assert role_members is None or isinstance(role_members, tuple)
            if role_members:
                new_role_members: str = role_members[0] + '#' + str(member_id)
                await base.execute("UPDATE salary_roles SET members = '" + new_role_members + "' WHERE role_id = " + str_role_id)
                
            await base.commit()

async def process_salary_roles(guild_id: int) -> None:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        roles_info: list[tuple[int, str, int, int, int]] | list = \
            await base.execute_fetchall("SELECT role_id, members, salary, salary_cooldown, last_time FROM salary_roles;") # type: ignore
        if roles_info:
            time_now: int = int(time())
            for role_id, role_owners, salary, t, last_time in roles_info:
                if not last_time or time_now - last_time >= t:
                    await base.execute("UPDATE salary_roles SET last_time = ? WHERE role_id = ?;", (time_now, role_id))
                    await base.commit()
                    str_member_ids: set[str] = {member_id for member_id in role_owners.split("#") if member_id}
                    for str_member_id in str_member_ids:
                        await base.execute("UPDATE users SET money = money + ? WHERE memb_id = " + str_member_id, (salary,))
                        await base.commit()

async def drop_users_cash_async(guild_id: int) -> None:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        await base.execute("UPDATE users SET money = 0;")
        await base.commit()

def peek_role_free_number_depricated(cur: Cursor) -> int:
    req: list[tuple[int]] = cur.execute("SELECT role_number FROM store ORDER BY role_number").fetchall()
    if req:
        role_numbers: list[int] = [r_n[0] for r_n in req]
        del req
        if role_numbers[0] != 1:
            return 1
        for current_role_number, next_role_number in pairwise(role_numbers):
            if current_role_number + 1 != next_role_number:
                return current_role_number + 1
        return len(role_numbers) + 1
    else:
        return 1

def peek_role_free_number(req: Iterable[tuple[int]] | list[tuple[int]]) -> int:
    if req:
        role_numbers: list[int] = [r_n[0] for r_n in req]
        if role_numbers[0] != 1:
            return 1
        for current_role_number, next_role_number in pairwise(role_numbers):
            if current_role_number + 1 != next_role_number:
                return current_role_number + 1
        return len(role_numbers) + 1
    else:
        return 1

def peek_free_request_id(cur: Cursor) -> int:
    request_ids_list: list[tuple[int]] = cur.execute("SELECT request_id FROM sale_requests ORDER BY request_id").fetchall()
    if request_ids_list:
        request_ids: set[int] = {req_id_tuple[0] for req_id_tuple in request_ids_list}
        del request_ids_list
        free_requests_ids: set[int] = set(range(1, len(request_ids) + 2)).__sub__(request_ids)
        return min(free_requests_ids)
    else:
        return 1

def peek_role_free_numbers(cur: Cursor, amount_of_numbers: int) -> list[int]:
    req: list[tuple[int]] = cur.execute("SELECT role_number FROM store").fetchall()
    if req:
        role_numbers: set[int] = {r_n[0] for r_n in req}
        del req
        after_last_number: int =  max(role_numbers) + 1
        free_numbers: set[int] = set(range(1, after_last_number)).__sub__(role_numbers)
        lack_numbers_len: int = amount_of_numbers - len(free_numbers)
        if lack_numbers_len <= 0:
            return list(free_numbers)[:amount_of_numbers]            
        free_numbers.update(range(after_last_number, after_last_number + lack_numbers_len))
        return list(free_numbers)
    else:
        return list(range(1, amount_of_numbers + 1))

def delete_role_from_db(guild_id: int, str_role_id: str) -> None:
    with closing(connect(DB_PATH.format(guild_id))) as base:
        with closing(base.cursor()) as cur:
            cur.executescript("""\
DELETE FROM server_roles WHERE role_id = {0};\
DELETE FROM salary_roles WHERE role_id = {0};\
DELETE FROM store WHERE role_id = {0};\
DELETE FROM sale_requests WHERE role_id = {0};""".format(str_role_id)
            )
            base.commit()
            memb_ids_and_roles: list[tuple[int, str]] = cur.execute("SELECT memb_id, owned_roles FROM users").fetchall()
            for memb_id, owned_roles in memb_ids_and_roles:
                if str_role_id in owned_roles:
                    cur.execute(
                        "UPDATE users SET owned_roles = ? WHERE memb_id = ?",
                        (owned_roles.replace('#' + str_role_id, ""), memb_id)
                    )
                    base.commit()

async def get_ignored_channels(guild_id: int) -> list[tuple[int, int, int]]:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        return await base.execute_fetchall("SELECT chnl_id, is_text, is_voice FROM ignored_channels;") # type: ignore

async def get_buy_command_params_async(guild_id: int, str_role_id: str) -> tuple[tuple[int, int, int, int] | None, str]:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        store: tuple[int, int, int, int] | None = await (await (base.execute(
            "SELECT quantity, price, salary, type FROM store WHERE role_id = " + str_role_id
        ))).fetchone() # type: ignore

        currency: str = (await (await base.execute(
            "SELECT str_value FROM server_info WHERE settings = 'currency';"
        )).fetchone())[0] if store else "" # type: ignore

        return (store, currency)

async def process_sell_command_async(guild_id: int, role_id: int, member_id: int) -> int:
    """Process role sale

    Args:
        guild_id (int): id of the guild (discord server)
        role_id (int): id of the role
        member_id (int): id of the member

    Returns:
        int:
            `-1` if guild's economy is disabled

            `-2` if role is not added to the bot

            `-3` if member does not have this role

            `price of the role` otherwise (non-negative integer)
    """
    str_role_id: str = str(role_id)
    time_now: int = int(time())

    async with connect_async(DB_PATH.format(guild_id)) as base:
        if not (await (await base.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled';")).fetchone())[0]: # type: ignore
            return -1

        role_info: tuple[int, int, int, Literal[1, 2, 3]] | None = await ((await base.execute(
            "SELECT price, salary, salary_cooldown, type FROM server_roles WHERE role_id = " + str_role_id
        )).fetchone()) # type: ignore
        
        if not role_info:
            return -2

        str_member_id: str = str(member_id)
        result = await (await base.execute("SELECT owned_roles FROM users WHERE memb_id = " + str_member_id)).fetchone()  
        assert result is None or isinstance(result, tuple)

        if result is not None:
            owned_roles: set[str] = {str_role_id for str_role_id in result[0].split('#') if str_role_id}
            if str_role_id not in owned_roles:
                return -3
            owned_roles.remove(str_role_id)
        else:
            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, 0, ?, 0, 0, 0)",
                (member_id, "")
            )
            await base.commit()
            return -3

        sale_price_percent: int = (await (await base.execute("SELECT value FROM server_info WHERE settings = 'sale_price_perc'")).fetchone())[0] # type: ignore
        role_price: int = role_info[0]
        sale_price: int = role_price if (sale_price_percent == 100) else (role_price * sale_price_percent // 100)
        assert isinstance(role_price, int)
        assert isinstance(sale_price, int)

        new_owned_roles: str = ('#' + '#'.join(owned_roles)) if owned_roles else ""
        await base.execute(
            "UPDATE users SET owned_roles = '" + new_owned_roles + "', money = money + ? WHERE memb_id = " + str_member_id,
            (sale_price,)
        )
        await base.execute("DELETE FROM sale_requests WHERE seller_id = " + str_member_id + " AND role_id = " + str_role_id)
        await base.commit()

        role_salary: int = role_info[1]
        role_salary_cooldown: int = role_info[2]
        role_type: int = role_info[3]
        assert isinstance(role_salary, int)
        assert isinstance(role_salary_cooldown, int)
        assert isinstance(role_type, int)

        if role_type == 1:
            req: Iterable[tuple[int]] = await base.execute_fetchall("SELECT role_number FROM store ORDER BY role_number;") # type: ignore
            role_free_number: int = peek_role_free_number(req)
            del req
            await base.execute(
                "INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, 1, ?, ?, ?, ?, 1);",
                (role_free_number, role_id, role_price, time_now, role_salary, role_salary_cooldown)
            )
        else:
            in_store_amount: int = (await (await base.execute("SELECT count() FROM store WHERE role_id = " + str_role_id)).fetchone())[0] # type: ignore
            if in_store_amount:
                query: LiteralString = \
                    "UPDATE store SET quantity = quantity + 1, last_date = ? WHERE role_id = ?;" \
                    if role_type == 2 else \
                    "UPDATE store SET last_date = ? WHERE role_id = ?;"
                await base.execute(query, (time_now, role_id))
            else:
                req: Iterable[tuple[int]] = await base.execute_fetchall("SELECT role_number FROM store ORDER BY role_number;") # type: ignore
                role_free_number: int = peek_role_free_number(req)
                
                query: LiteralString = \
                    "INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, 1, ?, ?, ?, ?, 2);" \
                    if role_type == 2 else \
                    "INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, -404, ?, ?, ?, ?, 3);"
                await base.execute(query, (role_free_number, role_id, role_price, time_now, role_salary, role_salary_cooldown))
        
        await base.commit()

        if role_salary:
            role_members: tuple[str] | None = await (await base.execute("SELECT members FROM salary_roles WHERE role_id = " + str_role_id)).fetchone() # type: ignore
            if role_members:
                new_role_members: str = role_members[0].replace('#' + str_role_id, "")
                await base.execute("UPDATE salary_roles SET members = '" + new_role_members + "' WHERE role_id = " + str_role_id)
                await base.commit()

        return sale_price

async def process_work_command_async(guild_id: int, member_id: int) -> tuple[int, int, list[tuple[int, int]] | None]:
    """Process `/work` command

    Args:
        guild_id (int): id of the guild (discord server)
        member_id (int): id of the member

    Returns:
        `tuple`:
            `(-1, 0, None)` if guild's economy is disabled

            `(-2, time_lasted_for_cooldown_break, None)` if user should wait some time to use the command again

            `(salary, additional_salary, list of role | None)` (`None` if `additional_salary` = `0`)
    """
    # init before open conn to db
    time_now: int = int(time())
    str_member_id: str = str(member_id)

    async with connect_async(DB_PATH.format(guild_id)) as base:
        if not (await (await base.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled';")).fetchone())[0]: # type: ignore
            return (-1, 0, None)

        sal_l: int = (await(await base.execute("SELECT value FROM server_info WHERE settings = 'sal_l';")).fetchone())[0] # type: ignore
        sal_r: int = (await(await base.execute("SELECT value FROM server_info WHERE settings = 'sal_r';")).fetchone())[0] # type: ignore
        assert isinstance(sal_l, int)
        assert isinstance(sal_r, int)

        salary: int = sal_l

        if sal_l != sal_r:
            # inlining random.randint
            getrandbits: Callable[[int], int] = _rnd.getrandbits
            n: int = sal_r - sal_l
            k: int = n.bit_length()  # don't use (n-1) here because n can be 1
            r: int = getrandbits(k)  # 0 <= r < 2**k
            while r > n:
                r = getrandbits(k)
            salary += r

        result = await (await base.execute(
            "SELECT owned_roles, work_date FROM users WHERE memb_id = " + str_member_id
        )).fetchone()
        assert result is None or isinstance(result, tuple)

        if result is None:    
            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, ?, ?, 0, 0, 0);",
                (member_id, salary, "")
            )
            await base.commit()
            return (salary, 0, None)

        work_date: int = result[1]
        command_cooldown: int = (await (await base.execute("SELECT value FROM server_info WHERE settings = 'w_cd';")).fetchone())[0] # type: ignore
        if work_date and (lasted_time := time_now - work_date) < command_cooldown:
            return (-2, command_cooldown - lasted_time, None)

        member_roles_ids: tuple[str, ...] = tuple(role_id for role_id in result[0].split('#') if role_id)
        if member_roles_ids:
            memb_roles_add_salary: list[tuple[int, int]] = await base.execute_fetchall(
"""\
WITH cte AS (SELECT role_id, additional_salary FROM server_roles WHERE role_id IN ({0}))
SELECT 0, sum(additional_salary) FROM cte
UNION SELECT * FROM cte;""".format(", ".join(member_roles_ids))
            ) # type: ignore
            
            # `additional_salary` may be equal to 0.
            additional_salary: int = memb_roles_add_salary[0][1]
            if additional_salary:
                assert len(memb_roles_add_salary) > 1
                # if additional_salary != 0 then there is at least one role
                # in `memb_roles_add_salary` so len(memb_roles_add_salary) > 1
                await base.execute(
                    "UPDATE users SET money = money + ?, work_date = ? WHERE memb_id = " + str_member_id,
                    (salary + additional_salary, time_now)
                )
                await base.commit()
                return (salary, additional_salary, memb_roles_add_salary[1:])

        await base.execute(
            "UPDATE users SET money = money + ?, work_date = ? WHERE memb_id = " + str_member_id,
            (salary, time_now)
        )
        await base.commit()
        return (salary, 0, None)

async def process_transfer_command_async(guild_id: int, member_id: int, target_id: int, value: int) -> tuple[int, str]:
    """Process `/transfer` command

    Args:
        guild_id (int): id of the guild (discord server)
        member_id (int): id of the member

    Returns:
        `tuple`:
            `(-1, currency)` if guild's economy is disabled

            `(-2, currency)` if transfer command is disabled

            `(member_cash + 1, currency)` if member has less money then `value`

            `(0, currency)` otherwise
    """
    assert value > 0
    async with connect_async(DB_PATH.format(guild_id)) as base:
        currency: str = (await (await base.execute("SELECT str_value FROM server_info WHERE settings = 'currency';")).fetchone())[0] # type: ignore

        if not (await (await base.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled';")).fetchone())[0]: # type: ignore
            return (-1, currency)
        
        assert CommandId.TRANSFER == 10
        cmd_status = await (await base.execute("SELECT is_enabled FROM commands_settings WHERE command_id = 10;")).fetchone()
        assert cmd_status is None or isinstance(cmd_status, tuple)
        if not cmd_status or not cmd_status[0]:
            return (-2, currency)

        str_member_id = str(member_id)
        member_cash_res = await (await base.execute("SELECT money FROM users WHERE memb_id = " + str_member_id)).fetchone()
        assert member_cash_res is None or isinstance(member_cash_res, tuple)
        if member_cash_res:
            member_cash: int = member_cash_res[0]
        else:
            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, 0, ?, 0, 0, 0)",
                (member_id, "")
            )
            await base.commit()
            return (1, currency)

        if member_cash < value:
            return (member_cash + 1, currency)

        await base.execute("UPDATE users SET money = money - ? WHERE memb_id = " + str_member_id, (value,))
        await base.commit()
        await base.execute("UPDATE users SET money = money + ? WHERE memb_id = " + str(target_id), (value,))
        await base.commit()
    
    return (0, currency)            

async def is_command_enabled_async(guild_id: int, command_id: CommandId) -> bool:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        res = await (await base.execute("SELECT is_enabled FROM commands_settings WHERE command_id = " + str(command_id))).fetchone()
        return res is not None and res[0]

async def is_command_disabled_async(guild_id: int, command_id: CommandId) -> bool:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        res = await (await base.execute("SELECT is_enabled FROM commands_settings WHERE command_id = " + str(command_id))).fetchone()
        return res is None or not res[0]

async def enable_economy_commands_async(guild_id: int) -> None:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        await base.executemany(
            "UPDATE commands_settings SET is_enabled = 1 WHERE command_id = ?",
            (# Pure economy commands.
                (CommandId.STORE,),
                (CommandId.BUY,),
                (CommandId.SELL,),
                (CommandId.SELL_TO,),
                (CommandId.ACCEPT_REQUEST,),
                (CommandId.DECLINE_REQUEST,),
                (CommandId.WORK,),
                (CommandId.DUEL,),
                (CommandId.TRANSFER,),
                (CommandId.SLOTS,),
                (CommandId.ROULETTE,)
            )
        )
        await base.commit()

async def disable_economy_commands_async(guild_id: int) -> None:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        await base.executemany(
            "UPDATE commands_settings SET is_enabled = 0 WHERE command_id = ?",
            (# Pure economy commands.
                (CommandId.STORE,),
                (CommandId.BUY,),
                (CommandId.SELL,),
                (CommandId.SELL_TO,),
                (CommandId.ACCEPT_REQUEST,),
                (CommandId.DECLINE_REQUEST,),
                (CommandId.WORK,),
                (CommandId.DUEL,),
                (CommandId.TRANSFER,),
                (CommandId.SLOTS,),
                (CommandId.ROULETTE,)
            )
        )
        await base.commit()

def check_db(guild_id: int, guild_locale: str | None) -> list[tuple[int, int, int]]:
    with closing(connect(DB_PATH.format(guild_id))) as base:
        with closing(base.cursor()) as cur:
            cur.executescript("""\
            CREATE TABLE IF NOT EXISTS users (
                memb_id INTEGER PRIMARY KEY,
                money INTEGER NOT NULL DEFAULT 0,
                owned_roles TEXT NOT NULL DEFAULT '',
                work_date INTEGER NOT NULL DEFAULT 0,
                xp INTEGER NOT NULL DEFAULT 0,
                voice_join_time INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS sale_requests (
                request_id INTEGER PRIMARY KEY,
                seller_id INTEGER NOT NULL DEFAULT 0,
                target_id INTEGER NOT NULL DEFAULT 0,
                role_id INTEGER NOT NULL DEFAULT 0,
                price INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS server_roles (
                role_id INTEGER PRIMARY KEY,
                price INTEGER NOT NULL DEFAULT 0,
                salary INTEGER NOT NULL DEFAULT 0,
                salary_cooldown INTEGER NOT NULL DEFAULT 0,
                type INTEGER NOT NULL DEFAULT 0,
                additional_salary INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS store (
                role_number INTEGER PRIMARY KEY,
                role_id INTEGER NOT NULL DEFAULT 0,
                quantity INTEGER NOT NULL DEFAULT 0,
                price INTEGER NOT NULL DEFAULT 0,
                last_date INTEGER NOT NULL DEFAULT 0,
                salary INTEGER NOT NULL DEFAULT 0,
                salary_cooldown INTEGER NOT NULL DEFAULT 0,
                type INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS salary_roles (
                role_id INTEGER PRIMARY KEY,
                members TEXT NOT NULL DEFAULT '',
                salary INTEGER NOT NULL DEFAULT 0,
                salary_cooldown INTEGER NOT NULL DEFAULT 0,
                last_time INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS server_info (
                settings TEXT PRIMARY KEY,
                value INTEGER NOT NULL DEFAULT 0,
                str_value TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS rank_roles (
                level INTEGER PRIMARY KEY,
                role_id INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS ignored_channels (
                chnl_id INTEGER PRIMARY KEY,
                is_text INTEGER NOT NULL DEFAULT 0,
                is_voice INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS mod_roles (
                role_id INTEGER PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS slots_table (
                bet INTEGER PRIMARY KEY,
                income INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS commands_settings (
                command_id INTEGER PRIMARY KEY,
                is_enabled INTEGER NOT NULL DEFAULT 0
            )
            """)
            base.commit()
            
            db_guild_language: tuple[int] | None = cur.execute("SELECT value FROM server_info WHERE settings = 'lang';").fetchone()
            if db_guild_language: 
                lng: int = db_guild_language[0]
            else: 
                lng: int = 1 if guild_locale and "ru" in guild_locale else 0
            
            settings_params: tuple[tuple[str, int, str], ...] = (
                ('lang', lng, ""),
                ('tz', 0, ""),
                ('xp_border', 100, ""),
                ('xp_per_msg', 1, ""),
                ('xp_for_voice', 6, ""),
                ('mn_per_msg', 1, ""),
                ('mn_for_voice', 6, ""),
                ('w_cd', 14400, ""),
                ('sal_l', 1, ""),
                ('sal_r', 250, ""),
                ('lvl_c', 0, ""),
                ('log_c', 0, ""),
                ('poll_v_c', 0, ""),
                ('poll_c', 0, ""),
                ('economy_enabled', 1, ""),
                ('ranking_enabled', 1, ""),
                ('currency', 0, ":coin:"),
                ('sale_price_perc', 100, ""),
                ('memb_join_rem_chnl', 0, ""),
                ('member_join_msg', 0, ""),
                ('member_remove_msg', 0, "")
            )
            cur.executemany("INSERT OR IGNORE INTO server_info (settings, value, str_value) VALUES(?, ?, ?)", settings_params)

            commands_settings: tuple[tuple[int, int], ...] = (
                (CommandId.STORE, 1),
                (CommandId.BUY, 1),
                (CommandId.SELL, 1),
                (CommandId.SELL_TO, 1),
                (CommandId.PROFILE, 1),
                (CommandId.ACCEPT_REQUEST, 1),
                (CommandId.DECLINE_REQUEST, 1),
                (CommandId.WORK, 1),
                (CommandId.DUEL, 1),
                (CommandId.TRANSFER, 1),
                (CommandId.LEADERS, 1),
                (CommandId.SLOTS, 1),
                (CommandId.ROULETTE, 1)
            )
            cur.executemany("INSERT OR IGNORE INTO commands_settings (command_id, is_enabled) VALUES(?, ?)", commands_settings)

            default_slot_sums: tuple[tuple[int, int], ...] = (
                (100, 80),
                (200, 160),
                (500, 400),
                (1000, 800)
            )
            cur.executemany("INSERT OR IGNORE INTO slots_table (bet, income) VALUES(?, ?)", default_slot_sums)
            base.commit()

            return cur.execute("SELECT chnl_id, is_text, is_voice FROM ignored_channels;").fetchall()

async def make_backup(guild_id: int) -> None:
    async with connect_async(DB_PATH.format(guild_id)) as src:
        async with connect_async(CWD_PATH + f"/bases/bases_{guild_id}/{guild_id}_backup.db") as dst:
            await src.backup(dst)

async def get_server_slots_table_async(guild_id: int) -> dict[int, int]:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        async with base.execute("SELECT bet, income FROM slots_table;") as cur:
            pairs: Iterable[Row] = await cur.fetchall()
    return {bet: income for bet, income in pairs}

async def update_server_slots_table_async(guild_id: int, slots_table: dict[int, int]) -> None:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        income_bet_pairs: Generator[tuple[int, int], None, None] = ((income, bet) for bet, income in slots_table.items())
        await base.executemany("UPDATE slots_table SET income = ? WHERE bet = ?", income_bet_pairs)        
        await base.commit()

async def listify_guild_roles(guild_id: int) -> tuple[list[tuple[int, int, int, int, int, int]], list[str]]:
    role_count: list[str] = []
    async with connect_async(DB_PATH.format(guild_id)) as base:
        roles: list[tuple[int, int, int, int, int, int]] = \
            await (await base.execute("SELECT role_id, price, salary, salary_cooldown, type, additional_salary FROM server_roles")).fetchall() # type: ignore

        for role in roles:
            role_type: int = role[4]
            if role_type == 1:
                role_count.append(str((await (await base.execute("SELECT count() FROM store WHERE role_id = " + str(role[0]))).fetchone())[0])) # type: ignore
            else:
                quantity_in_store = await (await base.execute("SELECT quantity FROM store WHERE role_id = " + str(role[0]))).fetchone()
                assert quantity_in_store is None or isinstance(quantity_in_store, tuple)

                if not quantity_in_store:
                    role_count.append('0')
                elif role_type == 2:
                    role_count.append(str(quantity_in_store[0]))
                else:
                    role_count.append('∞')

    assert len(roles) == len(role_count)
    return (roles, role_count)

async def get_member_message_async(guild_id: int, is_join: bool) -> tuple[int, str]:
    async with connect_async(DB_PATH.format(guild_id)) as base:
        pair = await (await base.execute(
            "SELECT value, str_value FROM server_info WHERE settings = 'member_join_msg';" \
            if is_join else \
            "SELECT value, str_value FROM server_info WHERE settings = 'member_remove_msg';"
        )).fetchone()

    assert isinstance(pair, tuple) and len(pair) == 2 and isinstance(pair[0], int) and isinstance(pair[1], str)
    return pair

async def set_member_message_async(guild_id: int, text: str, is_join: bool) -> None:
    flag: int = 0b01 if '%s' in text else 0b00
    if '%m' in text:
        flag |= 0b10

    async with connect_async(DB_PATH.format(guild_id)) as base:
        await base.execute(
            "UPDATE server_info SET value = ?, str_value = ? WHERE settings = 'member_join_msg';" \
            if is_join else \
            "UPDATE server_info SET value = ?, str_value = ? WHERE settings = 'member_remove_msg';",
            (flag, text)
        )
        await base.commit()

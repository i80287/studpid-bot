from sqlite3 import connect, Cursor, Row
from aiosqlite import connect as connect_async
from contextlib import closing
if __debug__:
    from collections.abc import Iterable

from Variables.vars import CWD_PATH


def update_server_info_table(guild_id: int, key_name: str, new_value: int) -> None:
    with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as base:
        with closing(base.cursor()) as cur:
            cur.execute("UPDATE server_info SET value = ? WHERE settings = ?", (new_value, key_name))
            base.commit()

def get_server_info_value(guild_id: int, key_name: str) -> int:
    with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as base:
        with closing(base.cursor()) as cur:
            return cur.execute("SELECT value FROM server_info WHERE settings = '" + key_name + "';").fetchone()[0]

async def get_server_info_value_async(guild_id: int, key_name: str) -> int:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        async with base.execute("SELECT value FROM server_info WHERE settings = '" + key_name + "';") as cur:
            return (await cur.fetchone())[0] # type: ignore

async def get_server_currency_async(guild_id: int) -> str:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        async with base.execute("SELECT str_value FROM server_info WHERE settings = 'currency';") as cur:
            return (await cur.fetchone())[0] # type: ignore

async def get_member_async(guild_id: int, member_id: int) -> tuple[int, int, str, int, int, int]:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        async with base.execute("SELECT memb_id, money, owned_roles, work_date, xp, voice_join_time FROM users WHERE memb_id = ?", (member_id,)) as cur:
            result: Row | None = await cur.fetchone()
            if result is not None:
                return tuple(result)

            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, ?, ?, ?, ?, ?)",
                (member_id, 0, "", 0, 0, 0)
            )
            await base.commit()

            return (member_id, 0, "", 0, 0, 0)

async def get_member_nocheck_async(guild_id: int, member_id: int) -> tuple[int, int, str, int, int, int]:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        async with base.execute("SELECT memb_id, money, owned_roles, work_date, xp, voice_join_time FROM users WHERE memb_id = ?", (member_id,)) as cur:
            return tuple(await cur.fetchone()) # type: ignore

async def update_member_cash_async(guild_id: int, member_id: int, cash: int) -> None:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        await base.execute("UPDATE users SET money = ? WHERE memb_id = ?", (cash, member_id))
        await base.commit()

async def check_member_level_async(guild_id: int, member_id: int) -> int:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        xp_b: int = (await (await base.execute("SELECT value FROM server_info WHERE settings = 'xp_border';")).fetchone())[0] # type: ignore
        mn_p_m: int = (await (await base.execute("SELECT value FROM server_info WHERE settings = 'mn_per_msg';")).fetchone())[0] # type: ignore
        xp_p_m: int = (await (await base.execute("SELECT value FROM server_info WHERE settings = 'xp_per_msg';")).fetchone())[0] # type: ignore 
        member_row: Row | None = await (await base.execute("SELECT xp FROM users WHERE memb_id = ?", (member_id,))).fetchone() # type: ignore
        
        if member_row:
            await base.execute("UPDATE users SET money = money + ?, xp = xp + ? WHERE memb_id = ?", (mn_p_m, xp_p_m, member_id))
            await base.commit()
            old_level: int = (member_row[0] - 1) // xp_b + 1
            new_level: int = (member_row[0] + xp_p_m - 1) // xp_b + 1
            if old_level == new_level:                
                return 0
            return new_level
        else:
            await base.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, ?, ?, ?, ?, ?)",
                (member_id, mn_p_m, "", 0, xp_p_m, 0)
            )
            await base.commit()
            return 1

async def register_user_voice_channel_join(guild_id: int, member_id: int, time_join: int) -> None:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        async with base.execute("SELECT rowid FROM users WHERE memb_id = ?", (member_id,)) as cur:
            result: Row | None = await cur.fetchone()
            if not result:
                await base.execute(
                    "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, ?, ?, ?, ?, ?)",
                    (member_id, 0, "", 0, 0, time_join)
                )
            else:
                await base.execute(
                    "UPDATE users SET voice_join_time = ? WHERE memb_id = ?",
                    (time_join, member_id)
                )
        
        await base.commit()

async def register_user_voice_channel_left(guild_id: int, member_id: int, money_for_voice: int, time_left: int) -> tuple[int, int]:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        voice_join_time: int = (await get_member_async(guild_id=guild_id, member_id=member_id))[5]
        if not voice_join_time:
            return (0, 0)

        income_for_voice: int = (time_left - voice_join_time) * money_for_voice // 600
        await base.execute("UPDATE users SET money = money + ?, voice_join_time = 0 WHERE memb_id = ?", (income_for_voice, member_id))
        await base.commit()

    return (income_for_voice, voice_join_time)

async def register_user_voice_channel_left_with_join_time(guild_id: int, member_id: int, money_for_voice: int, time_join: int, time_left: int) -> int:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        income_for_voice: int = (time_left - time_join) * money_for_voice // 600
        await base.execute("UPDATE users SET money = money + ?, voice_join_time = 0 WHERE memb_id = ?", (income_for_voice, member_id))
        await base.commit()
    
    return income_for_voice

def peek_role_free_number(cur: Cursor) -> int:
    req: list[tuple[int]] = cur.execute("SELECT role_number FROM store ORDER BY role_number").fetchall()
    if req:
        role_numbers: list[int] = [r_n[0] for r_n in req]
        del req
        if role_numbers[0] != 1:
            return 1
        for current_role_number, next_role_number in zip(role_numbers, role_numbers[1:]):
            if current_role_number + 1 != next_role_number:
                return current_role_number + 1
        return len(role_numbers) + 1
    else:
        return 1

def peek_free_request_id(cur: Cursor) -> int:
    request_ids_list: list[tuple[int]] = cur.execute(
        "SELECT request_id FROM sale_requests ORDER BY request_id"
    ).fetchall()
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
    with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as base:
        with closing(base.cursor()) as cur:
            cur.executescript(f"""\
            DELETE FROM server_roles WHERE role_id = {str_role_id};
            DELETE FROM salary_roles WHERE role_id = {str_role_id};
            DELETE FROM store WHERE role_id = {str_role_id};
            DELETE FROM sale_requests WHERE role_id = {str_role_id};""")
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
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        return await base.execute_fetchall("SELECT chnl_id, is_text, is_voice FROM ignored_channels;") # type: ignore

def check_db(guild_id: int, guild_locale: str | None) -> list[tuple[int, int, int]]:
    with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as base:
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
            );""")
            base.commit()
            
            db_guild_language: tuple[int] | None = cur.execute("SELECT value FROM server_info WHERE settings = 'lang';").fetchone()
            if db_guild_language: 
                lng: int = db_guild_language[0]
            else: 
                lng: int = 1 if guild_locale and "ru" in guild_locale else 0
            
            settings_params: list[tuple[str, int, str]] = [
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
                ('slots_on', 1, ""),
            ]
            cur.executemany("INSERT OR IGNORE INTO server_info (settings, value, str_value) VALUES(?, ?, ?)", settings_params)
            base.commit()

            default_slot_sums: list[tuple[int, int]] = [
                (100, 80),
                (200, 160),
                (500, 400),
                (1000, 800)
            ]
            cur.executemany("INSERT OR IGNORE INTO slots_table (bet, income) VALUES(?, ?)", default_slot_sums)
            base.commit()

            return cur.execute("SELECT chnl_id, is_text, is_voice FROM ignored_channels;").fetchall()

async def make_backup(guild_id: int) -> None:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as src:
        async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}_backup.db") as dst:
            await src.backup(dst)

async def get_server_slots_table_async(guild_id: int) -> dict[int, int]:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        async with base.execute("SELECT bet, income FROM slots_table;") as cur:
            pairs: Iterable[Row] = await cur.fetchall()
            return {bet: income for bet, income in pairs}

async def update_server_slots_table_async(guild_id: int, slots_table: dict[int, int]) -> None:
    async with connect_async(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db") as base:
        await base.executemany("UPDATE slots_table SET income = ? WHERE bet = ?", slots_table.items())        
        await base.commit()


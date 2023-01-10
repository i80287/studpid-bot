from typing import Literal
from time import time
from sqlite3 import connect, Connection, Cursor
from contextlib import closing

from Variables.vars import CWD_PATH


def update_server_info_table(guild_id: int, key_name: str, new_value: int) -> None:
    with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as base:
        with closing(base.cursor()) as cur:
            cur.execute("UPDATE server_info SET value = ? WHERE settings = ?", (new_value, key_name))
            base.commit()

def check_db_member(base: Connection, cur: Cursor, memb_id: int) -> tuple[int, int, str, int, int, int]:
    member: tuple[int, int, str, int, int, int] | None = \
        cur.execute(
            "SELECT memb_id, money, owned_roles, work_date, xp, voice_join_time FROM users WHERE memb_id = ?",
            (memb_id,)
        ).fetchone()

    if member:
        return member
    cur.execute(
        "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, ?, ?, ?, ?, ?)",
        (memb_id, 0, "", 0, 0, 0)
    )
    base.commit()
    return (memb_id, 0, "", 0, 0, 0)

def check_member(guild_id: int, memb_id: int) -> tuple[int, int, str, int, int, int]:
    with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as base:
        with closing(base.cursor()) as cur:
            member: tuple[int, int, str, int, int, int] | None = \
                cur.execute(
                    "SELECT memb_id, money, owned_roles, work_date, xp, voice_join_time FROM users WHERE memb_id = ?",
                    (memb_id,)
                ).fetchone()
            if member:
                return member

            cur.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, ?, ?, ?, ?, ?)",
                (memb_id, 0, "", 0, 0, 0)
            )
            base.commit()
            return (memb_id, 0, "", 0, 0, 0)

def register_user_voice_channel_join(guild_id: int, member_id: int):
    time_now = int(time())
    with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as base:
        with closing(base.cursor()) as cur:
            money_for_voice: int = cur.execute("SELECT value FROM server_info WHERE settings = 'mn_for_voice'").fetchone()[0]
            if not money_for_voice:
                return
            
            if not cur.execute("SELECT rowid FROM users WHERE memb_id = ?", (member_id,)):
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, ?, ?, ?, ?, ?)",
                (member_id, 0, "", 0, 0, 0)
            else:
                cur.execute("UPDATE users SET voice_join_time = ? WHERE memb_id = ?", (time_now, member_id))
            base.commit()

def register_user_voice_channel_left(guild_id: int, member_id: int):
    with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as base:
        with closing(base.cursor()) as cur:
            money_for_voice: int = cur.execute("SELECT value FROM server_info WHERE settings = 'mn_for_voice'").fetchone()[0]
            if not money_for_voice:
                return

            voice_join_time: int = check_db_member(base=base, cur=cur, memb_id=member_id)[5]
            if not voice_join_time:
                return

            time_delta: int = int(time()) - voice_join_time
            if not time_delta:
                return

            income_for_voice: int = time_delta * money_for_voice // 600
            cur.execute("UPDATE users SET money = money + ?, voice_join_time = 0 WHERE memb_id = ?", (income_for_voice, member_id))
            base.commit()

def peek_role_free_number(cur: Cursor) -> int:
    req: list[tuple[int]] = cur.execute("SELECT role_number FROM store ORDER BY role_number").fetchall()
    if req:
        role_numbers: list[int] = [int(r_n[0]) for r_n in req]
        if role_numbers[0] != 1:
            return 1
        for role_number_cur, role_number_next in zip(role_numbers, role_numbers[1:]):
            if role_number_next - role_number_cur != 1:
                return role_number_cur + 1
        return len(role_numbers) + 1
    else:
        return 1

def peek_free_request_id(cur: Cursor) -> int:
    request_ids_list: list[tuple[int]] = cur.execute(
        "SELECT request_id FROM sale_requests ORDER BY request_id"
    ).fetchall()
    if request_ids_list:
        request_ids: set[int] = {int(req_id_tuple[0]) for req_id_tuple in request_ids_list}
        free_requests_ids: set[int] = set(range(1, len(request_ids) + 2)).difference(request_ids)
        return min(free_requests_ids)
    else:
        return 1

def peek_role_free_numbers(cur: Cursor, amount_of_numbers: int) -> list[int]:
    req: list[tuple[int]] = cur.execute("SELECT role_number FROM store").fetchall()
    if req:
        role_numbers: set[int] = {r_n[0] for r_n in req}
        after_last_number: int =  max(role_numbers) + 1
        free_numbers: set[int] = set(range(1, after_last_number)).difference(role_numbers)
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

def check_db(guild_id: int, guild_locale: str | None):
    with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as base:
        with closing(base.cursor()) as cur:
            cur.executescript("""\
            CREATE TABLE IF NOT EXISTS users (
                memb_id INTEGER PRIMARY KEY,
                money INTEGER NOT NULL DEFAULT 0,
                owned_roles TEXT NOT NULL DEFAULT '',
                work_date INTEGER NOT NULL DEFAULT 0,
                xp INTEGER NOT NULL DEFAULT 0,
                voice_join_time INTEGER NOT NULL
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
                type INTEGER NOT NULL DEFAULT 0
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
                last_time INTEGER NOT NULL DEFAULT 0,
                additional_salary INTEGER NOT NULL DEFAULT 0
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
            CREATE TABLE IF NOT EXISTS ic (
                chnl_id INTEGER PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS mod_roles (
                role_id INTEGER PRIMARY KEY
            );""")
            base.commit()
            
            db_guild_language: tuple[int] | None = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()
            if db_guild_language: 
                lng: Literal[1, 0] = db_guild_language[0]
            else: 
                lng: Literal[1, 0] = 1 if guild_locale and "ru" in guild_locale else 0
            
            settings_params: list[tuple[str, int, str]] = [
                ('lang', lng, ""),
                ('tz', 0, ""),
                ('xp_border', 100, ""),
                ('xp_per_msg', 1, ""),
                ('mn_per_msg', 1, ""),
                ('mn_for_voice', 1, "")
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
            ]
            cur.executemany("INSERT OR IGNORE INTO server_info (settings, value, str_value) VALUES(?, ?, ?)", settings_params)
            base.commit()

            return {r[0] for r in cur.execute("SELECT chnl_id FROM ic").fetchall()}

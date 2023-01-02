from sqlite3 import connect, Connection, Cursor
from contextlib import closing

from Variables.vars import path_to


def update_server_info_table(guild_id: int, key_name: str, new_value: int) -> None:
    with closing(connect(f"{path_to}/bases/bases_{guild_id}/{guild_id}.db")) as base:
        with closing(base.cursor()) as cur:
            cur.execute("UPDATE server_info SET value = ? WHERE settings = ?", (new_value, key_name))
            base.commit()

def check_db_member(base: Connection, cur: Cursor, memb_id: int) -> tuple[int, int, str, int, int, int]:
    member: tuple[int, int, str, int, int, int] | None = \
        cur.execute(
            "SELECT memb_id, money, owned_roles, work_date, xp, pending_requests FROM users WHERE memb_id = ?",
            (memb_id,)
        ).fetchone()

    if member:
        return member
    cur.execute(
        "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, pending_requests) VALUES (?, ?, ?, ?, ?, ?)",
        (memb_id, 0, "", 0, 0, 0)
    )
    base.commit()
    return (memb_id, 0, "", 0, 0, 0)

def check_member(guild_id: int, memb_id: int) -> tuple[int, int, str, int, int, int]:
    with closing(connect(f"{path_to}/bases/bases_{guild_id}/{guild_id}.db")) as base:
        with closing(base.cursor()) as cur:
            member: tuple[int, int, str, int, int, int] | None = \
                cur.execute(
                    "SELECT memb_id, money, owned_roles, work_date, xp, pending_requests FROM users WHERE memb_id = ?",
                    (memb_id,)
                ).fetchone()

            if member:
                return member
            cur.execute(
                "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, pending_requests) VALUES (?, ?, ?, ?, ?, ?)",
                (memb_id, 0, "", 0, 0, 0)
            )
            base.commit()
            return (memb_id, 0, "", 0, 0, 0)

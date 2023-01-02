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

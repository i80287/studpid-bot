import os
from sqlite3 import connect, Cursor
from contextlib import closing

def verify_db(g_id: int) -> None:
    with closing(connect(f"./bases/bases_{g_id}/{g_id}.db")) as base:
        cur: Cursor = base.cursor()
        
        cur.executescript("""\
        CREATE TABLE IF NOT EXISTS server_roles (
            role_id INTEGER PRIMARY KEY,
            price INTEGER NOT NULL DEFAULT 0,
            salary INTEGER NOT NULL DEFAULT 0,
            salary_cooldown INTEGER NOT NULL DEFAULT 0,
            type INTEGER NOT NULL DEFAULT 0,
            additional_salary INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS salary_roles (
            role_id INTEGER PRIMARY KEY,
            members TEXT NOT NULL DEFAULT '',
            salary INTEGER NOT NULL DEFAULT 0,
            salary_cooldown INTEGER NOT NULL DEFAULT 0,
            last_time INTEGER NOT NULL DEFAULT 0
        );""")
        base.commit()

        columns_count_1: int = len(cur.execute(f"PRAGMA table_info(server_roles)").fetchall())
        columns_count_2: int = len(cur.execute(f"PRAGMA table_info(salary_roles)").fetchall())
        if columns_count_1 == 6 and columns_count_2 == 5:
            cur.close()
            return
        
        cur.executescript("""\
        CREATE TABLE tmp_server_roles (
            role_id INTEGER PRIMARY KEY,
            price INTEGER NOT NULL DEFAULT 0,
            salary INTEGER NOT NULL DEFAULT 0,
            salary_cooldown INTEGER NOT NULL DEFAULT 0,
            type INTEGER NOT NULL DEFAULT 0,
            additional_salary INTEGER NOT NULL DEFAULT 0
        );
        INSERT INTO tmp_server_roles (role_id, price, salary, salary_cooldown, type)
        SELECT role_id, price, salary, salary_cooldown, type FROM server_roles;
        
        CREATE TABLE tmp_salary_roles (
            role_id INTEGER PRIMARY KEY,
            members TEXT NOT NULL DEFAULT '',
            salary INTEGER NOT NULL DEFAULT 0,
            salary_cooldown INTEGER NOT NULL DEFAULT 0,
            last_time INTEGER NOT NULL DEFAULT 0
        );
        INSERT INTO tmp_salary_roles (role_id, members, salary, salary_cooldown, last_time)
        SELECT role_id, members, salary, salary_cooldown, last_time FROM salary_roles;""")
        base.commit()
        
        pairs: list[tuple[int, int]] = cur.execute("SELECT role_id, additional_salary FROM salary_roles").fetchall()
        for pair in pairs:
            cur.execute(
                "UPDATE tmp_server_roles SET additional_salary = ? WHERE role_id = ?",
                (pair[1], pair[0])
            )
            base.commit()

        cur.executescript("""\
        DROP TABLE server_roles;
        CREATE TABLE server_roles (
            role_id INTEGER PRIMARY KEY,
            price INTEGER NOT NULL DEFAULT 0,
            salary INTEGER NOT NULL DEFAULT 0,
            salary_cooldown INTEGER NOT NULL DEFAULT 0,
            type INTEGER NOT NULL DEFAULT 0,
            additional_salary INTEGER NOT NULL DEFAULT 0
        );

        INSERT INTO server_roles (role_id, price, salary, salary_cooldown, type, additional_salary)
        SELECT role_id, price, salary, salary_cooldown, type, additional_salary FROM tmp_server_roles;

        DROP TABLE tmp_server_roles;

        DROP TABLE salary_roles;
        CREATE TABLE salary_roles (
            role_id INTEGER PRIMARY KEY,
            members TEXT NOT NULL DEFAULT '',
            salary INTEGER NOT NULL DEFAULT 0,
            salary_cooldown INTEGER NOT NULL DEFAULT 0,
            last_time INTEGER NOT NULL DEFAULT 0
        );
        INSERT INTO salary_roles (role_id, members, salary, salary_cooldown, last_time)
        SELECT role_id, members, salary, salary_cooldown, last_time FROM tmp_salary_roles;

        DROP TABLE tmp_salary_roles;
        """)
        
        cur.close()


def main() -> None:
    for folder_name in os.listdir("bases"):
        guild_id: int = int(folder_name.split('_')[1])
        # if guild_id not in {998881217644613632}:
        #     continue
        # print(guild_id)
        verify_db(guild_id)
        
if __name__ == "__main__":
    main()
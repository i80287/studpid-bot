from sqlite3 import connect
from contextlib import closing

from Variables.vars import path_to


def update_server_info_table(unsigned long long guild_id, str key_name, unsigned long long new_value):
    with closing(connect(f"{path_to}/bases/bases_{guild_id}/{guild_id}.db")) as base:
        with closing(base.cursor()) as cur:
            cur.execute("UPDATE server_info SET value = ? WHERE settings = ?", (new_value, key_name))
            base.commit()

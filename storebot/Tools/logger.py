from aiofiles import open
from datetime import datetime, timedelta

from ..constants import CWD_PATH
DIR_PATH = CWD_PATH + '/'
GUILD_LOGS_PATH = CWD_PATH + "/logs/logs_{0}/"

_TZ_OFFSET = timedelta(hours=3.0)

async def write_log_async(filename: str, *report: str) -> None:
    # if not filename.endswith(".log"):
    #     filename += ".log"
    assert filename.endswith(".log")
    async with open(DIR_PATH + filename, mode="a+", encoding="utf-8") as f:
        await f.write(f"[{datetime.utcnow() + _TZ_OFFSET}] [{'] ['.join(map(str, report))}]\n")

async def write_one_log_async(filename: str, report: str) -> None:
    # if not filename.endswith(".log"):
    #     filename += ".log"
    assert filename.endswith(".log")
    async with open(DIR_PATH + filename, mode="a+", encoding="utf-8") as f:
        await f.write(f"[{datetime.utcnow() + _TZ_OFFSET}] {report}\n")

async def write_guild_log_async(filename: str, guild_id: int, report: str) -> None:
    # if not filename.endswith(".log"):
    #     filename += ".log"
    assert filename.endswith(".log")
    async with open(GUILD_LOGS_PATH.format(guild_id) + filename, mode="a+", encoding="utf-8") as f:
        await f.write(f"[{datetime.utcnow() + _TZ_OFFSET}] {report}\n")

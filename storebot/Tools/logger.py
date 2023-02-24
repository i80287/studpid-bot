import aiofiles
from datetime import datetime, timedelta

from storebot.Variables.vars import CWD_PATH

class Logger:
    @staticmethod
    async def write_log_async(filename: str, *report) -> None:
        if not filename.endswith(".log"):
            filename += ".log"

        async with aiofiles.open(file=filename, mode="a+", encoding="utf-8") as f:
            await f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3.0))}] {' '.join(['[' + s + ']' for s in report if s])}\n")

    @staticmethod
    async def write_one_log_async(filename: str, report: str) -> None:
        if not filename.endswith(".log"):
            filename += ".log"

        async with aiofiles.open(file=filename, mode="a+", encoding="utf-8") as f:
            await f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3.0))}] {report}\n")
    
    @staticmethod
    async def write_guild_log_async(filename: str, guild_id: int, report: str) -> None:
        if not filename.endswith(".log"):
            filename += ".log"

        async with aiofiles.open(file=f"{CWD_PATH}/logs/logs_{guild_id}/{filename}", mode="a+", encoding="utf-8") as f:
            await f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3.0))}] {report}\n")

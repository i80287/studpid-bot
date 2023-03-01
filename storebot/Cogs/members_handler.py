from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import NoReturn

    from nextcord import (
        Guild,
        Member
    )
    from nextcord.utils import SnowflakeList

    from ..storebot import StoreBot

import asyncio
from nextcord import (
    Embed,
    TextChannel
)
from nextcord.ext import tasks
from nextcord.ext.commands import Cog

from ..Tools.db_commands import (
    add_member_role_async,
    remove_member_role_async,
    get_server_info_value_async
)
from ..Tools.logger import Logger


class MembersHandlerCog(Cog):
    members_handler_text: dict[int, dict[int, str]] = {
        0: {
            0: "**`Role`** <@&{0}> **`was added to the member`** <@{1}> **`without bot tools and therefore was added to member's balance`**",
            1: "**`Role`** <@&{0}> **`was removed from the member`** <@{1}> **`without bot tools and therefore was removed from the member's balance`**"
        },
        1: {
            0: "**`Роль`** <@&{0}> **`была добавлена пользователю`** <@{1}> **`без использования бота, и поэтому была добавлена на баланс пользователя автоматически`**",
            1: "**`Роль`** <@&{0}> **`была убрана у пользователя`** <@{1}> **`без использования бота, и поэтому была убрана из баланса пользователя автоматически`**"
        }
    }

    bot_added_roles_queue: asyncio.Queue[int] = asyncio.Queue()
    bot_added_roles_lock: asyncio.Lock = asyncio.Lock()
    bot_removed_roles_queue: asyncio.Queue[int] = asyncio.Queue()
    bot_removed_roles_lock: asyncio.Lock = asyncio.Lock()

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot
        self.members_queue: asyncio.Queue[tuple[Guild, int, SnowflakeList, SnowflakeList, bool]] = asyncio.Queue()
        self.roles_updates_loop.start()

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        if before.bot:
            return
        
        before_roles: SnowflakeList = before._roles
        after_roles: SnowflakeList = after._roles
        if (l1 := len(before_roles)) != (l2 := len(after_roles)):
            self.members_queue.put_nowait((after.guild, after.id, before_roles, after_roles, l1 < l2))
    
    @tasks.loop()
    async def roles_updates_loop(self) -> NoReturn:
        while True:
            tup: tuple[Guild, int, SnowflakeList, SnowflakeList, bool] = await self.members_queue.get()
            guild: Guild = tup[0]
            guild_id: int = guild.id
            member_id: int = tup[1]
            before_roles: SnowflakeList = tup[2]
            after_roles: SnowflakeList = tup[3]
            is_role_added: bool = tup[4]
            changed_role_id: int = 0
            is_updated: bool = False
            
            if is_role_added:
                for role_id in after_roles:
                    if not before_roles.has(role_id):
                        if await self.check_bot_added_roles(role_id):
                            is_updated = await add_member_role_async(guild_id, member_id, role_id)
                            changed_role_id = role_id
                            break
                        else:
                            continue
            else:
                for role_id in before_roles:
                    if not after_roles.has(role_id):
                        if await self.check_bot_removed_roles(role_id):
                            is_updated = await remove_member_role_async(guild_id, member_id, role_id)
                            changed_role_id = role_id
                            break
                        else:
                            continue
            
            if not is_updated:
                continue

            await Logger.write_guild_log_async(
                "guild.log",
                guild_id,
                f"[role_change] [is_added: {is_role_added}] [guild: {guild_id}:{guild.name}] [member_id: {member_id}] [role_id: {changed_role_id}]"
            )

            log_channel_id: int = await get_server_info_value_async(guild_id, "log_c") 
            if log_channel_id and isinstance(log_channel := guild.get_channel(log_channel_id), TextChannel):
                server_lng: int = await get_server_info_value_async(guild_id, "lang")
                description: str = self.members_handler_text[server_lng][0 if is_role_added else 1].format(changed_role_id, member_id)
                try:
                    await log_channel.send(embed=Embed(description=description))
                except:
                    await Logger.write_guild_log_async(
                        "guild.log",
                        guild_id,
                        f"[ERROR] [send log message failed] [role_change] [is_added: {is_role_added}] [guild: {guild_id}:{guild.name}] [member_id: {member_id}] [role_id: {changed_role_id}]"
                    )

    @roles_updates_loop.before_loop
    async def before_voice_processor(self) -> None:
        await self.bot.wait_until_ready()

    @classmethod
    async def check_bot_added_roles(cls, role_id: int) -> bool:
        async with cls.bot_added_roles_lock:
            if cls.bot_added_roles_queue.empty():
                return True
            
            bot_added_role_id_1: int = await cls.bot_added_roles_queue.get()
    
        if bot_added_role_id_1 == role_id:
            return False
        
        async with cls.bot_added_roles_lock:
            if cls.bot_added_roles_queue.empty():
                cls.bot_added_roles_queue.put_nowait(bot_added_role_id_1)
                return True
        
            bot_added_role_id_2: int = await cls.bot_added_roles_queue.get()
            cls.bot_added_roles_queue.put_nowait(bot_added_role_id_1)
        
        if bot_added_role_id_2 == role_id:
            return False

        cls.bot_added_roles_queue.put_nowait(bot_added_role_id_2)
        return True

    @classmethod
    async def check_bot_removed_roles(cls, role_id: int) -> bool:
        async with cls.bot_removed_roles_lock:
            if cls.bot_removed_roles_queue.empty():
                return True
            
            bot_removed_role_id_1: int = await cls.bot_removed_roles_queue.get()
        
        if bot_removed_role_id_1 == role_id:
            return False
        
        async with cls.bot_removed_roles_lock:
            if cls.bot_removed_roles_queue.empty():
                cls.bot_removed_roles_queue.put_nowait(bot_removed_role_id_1)
                return True

            bot_removed_role_id_2: int = await cls.bot_added_roles_queue.get()
            cls.bot_removed_roles_queue.put_nowait(bot_removed_role_id_1)
        
        if bot_removed_role_id_2 == role_id:
            return False

        cls.bot_removed_roles_queue.put_nowait(bot_removed_role_id_2)
        return True


def setup(bot: StoreBot) -> None:
    bot.add_cog(MembersHandlerCog(bot))
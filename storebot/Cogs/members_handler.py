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
from ..Tools.logger import write_guild_log_async


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
        next_member_update_coro = self.members_queue.get
        m_check_bot_added_roles = self.check_bot_added_roles
        m_check_bot_removed_roles = self.check_bot_removed_roles
        s_members_handler_text = self.members_handler_text
        changed_role_id: int = 0
        is_updated: bool = False
        while True:
            guild, member_id, before_roles, after_roles, is_role_added = await next_member_update_coro()
            guild_id: int = guild.id
            is_updated = False
            
            if is_role_added:
                for role_id in after_roles:
                    if not before_roles.has(role_id):
                        if await m_check_bot_added_roles(role_id):
                            is_updated = await add_member_role_async(guild_id, member_id, role_id)
                            changed_role_id = role_id
                            break
                        else:
                            continue
            else:
                for role_id in before_roles:
                    if not after_roles.has(role_id):
                        if await m_check_bot_removed_roles(role_id):
                            is_updated = await remove_member_role_async(guild_id, member_id, role_id)
                            changed_role_id = role_id
                            break
                        else:
                            continue
            
            if not is_updated:
                continue

            await write_guild_log_async(
                "guild.log",
                guild_id,
                f"[role_change] [is_added: {is_role_added}] [guild: {guild_id}:{guild.name}] [member_id: {member_id}] [role_id: {changed_role_id}]"
            )

            log_channel_id: int = await get_server_info_value_async(guild_id, "log_c") 
            if log_channel_id and isinstance(log_channel := guild.get_channel(log_channel_id), TextChannel):
                server_lng: int = await get_server_info_value_async(guild_id, "lang")
                description: str = s_members_handler_text[server_lng][0 if is_role_added else 1].format(changed_role_id, member_id)
                try:
                    await log_channel.send(embed=Embed(description=description))
                except:
                    await write_guild_log_async(
                        "guild.log",
                        guild_id,
                        f"[ERROR] [send log message failed] [role_change] [is_added: {is_role_added}] [guild: {guild_id}:{guild.name}] [member_id: {member_id}] [role_id: {changed_role_id}]"
                    )

    @roles_updates_loop.before_loop
    async def before_voice_processor(self) -> None:
        await self.bot.wait_until_ready()

    async def check_bot_added_roles(self, role_id: int) -> bool:
        bot = self.bot
        added_roles_lock = bot.bot_added_roles_lock
        added_roles_queue = bot.bot_added_roles_queue
        async with added_roles_lock:
            if added_roles_queue.empty():
                return True
            
            bot_added_role_id_1: int = await added_roles_queue.get()
    
        if bot_added_role_id_1 == role_id:
            return False
        
        async with added_roles_lock:
            if added_roles_queue.empty():
                added_roles_queue.put_nowait(bot_added_role_id_1)
                return True
        
            bot_added_role_id_2: int = await added_roles_queue.get()
            added_roles_queue.put_nowait(bot_added_role_id_1)
        
        if bot_added_role_id_2 == role_id:
            return False

        added_roles_queue.put_nowait(bot_added_role_id_2)
        return True

    async def check_bot_removed_roles(self, role_id: int) -> bool:
        bot = self.bot
        removed_roles_lock = bot.bot_removed_roles_lock
        removed_roles_queue = bot.bot_removed_roles_queue
        async with removed_roles_lock:
            if removed_roles_queue.empty():
                return True
            
            bot_removed_role_id_1: int = await removed_roles_queue.get()
        
        if bot_removed_role_id_1 == role_id:
            return False
        
        async with removed_roles_lock:
            if removed_roles_queue.empty():
                removed_roles_queue.put_nowait(bot_removed_role_id_1)
                return True

            bot_removed_role_id_2: int = await removed_roles_queue.get()
            removed_roles_queue.put_nowait(bot_removed_role_id_1)
        
        if bot_removed_role_id_2 == role_id:
            return False

        removed_roles_queue.put_nowait(bot_removed_role_id_2)
        return True


def setup(bot: StoreBot) -> None:
    bot.add_cog(MembersHandlerCog(bot))

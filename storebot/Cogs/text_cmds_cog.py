from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import LiteralString

    from nextcord import Guild

    from storebot.storebot import StoreBot

from nextcord import (
    Embed,
    Colour,
    TextChannel,
)
from nextcord.ext.commands import Cog, Context
if __debug__:
    from nextcord.member import Member

from ..Tools.db_commands import (
    process_work_command_async,
    get_server_log_info_async,
    get_server_currency_async
)

class TextComandsCog(Cog):
    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot

    @staticmethod
    async def work_command(ctx: Context)-> None:
        assert ctx.guild is not None
        assert isinstance(ctx.author, Member)
        guild: Guild = ctx.guild
        guild_id: int = guild.id
        member_id: int = ctx.author.id

        salary: int
        additional_salary: int
        roles: list[tuple[int, int]] | None
        salary, additional_salary, roles = await process_work_command_async(guild_id, member_id)

        if salary < 0:
            if salary == -1:
                answer: str =  "**`Economy system is disabled on this server`**"
            else:
                hours: int = additional_salary // 3600
                seconds_for_minutes: int = additional_salary - hours * 3600 # aka additional_salary % 3600
                minutes: int = seconds_for_minutes // 60                    # aka (additional_salary % 3600) // 60
                seconds: int = seconds_for_minutes - minutes * 60           # aka additional_salary % 60
                answer: str = "**`Please, wait {0}:{1}:{2} before using this command`**".format(hours, minutes, seconds)
            
            await ctx.channel.send(embed=Embed(description=answer), reference=ctx.message, mention_author=False)
            return
        
        currency: str = await get_server_currency_async(guild_id)
        description_lines: list[str] = ["**`Income from the command: {0:0,}`** {1}".format(salary, currency)]
        if roles:
            assert additional_salary != 0
            description_lines.append("**`Total income from the roles: {0:0,}`** {1}".format(additional_salary, currency))
            description_lines.extend("<@&{0}> **`- {1:0,}`** ".format(role_id, role_salary) + currency for role_id, role_salary in roles if role_salary)

        success = True
        try:
            await ctx.channel.send(
                embed=Embed(
                    description='\n'.join(description_lines),
                    colour=Colour.gold()
                ),
                reference=ctx.message,
                mention_author=False
            )
        except:
            success = False

        log_channel_id, server_lng = await get_server_log_info_async(guild_id)
        if log_channel_id and isinstance(guild_log_channel := guild.get_channel(log_channel_id), TextChannel):
            log_text: str = \
                "<@{0}> **`заработал {1:0,}`** {2} **`от команды /work (/collect) и {3:0,}`** {2} **`от ролей`**" \
                if server_lng else \
                "<@{0}> **`gained {1:0,}`** {2} **`from the /work (/collect) command and {3:0,}`** {2} **`from the roles`**" \

            if not success:
                log_text += \
                    f"\nПри отправке сообщения возникла ошибка. Проверьте права бота в канале <#{ctx.channel.id}>" \
                    if server_lng else \
                    f"\nAn error occured while sending message. Check bot permissions in the <#{ctx.channel.id}> channel"

            try:
                await guild_log_channel.send(embed=Embed(description=log_text.format(
                    member_id,
                    salary,
                    currency,
                    additional_salary
                )))
            except:
                return

def setup(bot: StoreBot) -> None:
    bot.add_cog(TextComandsCog(bot))

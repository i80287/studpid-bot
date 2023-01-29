import asyncio
from random import randrange
from os import urandom
from typing import LiteralString

from nextcord import (
    TextChannel,
    ButtonStyle,
    Interaction,
    Guild,
    Embed
)
from nextcord.ext import tasks

from Tools.db_commands import (
    get_member_nocheck_async,
    update_member_cash_async,
    get_server_info_value_async
)
from CustomComponents.view_base import ViewBase
from CustomComponents.custom_button import CustomButton
from CustomComponents.custom_select import CustomSelect


class SlotsView(ViewBase):
    slots_panel: LiteralString = "```\n┌───────┬───────┬───────┐\n│ Slot 1│ Slot 2│ Slot 3│\n├───────┼───────┼───────┤\n│  >{0}<  │  >{1}<  │  >{2}<  │\n└───────┴───────┴───────┘```"
    slots_view_text: dict[int, dict[int, str]] = {
        0: {
            0: "**`Slots are disabled on this server`**",
            1: "Choose bet",
            2: "**`You have not chose the bet yet`**",
            3: "**`Sorry, but to make this bet you need at least {0}`** {1} **`more`**",
            4: "**`Now bet is {0}`** {1}",
            5: "**`You made bet {0}`** {1} **`and won {2}`** {1}",
            6: "Slots bet",
            7: "<@{0}> **`made bet {1}`** {2} **`and won {3}`** {2}"
        },
        1: {
            0: "**`Слоты отключены на этом сервере`**",
            1: "Выберите ставку",
            2: "**`You have not chose the bet yet`**",
            3: "**`Sorry, but to make this bet you need at least {0}`** {1} **`more`**",
            4: "**`Now bet is {0}`** {1}",
            5: "**`You made bet {0}`** {1} **`and won {2}`** {1}",
            6: "Slots bet",
            7: "<@{0}> **`made bet {1}`** {2} **`and won {3}`** {2}"
        }
    }

    def __init__(self, lng: int, author_id: int, timeout: int, guild: Guild, slots_table: dict[int, int], currency: str) -> None:
        super().__init__(lng=lng, author_id=author_id, timeout=timeout, auto_defer=False)
        self.add_item(item=CustomSelect(
            custom_id=f"120_{author_id}_{urandom(4).hex()}",
            placeholder=self.slots_view_text[lng][1],
            options=[("100", "100"), ("200", "200"), ("500", "500"), ("1000", "1000")]
        ))
        self.add_item(item=CustomButton(
            style=ButtonStyle.green,
            custom_id=f"60_{author_id}_{urandom(4).hex()}",
            emoji="🎰"
        ))
        self.bet: int = 0
        self.guild_id: int = guild.id
        self.currency: str = currency
        self.is_running: bool = True
        self.slot_runs_queue: asyncio.Queue[Interaction] = asyncio.Queue()        
        self.slot_runs_handler.start(guild=guild, slots_table=slots_table)
    
    async def check_bet(self, interaction: Interaction) -> int:
        bet: int = self.bet
        if not bet:
            await interaction.response.send_message(
                embed=Embed(description=self.slots_view_text[self.lng][2]),
                ephemeral=True
            )
            return 0
        
        member_cash: int = (await get_member_nocheck_async(guild_id=self.guild_id, member_id=self.author_id))[1]
        if member_cash < bet:
            await interaction.response.send_message(
                embed=Embed(description=self.slots_view_text[self.lng][3].format(bet - member_cash, self.currency)),
                ephemeral=True
            )
            return 0
        
        return member_cash

    @tasks.loop(count=None)
    async def slot_runs_handler(self, guild: Guild, slots_table: dict[int, int]) -> None:
        guild_id: int = self.guild_id
        member_id: int = self.author_id
        slot_run_text: str = self.slots_view_text[self.lng][5]
        currency: str = self.currency

        log_channel_id: int = await get_server_info_value_async(guild_id=guild_id, key_name="log_c")
        guild_log_channel: TextChannel | None = None
        guild_lng: int = 0
        if log_channel_id and isinstance(channel := guild.get_channel(log_channel_id), TextChannel):
            guild_log_channel = channel
            guild_lng = await get_server_info_value_async(guild_id=guild_id, key_name='lang')

        while self.is_running:
            interaction: Interaction = await self.slot_runs_queue.get()
            member_cash: int = await self.check_bet(interaction=interaction)
            if not member_cash:
                continue
            
            bet: int = self.bet
            result: int = randrange(1000)
            win_sum: int = int(slots_table[bet] * (result + 500) / 1000)            
            member_cash += win_sum - bet
            if member_cash < 0:
                member_cash = 0
            await update_member_cash_async(guild_id=guild_id, member_id=member_id, cash=member_cash)

            n1: int = result // 100
            n2: int = (result // 100) % 10
            n3: int = result % 10
            assert interaction.message is not None
            await interaction.message.edit(embed=Embed(description=self.slots_panel.format(n1, n2, n3)))
            await interaction.response.send_message(
                embed=Embed(description=slot_run_text.format(bet, currency, win_sum)),
                ephemeral=True
            )

            if guild_log_channel:
                try:
                    await guild_log_channel.send(embed=Embed(
                        title=self.slots_view_text[guild_lng][6],
                        description=self.slots_view_text[guild_lng][7].format(member_id, bet, currency, win_sum)
                    ))
                except:
                    continue

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        self.slot_runs_queue.put_nowait(interaction)
    
    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        bet: int = int(values[0])
        self.bet = bet
        if await self.check_bet(interaction=interaction):
            await interaction.response.send_message(
                embed=Embed(description=self.slots_view_text[self.lng][4].format(bet, self.currency)),
                ephemeral=True
            )
    
    async def on_timeout(self) -> None:
        self.is_running = False
        self.slot_runs_handler.cancel()

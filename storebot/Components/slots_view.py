from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import LiteralString

    from nextcord import (
        Guild,
        Interaction
    )

import asyncio
from random import randrange
from os import urandom

from nextcord import (
    TextChannel,
    ButtonStyle,
    Embed,
    SelectOption
)
from nextcord.ext import tasks

from ..Tools.db_commands import (
    get_member_nocheck_async,
    update_member_cash_async,
    get_server_info_value_async
)
from ..Components.view_base import ViewBase
from ..Components.custom_button import CustomButton
from ..Components.custom_select import CustomSelectWithOptions


class SlotsView(ViewBase):
    slots_panels: dict[int, LiteralString] = {
        0: "```fix\n┌───────┬───────┬───────┐\n│ Slot 1│ Slot 2│ Slot 3│\n├───────┼───────┼───────┤\n│  >{0}<  │  >{1}<  │  >{2}<  │\n└───────┴───────┴───────┘```",
        1: "```fix\n┌───────┬───────┬───────┐\n│ Слот 1│ Слот 2│ Слот 3│\n├───────┼───────┼───────┤\n│  >{0}<  │  >{1}<  │  >{2}<  │\n└───────┴───────┴───────┘```",
    }
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
            2: "**`Вы ещё не выбрали ставку`**",
            3: "**`Извините, но для того, чтобы сделать эту ставку, Вам нужно ещё хотя бы {0}`** {1}",
            4: "**`Теперь ставка - {0}`** {1}",
            5: "**`Вы сделали ставку {0}`** {1} **`и выиграли {2}`** {1}",
            6: "Slots bet",
            7: "<@{0}> **`сделал(а, о) ставку {1}`** {2} **`и выиграл(а, о) {3}`** {2}"
        }
    }

    def __init__(self, lng: int, author_id: int, timeout: int, guild: Guild, slots_table: dict[int, int], currency: str) -> None:
        super().__init__(lng=lng, author_id=author_id, timeout=timeout, auto_defer=False)
        self.bet_select: CustomSelectWithOptions = CustomSelectWithOptions(
            custom_id=f"120_{author_id}_" + urandom(4).hex(),
            placeholder=self.slots_view_text[lng][1],
            opts=[
                SelectOption(label="100", value="100"),
                SelectOption(label="200", value="200"),
                SelectOption(label="500", value="500"),
                SelectOption(label="1000", value="1000"),
            ]
        )
        self.add_item(item=self.bet_select)
        self.add_item(item=CustomButton(
            style=ButtonStyle.green,
            custom_id=f"60_{author_id}_" + urandom(4).hex(),
            emoji="🎰"
        ))
        self.bet: int = 0
        self.guild_id: int = guild.id
        self.currency: str = currency
        self.is_running: bool = True
        self.slot_runs_queue: asyncio.Queue[Interaction] = asyncio.Queue()        
        self.slot_runs_handler.start(guild=guild, slots_table=slots_table)
    
    async def check_bet(self, interaction: Interaction, bet: int, member_cash: int) -> bool:
        if not bet:
            await interaction.response.send_message(
                embed=Embed(description=self.slots_view_text[self.lng][2]),
                ephemeral=True
            )
            return False
        
        if member_cash < bet:
            await interaction.response.send_message(
                embed=Embed(description=self.slots_view_text[self.lng][3].format(bet - member_cash, self.currency)),
                ephemeral=True
            )
            return False
        
        return True

    @tasks.loop(count=None)
    async def slot_runs_handler(self, guild: Guild, slots_table: dict[int, int]) -> None:
        guild_id: int = self.guild_id
        member_id: int = self.author_id
        local_text: dict[int, str] = self.slots_view_text[self.lng]
        currency: str = self.currency
        slot_panel: str = self.slots_panels[self.lng]

        log_channel_id: int = await get_server_info_value_async(guild_id=guild_id, key_name="log_c")
        guild_log_channel: TextChannel | None = None
        guild_lng: int = 0
        if log_channel_id and isinstance(channel := guild.get_channel(log_channel_id), TextChannel):
            guild_log_channel = channel
            guild_lng = await get_server_info_value_async(guild_id=guild_id, key_name='lang')

        while self.is_running:
            interaction: Interaction = await self.slot_runs_queue.get()
            bet: int = self.bet            
            member_cash: int = (await get_member_nocheck_async(guild_id=guild_id, member_id=member_id))[1]
            if not await self.check_bet(interaction=interaction, bet=bet, member_cash=member_cash):
                continue
            
            result: int = randrange(1000)
            win_sum: int = int(slots_table[bet] * (result + 500) / 1000)            
            member_cash += win_sum - bet
            if member_cash < 0:
                member_cash = 0
            await update_member_cash_async(guild_id=guild_id, member_id=member_id, cash=member_cash)

            n1: int
            n2: int
            n3: int
            if result < 500:
                n1 = randrange(4)
                n2 = randrange(4)
                n3 = randrange(4)
            elif result == 500:
                if randrange(2):
                    n1 = 4
                    n2 = 3
                else:
                    n1 = 3
                    n2 = 4
                n3 = 4
            elif result < 750:
                n1 = randrange(4, 6)
                n2 = randrange(3, 5)
                n3 = randrange(3, 6)
            elif result < 900:
                n1 = randrange(5, 7)
                n2 = randrange(4, 7)
                n3 = randrange(4, 6)
            elif result < 950:
                n1 = 6
                n2 = 6
                n3 = 6
            else:
                n1 = 7
                n2 = 7
                n3 = 7
                
            assert interaction.message is not None
            try:
                await interaction.message.edit(embed=Embed(description=slot_panel.format(n1, n2, n3)), view=self)
            except:
                pass
            finally:
                await interaction.response.send_message(
                    embed=Embed(description=local_text[5].format(bet, currency, win_sum)),
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
        match self.bet:
            case 100:
                self.bet_select.options[0].default = False
            case 200:
                self.bet_select.options[1].default = False
            case 500:
                self.bet_select.options[2].default = False
            case 1000:
                self.bet_select.options[3].default = False
        bet: int = int(values[0])
        match bet:
            case 100:
                self.bet_select.options[0].default = True
            case 200:
                self.bet_select.options[1].default = True
            case 500:
                self.bet_select.options[2].default = True
            case 1000:
                self.bet_select.options[3].default = True
        self.bet = bet
        member_cash: int = (await get_member_nocheck_async(guild_id=self.guild_id, member_id=self.author_id))[1]
        if await self.check_bet(interaction=interaction, bet=bet, member_cash=member_cash):
            await interaction.response.send_message(
                embed=Embed(description=self.slots_view_text[self.lng][4].format(bet, self.currency)),
                ephemeral=True
            )
    
    async def on_timeout(self) -> None:
        self.is_running = False
        self.slot_runs_handler.cancel()

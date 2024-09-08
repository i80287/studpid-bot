from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import LiteralString

    from nextcord import (
        Guild,
        Interaction
    )

import asyncio
from random import Random
from os import urandom

from nextcord import (
    TextChannel,
    ButtonStyle,
    Embed,
    SelectOption
)
from nextcord.ext import tasks

from ..Tools.db_commands import (
    get_member_cash_nocheck_async,
    update_member_cash_async,
    get_server_log_info_async
)
from ..Components.view_base import ViewBase
from ..Components.custom_button import CustomButton
from ..Components.custom_select import CustomSelectWithOptions

s_rnd = Random()

class RouletteView(ViewBase):
    slot_panel: LiteralString = """```fix
                              v
│{0}│{1}│{2}│{3}│{4}│{5}│{6}│{7}│{8}│{9}│{10}│{11}│{12}│{13}│{14}│{15}│{16}│
                              ^
```"""
    
    roulette_view_text: dict[int, dict[int, str]] = {
        0: {
            0: "**`Roulette is disabled on this server`**",
            1: "Choose colour",
            2: "**`You have not chose the colour yet`**",
            3: "**`To make bet on this color you need at least {0:0,}`** {1} **`more`**",
            4: "**`Now colour is`** {0}",
            5: "**`You made bet {0:0,}`** {1} **`and won {2:0,}`** {1}",
            6: "Roulette bet",
            7: "<@{0}> **`made bet {1:0,}`** {2} **`and won {3:0,}`** {2}"
        },
        1: {
            0: "**`Рулетка отключена на этом сервере`**",
            1: "Выберите цвет",
            2: "**`Вы ещё не выбрали цвет`**",
            3: "**`Для того, чтобы сделать ставку на этот цвет, Вам нужно ещё хотя бы {0:0,}`** {1}",
            4: "**`Теперь цвет:`** {0}",
            5: "**`Вы сделали ставку {0:0,}`** {1} **`и выиграли {2:0,}`** {1}",
            6: "Ставка на рулетку",
            7: "<@{0}> **`сделал(а, о) ставку {1:0,}`** {2} **`и выиграл(а, о) {3:0,}`** {2}"
        }
    }

    def __init__(self, lng: int, author_id: int, bet: int, timeout: int, guild: Guild, currency: str) -> None:
        super().__init__(lng, author_id, timeout, False)
        self.bet_select: CustomSelectWithOptions = CustomSelectWithOptions(
            custom_id=f"140_{author_id}_" + urandom(4).hex(),
            placeholder=self.roulette_view_text[lng][1],
            opts=[
                SelectOption(label="x2", value='0', emoji='⬛', default=True),
                SelectOption(label="x2", value='1', emoji='🟥'),
                SelectOption(label="x3", value='2', emoji='🟩')
            ]
        )
        self.add_item(item=self.bet_select)
        self.add_item(item=CustomButton(
            style=ButtonStyle.green,
            custom_id=f"61_{author_id}_" + urandom(4).hex(),
            emoji="🎰"
        ))

        self.guild_id: int = guild.id
        self.bet: int = bet
        self.bet_color_number: int = 0
        self.currency: str = currency
        self.is_running: bool = True
        self.events_queue: asyncio.Queue[Interaction] = asyncio.Queue()        
        self.roulette_hanlder.start(guild=guild)

    def process_bet(self) -> tuple[str, int]:
        bet_color_num: int = self.bet_color_number
        getrandbits = s_rnd.getrandbits

        # inlining random.randint
        # 0 <= getrandbits(k) < 2**k = 16
        # getrandbits(k) // 7 =
        #   0, if getrandbits(k) in [0; 6]
        #   1, if getrandbits(k) in [7; 13]
        #   2, if getrandbits(k) in [14; 15]
        colors = [('⬛', '🟥', '🟩')[getrandbits(4) // 7] for _ in range(17)]

        result: int = getrandbits(4)
        while result >= 10:
            result = getrandbits(4)
        result_1: int = result >> 1 # //= 2

        if not result_1:
            # result == 0 or 1
            colors[8] = '⬛'
            if bet_color_num: # != 0
                return (self.slot_panel.format(*colors), 0)
        elif result_1 == 1:
            # result == 2 or 3
            colors[8] = '🟥'
            if bet_color_num != 1:
                return (self.slot_panel.format(*colors), 0)
        elif result == 4:
            colors[8] = '🟩'
            if bet_color_num != 2:
                return (self.slot_panel.format(*colors), 0)
        else:
            # result is [5; 9]
            # Player always lose in this case.
            # '⬛' ~ 0 => 2 ~ '🟥'
            # '🟥' ~ 1 => 1 ~ '🟩'
            # '🟩' ~ 2 => 0 ~ '⬛'
            colors[8] = ('⬛', '🟩', '🟥')[2 - bet_color_num]
            return (self.slot_panel.format(*colors), 0)
        
        return (self.slot_panel.format(*colors), (2, 2, 3)[bet_color_num])

    @tasks.loop(count=None)
    async def roulette_hanlder(self, guild: Guild) -> None:
        bet: int = self.bet
        member_id: int = self.author_id
        currency: str = self.currency
        guild_id: int = self.guild_id
        guild_log_channel: TextChannel | None = None
        log_channel_id, guild_lng = await get_server_log_info_async(guild_id)
        local_text = self.roulette_view_text[self.lng]
        if log_channel_id and isinstance(channel := guild.get_channel(log_channel_id), TextChannel):
            guild_log_channel = channel

        while self.is_running:
            interaction: Interaction = await self.events_queue.get()        
            
            member_cash: int = await get_member_cash_nocheck_async(guild_id, member_id)
            if member_cash < bet:
                await interaction.response.send_message(
                    embed=Embed(description=local_text[3].format(bet - member_cash, self.currency)),
                    ephemeral=True
                )
                self.finalize()
                return
            
            (slot_panel, win_sum_cofficient) = self.process_bet()
            if win_sum_cofficient:
                win_sum: int = win_sum_cofficient * bet
                member_cash += win_sum
            else:
                win_sum: int = 0
                member_cash -= bet

            await update_member_cash_async(guild_id, member_id, member_cash)

            assert interaction.message is not None
            try:
                await interaction.message.edit(embed=Embed(description=slot_panel), view=self)
            except:
                pass
            finally:
                await interaction.response.send_message(
                    embed=Embed(description=local_text[5].format(bet, currency, win_sum)),
                    ephemeral=True
                )
                if guild_log_channel is not None:
                    try:
                        await guild_log_channel.send(embed=Embed(
                            title=self.roulette_view_text[guild_lng][6],
                            description=self.roulette_view_text[guild_lng][7].format(member_id, bet, currency, win_sum)
                        ))
                    except:
                        continue

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        self.events_queue.put_nowait(interaction)
    
    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        assert values and values[0].isdecimal()
        self.bet_select.options[self.bet_color_number].default = False
        new_bet_color_number: int = int(values[0])
        self.bet_select.options[new_bet_color_number].default = True
        self.bet_color_number = new_bet_color_number

        member_cash: int = await get_member_cash_nocheck_async(self.guild_id, self.author_id)
        if member_cash < self.bet:
            await interaction.response.send_message(
                embed=Embed(description=self.roulette_view_text[self.lng][3].format(self.bet - member_cash, self.currency)),
                ephemeral=True
            )
            self.finalize()
            return

        await interaction.response.send_message(
            embed=Embed(description=self.roulette_view_text[self.lng][4].format(
                ('⬛', '🟥', '🟩')[self.bet_color_number])
            ),
            ephemeral=True
        )
    
    async def on_timeout(self) -> None:
        # inlined self.finalize()
        self.is_running = False
        self.roulette_hanlder.cancel()
        self.stop()

    def finalize(self) -> None:
        self.is_running = False
        self.roulette_hanlder.cancel()
        self.stop()

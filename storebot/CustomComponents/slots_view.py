import asyncio
from os import urandom
from typing import LiteralString

from nextcord import (
    ButtonStyle,
    Interaction,
    Embed
)

from Tools.db_commands import get_member_nocheck_async
from CustomComponents.view_base import ViewBase
from CustomComponents.custom_button import CustomButton
from CustomComponents.custom_select import CustomSelect


class SlotsView(ViewBase):
    slots_panel: LiteralString = "```\n┌──────┬──────┬──────┐\n│Слот 1│Слот 2│Слот 3│\n├──────┼──────┼──────┤\n│  {0:<2}  │  {1:<2}  │  {2:<2}  │\n└──────┴──────┴──────┘```"
    slots_view_text: dict[int, dict[int, str]] = {
        0: {
            0: "**`Slots are disabled on this server`**",
            1: "Choose bet",
            2: "Sorry, but you doesn't have enough money"
        },
        1: {
            0: "**`Слоты отключены на этом сервере`**",
            1: "Выберите ставку",
        }
    }

    def __init__(self, lng: int, author_id: int, timeout: int, guild_id: int) -> None:
        super().__init__(lng=lng, author_id=author_id, timeout=timeout)
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
        self.is_running: bool = True
        self.slot_runs_queue: asyncio.Queue[Interaction] = asyncio.Queue()        
        self.slots_task: asyncio.Task[None] = asyncio.get_event_loop().create_task(self.start_slot_runs_handler(guild_id=guild_id))        
    
    async def start_slot_runs_handler(self, guild_id: int) -> None:
        user_id: int = self.author_id
        while self.is_running:
            interaction = await self.slot_runs_queue.get()
            await get_member_nocheck_async(guild_id=guild_id, member_id=user_id)
            

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        self.slot_runs_queue.put_nowait(interaction)
    
    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        self.bet = int(values[0])
        await interaction.response.send_message(
            embed=Embed(description=self.slots_view_text[self.lng][]),
            ephemeral=True
        )
    
    async def on_timeout(self) -> None:
        self.is_running = False
        if not self.slots_task.done():
            self.slots_task.cancel()

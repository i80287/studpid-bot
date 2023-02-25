from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nextcord import Interaction

from os import urandom

from nextcord import (
    Embed,
    ButtonStyle
)

from storebot.CustomComponents.view_base import ViewBase
from storebot.CustomComponents.custom_button import CustomButton
from storebot.CustomModals.slots_manage_modal import SlotsManageModal
from storebot.Tools.db_commands import update_server_slots_table_async


class SlotsManageView(ViewBase):
    slots_manage_view_text: dict[int, dict[int, str]] = {
        0: {
            0: "💱 Expected income for bets:\n**`bet` : `income`**\n{0}\n\n> Press 💱 to manage income for bets"
        },
        1: {
            0: "💱 Ожидаемый доход от ставок:\n**`ставка` : `доход`**\n{0}\n\n> Нажмите 💱 для управления доходом от ставок"
        }
    }

    def __init__(self, lng: int, author_id: int, slots_enabled: int, slots_table: dict[int, int], currency: str) -> None:
        super().__init__(lng=lng, author_id=author_id, timeout=90)
        self.add_item(CustomButton(
            style=ButtonStyle.gray,
            custom_id=f"65_{author_id}_" + urandom(4).hex(),
            emoji="💱"
        ))
        # TODO
        # self.add_item(CustomButton(
        #     style=ButtonStyle.danger,
        #     custom_id=f"66_{author_id}_" + urandom(4).hex(),
        #     emoji="🎰"
        # ))
        self.slots_table: dict[int, int] = slots_table
        self.slots_enabled: int = slots_enabled
        self.currency: str = currency

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert interaction.guild_id is not None
        assert interaction.message is not None
        guild_id: int = interaction.guild_id
        lng: int = self.lng
        match int(custom_id[:2]):
            case 65:
                slots_manage_modal: SlotsManageModal = SlotsManageModal(
                    lng=lng,
                    author_id=self.author_id,
                    slots_table=self.slots_table
                )
                await interaction.response.send_modal(slots_manage_modal)

                await slots_manage_modal.wait()
                if slots_manage_modal.is_changed:
                    new_slots_table: dict[int, int] = slots_manage_modal.slots_table
                    self.slots_table = new_slots_table
                    await update_server_slots_table_async(guild_id=guild_id, slots_table=new_slots_table)
                    currency: str = self.currency
                    try:
                        await interaction.message.edit(embed=Embed(description=SlotsManageView.slots_manage_view_text[lng][0].format(
                            '\n'.join("**`{0}`{2} : `{1}`**{2}".format(bet, income, currency) for bet, income in new_slots_table.items())
                        )))
                    except:
                        return
            case 66:
                self.slots_enabled ^= 1
    
    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return

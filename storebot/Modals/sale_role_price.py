from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nextcord import Interaction

from os import urandom

from nextcord import (
    Embed,
    TextInputStyle
)
from nextcord.ui import (
    TextInput,
    Modal
)

from ..Tools.db_commands import update_server_info_table


class SalePriceModal(Modal):
    sale_price_modal_text: dict[int, dict[int, str]] = {
        0: {
            0: "Change role price for sale",
            1: "Percentage of the role price for sale",
            2: "What part of the role price will be the role have when selling (as a percentage)",
            3: "**`Percent must be integer number from 1 to 200`**",
            4: "**`From now role's price for sale is {} % from the role's price`**"
        },
        1: {
            0: "Изменение цены роли при продаже",
            1: "Процент цены продаваемой роли",
            2: "Какую часть от цены роли будет составлять цена роли при продаже (в процентах)",
            3: "**`Процент должен быть целым числом от 1 до 200`**",
            4: "**`Теперь цена продаваемой роли составляет {} % от цены покупки`**",
        },
    }

    def __init__(self, timeout: int, lng: int, auth_id: int, current_sale_role_percent: int) -> None:
        super().__init__(title=self.sale_price_modal_text[lng][0], timeout=timeout, custom_id=f"12000_{auth_id}_" + urandom(4).hex())
        self.sell_price_percent_textinput = TextInput(
            label=self.sale_price_modal_text[lng][1],
            style=TextInputStyle.paragraph,
            custom_id=f"12001_{auth_id}_" + urandom(4).hex(),
            min_length=1,
            max_length=3,
            required=True,
            default_value=str(current_sale_role_percent),
            placeholder=self.sale_price_modal_text[lng][2]
        )
        self.add_item(self.sell_price_percent_textinput)
        self.new_sale_role_percent: int | None = None
        self.lng: int = lng
    
    @staticmethod
    def check_ans(value: str | None) -> int:
        if value is None or not value.isdecimal() or \
            not (1 <= (sale_role_percent := int(value)) <= 200):
            return 0
        return sale_role_percent

    async def callback(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        if not (sale_role_percent := self.check_ans(self.sell_price_percent_textinput.value)):
            await interaction.response.send_message(
                embed=Embed(description=self.sale_price_modal_text[self.lng][3]),
                ephemeral=True
            )
            self.stop()
            return
        update_server_info_table(interaction.guild_id, "sale_price_perc", sale_role_percent)
        self.new_sale_role_percent = sale_role_percent
        await interaction.response.send_message(
            embed=Embed(
                description=self.sale_price_modal_text[self.lng][4].format(sale_role_percent)
            ),
            ephemeral=True
        )
        self.stop()

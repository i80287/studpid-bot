from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Coroutine
    from nextcord import (
        Interaction,
        Message,
    )

from os import urandom
import logging

from nextcord import (
    ButtonStyle,
    Embed,
    TextChannel,
)

from ..Components.view_base import ViewBase
from ..Components.custom_button import CustomButton
from ..Components.custom_select import CustomSelect
from ..Modals.promocode_modals import AddPromocodeModal, EditPromocodeModal

from ..Tools.db_commands import (
    get_promocodes_async,
    get_promocode_async,
    delete_promocode_async,
    Promocode
)

PROMOCODE_ID_SELECT_MENU_ID = 12377
ADD_PROMOCODE_BUTTON_ID = 12378
EDIT_PROMOCODE_BUTTON_ID = 12379
DELETE_PROMOCODE_BUTTON_ID = 12380


logger = logging.getLogger(__name__)


promocodes_view_text = (
    (
        "Promocode id",
        "**`Could not parse promocode id: integer number in [-2^63; 2^63) is expected`**",
        "**`Promocode with id {0} not found`**",
        "**`You deleted promocode with id {0}`**",
    ),
    (
        "Id промокода",
        "**`Не удалось распарсить id промокода: ожидалось целое число из полуинтервала [-2^63; 2^63)`**",
        "**`Промокод с id {0} не найден`**",
        "**`Вы удалили промокод с id {0}`**",
    ),
)


class PromocodesView(ViewBase):
    def __init__(self, lng: int, author_id: int, promocodes: list[Promocode]) -> None:
        super().__init__(lng, author_id)
        self.add_item(CustomSelect(
            custom_id=f"{PROMOCODE_ID_SELECT_MENU_ID}_{author_id}_{urandom(4).hex()}",
            placeholder=promocodes_view_text[lng][0],
            options=[(str(promo.promo_id), str(promo.promo_id)) for promo in promocodes]
        ))
        self.add_item(CustomButton(
            style=ButtonStyle.green,
            custom_id=f"{ADD_PROMOCODE_BUTTON_ID}_{author_id}_{urandom(4).hex()}",
            emoji="<:add01:999663315804500078>"
        ))
        self.add_item(CustomButton(
            style=ButtonStyle.gray,
            custom_id=f"{EDIT_PROMOCODE_BUTTON_ID}_{author_id}_{urandom(4).hex()}",
            emoji="🛠️",
            disabled=len(promocodes) == 0
        ))
        self.add_item(CustomButton(
            style=ButtonStyle.red,
            custom_id=f"{DELETE_PROMOCODE_BUTTON_ID}_{author_id}_{urandom(4).hex()}",
            emoji="<:remove01:999663428689997844>",
            disabled=len(promocodes) == 0
        ))
        self.__selected_promocode_id = None

    @staticmethod
    async def __update_promocodes_message(interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        _, embed = await PromocodesView.make_promocodes_embed(interaction.guild_id)
        if (message := interaction.message) is not None:
            try:
                await message.edit(embed=embed)
            except Exception as ex:
                logger.error(f"could not edit original message in the add_promocode: {ex}")

    @staticmethod
    def __parse_promocode_id(value) -> int | None:
        try:
            int_value = value if isinstance(value, int) else int(str(value))
            if -((1 << 53) - 1) <= int_value <= ((1 << 53) - 1):
                return int_value
        except:
            pass

        return None

    def __handle_invalid_promocode_id(self, interaction: Interaction) -> Coroutine:
        return interaction.send(
            embed=Embed(description=promocodes_view_text[self.lng][1]),
            ephemeral=True
        )

    def __handle_missing_promocode(self, interaction: Interaction, promocode_id: int) -> Coroutine:
        return interaction.send(
            embed=Embed(description=promocodes_view_text[self.lng][2].format(promocode_id)),
            ephemeral=True
        )

    async def __get_current_promocode(self, interaction: Interaction) -> None | Promocode:
        if (promocode_id := self.__parse_promocode_id(self.__selected_promocode_id)) is None:
            await self.__handle_invalid_promocode_id(interaction)
            return None
        assert interaction.guild_id is not None
        if (promocode := await get_promocode_async(interaction.guild_id, promocode_id)) is None:
            await self.__handle_missing_promocode(interaction, promocode_id)
        return promocode


    async def add_promocode(self, interaction: Interaction) -> None:
        modal = AddPromocodeModal(lng=self.lng)
        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.added_promocode is not None:
            await PromocodesView.__update_promocodes_message(interaction)

    async def edit_promocode(self, interaction: Interaction) -> None:
        if (promocode := await self.__get_current_promocode(interaction)) is None:
            return

        modal = EditPromocodeModal(lng=self.lng, current_promocode=promocode)
        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.edited_promocode is not None:
            await PromocodesView.__update_promocodes_message(interaction)

    async def delete_promocode(self, interaction: Interaction) -> None:
        if (promocode := await self.__get_current_promocode(interaction)) is None:
            return

        assert interaction.guild_id is not None
        await delete_promocode_async(interaction.guild_id, promocode.promo_id)
        await interaction.send(
            embed=Embed(description=promocodes_view_text[self.lng][3].format(promocode.promo_id)),
            ephemeral=True,
        )
        await PromocodesView.__update_promocodes_message(interaction)

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert ADD_PROMOCODE_BUTTON_ID == 12378
        assert EDIT_PROMOCODE_BUTTON_ID == 12379
        assert DELETE_PROMOCODE_BUTTON_ID == 12380
        match int(custom_id[:custom_id.find('_')]):
            case 12378:
                await self.add_promocode(interaction)
            case 12379:
                await self.edit_promocode(interaction)
            case 12380:
                await self.delete_promocode(interaction)


    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        assert int(custom_id[:custom_id.find('_')]) == PROMOCODE_ID_SELECT_MENU_ID
        assert len(values) == 1
        assert isinstance(values[0], str)
        assert values[0].isdecimal()
        self.__selected_promocode_id = int(values[0])

    @staticmethod
    def format_promocode(promocode: Promocode) -> str:
        return f"**`{'`** - **`'.join(promocode.str_components())}`**"

    @staticmethod
    def format_promocodes(promocodes: list[Promocode]) -> str:
        lines = ["**`id`** - **`money`** - **`for user (id)`** - **`count`**"]
        lines.extend(map(PromocodesView.format_promocode, promocodes))
        return '\n'.join(lines)

    @staticmethod
    async def make_promocodes_embed(guild_id: int):
        promocodes = await get_promocodes_async(guild_id)
        return promocodes, Embed(description=PromocodesView.format_promocodes(promocodes))

from __future__ import annotations

from nextcord import (
    Embed,
    TextInputStyle,
    Interaction
)
from nextcord.ui import Modal, TextInput

from ..Tools.db_commands import (
    add_promocode_async,
    update_promocode_async,
    PROMOCODE_INF_COUNT,
    PROMOCODE_FOR_ANY_USER_ID,
    Promocode
)

promocode_modals_text = (
    (
        "Add promocode",
        "Edit promocode",
        "Amount of money gained from the promocode",
        "Number of the promocodes",
        f"Input {PROMOCODE_INF_COUNT} if number of the promocodes is inf (can't run out)",
        "Id of the user who can use promocode",
        f"Input {PROMOCODE_FOR_ANY_USER_ID} if everyone should be able to use promocode",

        "**`Could not parse promocode money value: integer number >= 0 is expected`**",
        f"**`Could not parse promocode count: integer number > 0 or {PROMOCODE_INF_COUNT} for the infinite number of the promocodes is expected`**",
        f"**`Could not parse promocode owner id: integer number in [0; 2^63) or {PROMOCODE_FOR_ANY_USER_ID} for any user is expected`**",

        "**`You have not changed anything in the promocode date`**",
        "**`You added promocode: {pm_count} promocode[s] with id {pm_id}, each one gives {pm_money} money, who can use:`** {pm_owner}",
        "**`You edited promocode: {pm_count} promocode[s] with id {pm_id}, each one gives {pm_money} money, who can use:`** {pm_owner}",

    ),
    (
        "Добавление промокода",
        "Изменение промокода",
        "Количество валюты, получаемой за промокод",
        "Количество промокодов",
        f"Введите {PROMOCODE_INF_COUNT}, если количество промокодов бесконечно (промокод не может закончиться)",
        "Id юзера, который может использовать промокод",
        f"Введите {PROMOCODE_FOR_ANY_USER_ID}, если промокод может использовать любой пользователь",

        "**`Не удалось распарсить количество валюты, начисляемой за промокод: ожидалось целое число >= 0`**",
        f"**`Не удалось распарсить количество промокодов: ожидалось целое число > 0 или {PROMOCODE_INF_COUNT} для бесконечного количества промокодов`**",
        f"**`Не удалось распарсить id владельца промокода: ожидалось целое число из полуинтервала [0; 2^63) или {PROMOCODE_FOR_ANY_USER_ID} для любого пользователя`**",

        "**`Вы ничего не изменили в характеристиках промокоде`**",
        "**`Вы добавили промокод: {pm_count} промокод[ов] с id {pm_id}, каждый приносит {pm_money} валюты, кто может применить:`** {pm_owner}",
        "**`Вы изменили промокод: {pm_count} промокод[ов] с id {pm_id}, каждый приносит {pm_money} валюты, кто может применить:`** {pm_owner}",

    ),
)

assert len(promocode_modals_text[0]) == len(promocode_modals_text[1])


def _parse_promocode_money(value: str | None) -> tuple[bool, int]:
    return (True, int(value)) if value is not None and value.isdecimal() else (False, 0)


def _parse_promocode_count(value: str | None) -> tuple[bool, int]:
    if value is not None:
        try:
            int_value = int(value)
            if int_value > 0 or int_value == PROMOCODE_INF_COUNT:
                return (True, int_value)
        except:
            pass
    return (False, 0)


def _parse_promocode_for_user_id(value: str | None) -> tuple[bool, int]:
    if value is not None:
        try:
            int_value = int(value)
            if 0 <= int_value < (1 << 63) or int_value == PROMOCODE_FOR_ANY_USER_ID:
                return (True, int_value)
        except:
            pass
    return (False, 0)


class AddPromocodeModal(Modal):
    def __init__(self, lng: int) -> None:
        locale_text = promocode_modals_text[lng]
        if __debug__:
            for i in (2, 3, 5):
                assert len(promocode_modals_text[lng][i]) <= 45, "Modal label must be 45 or fewer in length"
        super().__init__(locale_text[1], timeout=40.0)
        self.__promocode_money_text_input = TextInput(
            label=locale_text[2],
            style=TextInputStyle.short,
            min_length=1,
            max_length=7,
            required=True,
        )
        self.__promocode_count_text_input = TextInput(
            label=locale_text[3],
            style=TextInputStyle.paragraph,
            min_length=1,
            max_length=6,
            required=True,
            default_value=f"{PROMOCODE_INF_COUNT}",
            placeholder=locale_text[4],
        )
        self.__promocode_for_user_id_text_input = TextInput(
            label=locale_text[5],
            style=TextInputStyle.paragraph,
            min_length=1,
            max_length=19,
            required=True,
            default_value=f"{PROMOCODE_FOR_ANY_USER_ID}",
            placeholder=locale_text[6],
        )
        self.add_item(self.__promocode_money_text_input)
        self.add_item(self.__promocode_count_text_input)
        self.add_item(self.__promocode_for_user_id_text_input)
        self.added_promocode: Promocode | None = None
        self.__lng = lng


    async def callback(self, interaction: Interaction) -> None:
        locale_text = promocode_modals_text[self.__lng]

        success, promocode_money = _parse_promocode_money(self.__promocode_money_text_input.value)
        if not success:
            await interaction.response.send_message(embed=Embed(description=locale_text[7]), ephemeral=True)
            return

        success, promocode_count = _parse_promocode_count(self.__promocode_count_text_input.value)
        if not success:
            await interaction.response.send_message(embed=Embed(description=locale_text[8]), ephemeral=True)
            return

        success, promocode_for_user_id = _parse_promocode_for_user_id(self.__promocode_for_user_id_text_input.value)
        if not success:
            await interaction.response.send_message(embed=Embed(description=locale_text[9]), ephemeral=True)
            return

        assert interaction.guild_id is not None
        self.added_promocode = await add_promocode_async(
            interaction.guild_id,
            promocode_money,
            promocode_count,
            promocode_for_user_id
        )

        assert interaction.guild is not None
        await interaction.response.send_message(embed=Embed(description=locale_text[11].format(
            pm_count=self.added_promocode.str_count(),
            pm_id=self.added_promocode.str_promo_id(),
            pm_money=self.added_promocode.str_money(),
            pm_owner=f"<@{self.added_promocode.for_user_id}>" if self.added_promocode.for_user_id != PROMOCODE_FOR_ANY_USER_ID else interaction.guild.default_role.mention
        )), ephemeral=True)
        self.stop()


class EditPromocodeModal(Modal):
    def __init__(self, lng: int, current_promocode: Promocode) -> None:
        locale_text = promocode_modals_text[lng]
        super().__init__(locale_text[0], timeout=40.0)
        self.__promocode_money_text_input = TextInput(
            label=locale_text[2],
            style=TextInputStyle.short,
            min_length=1,
            max_length=7,
            default_value=f"{current_promocode.money}",
            required=True,
        )
        self.__promocode_count_text_input = TextInput(
            label=locale_text[3],
            style=TextInputStyle.paragraph,
            max_length=6,
            required=True,
            default_value=f"{current_promocode.count}",
            placeholder=locale_text[4],
        )
        self.__promocode_for_user_id_text_input = TextInput(
            label=locale_text[5],
            style=TextInputStyle.paragraph,
            max_length=19,
            required=True,
            default_value=f"{current_promocode.for_user_id}",
            placeholder=locale_text[6],
        )
        self.add_item(self.__promocode_money_text_input)
        self.add_item(self.__promocode_count_text_input)
        self.add_item(self.__promocode_for_user_id_text_input)
        self.edited_promocode: Promocode | None = None
        self.__current_promocode = current_promocode
        self.__lng = lng


    async def callback(self, interaction: Interaction) -> None:
        locale_text = promocode_modals_text[self.__lng]

        success, promocode_money = _parse_promocode_money(self.__promocode_money_text_input.value)
        if not success:
            await interaction.response.send_message(embed=Embed(description=locale_text[7]), ephemeral=True)
            return

        success, promocode_count = _parse_promocode_count(self.__promocode_count_text_input.value)
        if not success:
            await interaction.response.send_message(embed=Embed(description=locale_text[8]), ephemeral=True)
            return

        success, promocode_for_user_id = _parse_promocode_for_user_id(self.__promocode_for_user_id_text_input.value)
        if not success:
            await interaction.response.send_message(embed=Embed(description=locale_text[9]), ephemeral=True)
            return

        current_promocode = self.__current_promocode
        if promocode_money == current_promocode.money and promocode_count == current_promocode.count and promocode_for_user_id == current_promocode.for_user_id:
            await interaction.response.send_message(embed=Embed(description=locale_text[10]), ephemeral=True)
            return

        assert interaction.guild_id is not None
        self.edited_promocode = await update_promocode_async(
            guild_id=interaction.guild_id,
            promocode_id=self.__current_promocode.promo_id,
            promocode_money=promocode_money,
            promocode_count=promocode_count,
            for_user_id=promocode_for_user_id,
        )

        assert interaction.guild is not None
        await interaction.response.send_message(embed=Embed(description=locale_text[12].format(
            pm_count=self.edited_promocode.str_count(),
            pm_id=self.edited_promocode.str_promo_id(),
            pm_money=self.edited_promocode.str_money(),
            pm_owner=f"<@{self.edited_promocode.for_user_id}>" if self.edited_promocode.for_user_id != PROMOCODE_FOR_ANY_USER_ID else interaction.guild.default_role.mention
        )), ephemeral=True)
        self.stop()

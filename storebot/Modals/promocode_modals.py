from __future__ import annotations

import re

from nextcord import (
    Embed,
    TextInputStyle,
    Interaction
)
from nextcord.ui import Modal, TextInput
from nextcord.utils import MISSING

from ..Tools.db_commands import (
    add_promocode_async,
    update_promocode_async,
    PROMOCODE_INF_COUNT,
    PROMOCODE_FOR_ANY_USER_ID,
    PROMOCODE_NAME_MAX_LENGTH,
    Promocode
)

SQL_INJECTION_PATTERN = re.compile(r"(\s*([\0\b\'\"\n\r\t\%\_\\]*\s*(((select\s*.+\s*from\s*.+)|(insert\s*.+\s*into\s*.+)|(update\s*.+\s*set\s*.+)|(delete\s*.+\s*from\s*.+)|(drop\s*.+)|(truncate\s*.+)|(alter\s*.+)|(exec\s*.+)|(\s*(all|any|not|and|between|in|like|or|some|contains|containsall|containskey)\s*.+[\=\>\<=\!\~]+.+)|(let\s+.+[\=]\s*.*)|(begin\s*.*\s*end)|(\s*[\/\*]+\s*.*\s*[\*\/]+)|(\s*(\-\-)\s*.*\s+)|(\s*(contains|containsall|containskey)\s+.*)))(\s*[\;]\s*)*)+)", flags=re.RegexFlag.MULTILINE | re.RegexFlag.IGNORECASE)

promocode_modals_text = (
    (
        "Add promocode",
        "Edit promocode",
        "Promocode name",
        f"Input promocode name whose length <= {PROMOCODE_NAME_MAX_LENGTH} characters",
        "Amount of money gained from the promocode",
        "Number of the promocodes",
        f"Input {PROMOCODE_INF_COUNT} if number of the promocodes is inf (can't run out)",
        "Id of the user who can use promocode",
        f"Input {PROMOCODE_FOR_ANY_USER_ID} if everyone should be able to use promocode",

        f"**`Could not parse promocode name: string with <= {PROMOCODE_NAME_MAX_LENGTH} character is expected`**",
        "**`Could not parse promocode money value: integer number >= 0 is expected`**",
        f"**`Could not parse promocode count: integer number > 0 or {PROMOCODE_INF_COUNT} for the infinite number of the promocodes is expected`**",
        f"**`Could not parse promocode owner id: integer number in [0; 2^63) or {PROMOCODE_FOR_ANY_USER_ID} for any user is expected`**",

        "**`You have not changed anything in the promocode date`**",
        "**`Promocode was deleted by the other command during the execution of the current command`**",
        "**`You added promocode: {pm_count} promocode[s] with id {pm_id} and name {pm_nm}, each one gives {pm_money} money, who can use:`** {pm_owner}",
        "**`You edited promocode: {pm_count} promocode[s] with id {pm_id} and name {pm_nm}, each one gives {pm_money} money, who can use:`** {pm_owner}",
    ),
    (
        "Добавление промокода",
        "Изменение промокода",
        "Имя промокода",
        f"Введите имя промокда длиной <= {PROMOCODE_NAME_MAX_LENGTH} символов",
        "Количество валюты, получаемой за промокод",
        "Количество промокодов",
        f"Введите {PROMOCODE_INF_COUNT}, если количество промокодов бесконечно (промокод не может закончиться)",
        "Id юзера, который может использовать промокод",
        f"Введите {PROMOCODE_FOR_ANY_USER_ID}, если промокод может использовать любой пользователь",

        f"**`Не удалось распарсить имя промокода: ожидалась строка символов длиной <= {PROMOCODE_NAME_MAX_LENGTH} символов`**",
        "**`Не удалось распарсить количество валюты, начисляемой за промокод: ожидалось целое число >= 0`**",
        f"**`Не удалось распарсить количество промокодов: ожидалось целое число > 0 или {PROMOCODE_INF_COUNT} для бесконечного количества промокодов`**",
        f"**`Не удалось распарсить id владельца промокода: ожидалось целое число из полуинтервала [0; 2^63) или {PROMOCODE_FOR_ANY_USER_ID} для любого пользователя`**",

        "**`Вы ничего не изменили в характеристиках промокоде`**",
        "**`Промокод был удалён вызовом другой команды во время изменения текущей командой`**",
        "**`Вы добавили промокод: {pm_count} промокод[ов] с id {pm_id} и именем {pm_nm}, каждый приносит {pm_money} валюты, кто может применить:`** {pm_owner}",
        "**`Вы изменили промокод: {pm_count} промокод[ов] с id {pm_id} и именем {pm_nm}, каждый приносит {pm_money} валюты, кто может применить:`** {pm_owner}",
    ),
)

assert len(promocode_modals_text[0]) == len(promocode_modals_text[1])


def _parse_promocode_money(value: str | None) -> int | None:
    return int(value) if value is not None and value.isdecimal() else None


def _parse_promocode_count(value: str | None) -> int | None:
    if value is not None:
        try:
            int_value = int(value)
            if int_value > 0 or int_value == PROMOCODE_INF_COUNT:
                return int_value
        except:
            pass
    return None


def _parse_promocode_for_user_id(value: str | None) -> int | None:
    if value is not None:
        try:
            int_value = int(value)
            if 0 <= int_value < (1 << 63) or int_value == PROMOCODE_FOR_ANY_USER_ID:
                return int_value
        except:
            pass
    return None


def _parse_promocode_name(value: str | None) -> str | None:
    return value if value is not None and SQL_INJECTION_PATTERN.search(value) is None else None


class PromocodeModal(Modal):
    def __init__(self, lng: int, current_promocode: Promocode | None = None) -> None:
        locale_text = promocode_modals_text[lng]

        if current_promocode is None:
            promo_name_txt_inp_def_val = None
            promo_money_txt_inp_def_val = None
            promo_count_txt_inp_def_val = f"{PROMOCODE_INF_COUNT}"
            promo_for_user_id_txt_inp_def_val = f"{PROMOCODE_FOR_ANY_USER_ID}"
        else:
            promo_name_txt_inp_def_val = current_promocode.promo_name
            promo_money_txt_inp_def_val = f"{current_promocode.money}"
            promo_count_txt_inp_def_val = f"{current_promocode.count}"
            promo_for_user_id_txt_inp_def_val = f"{current_promocode.for_user_id}"

        if __debug__:
            for i in (2, 4, 5, 7):
                assert len(promocode_modals_text[0][i]) <= 45, "Modal label must be 45 or fewer in length"
                assert len(promocode_modals_text[1][i]) <= 45, "Modal label must be 45 or fewer in length"

        super().__init__(locale_text[0 if current_promocode is None else 1], timeout=40.0)
        self.__promocode_name_text_input = TextInput(
            label=locale_text[2],
            style=TextInputStyle.paragraph,
            min_length=1,
            max_length=PROMOCODE_NAME_MAX_LENGTH,
            required=True,
            default_value=promo_name_txt_inp_def_val,
            placeholder=locale_text[3]
        )
        self.__promocode_money_text_input = TextInput(
            label=locale_text[4],
            style=TextInputStyle.paragraph,
            min_length=1,
            max_length=7,
            required=True,
            default_value=promo_money_txt_inp_def_val
        )
        self.__promocode_count_text_input = TextInput(
            label=locale_text[5],
            style=TextInputStyle.paragraph,
            min_length=1,
            max_length=6,
            required=True,
            default_value=promo_count_txt_inp_def_val,
            placeholder=locale_text[6],
        )
        self.__promocode_for_user_id_text_input = TextInput(
            label=locale_text[7],
            style=TextInputStyle.paragraph,
            min_length=1,
            max_length=19,
            required=True,
            default_value=promo_for_user_id_txt_inp_def_val,
            placeholder=locale_text[8],
        )
        self.add_item(self.__promocode_name_text_input)
        self.add_item(self.__promocode_money_text_input)
        self.add_item(self.__promocode_count_text_input)
        self.add_item(self.__promocode_for_user_id_text_input)
        self.__lng = lng
        self.__current_promocode: Promocode | None = current_promocode
        self.promocode: Promocode | None = None

    async def callback(self, interaction: Interaction) -> None:
        locale_text = promocode_modals_text[self.__lng]

        if (promocode_name := _parse_promocode_name(self.__promocode_name_text_input.value)) is None:
            await interaction.response.send_message(embed=Embed(description=locale_text[9]), ephemeral=True)
            return
        if (promocode_money := _parse_promocode_money(self.__promocode_money_text_input.value)) is None:
            await interaction.response.send_message(embed=Embed(description=locale_text[10]), ephemeral=True)
            return
        if (promocode_count := _parse_promocode_count(self.__promocode_count_text_input.value)) is None:
            await interaction.response.send_message(embed=Embed(description=locale_text[11]), ephemeral=True)
            return
        if (promocode_for_user_id := _parse_promocode_for_user_id(self.__promocode_for_user_id_text_input.value)) is None:
            await interaction.response.send_message(embed=Embed(description=locale_text[12]), ephemeral=True)
            return

        current_promocode = self.__current_promocode
        if current_promocode is not None and \
            promocode_name == current_promocode.promo_name and \
                promocode_money == current_promocode.money and \
                    promocode_count == current_promocode.count and \
                        promocode_for_user_id == current_promocode.for_user_id:
            await interaction.response.send_message(embed=Embed(description=locale_text[13]), ephemeral=True)
            return
        print(promocode_name)
        assert interaction.guild_id is not None
        self.promocode = new_promocode = await (
                add_promocode_async(
                    guild_id=interaction.guild_id,
                    promo_name=promocode_name,
                    promocode_money=promocode_money,
                    promocode_count=promocode_count,
                    for_user_id=promocode_for_user_id
                )
            if current_promocode is None
            else
                update_promocode_async(
                    guild_id=interaction.guild_id,
                    promocode_id=current_promocode.promo_id,
                    promo_name=promocode_name,
                    promocode_money=promocode_money,
                    promocode_count=promocode_count,
                    for_user_id=promocode_for_user_id,
                )
        )
        print(promocode_name)

        if new_promocode is None:
            await interaction.response.send_message(embed=Embed(description=locale_text[14]), ephemeral=True)
            return

        assert interaction.guild is not None
        await interaction.response.send_message(embed=Embed(description=locale_text[15 if current_promocode is None else 16].format(
            pm_count=new_promocode.str_count(),
            pm_id=new_promocode.str_promo_id(),
            pm_nm=promocode_name,
            pm_money=new_promocode.str_money(),
            pm_owner=f"<@{new_promocode.for_user_id}>" if new_promocode.for_user_id != PROMOCODE_FOR_ANY_USER_ID else interaction.guild.default_role.mention
        )), ephemeral=True)
        self.stop()


def AddPromocodeModal(lng: int) -> PromocodeModal:
    return PromocodeModal(lng=lng, current_promocode=None)    


def EditPromocodeModal(lng: int, current_promocode: Promocode) -> PromocodeModal:
    return PromocodeModal(lng=lng, current_promocode=current_promocode)

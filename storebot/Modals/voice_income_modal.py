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

from ..Tools.db_commands import update_server_info_table_async


class VoiceIncomeModal(Modal):
    voice_income_modal_text: tuple[tuple[str, ...], tuple[str, ...]] = (
        (
            "Change voice income",

            "Money income from presence in voice channel",

            "Income from presence in voice channel for 10 minutes (income will be given for every second)",

            "Xp gained from presence in voice channel",

            "Xp from presence in voice channel for 10 minutes (xp will be given for every second)",

            "**`From now money income from presence in voice channel for 10 minutes is {}`**\n\
            **`Income will be given for every second by formula:`**\n\
            **`time_presence_in_channel_in_seconds`** * **`money_income`** / **`600`**\n",

            "**`From now xp gained from presence in voice channel for 10 minutes is {}`**\n\
            **`Income will be given for every second by formula:`**\n\
            **`time_presence_in_channel_in_seconds`** * **`xp`** / **`600`**\n",

            "**`You have not changed the value`**",
        ),
        (
            "Изменение дохода",

            "Доход за присутствие в голосовом канале",

            "Доход за 10 минут присутствия в голосовом канале (сам доход начислится за каждую секунду)",

            "Опыт за присутствие в голосовом канале",

            "Опыт за 10 минут присутствия в голосовом канале (сам опыт начислится за каждую секунду)",

            "**`Теперь доход за 10 минут присутствия в голосовом канале равен {}`**\n\
            **`Сам доход начислится за каждую секунду по формуле:`**\n\
            **`время_присутствия_в_канале_в_секундах`** * **`доход`** / **`600`**",

            "**`Теперь опыт, получаемый за 10 минут присутствия в голосовом канале равен {}`**\n\
            **`Сам опыт начислится за каждую секунду по формуле:`**\n\
            **`время_присутствия_в_канале_в_секундах`** * **`опыт`** / **`600`**",

            "**`Вы не поменяли знечение`**",
        ),
    )
    assert len(voice_income_modal_text[0]) == len(voice_income_modal_text[1])

    def __init__(self, lng: int, income: int, is_money: bool) -> None:
        local_text: tuple[str, ...] = self.voice_income_modal_text[lng]
        assert len(local_text[1]) <= 45
        assert len(local_text[3]) <= 45
        assert len(local_text[2]) <= 100
        assert len(local_text[4]) <= 100

        super().__init__(title=local_text[0], timeout=30.0, custom_id="13000" + urandom(4).hex())
        self.income_text_input = TextInput(
            label=local_text[1 if is_money else 3],
            style=TextInputStyle.paragraph,
            custom_id=urandom(4).hex(),
            min_length=1,
            max_length=9,
            default_value=str(income),
            placeholder=local_text[2 if is_money else 4]
        )

        self.add_item(self.income_text_input)
        self.income: int = income
        self.lng: int = lng
        self.is_money: bool = is_money

    @staticmethod
    def check_ans(value: str | None) -> int | None:
        if value is not None and value.isdecimal():
            return int(value)
        return None

    async def callback(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None

        if (income := self.check_ans(self.income_text_input.value)) is not None and income != self.income:
            if self.is_money:
                await update_server_info_table_async(interaction.guild_id, "mn_for_voice", income)
                response = self.voice_income_modal_text[self.lng][5].format(income)
            else:
                await update_server_info_table_async(interaction.guild_id, "xp_for_voice", income)
                response = self.voice_income_modal_text[self.lng][6].format(income)

            self.income = income
        else:
            response = self.voice_income_modal_text[self.lng][7]

        await interaction.response.send_message(
            embed=Embed(description=response),
            ephemeral=True
        )

        self.stop()

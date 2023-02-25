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

from storebot.Tools.db_commands import update_server_info_table


class VoiceIncomeModal(Modal):
    voice_income_modal_text: dict[int, dict[int, str]] = {
        0: {
            0: "Change voice income",
            1: "Income from presence in voice channel",
            2: "Income from presence in voice channel for 10 minutes (income will be given for every second)",
            3: "**`From now income from presence in voice channel for 10 minutes is {}`**\n\
                **`Income will be given for every second by formula:`**\n\
                **`time_presence_in_channel_in_seconds`** * **`income`** / **`600`**",
            4: "**`You have not change value`**",
            5: "**`Income should be integer non-negative number`**",
        },
        1: {
            0: "Изменение дохода",
            1: "Доход за присутствие в голосовом канале",
            2: "Доход за 10 минут присутствия в голосовом канале (сам доход начислится за каждую секунду)",
            3: "**`Теперь доход за 10 минут присутствия в голосовом канале равен {}`**\n\
                **`Сам доход начислится за каждую секунду по формуле:`**\n\
                **`время_присутствия_в_канале_в_секундах`** * **`доход`** / **`600`**",
            4: "**`Вы не поменяли знечение`**",
            5: "**`Доход должен быть целым неотрицательным числом`**",
        },
    }

    def __init__(self, timeout: int, lng: int, auth_id: int, voice_income: int) -> None:
        super().__init__(title=self.voice_income_modal_text[lng][0], timeout=timeout, custom_id=f"13000_{auth_id}_" + urandom(4).hex())
        self.voice_income_textinput = TextInput(
            label=self.voice_income_modal_text[lng][1],
            style=TextInputStyle.paragraph,
            custom_id=f"13001_{auth_id}_" + urandom(4).hex(),
            min_length=1,
            max_length=9,
            required=True,
            default_value=str(voice_income),
            placeholder=self.voice_income_modal_text[lng][2]
        )
        self.add_item(self.voice_income_textinput)
        self.voice_income: int = voice_income
        self.lng: int = lng
    
    @staticmethod
    def check_ans(value: str | None) -> int | None:
        if value is not None and value.isdigit():
            return int(value)
        return None

    async def callback(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        if (voice_income := self.check_ans(self.voice_income_textinput.value)) is not None:
            if voice_income != self.voice_income:
                update_server_info_table(interaction.guild_id, "mn_for_voice", voice_income)
                self.voice_income = voice_income
                response: str = self.voice_income_modal_text[self.lng][3].format(voice_income)
            else:
                response: str = self.voice_income_modal_text[self.lng][4]
        else:
            response: str = self.voice_income_modal_text[self.lng][5]
        await interaction.response.send_message(
            embed=Embed(description=response),
            ephemeral=True
        )
        self.stop()

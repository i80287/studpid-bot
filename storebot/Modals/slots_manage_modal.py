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
    Modal,
    TextInput
)


class SlotsManageModal(Modal):
    slots_manage_modal_text: dict[int, dict[int, str]] = {
        0: {
            0: "Change expected income for bets",
            1: "Expected income for bet {0}",
            2: "Mathematical expectation of income for bet {0}",
            3: "**`Non-negative integer number expected in text input field {0}`**",
            4: "**`You updated expected income for bets:`**\n",
            5: "**`You have not changed anything`**"
        },
        1: {
            0: "Изменение ожидаемого выигрыша за ставки",
            1: "Ожидаемый выигрыш за ставку {0}",
            2: "Математическое ожидание выигрыша за ставку {0}",
            3: "**`В текстовом поле {0} ожидалось целое неотрицательное число`**",
            4: "**`Вы обновили доход за ставки:`**\n",
            5: "**`Вы ничего не поменяли`**"
        }
    }

    def __init__(self, lng: int, author_id: int, slots_table: dict[int, int]) -> None:
        locale_text: dict[int, str] = self.slots_manage_modal_text[lng]
        super().__init__(
            title=locale_text[0],
            timeout=90,
            custom_id=f"13100_{author_id}_" + urandom(4).hex()
        )
        self.income_for_bet_1 = TextInput(
            label=locale_text[1].format(100),
            style=TextInputStyle.paragraph,
            min_length=1,
            max_length=4,
            required=True,
            default_value=str(slots_table[100]),
            placeholder=locale_text[2].format(100)
        )
        self.income_for_bet_2 = TextInput(
            label=locale_text[1].format(200),
            style=TextInputStyle.paragraph,
            min_length=1,
            max_length=4,
            required=True,
            default_value=str(slots_table[200]),
            placeholder=locale_text[2].format(200)
        )
        self.income_for_bet_3 = TextInput(
            label=locale_text[1].format(500),
            style=TextInputStyle.paragraph,
            min_length=1,
            max_length=4,
            required=True,
            default_value=str(slots_table[500]),
            placeholder=locale_text[2].format(500)
        )
        self.income_for_bet_4 = TextInput(
            label=locale_text[1].format(1000),
            style=TextInputStyle.paragraph,
            min_length=1,
            max_length=4,
            required=True,
            default_value=str(slots_table[1000]),
            placeholder=locale_text[2].format(1000)
        )
        self.add_item(self.income_for_bet_1)
        self.add_item(self.income_for_bet_2)
        self.add_item(self.income_for_bet_3)
        self.add_item(self.income_for_bet_4)
        self.is_changed: bool = False
        self.slots_table: dict[int, int] = slots_table
        self.locale_text: dict[int, str] = locale_text
    
    def verify_user_input(self) -> int:
        errors_bit_mask: int = 0b0000

        if (income_1 := self.income_for_bet_1.value) and income_1.isdecimal():
            new_income_1: int = int(income_1)
            if self.slots_table[100] != new_income_1:
                self.slots_table[100] = new_income_1
                self.is_changed = True
        else:
            errors_bit_mask |= 0b0001
        
        if (income_2 := self.income_for_bet_2.value) and income_2.isdecimal():
            new_income_2: int = int(income_2)
            if self.slots_table[200] != new_income_2:
                self.slots_table[200] = new_income_2
                self.is_changed = True
        else:
            errors_bit_mask |= 0b0010
        
        if (income_3 := self.income_for_bet_3.value) and income_3.isdecimal():
            new_income_3: int = int(income_3)
            if self.slots_table[500] != new_income_3:
                self.slots_table[500] = new_income_3
                self.is_changed = True
        else:
            errors_bit_mask |= 0b0100
        
        if (income_4 := self.income_for_bet_4.value) and income_4.isdecimal():
            new_income_4: int = int(income_4)
            if self.slots_table[1000] != new_income_4:
                self.slots_table[1000] = new_income_4
                self.is_changed = True
        else:
            errors_bit_mask |= 0b1000
        
        return errors_bit_mask

    async def callback(self, interaction: Interaction) -> None:
        locale_text: dict[int, str] = self.locale_text
        if errors_bit_mask := self.verify_user_input():
            report: list[str] = []
            if errors_bit_mask & 0b0001:
                report.append(locale_text[3].format(1))
            if errors_bit_mask & 0b0010:
                report.append(locale_text[3].format(2))
            if errors_bit_mask & 0b0100:
                report.append(locale_text[3].format(3))
            if errors_bit_mask & 0b1000:
                report.append(locale_text[3].format(4))
            
            await interaction.response.send_message(
                embed=Embed(description='\n'.join(report)),
                ephemeral=True
            )
            return
        
        description: str = locale_text[4] + '\n'.join("**`{0}` : `{1}`**".format(bet, income) for bet, income in self.slots_table.items()) \
            if self.is_changed else locale_text[5] 
        await interaction.response.send_message(
            embed=Embed(description=description),
            ephemeral=True
        )

        self.stop()

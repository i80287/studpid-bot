from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Literal

    from nextcord import Interaction

from os import urandom

from ..Components.view_base import ViewBase
from ..Components.custom_select import CustomSelect


class SelectChannelView(ViewBase):
    ec_log_channel_view_text: dict[int, tuple[str, str]] = {
        0: ("Select one channel", "Not selected"),
        1: ("Выберите один канал", "Не выбрано")
    }

    def __init__(self, lng: int, author_id: int, timeout: float, channels_options: list[tuple[str, str]]) -> None:
        assert all(option[1].isdecimal() for option in channels_options)
        super().__init__(lng, author_id, timeout)
        channels_count: int = len(channels_options)
        local_text = self.ec_log_channel_view_text[lng]
        placeholder: str = local_text[0]
        default_value: list[tuple[str, Literal['0']]] = [(local_text[1], '0')]
        for i in range(min((channels_count + 23) // 24, 5)):
            self.add_item(CustomSelect(
                custom_id=f"{500+i}_{author_id}_{urandom(4).hex()}",
                placeholder=placeholder,
                options=default_value + channels_options[(i * 24):min((i + 1) * 24, channels_count)]
            ))

        self.channel_id: int | None = None

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        return

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        assert values and values[0].isdecimal()
        self.channel_id = int(values[0])
        self.stop()

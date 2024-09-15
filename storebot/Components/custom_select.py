from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nextcord import Interaction

import logging

from nextcord import SelectOption
from nextcord.ui import StringSelect

if __debug__:
    from ..Components.view_base import ViewBase


class CustomSelect(StringSelect):
    def __init__(
        self,
        *,
        custom_id: str,
        placeholder: str,
        options: list[tuple[str, str]],
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        row: int | None = None
    ) -> None:
        opts = [SelectOption(label=r[0], value=r[1]) for r in options]
        if len(opts) > 25:
            logging.getLogger(__name__).error(f"Options must be between 1 and 25 in length: {opts}")
            opts = opts[:25]

        super().__init__(custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values, options=opts, disabled=disabled, row=row)
    
    async def callback(self, interaction: Interaction) -> None:
        assert isinstance(self.view, ViewBase)
        await self.view.click_select_menu(interaction, self.custom_id, self.values)


class CustomSelectWithOptions(StringSelect):
    def __init__(self, custom_id: str, placeholder: str, opts: list[SelectOption]) -> None:
        super().__init__(custom_id=custom_id, placeholder=placeholder, options=opts)

    async def callback(self, interaction: Interaction) -> None:
        assert isinstance(self.view, ViewBase)
        await self.view.click_select_menu(interaction, self.custom_id, self.values)

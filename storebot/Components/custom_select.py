from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nextcord import Interaction

import logging

from nextcord import SelectOption
from nextcord.ui import StringSelect

if __debug__:
    from ..Components.view_base import ViewBase


def _validate_options(opts: list[SelectOption]) -> list[SelectOption]:
    assert len(opts) <= 25
    if len(opts) > 25:
        logging.getLogger(__name__).error(f"Options must be between 1 and 25 in length: {opts}")
        opts = opts[:25]
    for opt in opts:
        assert len(opt.label) <= 100
        if len(opt.label) > 100:
            logging.getLogger(__name__).error(f"Option label must be less than or equal to 100 in length: {opt.label}")
            opt.label = f"{opt.label[:97]}..."
        assert len(opt.value) <= 100
        if len(opt.value) > 100:
            logging.getLogger(__name__).error(f"Option value must be less than or equal to 100 in length: {opt.label}")
            opt.value = f"{opt.value[:97]}..."
    return opts

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
        super().__init__(custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values, options=_validate_options(opts), disabled=disabled, row=row)
    
    async def callback(self, interaction: Interaction) -> None:
        assert isinstance(self.view, ViewBase)
        await self.view.click_select_menu(interaction, self.custom_id, self.values)


class CustomSelectWithOptions(StringSelect):
    def __init__(self, custom_id: str, placeholder: str, opts: list[SelectOption]) -> None:
        super().__init__(custom_id=custom_id, placeholder=placeholder, options=_validate_options(opts))

    async def callback(self, interaction: Interaction) -> None:
        assert isinstance(self.view, ViewBase)
        await self.view.click_select_menu(interaction, self.custom_id, self.values)

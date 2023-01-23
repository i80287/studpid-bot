from nextcord import (
    SelectOption,
    Interaction
)
from nextcord.ui import StringSelect

from typing import (
    Optional,
    List
)
from CustomComponents.view_base import ViewBase


class CustomSelect(StringSelect):
    def __init__(
        self,
        *,
        custom_id: str,
        placeholder: str,
        options: List[tuple[str, str]],
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        row: Optional[int] = None
    ) -> None:
        opts: List[SelectOption] = [SelectOption(label=r[0], value=r[1]) for r in options]
        super().__init__(custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values, options=opts, disabled=disabled, row=row)
    
    async def callback(self, interaction: Interaction) -> None:
        assert isinstance(self.view, ViewBase)
        await self.view.click_select_menu(interaction, self.custom_id, self.values)

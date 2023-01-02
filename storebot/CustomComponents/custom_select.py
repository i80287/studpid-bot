from nextcord import SelectOption, Interaction
from nextcord.ui import Select


class CustomSelect(Select):
    def __init__(self, custom_id: str, placeholder: str, opts: list) -> None:
        options: list[SelectOption] = [SelectOption(label=r[0], value=r[1]) for r in opts]
        super().__init__(custom_id=custom_id, placeholder=placeholder, options=options)
    
    async def callback(self, interaction: Interaction) -> None:
        await self.view.click_menu(interaction, self.custom_id, self.values)
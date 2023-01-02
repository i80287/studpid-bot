from nextcord import ButtonStyle, Interaction
from nextcord.ui import Button


class CustomButton(Button):
    def __init__(self, style: ButtonStyle, label: str, custom_id: str, disabled: bool = False, emoji = None, row: int | None = None) -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row)

    async def callback(self, interaction: Interaction) -> None:
        await super().view.click(interaction, self.custom_id)

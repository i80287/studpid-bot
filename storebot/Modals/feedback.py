from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Literal

    from nextcord import (
        Thread,
        PartialMessageable
    )
    from nextcord.abc import (
        GuildChannel,
        PrivateChannel
    )

    from ..storebot import StoreBot

from os import urandom

from nextcord import (
    Embed,
    TextInputStyle,
    TextChannel,
    Interaction
)
from nextcord.ui import Modal, TextInput


class FeedbackModal(Modal):
    feedback_text: dict[int, dict[int, str]] = {
        0 : {
            0 : "Feedback",
            1 : "What problems did you get while using the bot? What new would you want to see in bot's functional?",
            2 : "**`Thanks a lot for your feedback!\nIt was delivered to the bot's support server`**",
            3 : "**`We're so sorry, but during the creation of feedback something went wrong. You can get help on the support server`**"        
        },
        1 : {
            0 : "Отзыв",
            1 : "Какие проблемы возникли у Вас при использовании бота? Чтобы бы Вы хотели добавить?",
            2 : "**`Спасибо большое за Ваш отзыв! Он был доставлен на сервер поддержки`**",
            3 : "**`Извнините, при создании фидбэка что-то пошло не так. Вы можете получить помощь/оставить отзыв на сервере поддержки`**"
        }
    }

    def __init__(self, bot: StoreBot, lng: int, auth_id: int) -> None:
        super().__init__(title=self.feedback_text[lng][0], timeout=1200, custom_id=f"10100_{auth_id}_" + urandom(4).hex())
        self.bot: StoreBot = bot
        self.feedback = TextInput(
            label=self.feedback_text[lng][0],
            placeholder=self.feedback_text[lng][1],
            custom_id=f"10101_{auth_id}_" + urandom(4).hex(),
            required=True,
            style=TextInputStyle.paragraph,
            min_length=2
        )
        self.add_item(self.feedback)
        
    
    async def callback(self, interaction: Interaction) -> None:    
        assert interaction.guild is not None
        assert interaction.user is not None
        dsc: tuple[str, str, str] = (
            f"`Guild: {interaction.guild.name} - {interaction.guild_id}`",
            f"`Author: {interaction.user.name} - {interaction.user.id}`",
            feedback if (feedback := self.feedback.value) else ""
        )

        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        chnl: GuildChannel | Thread | PrivateChannel | PartialMessageable | None = \
            self.bot.get_channel(self.bot.bot_feedback_channel)
        if isinstance(chnl, TextChannel):
            try:
                await chnl.send(embed=Embed(description="\n".join(dsc)))
            except:
                await interaction.response.send_message(embed=Embed(description=self.feedback_text[lng][3]), content="https://discord.gg/4kxkPStDaG", ephemeral=True)
        else:
            await interaction.response.send_message(embed=Embed(description=self.feedback_text[lng][3]), content="https://discord.gg/4kxkPStDaG", ephemeral=True)
            return
        
        await interaction.response.send_message(embed=Embed(description=self.feedback_text[lng][2]), ephemeral=True)
        self.stop()

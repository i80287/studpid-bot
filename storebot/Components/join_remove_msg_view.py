from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from nextcord import (
        Interaction,
        Guild,
        Member
    )

    from ..storebot import StoreBot

from os import urandom

from nextcord import (
    ButtonStyle,
    Embed
)

from ..Tools.db_commands import (
    set_member_message_async,
    update_server_info_table_async
)
from ..Components.view_base import ViewBase
from ..Components import custom_views
from ..Components.custom_button import CustomButton
from ..Components.select_channel_view import SelectChannelView
from ..Modals.custom_modals import OneTextInputModal

class JoinRemoveMsgView(ViewBase):
    view_text: dict[int, dict[int, str]] = {
        0: {
            0: "Member join message",
            1: "Message sent when new member joins",
            2: "%s will be replaced with server name and %m will be replaced with member mention (without ping)",
            3: "Message supports formatting: %s will be replaced with server name and %m will be replaced with member mention (without ping)",
            4: "**`You updated message sent when new member joins`**",
            5: "Member left message",
            6: "Message sent when member leaves",
            7: "**`You updated message sent when member leaves`**",
            8: "**`Select channel`**",
            9: "```fix\nnot selected\n```",
            10: "**`You updated channel for messages`**"
        },
        1: {
            0: "Member join message",
            1: "Сообщение при присоединении участника",
            2: "%s will be replaced with server name and %m will be replaced with member mention (without ping)",
            3: "Message supports formatting: %s will be replaced with server name and %m will be replaced with member mention (without ping)",
            4: "**`Вы обновили сообщение, отправляемое при присоединении участника`**",
            5: "Сообщение при ливе участника",
            6: "Сообщение, отправляемое при ливе участника",
            7: "**`Вы обновили сообщение, отправляемое при ливе участника`**",
            8: "**`Выберите канал`**",
            9: "```fix\nне выбран\n```",
            10: "**`Вы обновили канал для отправки сообщений`**"
        }
    }

    def __init__(self, lng: int, author_id: int, bot: StoreBot) -> None:
        super().__init__(lng, author_id, 60)
        self.add_item(CustomButton(style=ButtonStyle.green, custom_id=f"68_{author_id}_" + urandom(4).hex(), emoji="➕"))
        self.add_item(CustomButton(style=ButtonStyle.green, custom_id=f"69_{author_id}_" + urandom(4).hex(), emoji="➖"))
        self.add_item(CustomButton(style=ButtonStyle.gray, custom_id=f"70_{author_id}_" + urandom(4).hex(), emoji="📗"))
        self.bot = bot

    async def update_join_message(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        local_text: dict[int, str] = self.view_text[self.lng]
        assert len(local_text) >= 10
        join_msg_modal: OneTextInputModal = OneTextInputModal(
            local_text[0],
            local_text[1],
            local_text[2],
            0,
            512,
            local_text[3]
        )

        await interaction.response.send_modal(join_msg_modal)
        await join_msg_modal.wait()

        if (text := join_msg_modal.value) is not None:
            await set_member_message_async(interaction.guild_id, text, True)

            message = interaction.message
            assert message is not None
            embeds = message.embeds
            assert len(embeds) == 4
            embeds[1] = Embed(description=custom_views.SettingsView.join_remove_text[self.lng][1] + text)
            try:
                await message.edit(embeds=embeds)
            except:
                pass

            await interaction.followup.send(embed=Embed(description=local_text[4]), ephemeral=True)

    async def update_remove_message(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        local_text: dict[int, str] = self.view_text[self.lng]
        assert len(local_text) >= 10
        remove_msg_modal: OneTextInputModal = OneTextInputModal(
            local_text[5],
            local_text[6],
            local_text[2],
            0,
            512,
            local_text[3]
        )

        await interaction.response.send_modal(remove_msg_modal)
        await remove_msg_modal.wait()

        if (text := remove_msg_modal.value) is not None:
            await set_member_message_async(interaction.guild_id, text, False)
            
            message = interaction.message
            assert message is not None
            embeds = message.embeds
            assert len(embeds) == 4
            embeds[2] = Embed(description=custom_views.SettingsView.join_remove_text[self.lng][2] + text)
            try:
                await message.edit(embeds=embeds)
            except:
                pass

            await interaction.followup.send(embed=Embed(description=local_text[7]), ephemeral=True)

    async def update_message_channel(self, interaction: Interaction) -> None:
        assert interaction.guild is not None

        guild: Guild = interaction.guild
        guild_self_bot: Member = guild.me
        channels_options: list[tuple[str, str]] = \
            [(c.name, str(c.id)) for c in guild.text_channels if c.permissions_for(guild_self_bot).send_messages]

        lng: int = self.lng
        select_channel_view: SelectChannelView = SelectChannelView(
            lng,
            self.author_id,
            30,
            channels_options
        )
        del channels_options

        local_text: dict[int, str] = self.view_text[lng]
        assert len(local_text) >= 10
        await interaction.response.send_message(
            embed=Embed(description=local_text[8]),
            view=select_channel_view
        )

        await select_channel_view.wait()
        if (channel_id := select_channel_view.channel_id) is None:
            return

        guild_id: int = guild.id
        await update_server_info_table_async(guild_id, 'memb_join_rem_chnl', channel_id)
        bot = self.bot
        if channel_id:
            async with bot.member_join_remove_lock:
                bot.join_remove_message_channels[guild_id] = channel_id
        else:
            async with bot.member_join_remove_lock:
                if guild_id in bot.join_remove_message_channels:
                    del bot.join_remove_message_channels[guild_id]
        
        message = interaction.message
        assert message is not None
        embeds = message.embeds
        assert len(embeds) == 4
        embeds[3] = Embed(description=custom_views.SettingsView.join_remove_text[lng][3] + (local_text[9] if not channel_id else f"<#{channel_id}>"))
        try:
            await message.edit(embeds=embeds)
        except:
            pass

        await interaction.followup.send(embed=Embed(description=local_text[10]), ephemeral=True)
        await self.try_delete(interaction, select_channel_view)

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert custom_id.startswith("68_") or custom_id.startswith("69_") or custom_id.startswith("70_")
        second_char: str = custom_id[1]
        if second_char == '8':
            await self.update_join_message(interaction)
        elif second_char == '9':
            await self.update_remove_message(interaction)
        else:
            await self.update_message_channel(interaction)

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return

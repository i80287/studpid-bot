from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Literal

    from nextcord import Interaction

    from ..storebot import StoreBot

from os import urandom
from contextlib import closing
from sqlite3 import connect

from nextcord import (
    ButtonStyle,
    Embed
)

from ..constants import DB_PATH
from ..CustomComponents.view_base import ViewBase
from ..CustomComponents.custom_select import CustomSelect
from ..CustomComponents.custom_button import CustomButton


class IgnoredChannelsView(ViewBase):
    ignored_channels_text: dict[int, dict[int, str]] = {
        0: {
            0: "Add channel",
            1: "Remove channel",
            2: "Select channel",
            3: "Not selected",
            4: "__**channel**__ - __**id**__",
            5: "**`No channels were selected`**",
            6: "**`You added channel `**<#{}>",
            7: "**`You removed channel `**<#{}>",
            8: "**`You hasn't selected the channel yet`**",
            9: "**`This channel is already added`**",
            10: "**`This channel hasn't been added yet`**",
            11: "**`Sorry, but you can't manage menu called by another user`**"
        },
        1: {
            0: "Добавить канал",
            1: "Убрать канал",
            2: "Выберите канал",
            3: "Не выбрано",
            4: "__**канал**__ - __**id**__",
            5: "**`Не выбрано ни одного канала`**",
            6: "**`Вы добавили канал `**<#{}>",
            7: "**`Вы убрали канал `**<#{}>",
            8: "**`Вы не выбрали канал`**",
            9: "**`Этот канал уже добавлен`**",
            10: "**`Этот канал ещё не был добавлен`**",
            11: "**`Извините, но Вы не можете управлять меню, которое вызвано другим пользователем`**"
        },
    }

    def __init__(self, timeout: int, lng: int, auth_id: int, chnls: list[tuple[str, str]], rem_dis: bool, g_id: int, bot: StoreBot, is_text: bool) -> None:
        super().__init__(lng=lng, author_id=auth_id, timeout=timeout)
        l: int = len(chnls)
        for i in range(min((l + 23) // 24, 4)):
            self.add_item(CustomSelect(
                custom_id=f"{1100+i}_{auth_id}_{urandom(4).hex()}",
                placeholder=self.ignored_channels_text[lng][2],
                options=[(self.ignored_channels_text[lng][3], "0")] + chnls[(i * 24):min((i + 1) * 24, l)]
            ))
        self.add_item(CustomButton(
            style=ButtonStyle.green,
            label=self.ignored_channels_text[lng][0],
            emoji="<:add01:999663315804500078>",
            custom_id=f"25_{auth_id}_{urandom(4).hex()}"
        ))
        self.add_item(CustomButton(
            style=ButtonStyle.red,
            label=self.ignored_channels_text[lng][1],
            emoji="<:remove01:999663428689997844>",
            custom_id=f"26_{auth_id}_{urandom(4).hex()}",
            disabled=rem_dis
        ))
        self.chnl: int | None = None
        self.g_id: int = g_id
        self.auth_id: int = auth_id
        self.bot: StoreBot = bot
        self.is_text: bool = is_text

    async def add_chnl(self, interaction: Interaction, lng: int, channel_id: int) -> None:
        guild_id: int = self.g_id
        if self.is_text:
            with closing(connect(DB_PATH.format(guild_id))) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("INSERT OR IGNORE INTO ignored_channels (chnl_id, is_text, is_voice) VALUES(?, 1, 0)", (channel_id,))
                    base.commit()
            async with self.bot.text_lock:
                self.bot.ignored_text_channels[guild_id].add(channel_id)
        else:
            with closing(connect(DB_PATH.format(guild_id))) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("INSERT OR IGNORE INTO ignored_channels (chnl_id, is_text, is_voice) VALUES(?, 0, 1)", (channel_id,))
                    base.commit()
            async with self.bot.voice_lock:
                self.bot.ignored_voice_channels[guild_id].add(channel_id)

        assert interaction.message is not None
        emb: Embed = interaction.message.embeds[0]
        assert emb.description is not None
        dsc: list[str] = emb.description.split("\n")
        if len(dsc) == 1:
            emb.description = self.ignored_channels_text[lng][4] + f"\n<#{channel_id}>**` - {channel_id}`**"
            self.children[-1].disabled = False # type: ignore
            try:
                await interaction.message.edit(embed=emb, view=self)
            except:
                pass
        else:
            dsc.append(f"<#{channel_id}>**` - {channel_id}`**")
            emb.description = '\n'.join(dsc)
            try:
                await interaction.message.edit(embed=emb)
            except:
                pass

        await interaction.response.send_message(embed=Embed(description=self.ignored_channels_text[lng][6].format(channel_id)), ephemeral=True)
        self.chnl = None
    
    async def rem_chnl(self, interaction: Interaction, lng: int, channel_id: int) -> None:
        guild_id: int = self.g_id
        with closing(connect(DB_PATH.format(guild_id))) as base:
            with closing(base.cursor()) as cur:
                cur.execute("DELETE FROM ignored_channels WHERE chnl_id = ?", (channel_id,))
                base.commit()
        if self.is_text:
            async with self.bot.text_lock:
                try:
                    self.bot.ignored_text_channels[guild_id].remove(channel_id)
                except KeyError:
                    pass
        else:
            async with self.bot.voice_lock:
                try:
                    self.bot.ignored_voice_channels[guild_id].remove(channel_id)
                except KeyError:
                    pass
        assert interaction.message is not None
        emb: Embed = interaction.message.embeds[0]
        assert emb.description is not None
        dsc: list[str] = emb.description.split('\n')
        if len(dsc) <= 2:
            self.children[-1].disabled = True # type: ignore
            emb.description = self.ignored_channels_text[lng][5]
            await interaction.message.edit(embed=emb, view=self)
        else:
            s_c: str = str(channel_id)
            for i in range(len(dsc)):
                if s_c in dsc[i]:
                    del dsc[i]
                    break
            emb.description = '\n'.join(dsc)
            await interaction.message.edit(embed=emb)
        
        await interaction.response.send_message(embed=Embed(description=self.ignored_channels_text[lng][7].format(channel_id)), ephemeral=True)
        self.chnl = None

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert interaction.locale is not None
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        channel_id: int | None = self.chnl
        if not channel_id:
            await interaction.response.send_message(embed=Embed(description=self.ignored_channels_text[lng][8]), ephemeral=True)
            return
        
        if self.is_text:
            async with self.bot.text_lock:
                guild_ignored_channels: set[int] = self.bot.ignored_text_channels[self.g_id]
        else:
            async with self.bot.voice_lock:
                guild_ignored_channels: set[int] = self.bot.ignored_voice_channels[self.g_id]
        
        int_custom_id: int = int(custom_id[:2])
        if int_custom_id == 25:
            if channel_id in guild_ignored_channels:
                await interaction.response.send_message(embed=Embed(description=self.ignored_channels_text[lng][9]), ephemeral=True)
                return
            await self.add_chnl(interaction=interaction, lng=lng, channel_id=channel_id)
        elif int_custom_id == 26:
            if channel_id not in guild_ignored_channels:
                await interaction.response.send_message(embed=Embed(description=self.ignored_channels_text[lng][10]), ephemeral=True)
                return
            await self.rem_chnl(interaction=interaction, lng=lng, channel_id=channel_id)           

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        if custom_id.startswith("11"):
            self.chnl = int(values[0])

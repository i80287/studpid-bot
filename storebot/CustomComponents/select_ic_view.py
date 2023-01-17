from typing import Literal
from contextlib import closing
from sqlite3 import connect
from os import urandom

from nextcord import ButtonStyle, Interaction, Embed
from nextcord.ui import View

from Variables.vars import CWD_PATH
from CustomComponents.custom_button import CustomButton
from CustomComponents.ignored_channels_view import IgnoredChannelsView
from storebot import StoreBot


class SelectICView(View):
    select_ignored_channels_text: dict[int, dict[int, str]] = {
        0: {
            0: "> Press <:ignored_text:1064976269038583808> to see and manage `text channels` where members can't get money and xp\n\n\
                > Press :mute: to see and manage `voice channels` where members can't get money and xp",
        },
        1: {
            0: "> Нажмите <:ignored_text:1064976269038583808> для просмотра и управления `текстовыми каналами`, в которых пользователи не могут получать доход и опыт\n\n\
                > Нажмите :mute: для просмотра и управления `голосовыми каналами`, в которых пользователи не могут получать доход и опыт",
        },
    }

    def __init__(self, timeout: int, lng: int, auth_id: int, g_id: int, bot: StoreBot) -> None:
        super().__init__(timeout=timeout)
        
        self.add_item(CustomButton(
            style=ButtonStyle.green,
            label="",
            emoji="<:ignored_text:1064976269038583808>",
            custom_id=f"55_{auth_id}_{urandom(4).hex()}"
        ))
        self.add_item(CustomButton(
            style=ButtonStyle.green,
            label="",
            emoji="🔇",
            custom_id=f"56_{auth_id}_{urandom(4).hex()}",
        ))
        self.g_id: int = g_id
        self.auth_id: int = auth_id
        self.bot: StoreBot = bot
        self.lng: int = lng

    async def click(self, interaction: Interaction, c_id: str) -> None:
        guild_id: int = self.g_id
        with closing(connect(f"{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                db_text_chnls: list[tuple[int]] = cur.execute("SELECT chnl_id FROM ignored_channels WHERE is_text = 1").fetchall()
                db_voice_chnls: list[tuple[int]] = cur.execute("SELECT chnl_id FROM ignored_channels WHERE is_voice = 1").fetchall()
        
        guild_text_ignored_channels_ids: set[int] = {tup[0] for tup in db_text_chnls}
        guild_voice_ignored_channels_ids: set[int] = {tup[0] for tup in db_voice_chnls}
        del db_text_chnls
        del db_voice_chnls
        async with self.bot.lock:
            self.bot.ignored_text_channels[guild_id] = guild_text_ignored_channels_ids
            self.bot.ignored_voice_channels[guild_id] = guild_voice_ignored_channels_ids

        lng: int = self.lng
        match int(c_id[:2]):
            case 55:
                if guild_text_ignored_channels_ids:
                    dsc: list[str] = [IgnoredChannelsView.ignored_channels_text[lng][4]] + \
                        [f"<#{chnl_id}>**` - {chnl_id}`**" for chnl_id in guild_text_ignored_channels_ids]
                    rd: bool = False
                else:
                    rd: bool = True
                    dsc = [IgnoredChannelsView.ignored_channels_text[lng][5]]
                
                guild_text_channels: list[tuple[str, str]] = [(c.name, str(c.id)) for c in interaction.guild.text_channels]
                emb: Embed = Embed(description='\n'.join(dsc))     
                text_ic_v: IgnoredChannelsView = IgnoredChannelsView(
                    timeout=80,
                    lng=lng,
                    auth_id=self.auth_id,
                    chnls=guild_text_channels,
                    rem_dis=rd,
                    g_id=guild_id,
                    bot=self.bot,
                    is_text=True
                )

                await interaction.response.send_message(embed=emb, view=text_ic_v)
                await text_ic_v.wait()
                try:
                    await interaction.delete_original_message()
                except:
                    return
            case 56:
                if guild_voice_ignored_channels_ids:
                    dsc: list[str] = [IgnoredChannelsView.ignored_channels_text[lng][4]] + \
                        [f"<#{chnl_id}>**` - {chnl_id}`**" for chnl_id in guild_voice_ignored_channels_ids]
                    rd: bool = False
                else:
                    rd: bool = True
                    dsc = [IgnoredChannelsView.ignored_channels_text[lng][5]]
                
                guild_voice_channels: list[tuple[str, str]] = [(c.name, str(c.id)) for c in interaction.guild.voice_channels]
                emb: Embed = Embed(description='\n'.join(dsc))     
                voice_ic_v: IgnoredChannelsView = IgnoredChannelsView(
                    timeout=80,
                    lng=lng,
                    auth_id=self.auth_id,
                    chnls=guild_voice_channels,
                    rem_dis=rd,
                    g_id=guild_id,
                    bot=self.bot,
                    is_text=False
                )

                await interaction.response.send_message(embed=emb, view=voice_ic_v)
                await voice_ic_v.wait()
                try:
                    await interaction.delete_original_message()
                except:
                    return

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
            await interaction.response.send_message(embed=Embed(description=IgnoredChannelsView.ignored_channels_text[lng][11]), ephemeral=True)
            return False
        return True

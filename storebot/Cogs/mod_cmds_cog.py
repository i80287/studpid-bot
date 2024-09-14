from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Literal

    from ..storebot import StoreBot

from copy import copy

from nextcord import (
    Embed,
    Locale,
    slash_command,
    Interaction
)
from nextcord.ext import application_checks
from nextcord.ext.commands import Cog
from nextcord import Member

from ..Tools.db_commands import get_mod_roles_async
from ..Components.view_base import ViewBase
from ..Components.custom_views import SettingsView


class ModCommandsCog(Cog):
    settings_text: dict[int, dict[int, str]] = {
        0 : {
            0 : "Choose section",
            1: '\n'.join((
                "⚙️ general settings",
                "<:moder:1000090629897998336> manage moders' roles",
                "<:user:1002245779089535006> manage members",
                "💰 economy",
                "📈 ranking",
                "🎰 slots",
                ":no_entry_sign: manage ignored channels",
                "👋 manage message sent on member join/left"
                # "📊 polls",
            )),
        },
        1 : {
            0 : "Выберите раздел",
            1 : '\n'.join((
                "⚙️ основные настройки",
                "<:moder:1000090629897998336> настройка ролей модераторов",
                "<:user:1002245779089535006> управление пользователями",
                "💰 экономика",
                "📈 ранговая система",
                "🎰 слоты",
                ":no_entry_sign: управление игнорируемыми каналами",
                "👋 управление сообщением, отправляемым при присоединении/ливе участника"
                # "📊 поллы",
            )),
        }
    }

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot

    async def mod_check(interaction: Interaction) -> bool: # type: ignore # Wait for fix in the framework?
        assert interaction.guild_id is not None
        member = interaction.user
        if not isinstance(member, Member):
            return False

        if member.guild_permissions.administrator or member.guild_permissions.manage_guild:
            return True

        if (mod_roles_ids_list := await get_mod_roles_async(interaction.guild_id)):
            return not {role_id_tuple[0] for role_id_tuple in mod_roles_ids_list}.isdisjoint(copy(member._roles))

        return False

    @slash_command(
        name="settings",
        description="Show menu to see and manage bot's settings",
        description_localizations={
            Locale.ru : "Вызывает меню просмотра и управления настройками бота"
        },
        dm_permission=False
    )
    @application_checks.check(mod_check)
    async def settings(self, interaction: Interaction) -> None:
        assert interaction.locale is not None
        assert interaction.user is not None
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        st_view: SettingsView = SettingsView(
            lng=lng,
            author_id=interaction.user.id,
            timeout=120,
            bot=self.bot
        )
        local_text = self.settings_text[lng]
        assert len(local_text) == 2
        emb: Embed = Embed(title=local_text[0], description=local_text[1])
        await interaction.response.send_message(embed=emb, view=st_view)

        await st_view.wait()
        await ViewBase.try_delete(interaction, st_view)

def setup(bot: StoreBot) -> None:
    bot.add_cog(ModCommandsCog(bot))

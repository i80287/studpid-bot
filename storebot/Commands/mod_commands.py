from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Literal

    from ..storebot import StoreBot

from nextcord import (
    Embed,
    Locale,
    slash_command,
    Interaction
)
from nextcord.ext import application_checks
from nextcord.ext.commands import Cog
if __debug__:
    from nextcord import Member

from ..Tools.db_commands import get_mod_roles_async
from ..CustomComponents.custom_views import SettingsView
if __debug__:
    from ..CustomComponents.custom_button import CustomButton
    from ..CustomComponents.custom_select import CustomSelect

class ModCommandsCog(Cog):
    settings_text: dict[int, dict[int, str | list[str]]] = {
        0 : {
            0 : "Choose section",
            1: [
                "⚙️ general settings",
                "<:moder:1000090629897998336> manage moders' roles",
                "<:user:1002245779089535006> manage members",
                "💰 economy",
                "📈 ranking",
                "🎰 slots",
                ":no_entry_sign: manage ignored channels",
                "📊 polls",
            ],
        },
        1 : {
            0 : "Выберите раздел",
            1 : [
                "⚙️ основные настройки",
                "<:moder:1000090629897998336> настройка ролей модераторов",
                "<:user:1002245779089535006> управление пользователями",
                "💰 экономика",
                "📈 ранговая система",
                "🎰 слоты",
                ":no_entry_sign: управление игнорируемыми каналами",
                "📊 поллы",
            ],
        }
    }

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot

    async def mod_check(interaction: Interaction) -> bool: # type: ignore # Wait for fix in the framework?
        assert isinstance(interaction.user, Member)
        assert interaction.guild_id is not None
        member: Member = interaction.user
        if member.guild_permissions.administrator or member.guild_permissions.manage_guild:
            return True

        mod_roles_ids_list: list[tuple[int]] | list = await get_mod_roles_async(interaction.guild_id)
        if mod_roles_ids_list:
            return not {role_id_tuple[0] for role_id_tuple in mod_roles_ids_list}.isdisjoint(member._roles.__copy__())
            # mod_roles_ids_set: set[int] = {x[0] for x in mod_roles_ids_list}
            # del mod_roles_ids_list
            # return not mod_roles_ids_set.isdisjoint(member._roles.__copy__())

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
        emb: Embed = Embed(title=self.settings_text[lng][0], description="\n".join(self.settings_text[lng][1]))
        await interaction.response.send_message(embed=emb, view=st_view)

        await st_view.wait()
        for child_component in st_view.children:
            assert isinstance(child_component, (CustomButton, CustomSelect))
            child_component.disabled = True
        try:
            await interaction.edit_original_message(view=st_view)
        except:
            return
    

def setup(bot: StoreBot) -> None:
    bot.add_cog(ModCommandsCog(bot))

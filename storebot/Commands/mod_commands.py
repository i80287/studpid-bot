from typing import Literal
from sqlite3 import connect
from contextlib import closing

from nextcord import Embed, Locale, Interaction, User, Member, slash_command
from nextcord.ui import Button, StringSelect
from nextcord.ext import application_checks
from nextcord.ext.commands import Cog

from storebot import StoreBot
from Variables.vars import CWD_PATH
from CustomComponents.custom_views import SettingsView


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
                "📊 поллы",
            ],
        }
    }

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot

    @staticmethod
    def mod_check(interaction: Interaction) -> bool:
        member: User | Member | None = interaction.user
        if not member or not isinstance(member, Member):
            return False
        if member.guild_permissions.administrator or member.guild_permissions.manage_guild:
            return True

        with closing(connect(f'{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                mod_roles_ids_list: list[tuple[int]] | list = cur.execute("SELECT * FROM mod_roles").fetchall()
                if mod_roles_ids_list:
                    mod_roles_ids_set: set[int] = {x[0] for x in mod_roles_ids_list}
                    del mod_roles_ids_list
                    return any(role.id in mod_roles_ids_set for role in member.roles)
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
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        st_view: SettingsView = SettingsView(t_out=120, auth_id=interaction.user.id, bot=self.bot)
        emb: Embed = Embed(title=self.settings_text[lng][0], description="\n".join(self.settings_text[lng][1]))
        await interaction.response.send_message(embed=emb, view=st_view)

        await st_view.wait()
        for c in st_view.children:
            if isinstance(c, Button) or isinstance(c, StringSelect):
                c.disabled = True
        await interaction.edit_original_message(view=st_view)
    

def setup(bot: StoreBot) -> None:
    bot.add_cog(ModCommandsCog(bot))

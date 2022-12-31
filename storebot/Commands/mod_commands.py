from sqlite3 import connect
from contextlib import closing

from nextcord import Embed, Locale, Interaction, slash_command
from nextcord.ext import application_checks
from nextcord.ext.commands import Cog, Bot

from Variables.vars import path_to
from CustomComponents.custom_views import SettingsView


class ModCommandsCog(Cog):
    settings_text = {
        0 : {
            0 : "Choose section",
            1: [
                "⚙️ general settings",
                "<:moder:1000090629897998336> manage moders' roles",
                "<:user:1002245779089535006> manage members",
                "💰 economy",
                "📈 ranking",
                "📊 polls"
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
                "📊 поллы"
            ],
        }
    }

    def __init__(self, bot: Bot):
        self.bot = bot

    def mod_check(interaction: Interaction) -> bool:
        u = interaction.user
        if u.guild_permissions.administrator or u.guild_permissions.manage_guild:
            return True

        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                m_rls = cur.execute("SELECT * FROM mod_roles").fetchall()
                if m_rls:
                    m_rls = {x[0] for x in m_rls}
                    return any(role.id in m_rls for role in u.roles)
                return False

    async def settings(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        st_view = SettingsView(t_out=120, auth_id=interaction.user.id, bot=self.bot)
        emb = Embed(title=self.settings_text[lng][0], description="\n".join(self.settings_text[lng][1]))
        await interaction.response.send_message(embed=emb, view=st_view)

        await st_view.wait()
        for c in st_view.children:
            c.disabled = True
        await interaction.edit_original_message(view=st_view)


    @slash_command(
        name="settings",
        description="Show menu to see and manage bot's settings",
        description_localizations={
            Locale.ru : "Вызывает меню просмотра и управления настройками бота"
        }
    )
    @application_checks.check(mod_check)
    async def settings_e(self, interaction: Interaction):
        await self.settings(interaction=interaction)
    

def setup(bot: Bot):
    bot.add_cog(ModCommandsCog(bot))

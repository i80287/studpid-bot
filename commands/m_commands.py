from os import path, mkdir
from asyncio import sleep, TimeoutError
from contextlib import closing
from sqlite3 import connect
from datetime import datetime, timedelta

from colorama import Fore
from nextcord import Embed, Colour, Guild, Role, Member, TextChannel, Locale, Interaction, slash_command, SlashOption, ButtonStyle
from nextcord.ui import View, Button, button
from nextcord.ext import commands
from config import path_to, bot_guilds_e, bot_guilds_r, bot_guilds, prefix, in_row

mod_roles_text = {
    0 : {
        0 : "Current mod roles",
        1 : "No roles selected",
        2 : "Role - id",
        3 : "Add role",
        4 : "Remove role",
        5 : "Adding role",
        6 : "Write an id of the role or ping it"
    },
    1 : {
        0 : "Текущие мод роли",
        1 : "Не выбрано ни одной роли",
        2 : "Роль - id",
        3 : "Добавить роль",
        4 : "Убрать роль",
        5 : "Добавление роли",
        6 : "Напишите id роли или пинганите её"
    }
}

class c_button(Button):
    def __init__(self, style: ButtonStyle, label: str, custom_id: str, disabled: bool = False, emoji = None, row: int = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row)

    async def callback(self, interaction: Interaction):
       await super().view.click(interaction, self.custom_id)


class mod_roles_view(View):
    def __init__(self, t_out: int, m_rls: list, lng: int):
        super().__init__(timeout=t_out)
        self.m_rls = m_rls
        self.add_item(c_button(style=ButtonStyle.green, label=mod_roles_text[lng][3], emoji="<:add01:999663315804500078>", custom_id="0"))
        self.add_item(c_button(style=ButtonStyle.red, label=mod_roles_text[lng][4], emoji="<:remove01:999663428689997844>", custom_id="1"))
    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        if c_id == "0":
            m = interaction.message
            m_ans = await interaction.response.send_message(embed=Embed(title=mod_roles_text[lng][5], description=mod_roles_text[lng][6]))
            flag = 1
            while flag:
                try:
                    print(interaction.client.user.name)
                except TimeoutError:
                    await m_ans.delete()
                    flag = 0




class m_cmds(commands.Cog):
    def __init__(self, bot: commands.Bot, prefix, in_row):
        self.bot = bot
        global bot_guilds_e
        global bot_guilds_r


    def mod_check(ctx: commands.Context):
        
        if any(role.permissions.administrator or role.permissions.manage_guild for role in ctx.author.roles) or ctx.guild.owner == ctx.author:
            return True

        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                m_rls = cur.execute("SELECT * FROM mod_roles").fetchall()
                if m_rls != None and m_rls != []:
                    m_rls = {x[0] for x in m_rls}
                    return any(role.id in m_rls for role in ctx.author.roles)
                return False

    async def mod_roles(self, interaction: Interaction):
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild.id}/{interaction.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                m_rls = cur.execute("SELECT * FROM mod_roles").fetchall()
        emb = Embed(title=mod_roles_text[lng][0])
        if len(m_rls) == 0:
            emb.description=mod_roles_text[lng][1]
            m_rls = set()
        else:
            m_rls = {x[0] for x in m_rls}
            dsc = [mod_roles_text[lng][2]]
            for i in m_rls:
                dsc.append(f"<@{i}> - {i}")
            emb.description = "\n".join(dsc)

        m_rls_v = mod_roles_view(t_out=60, m_rls=m_rls, lng=lng)
        m = await interaction.response.send_message(embed=emb, view=m_rls_v)
        if await m_rls_v.wait():
            for c in m_rls_v.children:
                c.disabled = True
            await m.edit(view=m_rls_v)
        
    @slash_command(
        name="mod_roles",
        description="Show menu to manage mod roles",
        description_localizations={
            Locale.ru : "Вызывает меню управления ролями модераторов"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    async def mod_roles_e(self, interaction: Interaction):
        await self.mod_roles(interaction=interaction)
    
    
    @slash_command(
        name="mod_roles",
        description="Вызывает меню управления ролями модераторов",
        description_localizations={
            Locale.en_GB: "Show menu to manage mod roles",
            Locale.en_US: "Show menu to manage mod roles"
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    async def mod_roles_r(self, interaction: Interaction):
        await self.mod_roles(interaction=interaction)

def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(m_cmds(bot, **kwargs))
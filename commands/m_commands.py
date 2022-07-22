from os import path, mkdir
from asyncio import sleep, TimeoutError
from contextlib import closing
from sqlite3 import connect
from datetime import datetime, timedelta

from nextcord import Embed, Colour, Guild, Role, Member, TextChannel, Locale, Interaction, slash_command, SlashOption, ButtonStyle, Message
from nextcord.ui import View, Button, button
from nextcord.ext import commands, application_checks
from config import path_to, bot_guilds_e, bot_guilds_r, bot_guilds, prefix, in_row

mod_roles_text = {
    0 : {
        0 : "Current mod roles",
        1 : "No roles selected",
        2 : "role - id",
        3 : "Add role",
        4 : "Remove role",
        5 : "Add role",
        6 : "Write an id of the role or ping it",
        7 : "This role already in the list",
        8 : "Role {} added to the list",
        9 : "This role not in the list",
        10 : "Role {} removed from the list",
        11 : "**`Sorry, but you can't manage menu called by another user`**"
    },
    1 : {
        0 : "Текущие мод роли",
        1 : "Не выбрано ни одной роли",
        2 : "роль - id",
        3 : "Добавить роль",
        4 : "Убрать роль",
        5 : "Добавление роли",
        6 : "Напишите id роли или пинганите её",
        7 : "Эта роль уже в списке",
        8 : "Роль {} добавлена в список",
        9 : "Этой роли нет в списке",
        10 : "Роль {} убрана из списока",
        11 : "**`Извините, но Вы не можете управлять меню, которое вызвано другим пользователем`**"
    }
}

settings_text = {
    0 : [
        "Choose section",
        "⚙️ general settings",
        "💰 economy",
        "<:moder:1000090629897998336> manage moders' roles",
        "📈 ranking",
        "📊 polls",
    ],
    1 : [
        "Выберите раздел",
        "⚙️ основные настройки",
        "<:moder:1000090629897998336> настройка ролей модераторов",
        "💰 экономика",
        "📈 ранговая система",
        "📊 поллы",
    ]
}

gen_settings_text = {
    0 : {
        0 : "🧾server language: {}",
        1 : "⏱time zone: UTC{}",
        2 : "tap 🧾 to change language",
        3 : "tap ⚙️ to see pre-named time zones",
        4 : "tap ⏱ to change time zone",
        
    },
    1 : {
        0 : "🧾язык сервера: {}",
        1 : "⏱часовой пояс: UTC{}",
        2 : "нажмите 🧾, чтобы изменить язык",
        3 : "нажмите ⚙️, чтобы увидеть именные часовые пояса",
        4 : "нажмите ⏱, чтобы изменить часовой пояс",
    }
}

languages = {
    0 : {
        0 : "English",
        1 : "Russian"
    },
    1 : {
        0 : "английский",
        1 : "русский"
    }
}

#with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
#            with closing(base.cursor()) as cur:
#                 sets = cur.execute("SELECT * FROM server_info")
class c_button(Button):
    def __init__(self, style: ButtonStyle, label: str, custom_id: str, disabled: bool = False, emoji = None, row: int = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row)

    async def callback(self, interaction: Interaction):
        await super().view.click(interaction, self.custom_id)


class gen_settings_view(View):
    def __init__(self, t_out: int, auth_id: int):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.add_item(c_button(style=ButtonStyle.green, label=None, custom_id="5", emoji="🧾"))
        self.add_item(c_button(style=ButtonStyle.red, label=None, custom_id="6", emoji="⚙️"))
        self.add_item(c_button(style=ButtonStyle.blurple, label=None, custom_id="7", emoji="⏱"))
    
    async def click(self, interaction: Interaction, c_id: str):
        print(c_id)


class mod_roles_view(View):
    def __init__(self, t_out: int, m_rls: set, lng: int, auth_id: int, rem_dis: bool):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.m_rls = m_rls
        self.add_item(c_button(style=ButtonStyle.green, label=mod_roles_text[lng][3], emoji="<:add01:999663315804500078>", custom_id="8"))
        self.add_item(c_button(style=ButtonStyle.red, label=mod_roles_text[lng][4], emoji="<:remove01:999663428689997844>", custom_id="9", disabled=rem_dis))
    

    async def add_role(self, rl: Role, interaction: Interaction, lng: int, m: Message):
        if rl.id in self.m_rls:
            m_ra = await interaction.channel.send(embed=Embed(description=mod_roles_text[lng][7]))
        else:
            with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("INSERT OR IGNORE INTO mod_roles(role_id) VALUES(?)", (rl.id,))
                    base.commit()
            self.m_rls.add(rl.id)
            emb = m.embeds[0]
            dsc = emb.description.split("\n")

            if len(self.m_rls) == 1:
                for j in 0, 1:
                    if mod_roles_text[j][1] in dsc:
                        dsc.remove(mod_roles_text[j][1])
                dsc.append(mod_roles_text[lng][2])

            dsc.append(f"<@&{rl.id}> - {rl.id}")
            emb.description = "\n".join(dsc)
            await m.edit(embed=emb)
            m_ra = await interaction.channel.send(embed=Embed(description=mod_roles_text[lng][8].format(rl.mention)))
        return m_ra


    async def rem_role(self, rl: Role, interaction: Interaction, lng: int, m: Message):
        if not rl.id in self.m_rls:
            m_ra = await interaction.channel.send(embed=Embed(description=mod_roles_text[lng][9]))
        else:
            with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("DELETE FROM mod_roles WHERE role_id = ?", (rl.id,))
                    base.commit()
            self.m_rls.remove(rl.id)
            emb = m.embeds[0]

            if len(self.m_rls) == 0:
                dsc = [mod_roles_text[lng][1]]
            else:
                dsc = emb.description.split("\n")
                dsc.remove(f"<@&{rl.id}> - {rl.id}")

            emb.description = "\n".join(dsc)
            await m.edit(embed=emb)
            m_ra = await interaction.channel.send(embed=Embed(description=mod_roles_text[lng][10].format(rl.mention)))
        return m_ra


    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        m = interaction.message
        if c_id == "0":
            m_a = await interaction.response.send_message(embed=Embed(title=mod_roles_text[lng][5], description=mod_roles_text[lng][6]))
        else:
            m_a = await interaction.response.send_message(embed=Embed(title=mod_roles_text[lng][4], description=mod_roles_text[lng][6]))
        flag = True
        while flag:
            try:
                m_ans = await interaction.client.wait_for(event="message", check=lambda m: m.author.id == interaction.user.id and m.channel.id == interaction.channel_id, timeout=50)
            except TimeoutError:
                await m_a.delete()
                flag = False
            else:
                ans = m_ans.content
                if ans.startswith("<@&"):
                    ans = ans[3:-1]
                if ans.isdigit():
                    ans = int(ans)
                    rl = interaction.guild.get_role(ans)
                    if rl:
                        if c_id == "0":
                            m_ra = await self.add_role(rl=rl, interaction=interaction, lng=lng, m=m)
                            if len(self.m_rls) == 1:
                                for c in self.children:
                                    if c.custom_id == "8":
                                        c.disabled = False
                                await m.edit(view=self)
                        else:
                            m_ra = await self.rem_role(rl=rl, interaction=interaction, lng=lng, m=m)
                            if len(self.m_rls) == 0:
                                for c in self.children:
                                    if c.custom_id == "9":
                                        c.disabled = True
                                await m.edit(view=self)
                        await m_ra.delete(delay=5)
                        await m_a.delete()
                        try: await m_ans.delete()
                        except: pass
                        flag = False
                                
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class settings_view(View):
    
    def __init__(self, t_out: int, lng: int, auth_id: int):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.add_item(c_button(style=ButtonStyle.red, label=None, custom_id="0", emoji="⚙️"))
        self.add_item(c_button(style=ButtonStyle.red, label=None, custom_id="1", emoji="<:moder:1000090629897998336>"))
        self.add_item(c_button(style=ButtonStyle.green, label=None, custom_id="2", emoji="💰"))
        self.add_item(c_button(style=ButtonStyle.blurple, label=None, custom_id="3", emoji="📈"))
        self.add_item(c_button(style=ButtonStyle.blurple, label=None, custom_id="4", emoji="📊"))

    async def click(self, interaction: Interaction, custom_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        print(custom_id)
        if custom_id == "0":
            with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                with closing(base.cursor()) as cur:
                    s_lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                    tz = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]
            emb = Embed()
            dsc = [gen_settings_text[lng][0].format(languages[lng][s_lng])]
            if tz >= 0:
                dsc.append(gen_settings_text[lng][1].format(f"+{tz}"))
            else:
                dsc.append(gen_settings_text[lng][1].format(f"-{tz}"))
            for i in 2, 3, 4:
                dsc.append(gen_settings_text[lng][i])
            emb.description="\n".join(dsc)
            gen_view = gen_settings_view(t_out=50, auth_id=self.auth_id)
            m = await interaction.response.send_message(embed=emb, view=gen_view)
            if await gen_view.wait():
                gen_view.stop()
                await m.delete()
        elif custom_id == "1":
            with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                with closing(base.cursor()) as cur:
                    m_rls = cur.execute("SELECT * FROM mod_roles").fetchall()
            emb = Embed(title=mod_roles_text[lng][0])
            if len(m_rls) == 0:
                emb.description=mod_roles_text[lng][1]
                m_rls = set()
                rem_dis = True
            else:
                m_rls = {x[0] for x in m_rls}
                dsc = [mod_roles_text[lng][2]]
                for i in m_rls:
                    dsc.append(f"<@&{i}> - {i}")
                emb.description = "\n".join(dsc)
                rem_dis = False

            m_rls_v = mod_roles_view(t_out=50, m_rls=m_rls, lng=lng, auth_id=self.auth_id, rem_dis=rem_dis)
            m = await interaction.response.send_message(embed=emb, view=m_rls_v)
            if await m_rls_v.wait():
                m_rls_v.stop()
                await m.delete()
    

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True



class m_cmds(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        global bot_guilds_e
        global bot_guilds_r


    def mod_check(interaction: Interaction):
        u = interaction.user
        if u.guild_permissions.administrator or u.guild_permissions.manage_guild:
            return True

        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                m_rls = cur.execute("SELECT * FROM mod_roles").fetchall()
                if m_rls != None and m_rls != []:
                    m_rls = {x[0] for x in m_rls}
                    return any(role.id in m_rls for role in u.roles)
                return False


    async def mod_roles(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                m_rls = cur.execute("SELECT * FROM mod_roles").fetchall()
        emb = Embed(title=mod_roles_text[lng][0])
        if len(m_rls) == 0:
            emb.description=mod_roles_text[lng][1]
            m_rls = set()
            rem_dis = True
        else:
            m_rls = {x[0] for x in m_rls}
            dsc = [mod_roles_text[lng][2]]
            for i in m_rls:
                dsc.append(f"<@&{i}> - {i}")
            emb.description = "\n".join(dsc)
            rem_dis = False

        m_rls_v = mod_roles_view(t_out=60, m_rls=m_rls, lng=lng, auth_id=interaction.user.id, rem_dis=rem_dis)
        m = await interaction.response.send_message(embed=emb, view=m_rls_v)
        if await m_rls_v.wait():
            for c in m_rls_v.children:
                c.disabled = True
            await m.edit(view=m_rls_v)
        m_rls_v.stop()
    

    async def settings(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        dsc = []
        for i in settings_text[lng][1:]:
            dsc.append(i)
        st_view = settings_view(t_out=80, lng=lng, auth_id=interaction.user.id)
        emb = Embed(title=settings_text[lng][0], description="\n".join(dsc))
        m = await interaction.response.send_message(embed=emb, view=st_view)
        if await st_view.wait():
            for c in st_view.children:
                c.disabled = True
            await m.edit(view=st_view)
        st_view.stop()
        

    @slash_command(
        name="mod_roles",
        description="Show menu to manage mod roles",
        description_localizations={
            Locale.ru : "Вызывает меню управления ролями модераторов"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    @application_checks.check(mod_check)
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
    @application_checks.check(mod_check)
    async def mod_roles_r(self, interaction: Interaction):
        await self.mod_roles(interaction=interaction)

    @slash_command(
        name="settings",
        description="Show menu to see and manage bot's settings",
        description_localizations={
            Locale.ru : "Вызывает меню просмотра и управления настройками бота"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    @application_checks.check(mod_check)
    async def settings_e(self, interaction: Interaction):
        await self.settings(interaction=interaction)
    
    
    @slash_command(
        name="settings",
        description="Вызывает меню просмотра и управления настройками бота",
        description_localizations={
            Locale.en_GB: "Show menu to see and manage bot's settings",
            Locale.en_US: "Show menu to see and manage bot's settings"
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    @application_checks.check(mod_check)
    async def settings_r(self, interaction: Interaction):
        await self.settings(interaction=interaction)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(m_cmds(bot, **kwargs))
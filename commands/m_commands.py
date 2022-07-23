from os import path, mkdir
from asyncio import sleep, TimeoutError
from contextlib import closing
from sqlite3 import connect
from datetime import datetime, timedelta

from nextcord import Embed, Colour, Guild, Role, Member, TextChannel, Locale, Interaction, slash_command, SlashOption, ButtonStyle, Message, SelectOption
from nextcord.ui import View, Button, button, Select
from nextcord.ext import commands, application_checks

from config import path_to, bot_guilds_e, bot_guilds_r, bot_guilds, prefix, in_row

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
        0 : "🗣️ server language for description of slash commands: {}",
        1 : "⏱ time zone: UTC{}",
        2 : "tap 🗣️ to change language",
        3 : "tap 📃 to see pre-named time zones",
        4 : "tap ⏱ to change time zone",
        5 : "**`Current server time zone: UTC{}`**",
        6 : "Please, write an UTC hours difference (for example, write **`9`** for UTC+9 or **`-4`** for UTC-4) or a name of time zone",
        7 : "Timezone selected by you not in the list of available pre named time zones. You can see the list by pressing button with 📃",
        8 : "Hour difference must be integer number from -12 to 12 ( e.g. difference Є {-12; -11; ...; -11; -12} )",
        9 : "New time zone: **`UTC{}`**",
        10 : "Please, select language from the list:",
        11 : "`Eng` - for English language",
        12 : "`Rus` - for Russian language",
        13 : "New server language for description of slash commands: {}",
        14 : "Please, wait a bit...",
        15 : "This language is already selected as language for description of slash commands",

        
    },
    1 : {
        0 : "🗣️ язык сервера для описания слэш команд: {}",
        1 : "⏱ часовой пояс: UTC{}",
        2 : "нажмите 🗣️, чтобы изменить язык",
        3 : "нажмите 📃, чтобы посмотреть именные часовые пояса",
        4 : "нажмите ⏱, чтобы изменить часовой пояс",
        5 : "**`Текущий часовой пояс сервера: UTC{}`**",
        6 : "Пожалуйста, укажите часовую разницу от UTC (например, напишите **`9`** для UTC+9 или **`-4`** для UTC-4) или имя часового пояса",
        7 : "Указанного Вами названия часового пояса нет в списке поясов, доступного по кнопке 📃",
        8 : "Часовой сдвиг должнен быть целым числом от -12 до 12 ( т.е сдвиг Є {-12; -11; ...; -11; -12} )",
        9 : "Новый часовой пояс сервера: **`UTC{}`**",
        10 : "Пожалуйста, выберите язык из списка:",
        11 : "`Eng` - для английского языка",
        12 : "`Rus` - для русского языка",
        13 : "Новый язык сервера для описания слэш команд: {}",
        14 : "Пожалуйста, немного подождите...",
        15 : "Этот язык уже выбран в качестве языка для описания слэш команд"
    }
}

zones = {
    "0" : 0,
    "1" : 1,
    "2" : 2,
    "3" : 3,
    "4" : 4,
    "5" : 5,
    "6" : 6,
    "7" : 7,
    "8" : 8,
    "9" : 9,
    "10" : 10,
    "11" : 11,
    "12" : 12,
    "-1" : -1,
    "-2" : -2,
    "-3" : -3,
    "-4" : -4,
    "-5" : -5,
    "-6" : -6,
    "-7" : -7,
    "-8" : -8,
    "-9" : -9,
    "-10" : -10,
    "-11" : -11,
    "-12" : -12,
    "UTC" : 0,
    "BST" : 1,
    "CET" : 1,
    "BST" : 1,
    "EET" : 2,
    "MSK" : 3,
    "SAMT" : 4,
    "YEKT" : 5,
    "QYZT" : 6,
    "KRAT" : 7,
    "IRKT" : 8,
    "YAKT" : 9,
    "JST" : 9,
    "VLAT" : 10,
    "MAGT" : 11,
    "PETT" : 12,
    "BRT" : -3,
    "EDT" : -4,
    "CDT" : -5,
    "MDT" : -6,
    "MST" : -7,
    "PDT" : -7,
    "AKDT" : -8,
    "HDT" : -9,
    "HST" : -10
}
zone_nm = {
    "HST" :	"Hawaii Standard, Time UTC-10",
    "HDT" : "Hawaii-Aleutian, Daylight UTC-9",
    "AKDT" : "Alaska Daylight, Time UTC-8",
    "PDT" :	"Pacific Daylight, Time UTC-7",
    "MST" :	"Mountain Standard, Time UTC-7",
    "MDT" : "Mountain Daylight, Time UTC-6",
    "CDT" : "Central Daylight, Time UTC-5",   
    "EDT" :	"Eastern Daylight, Time UTC-4",    
    "BRT" : "Brasília Time, UTC-3",
    "UTC" : "Coordinated Universal Time, UTC+0",
    "BST" : "British Summer Time, UTC+1",
    "CET" : "Central European Time, UTC+1",
    "EET" : "Eastern European Time, UTC+2",
    "MSK" : "Moscow Standard Time, UTC+3",
    "SAMT" : "Samara Time, UTC+4",
    "YEKT" : "Yekaterinburg Time, UTC+5",
    "QYZT" : "Qyzylorda Time, UTC+6",
    "KRAT" : "Krasnoyarsk Time, UTC+7",
    "IRKT" : "Irkutsk Time, UTC+8",
    "YAKT" : "Yakutsk Time, UTC+9",
    "JST" : "Japan Standard Time, UTC+9",
    "VLAT" : "Vladivostok Time, UTC+10",
    "MAGT" : "Magadan Time, UTC+11",
    "PETT" : "Kamchatka Time, UTC+12",
}

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

ec_text = {
    0 : {
        0 : "Economy settings",
        1 : "💸 Money gained for message:\n**`{}`**",
        2 : "⏰ Cooldown for `/work`:\n**`{} seconds`**",
        3 : "💹 Salary from `/work`:\n**`{}`**",
        4 : "random integer from **`{}`** to **`{}`**",
        5 : "📙 Log channel for economic operations:\n{}",
        6 : "```fix\nnot selected```",
        7 : "To manage setting press button with\ncorresponding emoji",
        8 : "To see and manage roles available for\npurchase/sale in the bot press 🛠️"
    },
    1 : {
        0 : "Настройки экономики",
        1 : "💸 Количество денег, получаемое за сообщение:\n**`{}`**",
        2 : "⏰ Кулдаун для команды `/work`:\n**`{} секунд`**",
        3 : "💹 Доход от команды `/work`:\n**{}**",
        4 : "рандомное целое число от `{}` до `{}`",
        5 : "📙 Канал для логов экономических операций:\n{}",
        6 : "```fix\nне выбран```",
        7 : "> Для управления настройкой нажмите на кнопку с\nсоответствующим эмодзи",
        8 : "> Для просмотра и управления ролями, доступными\nдля покупки/продажи у бота, нажмите 🛠️"
    }
}

languages = {
    0 : {
        0 : "English",
        1 : "Russian",
        "ENG" : ("English", 0),
        "RUS": ("Russian", 1),
        "URUS" : ("Russian", 1)
    },
    1 : {
        0 : "английский",
        1 : "русский",
        "ENG" : ("английский", 0),
        "RUS": ("русский", 1),
        "URUS" : ("русский", 1)
    }
}


#with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
#            with closing(base.cursor()) as cur:
#                 sets = cur.execute("SELECT * FROM server_info")
class c_select(Select):
    def __init__(self, custom_id, placeholder: str, roles: list) -> None:
        options = [SelectOption(label=role.name, value=role.id) for role in roles]
        super().__init__(custom_id=custom_id, placeholder=placeholder, options=options)
    
    async def callback(self, interaction: Interaction):
        print(self.values)


class c_button(Button):
    def __init__(self, style: ButtonStyle, label: str, custom_id: str, disabled: bool = False, emoji = None, row: int = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row)

    async def callback(self, interaction: Interaction):
        await super().view.click(interaction, self.custom_id)


class gen_settings_view(View):

    def __init__(self, t_out: int, auth_id: int, bot):
        super().__init__(timeout=t_out)
        self.bot = bot
        self.auth_id = auth_id
        self.add_item(c_button(style=ButtonStyle.green, label=None, custom_id="5", emoji="🗣️"))
        self.add_item(c_button(style=ButtonStyle.red, label=None, custom_id="6", emoji="📃"))
        self.add_item(c_button(style=ButtonStyle.blurple, label=None, custom_id="7", emoji="⏱"))
    

    async def tz_list(self, interaction: Interaction, lng: int):
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                tz = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]
        if tz >= 0: tz = f"+{tz}"
        else: tz = f"{tz}"
        emb = Embed()
        emb.title=gen_settings_text[lng][5].format(tz)
        dsc = []
        for i in zone_nm:
            #emb.add_field(name=i, value=zone_text[i])
            dsc.append(f"**{i}**: {zone_nm[i]}")
        emb.description = "\n".join(dsc)
        m = await interaction.response.send_message(embed=emb)
        await m.delete(delay=50)


    async def digit_tz(self, ans: str, interaction: Interaction, m_b_ans, lng: int, m):
        
        if (ans.startswith("-") and ans[1:].isdigit()) or ans.isdigit():
            ans = int(ans)
            if -12 <= ans <= 12:
                with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                    with closing(base.cursor()) as cur:
                        cur.execute("UPDATE server_info SET value = ? WHERE settings = 'tz'", (ans,))
                        base.commit()
                if ans >= 0: ans = f"+{ans}"
                else: ans = f"{ans}"
                emb = m.embeds[0]
                dsc = emb.description.split("\n")
                t = dsc[1].find("UTC")
                dsc[1] = dsc[1][:t+3] + ans
                emb.description = "\n".join(dsc)
                await m.edit(embed=emb)
                await m_b_ans.delete()
                return await interaction.channel.send(embed=Embed(description=gen_settings_text[lng][9].format(ans))), 0
            else:
                return await interaction.channel.send(embed=Embed(description=gen_settings_text[lng][8])), 1
        elif ans in zones:
            tz = zones[ans]
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'tz'", (tz,))
                    base.commit()
            if tz >= 0: tz = f"+{tz}"
            else: tz = f"{tz}"
            emb = m.embeds[0]
            dsc = emb.description.split("\n")
            t = dsc[1].find("UTC")
            dsc[1] = dsc[1][:t+3] + tz
            emb.description = "\n".join(dsc)
            await m.edit(embed=emb)
            await m_b_ans.delete()
            return await interaction.channel.send(embed=Embed(description=gen_settings_text[lng][9].format(tz))), 0
        else:
            return await interaction.channel.send(embed=Embed(description=gen_settings_text[lng][7])), 1


    async def select_lng(self, ans: str, interaction: Interaction, m_b_ans, lng: int, m):
        if ans in languages[lng]:
            
            s_lng = languages[lng][ans][1]
            g_id = interaction.guild_id
            await m_b_ans.delete()
            with closing(connect(f"{path_to}/bases/bases_{g_id}/{g_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    if cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0] == s_lng:
                        return await interaction.channel.send(embed=Embed(description=gen_settings_text[lng][15])), 0
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'lang'", (s_lng,))
                    base.commit()
            
            if s_lng == 0:
                if not g_id in bot_guilds_e:
                    bot_guilds_e.add(g_id)
                if g_id in bot_guilds_r:
                    bot_guilds_r.remove(g_id)
            else:
                if not g_id in bot_guilds_r:
                    bot_guilds_r.add(g_id)
                if g_id in bot_guilds_e:
                    bot_guilds_e.remove(g_id)

            m_ans = await interaction.channel.send(embed=Embed(description=gen_settings_text[lng][14]))
            
            self.bot.unload_extension(f"commands.m_commands")
            self.bot.load_extension(f"commands.m_commands")
            await sleep(1)
            await self.bot.discover_application_commands()
            await sleep(10)
            await self.bot.sync_all_application_commands()
            s_lng_nm = languages[lng][ans][0]

            emb = m.embeds[0]
            dsc = emb.description.split("\n")
            t = dsc[0].find(":")
            dsc[0] = dsc[0][:t+2]+ s_lng_nm
            emb.description = "\n".join(dsc)
            await m.edit(embed=emb)

            return await m_ans.edit(embed=Embed(description=gen_settings_text[lng][13].format(s_lng_nm))), 0
        else:
            return None, 1


    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        m = interaction.message
        if c_id == "6":
            await self.tz_list(interaction=interaction, lng=lng)
            return
        flag = 1
        if c_id == "7":
            m_b_ans = await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][6]))
        elif c_id == "5":
            m_b_ans = await interaction.response.send_message(embed=Embed(title=gen_settings_text[lng][10], description=f"{gen_settings_text[lng][11]}\n{gen_settings_text[lng][12]}"))
        else:
            return
        while flag:
            try:
                m_ans = await interaction.client.wait_for(event="message", check=lambda m: m.author.id == self.auth_id and m.channel.id == interaction.channel_id, timeout=40)
            except TimeoutError:
                await m_b_ans.delete()
                return
            else:
                ans = m_ans.content.upper()
                if c_id == "7":
                    m_verif_ans, flag = await self.digit_tz(ans=ans, interaction=interaction, m_b_ans=m_b_ans, lng=lng, m=m)
                    await m_verif_ans.delete(delay=12)
                else:
                    m_verif_ans, flag = await self.select_lng(ans=ans, interaction=interaction, m_b_ans=m_b_ans, lng=lng, m=m)
                    if not flag: await m_verif_ans.delete(delay=12)
                try:
                    await m_ans.delete()
                except:
                    pass


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
        if c_id == "8":
            m_a = await interaction.response.send_message(embed=Embed(title=mod_roles_text[lng][5], description=mod_roles_text[lng][6]))
        else:
            m_a = await interaction.response.send_message(embed=Embed(title=mod_roles_text[lng][4], description=mod_roles_text[lng][6]))
        flag = True
        while flag:
            try:
                m_ans = await interaction.client.wait_for(event="message", check=lambda m: m.author.id == interaction.user.id and m.channel.id == interaction.channel_id, timeout=40)
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
                        if c_id == "8":
                            m_ra = await self.add_role(rl=rl, interaction=interaction, lng=lng, m=m)
                            if len(self.m_rls) == 1:
                                for c in self.children:
                                    if c.custom_id == "9":
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


class economy_view(View):
    def __init__(self, t_out: int, auth_id: int, rls):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.add_item(c_button(style=ButtonStyle.blurple, label="", custom_id="10", emoji="💸"))
        self.add_item(c_button(style=ButtonStyle.blurple, label="", custom_id="11", emoji="⏰"))
        self.add_item(c_button(style=ButtonStyle.blurple, label="", custom_id="12", emoji="💹"))
        self.add_item(c_button(style=ButtonStyle.green, label="", custom_id="13", emoji="📙"))
        self.add_item(c_button(style=ButtonStyle.red, label="", custom_id="14", emoji="🛠️"))
        """ for i in range((len(rls)+24)//25):
            self.add_item(c_select(custom_id=f"{15+i}", placeholder="Select role", roles=rls[i*25:min(len(rls), (i+1)*25)])) """

    async def click(self, interaction: Interaction, c_id):
        pass

class settings_view(View):
    
    def __init__(self, t_out: int, lng: int, auth_id: int, bot):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.bot = bot
        self.add_item(c_button(style=ButtonStyle.red, label=None, custom_id="0", emoji="⚙️"))
        self.add_item(c_button(style=ButtonStyle.red, label=None, custom_id="1", emoji="<:moder:1000090629897998336>"))
        self.add_item(c_button(style=ButtonStyle.green, label=None, custom_id="2", emoji="💰"))
        self.add_item(c_button(style=ButtonStyle.blurple, label=None, custom_id="3", emoji="📈"))
        self.add_item(c_button(style=ButtonStyle.blurple, label=None, custom_id="4", emoji="📊"))


    async def click(self, interaction: Interaction, custom_id: str):
        lng = 1 if "ru" in interaction.locale else 0
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
                dsc.append(gen_settings_text[lng][1].format(f"{tz}"))
            for i in 2, 3, 4:
                dsc.append(gen_settings_text[lng][i])
            emb.description="\n".join(dsc)
            gen_view = gen_settings_view(t_out=50, auth_id=self.auth_id, bot=self.bot)
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
        elif custom_id == "2":
            with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                with closing(base.cursor()) as cur:
                    money_p_m = cur.execute("SELECT value FROM server_info WHERE settings = 'mn_per_msg'").fetchone()[0]
                    w_cd = cur.execute("SELECT value FROM server_info WHERE settings = 'w_cd'").fetchone()[0]
                    sal_l = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_l'").fetchone()[0]
                    sal_r = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_r'").fetchone()[0]
                    e_l_c = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]
            emb = Embed(title=ec_text[lng][0])
            dsc = []
            dsc.append(ec_text[lng][1].format(money_p_m))
            dsc.append(ec_text[lng][2].format(w_cd))
            if sal_l == sal_r:
                dsc.append(ec_text[lng][3].format(sal_l))
            else:
                dsc.append(ec_text[lng][3].format(ec_text[lng][4].format(sal_l, sal_r)))
            if e_l_c == 0:
                dsc.append(ec_text[lng][5].format(ec_text[lng][6]))
            else:
                dsc.append(ec_text[lng][5].format(f"<#{e_l_c}>"))
            dsc.append(ec_text[lng][7])
            dsc.append(ec_text[lng][8])
            emb.description = "\n\n".join(dsc)
            rls = [r for r in interaction.guild.roles if (not r.is_integration() and r.is_assignable())]
            ec_v = economy_view(t_out=50, auth_id=self.auth_id, rls=rls)
            m = await interaction.response.send_message(embed=emb, view=ec_v)
            if await ec_v.wait():
                ec_v.stop()
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


    async def settings(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        dsc = []
        for i in settings_text[lng][1:]:
            dsc.append(i)
        st_view = settings_view(t_out=80, lng=lng, auth_id=interaction.user.id, bot=self.bot)
        emb = Embed(title=settings_text[lng][0], description="\n".join(dsc))
        m = await interaction.response.send_message(embed=emb, view=st_view)
        if await st_view.wait():
            for c in st_view.children:
                c.disabled = True
            await m.edit(view=st_view)
        st_view.stop()
        

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
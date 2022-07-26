
from asyncio import sleep, TimeoutError
from contextlib import closing
from sqlite3 import connect
from random import randint
from datetime import datetime, timedelta

from nextcord import Embed, Colour, Guild, Role, Locale, Interaction, slash_command, ButtonStyle, Message, SelectOption, TextChannel, TextInputStyle
import nextcord
from nextcord.ui import View, Button, button, Select, TextInput, Modal
from nextcord.ext import commands, application_checks

from config import path_to, bot_guilds_e, bot_guilds_r, prefix, in_row

settings_text = {
    0 : [
        "Choose section",
        "⚙️ general settings",
        "💰 economy",
        "<:moder:1000090629897998336> manage moders' roles",
        "📈 ranking",
        "📊 polls",
        "Select role",
        "Adding role"
        
    ],
    1 : [
        "Выберите раздел",
        "⚙️ основные настройки",
        "<:moder:1000090629897998336> настройка ролей модераторов",
        "💰 экономика",
        "📈 ранговая система",
        "📊 поллы",
        "Выберите роль",
        "Добавление роли"
    ]
}

gen_settings_text = {
    0 : {
        0 : "🗣️ server language for description of slash commands: {}",
        1 : "⏱ time zone: UTC{}",
        2 : "tap 🗣️ to change language",
        3 : "tap ⏱ to change time zone",
        4 : "Select new language",
        5 : "Select new time zone",
        6 : "You hasn't selected the language yet",
        7 : "You hasn't selected time zone yet",
        8 : "**`Current server time zone: UTC{}`**",
        9 : "New time zone: **`UTC{}`**",
        10 : "New server language for description of slash commands: {}",
        11 : "Language is changing, please wait a bit...",
        12 : "This language is already selected as language for description of slash commands"        
    },
    1 : {
        0 : "🗣️ язык сервера для описания слэш команд: {}",
        1 : "⏱ часовой пояс: UTC{}",
        2 : "нажмите 🗣️, чтобы изменить язык",
        3 : "нажмите ⏱, чтобы изменить часовой пояс",
        4 : "Выбрать новый язык",
        5 : "Выбрать новый часовой пояс",
        6 : "Вы не выбрали язык",
        7 : "Вы не выбрали часовой пояс",
        8 : "**`Текущий часовой пояс сервера: UTC{}`**",
        9 : "Новый часовой пояс сервера: **`UTC{}`**",
        10 : "Новый язык сервера для описания слэш команд: {}",
        11 : "Язык изменяется, пожалуйста, подождите немного...",
        12 : "Этот язык уже выбран в качестве языка для описания слэш команд"
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
        6 : "**`You hasn't selected role yet`**",
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
        6 : "**`Вы не выбрали роль`**",
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
        7 : "> To manage setting press button with\ncorresponding emoji",
        8 : "> To see and manage roles available for\npurchase/sale in the bot press 🛠️",
        9 : "Write amount of money gained for message (non negative integer number)",
        10 : "Amount of money gained from messages set to: `{}`",
        11 : "Write cooldown for `/work` command **in seconds** (integer at least 60)",
        12 : "Cooldown for `/work` set to: `{}`",
        13 : "Write salary from `/work`:\nTwo non-negative numbers, second at least as much as first\nSalary will be random integer \
            between them\nIf you want salary to constant write one number\nFor example, if you write `1` `100` then salary \
            will be random integer from `1` to `100`\nIf you write `10`, then salary will always be `10`",
        14 : "Now salary is {}",
        15 : "Select channel",
        16 : "You chose channel {}",
        17 : "Timeout expired",
        18 : "role - role id - salary - cooldown for salary - type",
        19 : "No roles were added",
        20 : "**If role isn't shown in the menus it\nmeans that bot can't manage this role**"
    },
    1 : {
        0 : "Настройки экономики",
        1 : "💸 Количество денег, получаемых за сообщение:\n**`{}`**",
        2 : "⏰ Кулдаун для команды `/work`:\n**`{} секунд`**",
        3 : "💹 Доход от команды `/work`:\n**{}**",
        4 : "рандомное целое число от `{}` до `{}`",
        5 : "📙 Канал для логов экономических операций:\n{}",
        6 : "```fix\nне выбран```",
        7 : "> Для управления настройкой нажмите на кнопку с\nсоответствующим эмодзи",
        8 : "> Для просмотра и управления ролями, доступными\nдля покупки/продажи у бота, нажмите 🛠️",
        9 : "Укажите количество денег, получаемых за сообщение\n(неотрицательное целое число)",
        10 : "Количество денег, получаемых за одно сообщение, теперь равно: `{}`",
        11 : "Укажите кулдаун для команды `/work` **в секундах** (целое число не менее 60)",
        12 : "Кулдаун для команды `/work` теперь равен: `{}`",
        13 : "Укажите заработок от команды `/work`:\nДва неотрицательных числа, второе не менее первого\nЗаработок будет \
            рандомным целым числом между ними\nЕсли Вы хотите сделать заработок постоянным, укажите одно число\nНапример, \
            если Вы укажите `1` `100`, то заработок будет рандомным целым числом от `1` до `100`\nЕсли Вы укажите `10`, то \
            заработок всегда будет равен `10`",
        14 : "Теперь заработок: {}",
        15 : "Выберите канал",
        16 : "Вы выбрали канал {}",
        17 : "Время ожидания вышло",
        18 : "роль - id роли - заработок - кулдаун заработка - тип",
        19 : "Не добавлено ни одной роли",
        20 : "**Если роль не отображается ни в одном\nменю, значит, бот не может управлять ею**"
    }
}

ec_mr_text = { 
    0 : {
        0 : "Edit role",
        1 : "Yes",
        2 : "No",
        3 : "You declined removing the role <@&{}>",
        4 : "Please, wait a bit...",
        5 : "You removed role <@&{}>",
        6 : "Are you sure you want to delete role <@&{}> from the bot's settings?\nAll information about it will be deleted and it will be withdrawn from the store",
        7 : "You can't remove role that is not in the list",
        8 : "You can't edit role that is not in the list",
        9 : "This role is already in the list",
        10 : "Role's price",
        11 : "Write positive integer number as price of the role",
        12 : "Role's salary (not necessary)",
        13 : "If you want role to bring money to it's owners then write a salary: positive integer number",
        14 : "Cooldown for salary salary_cooldown",
        15 : "If salary is selected, select cooldown: once at a set time (in hours) role's owners will gain salary",
        16 : "How the role will be displayed in the store",
        17 : "Print 1 if the same roles will be separated (nonstacking) (each answer can be written in any window)",
        18 : "Print 2 if the same roles will be countable (can run out in the store) and stacking as one item",
        19 : "Print 3 if the same roles will be uncountable (can't run out in the store) and stacking as one item",
        20 : "Price must be positive integer number",
        21 : "If selected, salary should be positive integer number",
        22 : "If salary selected, cooldown should be positive integer number",
        23 : "Type of the role should be one of three numbers: 1, 2 or 3",
        24 : "You chosen different types of displaying for the role"
        
    },
    1 : {
        0 : "Редактировать роль",
        1 : "Да",
        2 : "Нет",
        3 : "Вы отменили удаление роли <@&{}>",
        4 : "Пожалуйста, подождите...",
        5 : "Вы удалили роль <@&{}>",
        6 : "Вы уверены, что хотите удалить роль <@&{}> из настроек бота?\nВся информация о ней будет удалена и она будет изъята из магазина",
        7 : "Вы не можете убрать роль, которая не неходится в списке",
        8 : "Вы не можете редактировать роль, которая не неходится в списке",
        9 : "Эта роль уже находится в списке",
        10 : "Цена роли",
        11 : "Укажите целое положительное число",
        12 : "Доход роли (необязательно)",
        13 : "Если Вы хотите, чтобы роль приносила деньги её владельцам, укажите доход: целое положительное число",
        14 : "Кулдаун дохода",
        15 : "Если Вы указали доход, укажите кулдаун: раз в какое время (в часах) овнеры роли будут получать доход",
        16 : "Как роль будет отображаться в магазине",
        17 : "Напишите 1, если одинаковые роли будут отображаться отдельно (ответ можно написать в любом поле)",
        18 : "Напишите 2, если одинаковые роли будут стакающимеся и исчисляемыми (могут закончиться в магазине)",
        19 : "Напишите 3, если одинаковые роли будут стакающимеся и бесконечными (не могут закончиться в магазине)",
        20 : "В качестве цены роли надо указать целое положительное число",
        21 : "Если выбрано, то в качестве дохода роли надо указать целое положительное число",
        22 : "Если выбран доход, то в качестве кулдауна дохода роли надо указать целое положительное число (количество часов)",
        23 : "В качестве типа роли надо указать одно из трёх чисел: 1, 2 или 3",
        24 : "Вы выбрали несколько разных типов отображения для роли"
    }
}

r_type = {
    0 : {
        0 : "Nonstacking",
        1 : "Stacking",
        2 : "Infinite"
    },
    1 : {
        0 : "Нестакающаяся",
        1 : "Cтакающаяся",
        2 : "Бесконечная"
    }
}

languages = {
    0 : {
        0 : "English",
        1 : "Russian",
        "ENG" : ("English", 0),
        "RUS": ("Russian", 1)
    },
    1 : {
        0 : "английский",
        1 : "русский",
        "ENG" : ("английский", 0),
        "RUS": ("русский", 1)
    },
    2 : {
        0 : [("English", 0), ("Russian", 1)],
        1 : [("английский", 0), ("русский", 1)]
    },
    "English" : 0,
    "английский" : 0,
    "Russian" : 1,
    "русский" : 1
}

#with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
#            with closing(base.cursor()) as cur:
#                 sets = cur.execute("SELECT * FROM server_info")

class c_modal_add(Modal):
    def __init__(self, timeout: int, lng: int):
        super().__init__(title=settings_text[lng][7], timeout=timeout, custom_id=f"modal_add_{randint(1, 100)}")
        self.price = TextInput(
            label=ec_mr_text[lng][10],
            min_length=1,
            max_length=8,
            placeholder=ec_mr_text[lng][11],
            required=True,
            custom_id=f"modal_p_{randint(1, 100)}"
        )
        self.salary = TextInput(
            label=ec_mr_text[lng][12],
            min_length=1,
            max_length=8,
            style=nextcord.TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][13],
            required=False,
            custom_id=f"modal_s_{randint(1, 100)}"
        )
        self.salary_c = TextInput(
            label=ec_mr_text[lng][14],
            min_length=1,
            max_length=2,
            style=nextcord.TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][15],
            required=False,
            custom_id=f"modal_sc_{randint(1, 100)}"
        )
        self.r_type1 = TextInput(
            label=ec_mr_text[lng][16],
            min_length=1,
            max_length=1,
            style=nextcord.TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][17],
            required=False,
            custom_id=f"modal_t1_{randint(1, 100)}"
        )
        self.r_type2 = TextInput(
            label=ec_mr_text[lng][16],
            min_length=1,
            max_length=1,
            style=nextcord.TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][18],
            required=False,
            custom_id=f"modal_t2_{randint(1, 100)}"
        )
        self.r_type3 = TextInput(
            label=ec_mr_text[lng][16],
            min_length=1,
            max_length=1,
            style=nextcord.TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][19],
            required=False,
            custom_id=f"modal_t3_{randint(1, 100)}"
        )
        self.add_item(self.price)
        self.add_item(self.salary)
        self.add_item(self.salary_c)
        self.add_item(self.r_type1)
        self.add_item(self.r_type2)
        #self.add_item(self.r_type3)
        self.r_t = set()


    def check_answers(self) -> int:
        ans = 0

        if not self.price.value.isdigit():
            ans += 1
        elif int(self.price.value) <= 0:
            ans += 1
        
        if self.salary:
            if not self.salary.value.isdigit():
                ans += 10
            elif int(self.salary.value) <= 0:
                ans += 10

            if not self.salary_c.value.isdigit():
                ans += 100
            elif int(self.price.value) <= 0:
                ans += 100
        
        if self.r_type1.value:
            if self.r_type1.value.isdigit() and int(self.r_type1.value) in {1, 2, 3}:
                self.r_t.add(int(self.r_type1.value))
        
        if self.r_type2.value:
            if self.r_type2.value.isdigit() and int(self.r_type2.value) in {1, 2, 3}:
                self.r_t.add(int(self.r_type2.value))
        
        if self.r_type3.value:
            if self.r_type3.value.isdigit() and int(self.r_type3.value) in {1, 2, 3}:
                self.r_t.add(int(self.r_type3.value))
        
        if len(self.r_t) == 0:
            ans += 1000
        elif len(self.r_t) > 1:
            ans += 10000

        return ans

    async def callback(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        ans_c = self.check_answers()
        rep = []
        if ans_c % 2 == 1:
            rep.append(ec_mr_text[lng][18])
        if (ans_c // 10) % 2 == 1:
            rep.append(ec_mr_text[lng][19])
        if (ans_c // 100) % 2 == 1:
            rep.append(ec_mr_text[lng][20])
        if (ans_c // 1000) % 2 == 1:
            rep.append(ec_mr_text[lng][21])
        if (ans_c // 10000) % 2 == 1:
            rep.append(ec_mr_text[lng][22])

        if len(rep):
            await interaction.response.send_message(embed=Embed(description="\n".join(rep)), ephemeral=True)
            self.stop()
            return
        price = int(self.price.value)
        if self.salary.value:
            salary = int(self.salary.value)
            salary_c = int(self.salary_c.value)
        else:
            salary = salary_c = 0
        r_type = int(self.r_t[0])
        await interaction.response.send_message(embed=Embed(description=f"{price}, {salary}, {salary_c}, {r_type}"), ephemeral=True)
        self.stop()
        return

class c_select_gen(Select):
    def __init__(self, custom_id: str, placeholder: str, opts: list) -> None:
        options = [SelectOption(label=r[0], value=r[1]) for r in opts]
        super().__init__(custom_id=custom_id, placeholder=placeholder, options=options)
    
    async def callback(self, interaction: Interaction):
        await self.view.click_menu(interaction, self.custom_id, self.values)        


class c_select(Select):
    def __init__(self, custom_id, placeholder: str, roles: list) -> None:
        options = [SelectOption(label=role.name, value=role.id) for role in roles]
        super().__init__(custom_id=custom_id, placeholder=placeholder, options=options)
    
    async def callback(self, interaction: Interaction):
        await self.view.click_menu(interaction, self.custom_id, self.values)


class c_button(Button):
    def __init__(self, style: ButtonStyle, label: str, custom_id: str, disabled: bool = False, emoji = None, row: int = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row)

    async def callback(self, interaction: Interaction):
        await super().view.click(interaction, self.custom_id)


class gen_settings_view(View):

    def __init__(self, t_out: int, auth_id: int, bot, lng: int):
        super().__init__(timeout=t_out)
        self.bot = bot
        self.auth_id = auth_id
        self.lang = None
        self.tz = None
        tzs = [(f"UTC{i}", i) for i in range(-12, 0)] + [(f"UTC+{i}", i) for i in range(0, 13)]
        self.add_item(c_select_gen(custom_id="100", placeholder=gen_settings_text[lng][4], opts=languages[2][lng]))
        self.add_item(c_select_gen(custom_id="101", placeholder=gen_settings_text[lng][5], opts=tzs))
        self.add_item(c_button(style=ButtonStyle.green, label=None, custom_id="5", emoji="🗣️"))
        self.add_item(c_button(style=ButtonStyle.blurple, label=None, custom_id="6", emoji="⏱"))


    async def digit_tz(self, interaction: Interaction, lng: int):
            tz = self.tz
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'tz'", (tz,))
                    base.commit()
            if tz >= 0: tz = f"+{tz}"
            else: tz = f"{tz}"

            m = interaction.message
            emb = m.embeds[0]
            dsc = emb.description.split("\n")
            t = dsc[1].find("UTC")
            dsc[1] = dsc[1][:t+3] + tz
            emb.description = "\n".join(dsc)
            await m.edit(embed=emb)

            await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][9].format(tz)), ephemeral=True)
            self.tz = None

    async def select_lng(self, interaction: Interaction, lng: int):
        s_lng = self.lang
        g_id = interaction.guild_id
        with closing(connect(f"{path_to}/bases/bases_{g_id}/{g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                if cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0] == s_lng:
                    await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][12]), ephemeral=True)
                    return
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
        
        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][11]), ephemeral=True)
        
        self.bot.unload_extension(f"commands.m_commands")
        self.bot.unload_extension(f"commands.basic")
        self.bot.unload_extension(f"commands.slash_shop")
        self.bot.load_extension(f"commands.m_commands")
        self.bot.load_extension(f"commands.basic", extras={"prefix": prefix, "in_row": in_row})
        self.bot.load_extension(f"commands.slash_shop", extras={"prefix": prefix, "in_row": in_row})

        await sleep(2)
        await self.bot.sync_all_application_commands()
        await sleep(1)
        s_lng_nm = languages[lng][s_lng]
        
        m = interaction.message
        emb = m.embeds[0]
        dsc = emb.description.split("\n")
        t = dsc[0].find(":")
        dsc[0] = dsc[0][:t+2]+ s_lng_nm
        emb.description = "\n".join(dsc)
        await m.edit(embed=emb)

        await interaction.edit_original_message(embed=Embed(description=gen_settings_text[lng][10].format(s_lng_nm)))
        self.lang = None

    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        
        if c_id == "5" and self.lang == None:
            await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][6]), ephemeral=True)
            return
        elif c_id == "6" and self.tz == None:
            await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][7]), ephemeral=True)
            return
                
        if c_id == "5":
            await self.select_lng(interaction=interaction, lng=lng)
        else:
            await self.digit_tz(interaction=interaction, lng=lng)

    async def click_menu(self, __, c_id, values):
        if c_id == "100":
            self.lang = int(values[0])
        elif c_id == "101":
            self.tz = int(values[0])
    

class mod_roles_view(View):

    def __init__(self, t_out: int, m_rls: set, lng: int, auth_id: int, rem_dis: bool, rls: list):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.m_rls = m_rls
        self.role = None
        for i in range((len(rls)+24)//25):
            self.add_item(c_select(custom_id=f"{200+i}", placeholder=settings_text[lng][6], roles=rls[i*25:min(len(rls), (i+1)*25)]))
        self.add_item(c_button(style=ButtonStyle.green, label=mod_roles_text[lng][3], emoji="<:add01:999663315804500078>", custom_id="8"))
        self.add_item(c_button(style=ButtonStyle.red, label=mod_roles_text[lng][4], emoji="<:remove01:999663428689997844>", custom_id="9", disabled=rem_dis))
    

    async def add_role(self, rl: Role, interaction: Interaction, lng: int, m: Message):
        if rl.id in self.m_rls:
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][7]), ephemeral=True)
            return
        
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
        await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][8].format(rl.mention)), ephemeral=True)
    

    async def rem_role(self, rl: Role, interaction: Interaction, lng: int, m: Message):
        if not rl.id in self.m_rls:
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][9]), ephemeral=True)
            return

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
        await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][10].format(rl.mention)), ephemeral=True)


    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        m = interaction.message
        if self.role == None:
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][6]), ephemeral=True)
            return

        rl_id = self.role
        rl = interaction.guild.get_role(rl_id)
        if rl:
            if c_id == "8":
                await self.add_role(rl=rl, interaction=interaction, lng=lng, m=m)
                if len(self.m_rls) == 1:
                    for c in self.children:
                        if c.custom_id == "9":
                            c.disabled = False
                    await m.edit(view=self)
                self.role = None
            else:
                await self.rem_role(rl=rl, interaction=interaction, lng=lng, m=m)
                if len(self.m_rls) == 0:
                    for c in self.children:
                        if c.custom_id == "9":
                            c.disabled = True
                    await m.edit(view=self)
                self.role = None


    async def click_menu(self, __, ___, values):
        self.role =  int(values[0])

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class economy_view(View):

    def __init__(self, t_out: int, auth_id: int):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.channel = None
        self.add_item(c_button(style=ButtonStyle.blurple, label="", custom_id="10", emoji="💸"))
        self.add_item(c_button(style=ButtonStyle.blurple, label="", custom_id="11", emoji="⏰"))
        self.add_item(c_button(style=ButtonStyle.blurple, label="", custom_id="12", emoji="💹"))
        self.add_item(c_button(style=ButtonStyle.green, label="", custom_id="13", emoji="📙"))
        self.add_item(c_button(style=ButtonStyle.red, label="", custom_id="14", emoji="🛠️"))        

    async def msg_salary(self, interaction: Interaction, lng: int, ans) -> bool:
        if ans.isdigit() and int(ans) >= 0:
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'mn_per_msg'", (int(ans),))
                    base.commit()
            
            await interaction.edit_original_message(embed=Embed(description=ec_text[lng][10].format(ans)))
            
            emb = interaction.message.embeds[0]
            dsc = emb.description.split("\n\n")
            dsc[0] = ec_text[lng][1].format(ans)
            emb.description = "\n\n".join(dsc)
            await interaction.message.edit(embed=emb)

            return False
        else:
            return True

    async def work_cldwn(self, interaction: Interaction, lng: int, ans) -> bool:
        if ans.isdigit() and int(ans) >= 60:
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'w_cd'", (int(ans),))
                    base.commit()
            await interaction.edit_original_message(embed=Embed(description=ec_text[lng][12].format(ans)))
            
            emb = interaction.message.embeds[0]
            dsc = emb.description.split("\n\n")
            dsc[1] = ec_text[lng][2].format(ans)
            emb.description = "\n\n".join(dsc)
            await interaction.message.edit(embed=emb)

            return False
        else:
            return True

    async def work_salary(self, interaction: Interaction, lng: int, ans) -> bool:
        ans = ans.split()
        fl = 0
        if len(ans) >= 2:
            n1 = ans[0]
            n2 = ans[1]
            if n1.isdigit() and n2.isdigit():
                n1 = int(n1); n2 = int(n2)
                if 0 <= n1 <= n2: fl = 1
            
        elif len(ans):
            n1 = ans[0]
            if n1.isdigit() and 0 <= int(n1):
                n2 = n1 = int(n1)
                fl = 1       
        
        if fl:
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'sal_l'", (n1,))
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'sal_r'", (n2,))
                    base.commit()
            
            emb = interaction.message.embeds[0]
            dsc = emb.description.split("\n\n")
            if n1 == n2:
                await interaction.edit_original_message(embed=Embed(description=ec_text[lng][14].format(n1)))
                dsc[2] = ec_text[lng][3].format(n1)
            else:
                await interaction.edit_original_message(embed=Embed(description=ec_text[lng][14].format(ec_text[lng][4].format(n1, n2))))
                dsc[2] = ec_text[lng][3].format(ec_text[lng][4].format(n1, n2))
            
            emb.description = "\n\n".join(dsc)
            await interaction.message.edit(embed=emb)

            return False
        else:
            return True

    async def log_chnl(self, interaction: Interaction, lng: int):
        
        channels = [(c.name, c.id) for c in interaction.guild.text_channels]
        ids = set()
        for i in range(min((len(channels) + 24) // 25, 6)):
            self.add_item(c_select_gen(custom_id=f"{500+i}", placeholder=ec_text[lng][15], opts=channels[i*25:min((i+1)*25, len(channels))]))
            ids.add(f"{500+i}")
            
        await interaction.message.edit(view=self)
        await interaction.response.send_message(embed=Embed(description=ec_text[lng][15]), ephemeral=True)
        cnt = 0
        while cnt <= 40 and self.channel == None:
            cnt += 1
            await sleep(1)
        cld = self.children
        while i < len(cld):
            if cld[i].custom_id in ids:
                self.remove_item(item=cld[i])
            else:
                i += 1
        
        if not self.channel is None:
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'log_c'", (self.channel,))
                    base.commit()
            emb = interaction.message.embeds[0]
            dsc = emb.description.split("\n\n")
            dsc[3] = ec_text[lng][5].format(f"<#{self.channel}>")
            emb.description = "\n\n".join(dsc)
            await interaction.message.edit(embed=emb, view=self)
            await interaction.edit_original_message(embed=Embed(description=ec_text[lng][16].format(f"<#{self.channel}>")))
            self.channel = None
        else:
            await interaction.message.edit(view=self)
            await interaction.edit_original_message(embed=Embed(description=ec_text[lng][17]))
   
    async def click(self, interaction: Interaction, c_id):
        lng = 1 if "ru" in interaction.locale else 0
        if c_id == "13":
            await self.log_chnl(interaction=interaction, lng=lng)
        elif c_id == "14":
            with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                with closing(base.cursor()) as cur:
                    roles = cur.execute('SELECT * FROM server_roles').fetchall()
            emb = Embed()
            descr = []
            st_rls = set()
            if len(roles):
                emb.title = ec_text[lng][18]
                for role in roles:
                    st_rls.add(role[0])
                    r_time = f"{role[3]//3600}:{role[3] // 60 % 60}:{role[3] % 60}"
                    descr.append(f"<@&{role[0]}> - **`{role[0]}`** - **`{role[1]}`** - **`{role[2]}`** - **`{r_time}`** - **`{r_type[lng][role[4]]}`**")
            else:
                emb.title = ec_text[lng][19]
            descr.append("\n" + ec_text[lng][20])
            emb.description="\n".join(descr)
            
            rls = [(r.name, r.id) for r in interaction.guild.roles if r.is_assignable()]
            if len(rls): rd = False
            else: rd = True
            ec_rls_view = economy_roles_manage_view(t_out=49, lng=lng, auth_id=interaction.user.id, rem_dis=rd, rls=rls, st_rls=st_rls)
            await interaction.response.send_message(embed=emb, view=ec_rls_view)
            if await ec_rls_view.wait():
                ec_rls_view.stop()
                await interaction.delete_original_message()  

        else:
            await interaction.response.send_message(embed=Embed(description=ec_text[lng][9 + (int(c_id) - 10) * 2]), ephemeral=True)
            flag = True
            while flag:
                try:
                    user_ans = await interaction.client.wait_for(event="message", check=lambda m: m.author.id == self.auth_id and m.channel.id == interaction.channel_id, timeout=40)
                except TimeoutError:
                    flag = 0
                else:
                    ans = user_ans.content
                    if c_id == "10": flag = await self.msg_salary(interaction=interaction, lng=lng, ans=ans)
                    elif c_id == "11": flag = await self.work_cldwn(interaction=interaction, lng=lng, ans=ans)
                    elif c_id == "12": flag = await self.work_salary(interaction=interaction, lng=lng, ans=ans)
                try:
                    await user_ans.delete()
                except:
                    pass

    async def click_menu(self, interaction, c_id, values):
        self.channel = int(values[0])

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True
    

class economy_roles_manage_view(View):

    def __init__(self, t_out: int, lng: int, auth_id: int, rem_dis: bool, rls: list, st_rls: set):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.st_rls = st_rls
        self.role = None
        for i in range((len(rls)+24)//25):
            self.add_item(c_select_gen(custom_id=f"{800+i}", placeholder=settings_text[lng][6], opts=rls[i*25:min(len(rls), (i+1)*25)]))
        self.add_item(c_button(style=ButtonStyle.green, label=mod_roles_text[lng][3], emoji="<:add01:999663315804500078>", custom_id="15"))
        self.add_item(c_button(style=ButtonStyle.blurple, label=ec_mr_text[lng][0], emoji="🔧", custom_id="16", disabled=rem_dis))
        self.add_item(c_button(style=ButtonStyle.red, label=mod_roles_text[lng][4], emoji="<:remove01:999663428689997844>", custom_id="17", disabled=rem_dis))


    async def click(self, interaction: Interaction, c_id):
        lng = 1 if "ru" in interaction.locale else 0
        if self.role is None:
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][6]), ephemeral=True)
            return
        if c_id == "17":
            if not self.role in self.st_rls:
                await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][7]))
                return
            v_d = verify_delete(lng=lng, role=self.role)
            await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][6].format(self.role)), view=v_d)
            if await v_d.wait():
                for c in v_d.children:
                    c.disabled = True
                await interaction.edit_original_message(view=v_d)
        elif c_id == "15":
            add_mod = c_modal_add(timeout=90, lng=lng)
            await interaction.response.send_modal(modal=add_mod)
            if await add_mod.wait():
                for c in add_mod.children:
                    c.disabled = True
                await interaction.edit_original_message(view=add_mod)


    async def click_menu(self, interacion, c_id, values):
        if int(c_id) >= 800:
            self.role = int(values[0])

class verify_delete(View):
    def __init__(self, lng: int, role: int):
        super().__init__(timeout=30)
        self.role = role
        self.add_item(c_button(style=ButtonStyle.red, label=ec_mr_text[lng][1], custom_id="10000"))
        self.add_item(c_button(style=ButtonStyle.green, label=ec_mr_text[lng][2], custom_id="10001"))
    
    async def click(self, interaction: Interaction, c_id):
        lng = 1 if "ru" in interaction.locale else 0
        if c_id == "10001":
            await interaction.message.delete()
            await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][3].format(self.role)), ephemeral=True)
            self.stop()
        else:
            await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][4]), ephemeral=True)
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    cur.executescript(f"""
                        DELETE FROM server_roles WHERE role_id = {self.role};
                        DELETE FROM salary_roles WHERE role_id = {self.role};
                        DELETE FROM store WHERE role_id = {self.role};
                    """)
                    base.commit()
                    for r in cur.execute("SELECT * FROM users").fetchall():
                        if f"{self.role}" in r[2]:
                            cur.execute("UPDATE users SET owned_roles = ? WHERE memb_id = ?", (r[2].replace(f"{self.role}#", ""), r[0]))
                            base.commit()
            await interaction.edit_original_message(embed=Embed(description=ec_mr_text[lng][5].format(self.role)))
            await interaction.message.delete()
            self.stop()


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
            for i in 2, 3:
                dsc.append(gen_settings_text[lng][i])
            emb.description="\n".join(dsc)
            gen_view = gen_settings_view(t_out=50, auth_id=self.auth_id, bot=self.bot, lng=lng)
            await interaction.response.send_message(embed=emb, view=gen_view)
            if await gen_view.wait():
                gen_view.stop()
                await interaction.delete_original_message()

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
            rls = [r for r in interaction.guild.roles if not r.is_bot_managed()]
            
            m_rls_v = mod_roles_view(t_out=50, m_rls=m_rls, lng=lng, auth_id=self.auth_id, rem_dis=rem_dis, rls=rls)
            await interaction.response.send_message(embed=emb, view=m_rls_v)
            if await m_rls_v.wait():
                m_rls_v.stop()
                await interaction.delete_original_message()

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
            rls = [r for r in interaction.guild.roles if (not r.is_bot_managed() and r.is_assignable())]
            ec_v = economy_view(t_out=50, auth_id=self.auth_id)
            await interaction.response.send_message(embed=emb, view=ec_v)
            if await ec_v.wait():
                ec_v.stop()
                await interaction.delete_original_message()

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
        for i in settings_text[lng][1:6]:
            dsc.append(i)
        st_view = settings_view(t_out=80, lng=lng, auth_id=interaction.user.id, bot=self.bot)
        emb = Embed(title=settings_text[lng][0], description="\n".join(dsc))
        await interaction.response.send_message(embed=emb, view=st_view)
        if await st_view.wait():
            for c in st_view.children:
                c.disabled = True
            await interaction.edit_original_message(view=st_view)
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
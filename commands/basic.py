
from sqlite3 import connect, Connection, Cursor
from contextlib import closing
from datetime import datetime, timedelta

from nextcord.ext import commands
from nextcord.ext.commands import CheckFailure
from nextcord import Embed, Colour, Locale, Interaction, slash_command, ButtonStyle
from nextcord.ui import Button

from config import *

guide = {
    0 : {
        0 : "The guide",
        1 : "Economic operations with the roles",
        2 : "In order to make role able to be bought and sold on the server and it could bring money you should add it to the list of roles, available for the purchase/sale in the \
            menu **`/settings`** -> \"💰\" -> \"🛠️\". Also in this menu you can manage added roles",
        3 : "Bot devides roles on three types:",
        4 : "1, 2 and 3",
        5 : "Type 1",
        6 : "\"Nonstacking\" roles, that are not stacking in the store (are shown as different items in the store)",
        7 : "Type 2",
        8 : "\"Stacking\" roles that are stacking in the store (are shown as one item with quantity)",
        9 : "Type 3",
        10 : "\"Infinite\" roles that can't run out in the store (you can buy them endless times)",
        11 : "Salary of the roles",
        12 : "Each role can have passive salary: once per every cooldown time, set in the menu **`/settings`** -> \"💰\" -> \"🛠️\", members that have this role on their balance will \
            gain money (salary) that is selected in the menu **`/settings`** -> \"💰\" -> \"🛠️\"",
        13 : "Work",
        14 : "Members can gain money by using **`/work`** command. Amount of gained money is set in the menu **`/settings`** -> \"💰\" -> \"💹\". Cooldown \
            for the command is set in the menu **`/settings`** -> \"💰\" -> \"⏰\"",
        15 : "Rank system",
        16 : "For each message member gains amount of xp set in the menu **`/settings`** -> \"📈\" -> \"✨\" After achieving \"border\" of the level set in the menu \
            **`/settings`** -> \"📈\" -> \"✨\" member's level growths. For each new level bot can add role (and for old - remove, if new role is added) set in the menu \
            **`/settings`** -> \"📈\" -> \"🥇\" for each level separately",
        17 : "Money for messages",
        18 : "Besides the xp member can gain money for every message. Amount of money gained from message is set in the menu **`/settings`** -> \"💰\" -> \"💸\"\
            If you want to turn off this function you can make this value equal to 0",
        19 : "Polls",
        20 : "Members can create polls via **`/poll`**. They can be open/anonymous and have one/multiple choice. After creation poll will be posted in verification channel set \
            in the menu **`/settings`** -> \"📊\" -> \"🔎\". After being approved by moderator poll will be posted in channel for publishing polls set in the \
            menu **`/settings`** -> \"📊\" -> \"📰\""
    },
    1 : {
        0 : "Гайд",
        1 : "Экономические операции с ролями",
        2 : "Чтобы роль можно было покупать и продавать на сервере, а также она могла приносить заработок, нужно добавить её в список ролей, \
            доступных для покупки/продажи на сервере при помоши меню **`/settings`** -> \"💰\" -> \"🛠️\". В этом же меню можно и управлять добавленными ролями",
        3 : "Бот делит роли на 3 типа:",
        4 : "1, 2 и 3",
        5 : "Тип 1",
        6 : "\"Нестакающиеся\" роли, которые не стакаются в магазине (т.е. отображаются как отдельные товары)",
        7 : "Тип 2",
        8 : "\"Стакающиеся\" роли, которые стакаются в магазине (т.е. отображаются как один товар с указанным количеством)",
        9 : "Тип 3",
        10 : "\"Бесконечные\" роли, которые не заканчиваются в магазине (т.е. их можно купить бесконечное количество раз)",
        11 : "Заработок роли",
        12 : "Каждая роль может иметь пассивный заработок: раз в некоторое установленное время, установленное в меню **`/settings`** -> \"💰\" -> \"🛠️\", участники, на балансе \
            которых находится эта роль, получают заработок, установленный для каждой роли отдельно в меню **`/settings`** -> \"💰\" -> \"🛠️\"",
        13 : "Работа",
        14 : "Пользователи могут получать деньги за использование команды **`/work`**. Заработок от команды устанавливается в меню **`/settings`** -> \"💰\" -> \"💹\". Кулдаун команды \
            устанавливается в меню **`/settings`** -> \"💰\" -> \"⏰\"",
        15 : "Система рангов",
        16 : "За каждое сообщение на сервере пользователь получает количество опыта, установленное в меню **`/settings`** -> \"📈\" -> \"✨\" По достижении \"границы\" уровня, \
            установленной в меню **`/settings`** -> \"📈\" -> \"✨\", уровень пользователя повышается. За каждый новый уровень бот может выдавать роль (а за пройденный - снимать, \
            если выдана новая), установленную в меню **`/settings`** -> \"📈\" -> \"🥇\" для каждого уровня отдельно",
        17 : "Деньги за сообщения",
        18 : "За каждое сообщение пользователь получает не только опыт, но и деньги. Количество денег, получаемое за сообщение, устанавливается в меню **`/settings`** -> \"💰\" -> \"💸\"\
            Если Вы хотите отключить эту функцию, Вы можете установить это значение равным нулю",
        19 : "Поллы",
        20 : "Пользователи могут создавать поллы (опросы) при помощи **`/poll`**. Они могут быть открытыми/анонимными и содержать один или несколько вариантов выбора. После создания \
            полл будет отправлен на верификацию в канал, установленный в меню **`/settings`** -> \"📊\" -> \"🔎\". Если полл будет одобрен модератором, то он будет отправлен в \
            канал для публикаций, установленный в меню  **`/settings`** -> \"📊\" -> \"📰\""
    }
}

help_text = {
    0 : {
        0 : "Help menu",
        1 : "Choose a category",
    },
    1 : {
        0 : "Меню помощи",
        1 : "Выберите категорию",
    }
}

text_help_view = {
    0 : {
        0 : "User's commands",
        1 : "Mod's commands",
        2 : "**`Sorry, but you can't manage menu called by another user`**",
        3 : "**`Sorry, but you don't have permissions to watch mod's section`**",
        4 : "Economy",
        5 : "Personal",
        6 : "Other",
    },
    1 : {
        0 : "Команды пользователей",
        1 : "Команды модераторов",
        2 : "**`Извините, но Вы не можете управлять меню, которое вызвано другим пользователем`**",
        3 : "**`Извините, но у Вас нет прав для просмотра команд для модераторов`**",
        4 : "Экономика",
        5 : "Персональные",
        6 : "Остальные",
    }
}

u_ec_cmds = {
    0 : [
        ("`/store`", "Show store"), ("`/buy`", "Make a role purchase"),
        ("`/sell`", "Sell the role"), ("`/leaders`", "Show top members by balance/xp"),
    ],
    1 : [
        ("`/store`", "Открывает меню магазина"), ("`/buy`", "Совершает покупку роли"), 
        ("`/sell`", "Совершает продажу роли"), ("`/leaders`", "Показывет топ пользователей по балансу/опыту")
    ],
}
u_pers_cmds = {
    0 : [
        ("`/profile`", "Show your profile"), ("`/work`", "Start working, so you get salary"),
        ("`/transfer`", "Transfer money to another member"), ("`/duel`", "Make a bet"),
    ],
    1 : [
        ("`/profile`", "Показывает меню Вашего профиля"), ("`/work`", "Начинает работу, за которую Вы полчите заработок"),
        ("`/transfer`", "Совершает перевод валюты другому пользователю"), ("`/duel`", "Делает ставку"),
    ]
}
u_other_cmds = {
    0 : [
        ("`/poll`", "Make a poll"), ("`/server`", "Show information about the server"),
        ("`/emoji`", "Show emoji's png and url")
    ],
    1 : [
        ("`/poll`", "Создаёт полл (опрос)"), ("`/server`", "Показывает информацию о сервере"),
        ("`/emoji`", "Показывает png и url эмодзи")
    ]
}
m_cmds = {
    0 : [
        ("`/guide`", "Show guide about bot's system"), ("`/settings`", "Call bot's settings menu")
    ],
    1 : [
        ("`/guide`", "Показывает гайд о системе бота"), ("`/settings`", "Вызывает меню настроек бота")
    ]
}



class custom_b(Button):

    def __init__(self, label: str, style: ButtonStyle, emoji, c_id: str):
        super().__init__(style=style, label=label, emoji=emoji, custom_id=c_id)
    
    async def callback(self, interaction: Interaction):
        return await self.view.click(interaction=interaction, c_id=self.custom_id)


class mod_commands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        global bot_guilds
        global bot_guilds_e
        global bot_guilds_r

        global text
        text = {
            0 : {
                404 : 'Error',
                18 : "**`This user not found on the server.`**",
                19 : '**`Please, use correct arguments for command. More info via \n{}help_m {}`**',
                20 : '**`This command not found`**',
                21 : '**`This user not found`**',
                22 : '**`Please, wait before reusing this command`**',
                23 : "**`Sorry, but you don't have enough permissions for using this command`**",
                24 : f"**Economic moderator role is not chosen! User with administrator or manage server permissions can do it via `{prefix}mod_role` `role_id`**",
                40 : "**`This role not found`**",
                41 : "**`This channel not found`**"
            },
            1 : {
                404 : 'Ошибка',
                18 : "**`На сервере не найден такой пользователь`**",
                19 : "**`Пожалуйста, укажите верные аргументы команды. Подробнее - {}help_m {}`**",
                20 : "**`Такая команда не найдена`**",
                21 : "**`Такой пользователь не найден`**",
                22 : "**`Пожалуйста, подождите перед повторным использованием команды`**",
                23 : "**`У Ваc недостаточно прав для использования этой команды`**",
                24 : f"**Роль модератора экономики не выбрана! Пользователь с правами админитратора или управляющего сервером должен сделать это при помощи `{prefix}mod_role` `role_id`**",
                40 : "**`Такая роль не найдена`**",
                41 : "**`Такой канал не найден`**"
            }
        }
        

    def mod_role_set(self, ctx: commands.Context) -> bool:
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                r = cur.execute("SELECT count() FROM mod_roles").fetchone()
                if r is None or r[0] == 0:
                    return False
                return True
    

    def mod_check(ctx: commands.Context) -> bool:
        u = ctx.author
        if u.guild_permissions.administrator or u.guild_permissions.manage_guild:
            return True

        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                m_rls = cur.execute("SELECT * FROM mod_roles").fetchall()
                if m_rls:
                    m_rls = {x[0] for x in m_rls}
                    return any(role.id in m_rls for role in u.roles)
                return False

    
    def mod_check_intr(interaction) -> bool:
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


    def check(self, base: Connection, cur: Cursor, memb_id: int):
        member = cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()
        if member is None:
            cur.execute('INSERT INTO users(memb_id, money, owned_roles, work_date, xp) VALUES(?, ?, ?, ?, ?)', (memb_id, 0, "", 0, 0))
            base.commit()
        else:
            if member[1] is None or member[1] < 0:
                cur.execute('UPDATE users SET money = ? WHERE memb_id = ?', (0, memb_id))
                base.commit()
            if member[2] is None:
                cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', ("", memb_id))
                base.commit()
            if member[3] is None:
                cur.execute('UPDATE users SET work_date = ? WHERE memb_id = ?', (0, memb_id))
                base.commit()
            if member[4] is None:
                cur.execute('UPDATE users SET xp = ? WHERE memb_id = ?', (0, memb_id))
                base.commit()
        return cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()


    async def guide(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        emb = Embed(title=guide[lng][0])
        for i in range(1, 20, 2):
            emb.add_field(name=guide[lng][i], value=guide[lng][i+1], inline=False)
        await interaction.response.send_message(embed=emb)


    async def help(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0

        emb1 = Embed(title=text_help_view[lng][0], description=text_help_view[lng][4])
        emb2 = Embed(description=text_help_view[lng][5])
        emb3 = Embed(description=text_help_view[lng][6])
        emb4 = Embed(title=text_help_view[lng][1])
        for n, v in u_ec_cmds[lng]:
            emb1.add_field(name=n, value=v, inline=False)
        for n, v in u_pers_cmds[lng]:
            emb2.add_field(name=n, value=v, inline=False)
        for n, v in u_other_cmds[lng]:
            emb3.add_field(name=n, value=v, inline=False)
        for n, v in m_cmds[lng]:
            emb4.add_field(name=n, value=v, inline=False)
        await interaction.response.send_message(embeds=[emb1, emb2, emb3, emb4])
            

    @slash_command(
        name="guide",
        description="show guide about bot's system",
        description_localizations={
            Locale.ru: "показывает гайд о системе бота"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    async def guide_e(self, interaction: Interaction):
        await self.guide(interaction)


    @slash_command(
        name="guide",
        description="показывает гайд о системе бота",
        description_localizations={
            Locale.en_GB: "show guide about bot's system",
            Locale.en_US: "show guide about bot's system"
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    async def guide_r(self, interaction: Interaction):
        await self.guide(interaction)


    @slash_command(
        name="help", 
        description="Calls menu with commands",
        description_localizations={
            Locale.ru : "Вызывает меню команд"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    async def help_e(self, interaction: Interaction):
        await self.help(interaction=interaction)
    

    @slash_command(
        name="help", 
        description="Вызывает меню команд",
        description_localizations={
            Locale.en_GB: "Calls menu with commands",
            Locale.en_US: "Calls menu with commands"
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    async def help_r(self, interaction: Interaction):
        await self.help(interaction=interaction)


    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        lng = 1 if "ru" in ctx.guild.preferred_locale else 0
        emb=Embed(title=text[lng][404],colour=Colour.red())
        if isinstance(error, commands.MemberNotFound):
            emb.description = text[lng][18]
            """elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            try:
                emb.description = text[lng][19].format(self.prefix, str(ctx.command)[1:])
            except:
                emb.description = text[lng][19].format(self.prefix, "name_of_the_command") """

        elif isinstance(error, commands.CommandNotFound):
            return
            #emb.description = text[lng][20]
        elif isinstance(error, commands.UserNotFound):
            emb.description = text[lng][21]
        elif isinstance(error, commands.RoleNotFound):
            emb.description = text[lng][40]
        elif isinstance(error, commands.ChannelNotFound):
            emb.description = text[lng][41]
        elif isinstance(error, commands.CommandOnCooldown):
            emb.description = text[lng][22]
        elif isinstance(error, CheckFailure):
            if self.mod_role_set(ctx=ctx):
                emb.description = text[lng][23]
            else:
                emb.description = text[lng][24]
        else:
            #raise error
            with open("error.log", "a+", encoding="utf-8") as f:
                f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [{ctx.guild.id}] [{ctx.guild.name}] [{str(error)}]\n")
            return
        await ctx.reply(embed=emb, mention_author=False)
  
def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(mod_commands(bot, **kwargs))
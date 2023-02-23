import re
from asyncio import (
    sleep,
    TimeoutError
)
from typing import (
    Optional,
    Union,
    Tuple,
    Dict
)

from contextlib import closing
from sqlite3 import connect
from os import urandom

from nextcord import (
    Embed,
    Emoji,
    Interaction,
    Permissions,
    ButtonStyle,
    Message,
    Member,
    Guild
)
if __debug__:
    from nextcord import Role
    from typing import Callable

from storebot import StoreBot
from Tools.db_commands import (
    get_member_async,
    delete_role_from_db,
    get_server_info_value_async,
    get_server_slots_table_async,
    get_server_currency_async,
    drop_users_cash_async,
    update_server_info_table_uncheck_async
)
from Tools.parse_tools import parse_emoji
from Variables.vars import CWD_PATH
from CustomComponents.custom_button import CustomButton
from CustomComponents.custom_select import CustomSelect
from CustomComponents.select_ic_view import SelectICView
from CustomComponents.view_base import ViewBase
from CustomComponents.verification_view import VerificationView
from CustomModals.custom_modals import (
    RoleAddModal,
    RoleEditModal,
    XpSettingsModal,
    SelectLevelModal,
    ManageMemberCashXpModal,
    OneTextInputModal
)
from CustomComponents.select_channel_view import SelectChannelView
from CustomModals.sale_role_price import SalePriceModal
from CustomModals.voice_income_modal import VoiceIncomeModal
from CustomComponents.slots_manage_view import SlotsManageView


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
        0 : [("English", "0"), ("Russian", "1")],
        1 : [("английский", "0"), ("русский", "1")]
    },
    "English" : 0,
    "английский" : 0,
    "Russian" : 1,
    "русский" : 1
}

system_status: Dict[int, Dict[int, str]] = {
    0 : {
        0 : "`disabled`",
        1 : "`enabled`",
        2 : "`enable`",
        3 : "`disable`",
        4 : "`disabled`",
        5 : "`enabled`",
    },
    1 : {
        0 : "`отключена`",
        1 : "`включена`",
        2 : "`включить`",
        3 : "`выключить`",
        4 : "`отключили`",
        5 : "`включили`",
    }
}

settings_text: Dict[int, Dict[int, str]] = {
    0 : {
        2 : "Select role",
        3 : "Adding role",
        4 : "Add role",
        5 : "Remove role",
        6 : "**`You hasn't selected the role yet`**",
        7 : "`Ping` member or write member's `id`\n\nWrite `cancel` to cancel the menu",
        8 : "Add channel",
        9 : "Remove channel",
        10 : "Select channel",
        11 : "**`Select channel`**",
        12 : "Not selected",
        13 : "```fix\nnot selected\n```",
        14 : "**`This role not found on the server. Please try to recall the command`**"
    },
    1 : {
        2 : "Выберите роль",
        3 : "Добавление роли",
        4 : "Добавить роль",
        5 : "Убрать роль",
        6 : "**`Вы не выбрали роль`**",
        7 : "Напишите `id` участника сервера или `пинганите` его\n\nНапишите `cancel` для отмены",
        8 : "Добавить канал",
        9 : "Убрать канал",
        10 : "Выберите канал",
        11 : "**`Выберите канал`**",
        12 : "Не выбрано",
        13 : "```fix\nне выбран\n```",
        14 : "**`Эта роль не найдена на сервере. Пожалуйста, попробуйте вызвать команду снова`**"
    }
}

gen_settings_text: Dict[int, Dict[int, str]] = {
    0 : {
        0 : "🗣️ language for new level announcements: {}",
        1 : "⏱ time zone: UTC{}",
        2 : "💵 server money emoji: {}",
        3 : "💰 economy system is {}",
        4: "📈 leveling system is {}",
        5: "tap 🗣️ to change language",
        6: "tap ⏱ to change time zone",
        7 : "tap 💵 to change money emoji",
        8: "tap 💰 to {} economy system",
        9 : "tap 📈 to {} leveling system",
        20 : "Select new language",
        21 : "Select new time zone",
        22 : "**`You hasn't selected the language yet`**",
        23 : "**`You hasn't selected time zone yet`**",
        24 : "**`New time zone: UTC{}`**",
        25 : "**`New language for new level announcements: {}`**",
        26 : "**`This language is already selected as language for new level announcements`**",
        27 : "**You {} economy system**",
        28 : "**You {} leveling system**",
        29 : "**Print `emoji` or it's `id`. In order to select emoji that you can't use, you can print it's `id`**",
        30 : "**`New money emoji is `**{}"
    },
    1 : {
        0 : "🗣️ язык сообщений для оповещений о новом уровне: {}",
        1 : "⏱ часовой пояс: UTC{}",
        2 : "💵 эмодзи валюты сервера: {}",
        3 : "💰 экономическая система: {}",
        4 : "📈 уровневая система: {}",
        5 : "нажмите 🗣️, чтобы изменить язык",
        6 : "нажмите ⏱, чтобы изменить часовой пояс",
        7 : "нажмите 💵, чтобы изменить эмодзи валюты сервера",
        8 : "нажмите 💰, чтобы {} экономическую систему",
        9 : "нажмите 📈, чтобы {} уровневую систему",
        20 : "Выбрать новый язык",
        21 : "Выбрать новый часовой пояс",
        22 : "**`Вы не выбрали язык`**",
        23 : "**`Вы не выбрали часовой пояс`**",
        24 : "**`Новый часовой пояс сервера: UTC{}`**",
        25 : "**`Новый язык сообщений для оповещений о новом уровне: {}`**",
        26 : "**`Этот язык уже выбран в качестве языка для оповещений о новом уровне`**",
        27 : "**Вы {} экономическую систему**",
        28 : "**Вы {} уровневую систему**",
        29 : "**Напишите `эмодзи` или его `id`. Если надо указать эмодзи, которое Вы не можете использовать, Вы можете указать `id`**",
        30 : "**`Новое эмодзи валюты сервера: `**{}"
    }
}

mod_roles_text: Dict[int, Dict[int, str]] = {
    0 : {
        0 : "Current mod roles",
        1 : "No roles selected",
        2 : "__**role - id**__",
        7 : "**`This role already in the list`**",
        8 : "**`Role `**{}**` was added to the list`**",
        9 : "**`This role is not in the list`**",
        10 : "**`Role `**{}**` was removed from the list`**",
        11 : "**`Sorry, but you can't manage menu called by another user`**"
    },
    1 : {
        0 : "Текущие мод роли",
        1 : "Не выбрано ни одной роли",
        2 : "__**роль - id**__",
        7 : "**`Эта роль уже в списке`**",
        8 : "**`Роль `**{}**` добавлена в список`**",
        9 : "**`Этой роли нет в списке`**",
        10 : "**`Роль `**{}**` убрана из списока`**",
        11 : "**`Извините, но Вы не можете управлять меню, которое вызвано другим пользователем`**"
    }
}

ec_text: Dict[int, Dict[int, str]] = {
    0 : {
        0 : "Economy settings",
        1: "💸 Money gained for message:\n**`{}`** {}",
        2: "⏰ Cooldown for `/work`:\n**`{} seconds`**",
        3: "💹 Salary from `/work`:\n**`{}`** {}",
        4: "random integer from {} to {}",
        5: "🎤 Income from presenting in voice channel (for ten minutes):\n**`{}`** {}",
        6: "🛍️ Sale price of the role, from the purchase price: **`{}`** %",
        7: "📙 Log channel for economic operations:\n{}",
        8: "> To manage setting press button with corresponding emoji",
        9: "> To see and manage roles available for purchase/sale in the bot press 🛠️",
        10: "**`Write amount of money gained for message (non negative integer number)`**",
        11: "Amount of money gained from messages set to: **`{}`** {}",
        12: "Write cooldown for `/work` command **in seconds** (integer from 60 to 604800)\nFor example, to make cooldown equalt to 240 seconds, write `240` in the chat",
        13: "Cooldown for `/work` set to: **`{}`** seconds",
        14: "Write salary from `/work`:\nTwo non-negative numbers, second at least as much as first\nSalary will be random integer \
            between them\nIf you want salary to constant write one number\nFor example, if you write `1` `100` then salary \
            will be random integer from `1` to `100`\nIf you write `10`, then salary will always be `10`",
        15: "**`Now salary is {}`** {}",
        16: "Select channel",
        17: "**`You chose channel`** {}",
        18: "**`Timeout expired`**",
        19: "__**role - role id - price - salary - cooldown for salary in hours - type - how much in the store - additional income from /work**__",
        20: "No roles were added",
        21: "`If role isn't shown in the menu(s) down below it means that bot can't manage this role`",
        22: "**`You reseted log channel`**",
        23: "**`Are you sure you want to drop cash of all members on the server? This operation can not be undone`**",
        24: "**`You dropped cash for all members`**",
        25: "**`You rejected operation`**"
    },
    1 : {
        0: "Настройки экономики",
        1: "💸 Количество денег, получаемых за сообщение:\n**`{}`** {}",
        2: "⏰ Кулдаун для команды `/work`:\n**`{} секунд`**",
        3: "💹 Доход от команды `/work`:\n**`{}`** {}",
        4: "рандомное целое число от {} до {}",
        5: "🎤 Доход от присутствия в голосовом канале (доход указан за 10 минут):\n**`{}`** {}",
        6: "🛍️ Цена роли при продаже, от цены покупки: **`{}`** %",
        7: "📙 Канал для логов экономических операций:\n{}",
        8: "> Для управления настройкой нажмите на кнопку с соответствующим эмодзи",
        9: "> Для просмотра и управления ролями, доступными для покупки/продажи у бота, нажмите 🛠️",
        10: "**`Укажите количество денег, получаемых за сообщение\n(неотрицательное целое число)`**",
        11: "Количество денег, получаемых за одно сообщение, теперь равно: **`{}`** {}",
        12: "Укажите кулдаун для команды `/work` **в секундах** (целое число от 60 до 604800)\nНапример, чтобы поставить кулдаун 240 секунд, напишите в чат `240`",
        13: "Кулдаун для команды `/work` теперь равен: **`{}`** секунд",
        14: "Укажите заработок от команды `/work`:\nДва неотрицательных числа, второе не менее первого\nЗаработок будет \
            рандомным целым числом между ними\nЕсли Вы хотите сделать заработок постоянным, укажите одно число\nНапример, \
            если Вы укажите `1` `100`, то заработок будет рандомным целым числом от `1` до `100`\nЕсли Вы укажите `10`, то \
            заработок всегда будет равен `10`",
        15: "**`Теперь заработок: {}`** {}",
        16: "Выберите канал",
        17: "**`Вы выбрали канал`** {}",
        18: "**`Время ожидания вышло`**",
        19: "__**роль - id роли - цена - заработок - кулдаун заработка в часах - тип - сколько в магазине - дополнительный заработок от /work**__",
        20: "Не добавлено ни одной роли",
        21: "`Если роль не отображается ни в одном меню снизу, значит, бот не может управлять ею`",
        22: "**`Вы сбросили канал логов`**",
        23: "**`Вы уверены, что хотите сбросить кэш всех пользователей на сервере? Эта операция не может быть отменена`**",
        24: "**`Вы сбросили кэш всех участников сервера`**",
        25: "**`Вы отменили операцию сброса кэша`**"
    }
}

ec_mr_text: Dict[int, Dict[int, str]] = { 
    0 : {
        0 : "Edit role",
        1 : "Yes",
        2 : "No",
        3 : "**`You declined removing the role `**<@&{}>",
        4 : "**`Please, wait a bit...`**",
        5 : "**`You removed role `**<@&{}>",
        6 : "Are you sure you want to delete role <@&{}> from the bot's settings?\nAll information about it will be deleted and it will be withdrawn from the store",
        7 : "**`You can't remove role that is not in the list`**",
        8 : "**`You can't edit role that is not in the list`**",
        9 : "**`This role is already in the list`**",
    },
    1 : {
        0 : "Редактировать роль",
        1 : "Да",
        2 : "Нет",
        3 : "**`Вы отменили удаление роли `**<@&{}>",
        4 : "**`Пожалуйста, подождите...`**",
        5 : "**`Вы удалили роль `**<@&{}>",
        6 : "Вы уверены, что хотите удалить роль <@&{}> из настроек бота?\nВся информация о ней будет удалена и она будет изъята из магазина",
        7 : "**`Вы не можете убрать роль, которая не неходится в списке`**",
        8 : "**`Вы не можете редактировать роль, которая не неходится в списке`**",
        9 : "**`Эта роль уже находится в списке`**",
    }
}

mng_membs_text: Dict[int, Dict[int, str]] = {
    0 : {
        0 : "Change cash/xp",
        1 : "Cash",
        2 : "Xp",
        3 : "Level",
        4 : "Place in the rating",
        5 : "**`Information about member `**<@{}>**`\nwith id {}`**",
        6 : "**`Member doesn't have any roles from the bot's store`**",
        7 : "**`Member already has this role`**",
        8 : "**`You added role `**<@&{}>**` to the `**<@{}>",
        9 : "**`Member doesn't have this role`**",
        10 : "**`You removed role`**<@&{}>**` from the `**<@{}>",
        11 : "Cash of the member",
        12 : "Write a non-negative integer number",
        13 : "Xp of the member",
        14 : "**`Member's cash should be a non-negative integer number`**",
        15 : "**`Member's xp should be a non-negative integer number`**",
        16 : "**`You changed information about member `**<@{}>**` Now member's cash is {} and xp is {}`**",
        17 : "**`You changed information about member `**<@{}>**` Now member's cash is {}`**",
        18 : "**`You changed information about member `**<@{}>**` Now member's xp is {}`**",
        19 : "Member management menu"
        
    },
    1 : {
        0 : "Изменить кэш/опыт",
        1 : "Кэш",
        2 : "Опыт",
        3 : "Уровень",
        4 : "Место в рейтинге",
        5 : "**`Информация о пользователе `**<@{}>**`\nс id {}`**",
        6 : "**`У пользователя нет ролей из магазина бота`**",
        7 : "**`Эта роль уже есть у пользователя`**",
        8 : "**`Вы добавили роль `**<@&{}>**` пользователю `**<@{}>",
        9 : "**`Этой роли нет у пользователя`**",
        10 : "**`Вы убрали роль `**<@&{}>**` у пользователя `**<@{}>",
        11 : "Кэш пользователя",
        12 : "Напишите целое неотрицательное число",
        13 : "Опыт пользователя",
        14 : "**`Кэш пользователя должен быть целым неотрицательным числом`**",
        15 : "**`Опыт пользователя должен быть целым неотрицательным числом`**",
        16 : "**`Вы изменили данные пользователя `**<@{}>**` Теперь кэш пользователя - {}, а опыт - {}`**",
        17 : "**`Вы изменили данные пользователя `**<@{}>**` Теперь кэш пользователя - {}`**",
        18 : "**`Вы изменили данные пользователя `**<@{}>**` Теперь опыт пользователя - {}`**",
        19 : "Меню управления пользователем"
    }
}

poll_text: Dict[int, Dict[int, str]] = {
    0 : {
        0 : "🔎 Polls verification channel:\n{}",
        1 : "📰 Channel for publishing polls:\n{}",
        2 : "> **`Press `**🔎**` to change polls`**\n> **`verifcation channel`**",
        3 : "> **`Press `**📰**` to change channel`**\n> **`for publishing polls`**",
        4 : "**`New polls verification channel is `**<#{}>",
        5 : "**`You reseted polls verification channel`**",
        6 : "**`New channel for publishing polls is `**<#{}>",
        7 : "**`You reseted channel for publishing polls`**",

    },
    1 : {
        0 : "🔎 Канал для верификации поллов:\n{}",
        1 : "📰 Канал для публикации поллов:\n{}",
        2 : "> **`Нажмите `**🔎**`, чтобы изменить канал`**\n> **`для верификации поллов`**",
        3 : "> **`Нажмите `**📰**`, чтобы изменить канал`**\n> **`для публикации поллов`**",
        4 : "**`Новый канал для верификации поллов: `**<#{}>",
        5 : "**`Вы сбросили канал для верификации поллов`**",
        6 : "**`Новый канал для публикации поллов: `**<#{}>",
        7 : "**`Вы сбросили канал для публикации поллов`**",
    }
}

ranking_text: Dict[int, Dict[int, str]] = {
    0 : {
        0 : "✨ Xp gained per message:\n**`{}`**",
        1 : "✨ Amount of xp between adjacent levels:\n**`{}`**",
        2 : "📗 Channel for the notification about new levels:\n{}",
        4 : "> To manage setting press button with corresponding emoji\n",
        6 : "> Press 🥇 to manage roles given for levels",
        24 : "level",
        25 : "**`No roles matched for levels`**",
        26 : "Roles for level",
        27 : "**`Press `**<:add01:999663315804500078>🔧**`to add / change role for the level`**\n**`Press `**<:remove01:999663428689997844>**` to remove role for the level`**",
        29 : "**`Select role for level {}`**",
        30 : "**`Bot can't give any role on the server`**",
        31 : "**`From now role given for the level {} is `**<@&{}>",
        32 : "**`Timeout has expired`**",
        33 : "**`You removed role for level {}`**",
        34 : "**`No roles matches level {}`**",
    },
    1 : {
        0 : "✨ Опыт, получаемый за одно сообщение:\n**`{}`**",
        1 : "✨ Количество опыта между соседними уровнями:\n**`{}`**",
        2 : "📗 Канал для оповещений о получении нового уровня:\n{}",
        4 : "> Для управления настройкой нажмите на кнопку с соответствующим эмодзи\n",
        6 : "> Нажмите 🥇 для управления ролями, выдаваемыми за уровни",
        24 : "уровень",
        25 : "**`Роли за уровни не назначены`**",
        26 : "Роли за уровни",
        27 : "**`Нажмите `**<:add01:999663315804500078>🔧**`, чтобы добавить / изменить роль за уровень`**\n**`Нажмите `**<:remove01:999663428689997844>**`, чтобы убрать роль за уровень`**",
        29 : "**`Выберите роль для уровня {}`**",
        30 : "**`Бот не может выдать ни одной роли на сервере`**",
        31 : "**`Теперь за уровень {} выдаётся роль `**<@&{}>",
        32 : "**`Время истекло`**",
        33 : "**`Вы убрали роль за уровень {}`**",
        34 : "**`Уровню {} не соответствует ни одна роль`**",
    }
}

code_blocks: dict[int, str] = {
    0 : "```\nOwned roles\n```",
    5 : "```\nЛичные роли\n```",
    1 : "```fix\n{}\n```",
    2 : "```c\n{}\n```",
}


class GenSettingsView(ViewBase):
    def __init__(self, t_out: int, auth_id: int, bot: StoreBot, lng: int, ec_status: int, rnk_status: int) -> None:
        super().__init__(lng=lng, author_id=auth_id, timeout=t_out)
        self.bot: StoreBot = bot
        self.lang: Optional[int] = None
        self.tz: Optional[int] = None
        self.ec_status: int = ec_status
        self.rnk_status: int = rnk_status
        tzs: list[tuple[str, str]] = [(f"UTC{i}", str(i)) for i in range(-12, 0)] + [(f"UTC+{i}", str(i)) for i in range(0, 13)]
        self.add_item(CustomSelect(custom_id=f"100_{auth_id}_" + urandom(4).hex(), placeholder=gen_settings_text[lng][20], options=languages[2][lng]))
        self.add_item(CustomSelect(custom_id=f"101_{auth_id}_" + urandom(4).hex(), placeholder=gen_settings_text[lng][21], options=tzs))
        self.add_item(CustomButton(style=ButtonStyle.green, label="", custom_id=f"6_{auth_id}_" + urandom(4).hex(), emoji="🗣️"))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label="", custom_id=f"7_{auth_id}_" + urandom(4).hex(), emoji="⏱"))
        self.add_item(CustomButton(style=ButtonStyle.gray, label="", custom_id=f"42_{auth_id}_" + urandom(4).hex(), emoji="💵"))
        self.add_item(CustomButton(style=ButtonStyle.red, label="", custom_id=f"43_{auth_id}_" + urandom(4).hex(), emoji="💰", row=2))
        self.add_item(CustomButton(style=ButtonStyle.red, label="", custom_id=f"44_{auth_id}_" + urandom(4).hex(), emoji="📈", row=2))
        
    async def select_lng(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        s_lng: Optional[int] = self.lang
        lng: int = self.lng
        if s_lng is None:
            await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][22]), ephemeral=True)
            return

        g_id: int = interaction.guild_id
        with closing(connect(f"{CWD_PATH}/bases/bases_{g_id}/{g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                if cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0] == s_lng:
                    await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][26]), ephemeral=True)
                    return
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'lang'", (s_lng,))
                base.commit()
        
        s_lng_nm: str = languages[lng][s_lng]
        
        assert interaction.message is not None
        emb: Embed = interaction.message.embeds[0]
        assert emb.description is not None
        dsc: list[str] = emb.description.split("\n")
        dsc[0] = gen_settings_text[lng][0].format(s_lng_nm)
        emb.description = "\n".join(dsc)
        await interaction.message.edit(embed=emb)

        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][25].format(s_lng_nm)), ephemeral=True)
        self.lang = None
    
    async def digit_tz(self, interaction: Interaction) -> None:
        tz: Optional[int] = self.tz
        lng: int = self.lng
        if tz is None:
            await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][23]), ephemeral=True)
            return
        with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'tz'", (tz,))
                base.commit()
        
        assert interaction.message is not None
        formatted_tz: str =  f"+{tz}" if tz >= 0 else str(tz)
        emb: Embed = interaction.message.embeds[0]
        assert emb.description is not None
        dsc: list[str] = emb.description.split("\n")
        dsc[1] = gen_settings_text[lng][1].format(formatted_tz)
        emb.description = "\n".join(dsc)
        await interaction.message.edit(embed=emb)

        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][24].format(formatted_tz)), ephemeral=True)
        self.tz = None

    async def change_currency(self, interaction: Interaction) -> None:
        lng: int = self.lng
        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][29]), ephemeral=True)
        try:
            user_ans: Message = await self.bot.wait_for(event="message", check=lambda m: m.channel.id == interaction.channel_id and m.author.id == self.author_id, timeout=25)
        except TimeoutError:
            return
        else:
            user_ans_content: str = user_ans.content
            emoji: Optional[Union[Emoji, str]] = parse_emoji(self.bot, user_ans_content)
            if emoji is None:
                emoji_str: str = user_ans_content
            elif isinstance(emoji, Emoji):
                emoji_str: str = emoji.__str__()
            else:
                emoji_str: str = emoji

            with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("UPDATE server_info SET str_value = ? WHERE settings = 'currency'", (emoji_str,))
                    base.commit()

            assert interaction.message is not None
            emb: Embed = interaction.message.embeds[0]
            assert emb.description is not None
            dsc: list[str] = emb.description.split("\n")
            dsc[2] = gen_settings_text[lng][2].format(emoji_str)
            emb.description = "\n".join(dsc)
            await interaction.message.edit(embed=emb)

            try:
                await interaction.edit_original_message(embed=Embed(description=gen_settings_text[lng][30].format(emoji_str)))
            except:
                pass

    async def change_ec_system(self, interaction: Interaction) -> None:
        self.ec_status ^= 1
        with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'economy_enabled'", (self.ec_status,))
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'mn_per_msg'", (self.ec_status,))
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'mn_for_voice'", (self.ec_status*6,))
                base.commit()

        assert interaction.message is not None
        emb: Embed = interaction.message.embeds[0]
        assert emb.description is not None
        dsc: list[str] = emb.description.split("\n")
        lng: int = self.lng
        dsc[3] = gen_settings_text[lng][3].format(system_status[lng][self.ec_status])
        dsc[8] = gen_settings_text[lng][8].format(system_status[lng][self.ec_status+2])
        emb.description = "\n".join(dsc)
        await interaction.message.edit(embed=emb)

        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][27].format(system_status[lng][self.ec_status+4])), ephemeral=True)

    async def change_rnk_system(self, interaction: Interaction) -> None:
        self.rnk_status ^= 1
        with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'ranking_enabled'", (self.rnk_status,))
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'xp_per_msg'", (self.rnk_status,))
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'xp_for_voice'", (self.rnk_status*6,))
                base.commit()
        
        assert interaction.message is not None
        emb: Embed = interaction.message.embeds[0]
        assert emb.description is not None
        dsc: list[str] = emb.description.split("\n")
        lng: int = self.lng
        dsc[4] = gen_settings_text[lng][4].format(system_status[lng][self.rnk_status])
        dsc[9] = gen_settings_text[lng][9].format(system_status[lng][self.rnk_status+2])
        emb.description = "\n".join(dsc)
        await interaction.message.edit(embed=emb)
            
        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][28].format(system_status[lng][self.rnk_status+4])), ephemeral=True)

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        match custom_id[:2]:
            case "6_":
                await self.select_lng(interaction=interaction)
            case "7_":
                await self.digit_tz(interaction=interaction)
            case "42":
                await self.change_currency(interaction=interaction)
            case "43":
                await self.change_ec_system(interaction=interaction)
            case "44":
                await self.change_rnk_system(interaction=interaction)

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        if custom_id.startswith("100_"):
            self.lang = int(values[0])
        elif custom_id.startswith("101_"):
            self.tz = int(values[0])


class ModRolesView(ViewBase):
    def __init__(self, t_out: int, m_rls: set[int], lng: int, auth_id: int, rem_dis: bool, rls: list[tuple[str, str]]) -> None:
        super().__init__(lng=lng, author_id=auth_id, timeout=t_out)
        self.m_rls: set[int] = m_rls
        self.role: Optional[int] = None
        for i in range((len(rls) + 24) // 25):
            self.add_item(CustomSelect(
                custom_id=f"{200+i}_{auth_id}_" + urandom(4).hex(),
                placeholder=settings_text[lng][2],
                options=rls[(i * 25):(min(len(rls), (i + 1) * 25))]
            ))
        self.add_item(CustomButton(style=ButtonStyle.green, label=settings_text[lng][4], emoji="<:add01:999663315804500078>", custom_id=f"8_{auth_id}_" + urandom(4).hex()))
        self.add_item(CustomButton(style=ButtonStyle.red, label=settings_text[lng][5], emoji="<:remove01:999663428689997844>", custom_id=f"9_{auth_id}_" + urandom(4).hex(), disabled=rem_dis))
    

    async def add_role(self, interaction: Interaction) -> None:
        assert interaction.message is not None
        assert self.role is not None
        rl_id: int = self.role
        lng: int = self.lng
        if rl_id in self.m_rls:
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][7]), ephemeral=True)
            return       
                
        with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("INSERT OR IGNORE INTO mod_roles(role_id) VALUES(?)", (rl_id,))
                base.commit()

        self.m_rls.add(rl_id)
        
        emb: Embed = interaction.message.embeds[0]
        assert emb.description is not None
        dsc: list[str] = emb.description.split("\n")
        if len(self.m_rls) == 1:
            assert isinstance(self.children[-1], CustomButton)
            self.children[-1].disabled = False
            emb.description = f"{mod_roles_text[lng][2]}\n<@&{rl_id}> - {rl_id}"
            await interaction.message.edit(view=self, embed=emb)
        else:
            dsc.append(f"<@&{rl_id}> - {rl_id}")
            emb.description = "\n".join(sorted(dsc))
            await interaction.message.edit(embed=emb)

        self.role = None
        await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][8].format(f"<@&{rl_id}>")), ephemeral=True)
    
    async def rem_role(self, interaction: Interaction) -> None:
        assert interaction.message is not None
        assert self.role is not None
        rl_id: int = self.role
        lng: int = self.lng
        if not rl_id in self.m_rls:
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][9]), ephemeral=True)
            return
        
        with closing(connect(f'{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                cur.execute("DELETE FROM mod_roles WHERE role_id = ?", (rl_id,))
                base.commit()
        self.m_rls.remove(rl_id)
        emb: Embed = interaction.message.embeds[0]

        if self.m_rls:
            assert emb.description is not None
            dsc: list[str] = emb.description.split("\n")
            dsc.remove(f"<@&{rl_id}> - {rl_id}")
            emb.description = "\n".join(sorted(dsc))
            await interaction.message.edit(embed=emb)
        else:
            assert isinstance(self.children[-1], CustomButton)
            self.children[-1].disabled = True
            emb.description = mod_roles_text[lng][1]
            await interaction.message.edit(embed=emb, view=self)

        self.role = None        
        await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][10].format(f"<@&{rl_id}>")), ephemeral=True)

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert interaction.guild is not None
        lng: int = self.lng
        if self.role is None:
            await interaction.response.send_message(embed=Embed(description=settings_text[lng][6]), ephemeral=True)
            return

        if interaction.guild.get_role(self.role):
            if custom_id.startswith("8_"):
                await self.add_role(interaction=interaction)
            elif custom_id.startswith("9_"):
                await self.rem_role(interaction=interaction)
        else:
            await interaction.response.send_message(
                embed=Embed(description=settings_text[lng][14]),
                ephemeral=True
            )

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        if custom_id.startswith("20") and custom_id[3] == "_":
            self.role = int(values[0])


class EconomyView(ViewBase):
    r_types: Dict[int, Dict[int, str]] = {
        0 : {
            1 : "Nonstacking, displayed separated",
            2 : "Stacking, countable",
            3 : "Stacking, infinite"
        },
        1 : {
            1 : "Нестакающаяся, отображается отдельно",
            2 : "Cтакающаяся, конечная",
            3 : "Cтакающаяся, бесконечная"
        }
    }
    money_per_message_modal_text: dict[int, dict[int, str]] = {
        0: {
            0: "Money per message",
            1: "Amount of money gained by member for message",
            2: "Amount of money gained by member for one message (non-negative integer number)",
            3: "**`Amount of money gained by member for one message set to: {0}`** {1}",
            4: "**`Money gained by member for one message should be non-negative integer number`**"
        },
        1: {
            0: "Заработок за сообщение",
            1: "Количество валюты, получаемой за сообщение",
            2: "Количество валюты, получаемой пользователем за одно сообщение (целое неотрицательное число)",
            3: "**`Количество валюты, получаемой пользователем за одно сообщение, теперь равно: {0}`** {1}",
            4: "**`Количество валюты, получаемой пользователем за одно сообщение, должно быть целым неотрицательным числом`**"
        }
    }

    def __init__(self, lng: int, author_id: int, timeout: int, sale_price_percent: int, voice_income: int, currency: str, bot: StoreBot) -> None:
        super().__init__(lng=lng, author_id=author_id, timeout=timeout)
        self.sale_price_percent: int = sale_price_percent
        self.voice_income: int = voice_income
        self.currency: str = currency
        self.bot: StoreBot = bot
        self.add_item(CustomButton(style=ButtonStyle.blurple, label="", custom_id=f"10_{author_id}_" + urandom(4).hex(), emoji="💸"))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label="", custom_id=f"11_{author_id}_" + urandom(4).hex(), emoji="⏰"))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label="", custom_id=f"12_{author_id}_" + urandom(4).hex(), emoji="💹"))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label="", custom_id=f"45_{author_id}_" + urandom(4).hex(), emoji="🎤"))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label="", custom_id=f"46_{author_id}_" + urandom(4).hex(), emoji="🛍️"))
        self.add_item(CustomButton(style=ButtonStyle.green, label="", custom_id=f"13_{author_id}_" + urandom(4).hex(), emoji="📙"))
        self.add_item(CustomButton(style=ButtonStyle.red, label="", custom_id=f"47_{author_id}_" + urandom(4).hex(), emoji="0️⃣"))
        self.add_item(CustomButton(style=ButtonStyle.red, label="", custom_id=f"14_{author_id}_" + urandom(4).hex(), emoji="🛠️"))

    async def msg_salary(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        lng: int = self.lng
        modal_text: dict[int, str] = self.money_per_message_modal_text[lng]
        money_per_message_modal: OneTextInputModal = \
            OneTextInputModal(modal_text[0], modal_text[1], modal_text[2], 1, 6)
        await interaction.response.send_modal(money_per_message_modal)
        await money_per_message_modal.wait()

        user_input: str | None = money_per_message_modal.value
        if not user_input:
            return

        if user_input.isdigit():
            await update_server_info_table_uncheck_async(interaction.guild_id, "mn_per_msg", user_input)
            
            assert interaction.message is not None
            emb: Embed = interaction.message.embeds[0]
            assert emb.description is not None
            dsc: list[str] = emb.description.split("\n\n")
            dsc[0] = ec_text[lng][1].format(user_input, self.currency)
            emb.description = "\n\n".join(dsc)
            try:
                await interaction.message.edit(embed=emb)
            except:
                pass

            await interaction.followup.send(embed=Embed(description=modal_text[3].format(user_input, self.currency)), ephemeral=True)
        else:
            await interaction.followup.send(embed=Embed(description=modal_text[4]), ephemeral=True)

    async def work_cldwn(self, interaction: Interaction, ans: str) -> bool:
        if ans.isdigit() and 60 <= (work_command_cooldown := int(ans)) <= 604800:
            lng: int = self.lng

            with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'w_cd'", (work_command_cooldown,))
                    base.commit()
            try:
                await interaction.edit_original_message(embed=Embed(description=ec_text[lng][13].format(ans)))
            except:
                pass
            
            assert interaction.message is not None
            emb: Embed = interaction.message.embeds[0]
            assert emb.description is not None
            dsc: list[str] = emb.description.split("\n\n")
            dsc[1] = ec_text[lng][2].format(ans)
            emb.description = "\n\n".join(dsc)
            await interaction.message.edit(embed=emb)
            return False
        else:
            return True

    async def work_salary(self, interaction: Interaction, ans: str) -> bool:
        splitted_ans: list[str] = ans.split()
        fl: bool = False
        n1: int = 0
        n2: int = 0
        if len(splitted_ans) >= 2:
            arg1: str = splitted_ans[0]
            arg2: str = splitted_ans[1]
            if arg1.isdigit() and arg2.isdigit():
                n1 = int(arg1)
                n2 = int(arg2)
                if 0 <= n1 <= n2:
                    fl = True
        elif len(splitted_ans):
            arg: str = splitted_ans[0]
            if arg.isdigit() and (n1 := int(arg)) >= 0:
                n2 = n1
                fl = True
        if fl:
            lng: int = self.lng

            with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'sal_l'", (n1,))
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'sal_r'", (n2,))
                    base.commit()
            
            assert interaction.message is not None
            emb: Embed = interaction.message.embeds[0]
            assert emb.description is not None
            dsc: list[str] = emb.description.split("\n\n")
            if n1 == n2:
                try:
                    await interaction.edit_original_message(embed=Embed(description=ec_text[lng][15].format(n1, self.currency)))
                except:
                    pass
                dsc[2] = ec_text[lng][3].format(n1, self.currency)
            else:
                try:
                    await interaction.edit_original_message(embed=Embed(description=ec_text[lng][15].format(ec_text[lng][4].format(n1, n2), self.currency)))
                except:
                    pass
                dsc[2] = ec_text[lng][3].format(ec_text[lng][4].format(n1, n2), self.currency)
            
            emb.description = "\n\n".join(dsc)
            await interaction.message.edit(embed=emb)

            return False
        else:
            return True

    async def update_voice_income(self, interaction: Interaction) -> None:
        lng: int = self.lng
        voice_income_modal: VoiceIncomeModal = VoiceIncomeModal(
            timeout=30,
            lng=lng,
            auth_id=self.author_id,
            voice_income=self.voice_income
        )
        await interaction.response.send_modal(voice_income_modal)

        await voice_income_modal.wait()
        if (new_voice_income := voice_income_modal.voice_income) != self.voice_income:
            self.voice_income = new_voice_income
            assert interaction.message is not None
            emb: Embed = interaction.message.embeds[0]
            assert emb.description is not None
            descript_lines: list[str] = emb.description.split("\n\n")
            descript_lines[3] = ec_text[lng][5].format(new_voice_income, self.currency)
            emb.description = "\n\n".join(descript_lines)
            await interaction.message.edit(embed=emb)
    
    async def update_sale_role_price(self, interaction: Interaction) -> None:
        lng: int = self.lng
        sale_price_modal: SalePriceModal = SalePriceModal(
            timeout=40,
            lng=lng,
            auth_id=self.author_id,
            current_sale_role_percent=self.sale_price_percent
        )
        await interaction.response.send_modal(sale_price_modal)

        await sale_price_modal.wait()
        if (new_sale_percent := sale_price_modal.new_sale_role_percent) is not None:
            self.sale_price_percent = new_sale_percent
            assert interaction.message is not None
            emb: Embed = interaction.message.embeds[0]
            assert emb.description is not None
            descript_lines: list[str] = emb.description.split("\n\n")
            descript_lines[4] = ec_text[lng][6].format(new_sale_percent)
            emb.description = "\n\n".join(descript_lines)
            await interaction.message.edit(embed=emb)

    async def log_chnl(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.message is not None
        lng: int = self.lng
        
        guild_self_bot: Member = interaction.guild.me
        verify_permissions: Callable[[Permissions], bool] = \
            lambda permissions: permissions.read_message_history and permissions.read_messages and permissions.send_messages
        channels_options: list[tuple[str, str]] = [(c.name, c.id.__str__()) for c in interaction.guild.text_channels if verify_permissions(c.permissions_for(guild_self_bot))]

        select_channel_view: SelectChannelView = SelectChannelView(lng, self.author_id, 40, channels_options)
        await interaction.response.send_message(embed=Embed(description=settings_text[lng][11]), view=select_channel_view, ephemeral=True)
        await select_channel_view.wait()

        try:
            await interaction.delete_original_message()
        except:
            pass

        if (channel_id := select_channel_view.channel_id) is None:
            return

        guild_id: str = str(interaction.guild_id)
        with closing(connect(CWD_PATH + f"/bases/bases_{guild_id}/{guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'log_c'", (channel_id,))
                base.commit()
        
        emb: Embed = interaction.message.embeds[0]
        assert emb.description is not None
        dsc: list[str] = emb.description.split("\n\n")
        dsc[5] = ec_text[lng][7].format(f"<#{channel_id}>") if channel_id else ec_text[lng][7].format(settings_text[lng][13])
        emb.description = "\n\n".join(dsc)
        await interaction.message.edit(embed=emb)

        try:
            if channel_id:
                await interaction.edit_original_message(embed=Embed(description=ec_text[lng][17].format(f"<#{channel_id}>")))
            else:
                await interaction.edit_original_message(embed=Embed(description=ec_text[lng][22]))
        except:
            return

    async def manage_economy_roles(self, interaction: Interaction) -> None:
        lng: int = self.lng
        server_roles_ids: set[int] = set()
        with closing(connect(f'{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                roles: list[tuple[int, int, int, int, int, int]] = cur.execute(
                    "SELECT role_id, price, salary, salary_cooldown, type, additional_salary FROM server_roles"
                ).fetchall()
                if roles:
                    descr: list[str] = [ec_text[lng][19]]
                    for role in roles:
                        role_id: int = role[0]
                        server_roles_ids.add(role_id)
                        if role[4] == 1:
                            cnt: str = str(cur.execute("SELECT count() FROM store WHERE role_id = ?", (role_id,)).fetchone()[0])
                        else:
                            quantity_in_store: Optional[tuple[int]] = cur.execute("SELECT quantity FROM store WHERE role_id = ?", (role_id,)).fetchone()
                            if not quantity_in_store:
                                cnt: str = "0"
                            elif role[4] == 2:
                                cnt: str = str(quantity_in_store[0])
                            else:
                                cnt: str = "∞"
                        descr.append(
                            f"<@&{role_id}> - **`{role_id}`** - **`{role[1]}`** - **`{role[2]}`** - **`{role[3]//3600}`** - **`{self.r_types[lng][role[4]]}`** - **`{cnt}`** - **`{role[5]}`**"
                        )
                else:
                    descr: list[str] = [ec_text[lng][20]]
        descr.append('\n' + ec_text[lng][21])
        
        assert interaction.guild is not None
        guild: Guild = interaction.guild
        assignable_and_boost_roles: list[tuple[str, str]] = [(r.name, str(r.id)) for r in guild.roles if r.is_assignable() or r.is_premium_subscriber()]
        remove_role_button_is_disabled: bool = False if assignable_and_boost_roles else True
        ec_rls_view: EconomyRolesManageView = EconomyRolesManageView(
            t_out=155,
            lng=lng,
            auth_id=self.author_id,
            rem_dis=remove_role_button_is_disabled,
            assignable_and_boost_roles=assignable_and_boost_roles,
            server_roles_ids=server_roles_ids
        )
        await interaction.response.send_message(embed=Embed(description='\n'.join(descr)), view=ec_rls_view)
        await ec_rls_view.wait()
        for child_component in ec_rls_view.children:
            assert isinstance(child_component, (CustomButton, CustomSelect))
            child_component.disabled = True
        try:
            await interaction.edit_original_message(view=ec_rls_view)
        except:
            pass

    async def drop_users_cash(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        assert interaction.locale is not None
        self.lng
        verification_view: VerificationView = VerificationView(self.author_id)
        await interaction.response.send_message(embed=Embed(description=ec_text[self.lng][23]), view=verification_view)
        await verification_view.wait()
        try:
            await interaction.delete_original_message()
        except:
            pass
        
        if verification_view.approved:
            await drop_users_cash_async(interaction.guild_id)
            await interaction.followup.send(embed=Embed(description=ec_text[self.lng][24]), ephemeral=True)
        else:
            await interaction.followup.send(embed=Embed(description=ec_text[self.lng][25]), ephemeral=True)

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert interaction.channel_id is not None
        int_custom_id: int = int(custom_id[:2])
        match int_custom_id:
            case 10:
                await self.msg_salary(interaction)
            case 13:
                await self.log_chnl(interaction)
            case 14:
                await self.manage_economy_roles(interaction)
            case 45:
                await self.update_voice_income(interaction)
            case 46:
                await self.update_sale_role_price(interaction)
            case 47:
                await self.drop_users_cash(interaction)
            case _:
                assert int_custom_id in {11, 12}
                await interaction.response.send_message(embed=Embed(description=ec_text[self.lng][10 + ((int_custom_id - 10) << 1)]), ephemeral=True)
                flag: bool = True
                author_id: int = self.author_id
                channel_id: int = interaction.channel_id
                while flag:
                    user_ans: Message
                    try:
                        user_ans = await self.bot.wait_for(
                            event="message",
                            check=lambda m: m.author.id == author_id and m.channel.id == channel_id,
                            timeout=40.0
                        )
                    except TimeoutError:
                        flag = False
                    else:
                        match int_custom_id:
                            case 11: 
                                flag = await self.work_cldwn(interaction=interaction, ans=user_ans.content)
                            case 12: 
                                flag = await self.work_salary(interaction=interaction, ans=user_ans.content)
                        try:
                            await user_ans.delete()
                        except:
                            pass

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return


class EconomyRolesManageView(ViewBase):
    def __init__(self, t_out: int, lng: int, auth_id: int, rem_dis: bool, assignable_and_boost_roles: list[tuple[str, str]], server_roles_ids: set[int]) -> None:
        super().__init__(lng=lng, author_id=auth_id, timeout=t_out)
        self.server_roles_ids: set[int] = server_roles_ids
        self.role: Optional[int] = None
        length: int = len(assignable_and_boost_roles)
        for i in range(min((length + 24) // 25, 4)):
            self.add_item(CustomSelect(
                custom_id=f"{800 + i}",
                placeholder=settings_text[lng][2],
                options=assignable_and_boost_roles[(i * 25):min(length, (i + 1) * 25)]
            ))
        self.add_item(CustomButton(style=ButtonStyle.green, label=settings_text[lng][4], emoji="<:add01:999663315804500078>", custom_id=f"15_{auth_id}_" + urandom(4).hex()))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label=ec_mr_text[lng][0], emoji="🔧", custom_id=f"16_{auth_id}_" + urandom(4).hex(), disabled=rem_dis))
        self.add_item(CustomButton(style=ButtonStyle.red, label=settings_text[lng][5], emoji="<:remove01:999663428689997844>", custom_id=f"17_{auth_id}_" + urandom(4).hex(), disabled=rem_dis))
    
    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert interaction.message is not None
        assert isinstance(interaction.user, Member)
        lng: int = self.lng

        if self.role is None:
            await interaction.response.send_message(embed=Embed(description=settings_text[lng][6]), ephemeral=True)
            return

        match int(custom_id[:2]):
            case 17:
                role_id: int = self.role
                if role_id not in self.server_roles_ids:
                    await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][7]), ephemeral=True)
                    return
                v_d: VerifyDeleteView = VerifyDeleteView(lng=lng, role=role_id, m=interaction.message, auth_id=interaction.user.id)
                await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][6].format(role_id)), view=v_d)
                
                if await v_d.wait():
                    for child_component in v_d.children:
                        assert isinstance(child_component, CustomButton)
                        child_component.disabled = True
                    try:
                        await interaction.edit_original_message(view=v_d)
                    except:
                        pass

                if v_d.deleted:
                    self.server_roles_ids.remove(role_id)
                    self.role = None
            case 15:
                role_id: int = self.role
                if role_id in self.server_roles_ids:
                    await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][9]), ephemeral=True)
                    return
                add_mod: RoleAddModal = RoleAddModal(
                    timeout=90,
                    lng=lng,
                    role=role_id,
                    message=interaction.message,
                    auth_id=interaction.user.id
                )
                await interaction.response.send_modal(modal=add_mod)
                
                await add_mod.wait()
                if add_mod.added:
                    self.server_roles_ids.add(role_id)
                    self.role = None
            case 16:
                role_id: int = self.role
                if not role_id in self.server_roles_ids:
                    await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][8]), ephemeral=True)
                    return
                
                with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                    with closing(base.cursor()) as cur:
                        req: tuple[int, int, int, int, int, int] = cur.execute(
                            "SELECT role_id, price, salary, salary_cooldown, type, additional_salary FROM server_roles WHERE role_id = ?", 
                            (role_id,)
                        ).fetchone()
                        role_type: int = req[4]
                        if role_type != 2:
                            role_in_store_count: int = cur.execute("SELECT count() FROM store WHERE role_id = ?", (role_id,)).fetchone()[0]
                        else:
                            quantity: tuple[int] = cur.execute("SELECT quantity FROM store WHERE role_id = ?", (role_id,)).fetchone()                        
                            role_in_store_count: int = quantity[0] if quantity else 0
                
                edit_mod: RoleEditModal = RoleEditModal(
                    timeout=90,
                    role=role_id,
                    message=interaction.message,
                    lng=lng,
                    auth_id=self.author_id,
                    price=req[1],
                    salary=req[2],
                    salary_cooldown=req[3],
                    r_t=role_type,
                    additional_salary=req[5],
                    in_store=role_in_store_count
                )
                await interaction.response.send_modal(modal=edit_mod)
                await edit_mod.wait()
                if edit_mod.changed:
                    self.role = None

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        if custom_id.startswith("80"):
            self.role = int(values[0])


class SettingsView(ViewBase):
    member_id_pattern: re.Pattern[str] = re.compile(r"\d+", flags=re.RegexFlag.MULTILINE | re.RegexFlag.IGNORECASE)

    def __init__(self, lng: int, author_id: int, timeout: int, bot: StoreBot) -> None:
        super().__init__(lng=lng, author_id=author_id, timeout=timeout)
        self.bot: StoreBot = bot
        self.add_item(CustomButton(style=ButtonStyle.red, label=None, custom_id=f"0_{author_id}_" + urandom(4).hex(), emoji="⚙️"))
        self.add_item(CustomButton(style=ButtonStyle.red, label=None, custom_id=f"1_{author_id}_" + urandom(4).hex(), emoji="<:moder:1000090629897998336>"))
        self.add_item(CustomButton(style=ButtonStyle.red, label=None, custom_id=f"2_{author_id}_" + urandom(4).hex(), emoji="<:user:1002245779089535006>"))
        self.add_item(CustomButton(style=ButtonStyle.green, label=None, custom_id=f"3_{author_id}_" + urandom(4).hex(), emoji="💰", row=2))
        self.add_item(CustomButton(style=ButtonStyle.green, label=None, custom_id=f"4_{author_id}_" + urandom(4).hex(), emoji="📈", row=2))
        self.add_item(CustomButton(style=ButtonStyle.green, label=None, custom_id=f"64_{author_id}_" + urandom(4).hex(), emoji="🎰", row=2))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label=None, custom_id=f"54_{author_id}_" + urandom(4).hex(), emoji="🚫", row=3))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label=None, custom_id=f"5_{author_id}_" + urandom(4).hex(), emoji="📊", row=3))
    
    @classmethod
    def check_ans(cls, guild: Guild, ans: str) -> Tuple[Optional[Member], bool]:
        for member_id in cls.member_id_pattern.findall(ans):
            if member := guild.get_member(int(member_id)):
                return member, False
        if ans == "cancel":
            return None, False
        return None, True

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert isinstance(interaction.user, Member)
        lng: int = self.lng
        guild_id: int = interaction.guild_id
        author_id: int = self.author_id
        int_custom_id: int = int(custom_id.split('_')[0])
        match int_custom_id:
            case 0:
                with closing(connect(f'{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db')) as base:
                    with closing(base.cursor()) as cur:
                        s_lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                        tz: int = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]
                        currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
                        ec_status: int = cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]
                        rnk_status: int = cur.execute("SELECT value FROM server_info WHERE settings = 'ranking_enabled'").fetchone()[0]

                dsc = [gen_settings_text[lng][0].format(languages[lng][s_lng])]
                if tz >= 0:
                    dsc.append(gen_settings_text[lng][1].format(f"+{tz}"))
                else:
                    dsc.append(gen_settings_text[lng][1].format(f"{tz}"))
                dsc.append(gen_settings_text[lng][2].format(currency))
                dsc.append(gen_settings_text[lng][3].format(system_status[lng][ec_status]))
                dsc.append(gen_settings_text[lng][4].format(system_status[lng][rnk_status]))
                dsc.extend(gen_settings_text[lng][i] for i in (5, 6, 7))
                dsc.append(gen_settings_text[lng][8].format(system_status[lng][ec_status+2]))
                dsc.append(gen_settings_text[lng][9].format(system_status[lng][rnk_status+2]))
                
                gen_view: GenSettingsView = GenSettingsView(
                    t_out=50,
                    auth_id=author_id,
                    bot=self.bot,
                    lng=lng,
                    ec_status=ec_status,
                    rnk_status=rnk_status
                )
                await interaction.response.send_message(embed=Embed(description="\n".join(dsc)), view=gen_view)
                await gen_view.wait()
                for child_component in gen_view.children:
                    assert isinstance(child_component, (CustomSelect, CustomButton))
                    child_component.disabled = True
                try:
                    await interaction.edit_original_message(view=gen_view)
                except:
                    pass

            case 1:
                with closing(connect(f'{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db')) as base:
                    with closing(base.cursor()) as cur:
                        db_m_rls: list[tuple[int]] = cur.execute("SELECT role_id FROM mod_roles").fetchall()
                emb = Embed(title=mod_roles_text[lng][0])
                if db_m_rls:
                    m_rls: set[int] = {x[0] for x in db_m_rls}
                    emb.description = "\n".join([mod_roles_text[lng][2]] + [f"<@&{i}> - {i}" for i in m_rls])
                    rem_dis: bool = False
                    del db_m_rls
                else:
                    emb.description=mod_roles_text[lng][1]
                    m_rls: set[int] = set()
                    rem_dis: bool = True

                rls: list[tuple[str, str]] = [(r.name, str(r.id)) for r in interaction.guild.roles if not r.is_bot_managed()]
                m_rls_v: ModRolesView = ModRolesView(
                    t_out=50,
                    m_rls=m_rls,
                    lng=lng,
                    auth_id=author_id,
                    rem_dis=rem_dis,
                    rls=rls
                )
                await interaction.response.send_message(embed=emb, view=m_rls_v)
                await m_rls_v.wait()
                for child_component in m_rls_v.children:
                    assert isinstance(child_component, (CustomSelect, CustomButton))
                    child_component.disabled = True
                try:
                    await interaction.edit_original_message(view=m_rls_v)
                except:
                    pass
            
            case 2:
                await interaction.response.send_message(embed=Embed(description=settings_text[lng][7]))
                try_get_member_flag: bool = True
                memb: Optional[Member] = None
                while try_get_member_flag:
                    try:
                        message_answer: Message = await interaction.client.wait_for(
                            event="message",
                            check=lambda m: m.author.id == author_id and m.channel.id == interaction.channel_id,
                            timeout=30
                        )
                    except TimeoutError:
                        try_get_member_flag = False
                    else:
                        memb, try_get_member_flag = self.check_ans(guild=interaction.guild, ans=message_answer.content)
                        try: 
                            await message_answer.delete()
                        except:
                            pass
                try:
                    await interaction.delete_original_message()
                except:
                    pass
                
                if memb is None:
                    return
                
                memb_id: int = memb.id
                memb_info: tuple[int, int, str, int, int, int] = await get_member_async(guild_id=guild_id, member_id=memb_id)
                
                with closing(connect(f'{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db')) as base:
                    with closing(base.cursor()) as cur:
                        xp_b: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
                        membs_cash: list[tuple[int, int]] = cur.execute("SELECT memb_id, money FROM users ORDER BY money DESC;").fetchall()
                        membs_xp: list[tuple[int, int]] = cur.execute("SELECT memb_id, xp FROM users ORDER BY xp DESC;").fetchall()
                        db_roles: list[tuple[int]] = cur.execute("SELECT role_id FROM server_roles").fetchall()

                l: int = len(membs_cash)     

                # cnt_cash is a place in the rating sorded by cash
                cash: int = memb_info[1]
                if membs_cash[l >> 1][1] < cash:
                    cnt_cash: int = 1
                    while cnt_cash < l and memb_id != membs_cash[cnt_cash-1][0]:
                        cnt_cash += 1
                else:
                    cnt_cash: int = l
                    while cnt_cash > 1 and memb_id != membs_cash[cnt_cash-1][0]:
                        cnt_cash -= 1

                emb1: Embed = Embed()
                emb1.description = mng_membs_text[lng][5].format(memb_id, memb_id)
                emb1.add_field(name=mng_membs_text[lng][1], value=code_blocks[1].format(cash), inline=True)
                emb1.add_field(name=mng_membs_text[lng][4], value=code_blocks[1].format(cnt_cash), inline=True)

                # cnt_cash is a place in the rating sorded by xp
                xp: int = memb_info[4]
                if membs_xp[l >> 1][1] < xp:
                    cnt_xp: int = 1
                    while cnt_xp < l and memb_id != membs_xp[cnt_xp-1][0]:
                        cnt_xp += 1
                else:
                    cnt_xp: int = l
                    while cnt_xp > 1 and memb_id != membs_xp[cnt_xp-1][0]:
                        cnt_xp -= 1

                level: int = (xp + xp_b - 1) // xp_b
                
                emb2: Embed = Embed()
                emb2.add_field(name=mng_membs_text[lng][2], value=code_blocks[2].format(f"{xp}/{level * xp_b + 1}"), inline=True)
                emb2.add_field(name=mng_membs_text[lng][3], value=code_blocks[2].format(level), inline=True)
                emb2.add_field(name=mng_membs_text[lng][4], value=code_blocks[2].format(cnt_xp), inline=True)

                emb3: Embed = Embed()
                member_roles_ids: set[int] = {int(r) for r in memb_info[2].split("#") if r.isdigit()}
                if member_roles_ids:
                    dsc = [code_blocks[lng*5]] + [f"<@&{r}>**` - {r}`**" for r in member_roles_ids]
                else:
                    dsc = [mng_membs_text[lng][6]]
                emb3.description = "\n".join(dsc)
                rem_dis: bool = True if len(dsc) == 1 else False

                if db_roles:
                    db_roles_set: set[int] = {x[0] for x in db_roles}
                    roles: list[tuple[str, str]] = [(rl.name, str(rl.id)) for rl in interaction.guild.roles if rl.is_assignable() and rl.id in db_roles_set]
                    del db_roles_set
                else:
                    roles: list[tuple[str, str]] = [(rl.name, str(rl.id)) for rl in interaction.guild.roles if rl.is_assignable()]
                del db_roles

                mng_v: ManageMemberView = ManageMemberView(
                    timeout=110, 
                    lng=lng, 
                    auth_id=author_id, 
                    memb_id=memb_id, 
                    memb_rls=member_roles_ids, 
                    rls=roles,
                    cur_money=cash,
                    cur_xp=xp,
                    rem_dis=rem_dis,
                    g_id=guild_id,
                    member=memb
                )
                
                await interaction.send(embeds=[emb1, emb2, emb3], view=mng_v)
                await mng_v.wait()
                for child_component in mng_v.children:
                    assert isinstance(child_component, (CustomButton, CustomSelect))
                    child_component.disabled = True
                try:
                    await interaction.edit_original_message(view=mng_v)
                except:
                    pass

            case 3:
                with closing(connect(f'{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db')) as base:
                    with closing(base.cursor()) as cur:
                        money_p_m: int = cur.execute("SELECT value FROM server_info WHERE settings = 'mn_per_msg';").fetchone()[0]
                        w_cd: int = cur.execute("SELECT value FROM server_info WHERE settings = 'w_cd';").fetchone()[0]
                        sal_l: int = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_l';").fetchone()[0]
                        sal_r: int = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_r';").fetchone()[0]
                        e_l_c: int = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c';").fetchone()[0]
                        sale_price_percent: int = cur.execute("SELECT value FROM server_info WHERE settings = 'sale_price_perc';").fetchone()[0]
                        voice_income: int = cur.execute("SELECT value FROM server_info WHERE settings = 'mn_for_voice';").fetchone()[0]
                        currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency';").fetchone()[0]

                emb: Embed = Embed(title=ec_text[lng][0])
                dsc: list[str] = [ec_text[lng][1].format(money_p_m, currency)]
                dsc.append(ec_text[lng][2].format(w_cd))
                if sal_l == sal_r:
                    dsc.append(ec_text[lng][3].format(sal_l, currency))
                else:
                    dsc.append(ec_text[lng][3].format(ec_text[lng][4].format(sal_l, sal_r), currency))
                dsc.append(ec_text[lng][5].format(voice_income, currency))
                dsc.append(ec_text[lng][6].format(sale_price_percent))
                if e_l_c:
                    dsc.append(ec_text[lng][7].format(f"<#{e_l_c}>"))
                else:
                    dsc.append(ec_text[lng][7].format(settings_text[lng][13]))
                dsc.append(ec_text[lng][8])
                dsc.append(ec_text[lng][9])
                emb.description = "\n\n".join(dsc)
                
                ec_v: EconomyView = EconomyView(
                    lng=lng, 
                    author_id=self.author_id,
                    timeout=110,
                    sale_price_percent=sale_price_percent,
                    voice_income=voice_income,
                    currency=currency,
                    bot=self.bot
                )
                await interaction.response.send_message(embed=emb, view=ec_v)
                await ec_v.wait()
                for child_component in ec_v.children:
                    assert isinstance(child_component, (CustomButton, CustomSelect))
                    child_component.disabled = True
                try:
                    await interaction.edit_original_message(view=ec_v)
                except:
                    pass

            case 4:
                with closing(connect(f'{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db')) as base:
                    with closing(base.cursor()) as cur:
                        xp_p_m: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_per_msg'").fetchone()[0]
                        xp_b: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
                        lvl_c_a: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lvl_c'").fetchone()[0]

                emb = Embed()
                dsc = [ranking_text[lng][0].format(xp_p_m)]
                dsc.append(ranking_text[lng][1].format(xp_b))
                if lvl_c_a == 0:
                    dsc.append(ranking_text[lng][2].format(settings_text[lng][13]))
                else:
                    dsc.append(ranking_text[lng][2].format(f"<#{lvl_c_a}>"))
                dsc.extend(ranking_text[lng][i] for i in (4, 6))

                emb.description = "\n\n".join(dsc)
                rnk_v: RankingView = RankingView(
                    lng=lng,
                    author_id=author_id,
                    timeout=90,
                    g_id=guild_id,
                    cur_xp_pm=xp_p_m,
                    cur_xpb=xp_b,
                    bot=self.bot
                )
                
                await interaction.response.send_message(embed=emb, view=rnk_v)

                await rnk_v.wait()
                for child_component in rnk_v.children:
                    assert isinstance(child_component, (CustomButton, CustomSelect))
                    child_component.disabled = True
                try:
                    await interaction.edit_original_message(view=rnk_v)
                except:
                    pass

            case 5:
                with closing(connect(f'{CWD_PATH}/bases/bases_{guild_id}/{guild_id}.db')) as base:
                    with closing(base.cursor()) as cur:
                        p_v_c: int = cur.execute("SELECT value FROM server_info WHERE settings = 'poll_v_c'").fetchone()[0]
                        p_c: int = cur.execute("SELECT value FROM server_info WHERE settings = 'poll_c'").fetchone()[0]
                
                if p_v_c:
                    dsc = [poll_text[lng][0].format(f"<#{p_v_c}>")]
                else:
                    dsc = [poll_text[lng][0].format(settings_text[lng][13])]
                if p_c:
                    dsc.append(poll_text[lng][1].format(f"<#{p_c}>"))
                else:
                    dsc.append(poll_text[lng][1].format(settings_text[lng][13]))
                dsc.append(poll_text[lng][2])
                dsc.append(poll_text[lng][3])

                p_v: PollSettingsView = PollSettingsView(lng=lng, author_id=author_id, timeout=100)
                await interaction.response.send_message(embed=Embed(description="\n\n".join(dsc)), view=p_v)
                
                await p_v.wait()
                for child_component in p_v.children:
                    assert isinstance(child_component, CustomButton)
                    child_component.disabled = True
                try:
                    await interaction.edit_original_message(view=p_v)
                except:
                    pass
            
            case 54:
                emb = Embed(description=SelectICView.select_ignored_channels_text[lng][0])
                select_ic_view: SelectICView = SelectICView(
                    lng=lng,
                    author_id=author_id,
                    timeout=90,
                    g_id=guild_id,
                    bot=self.bot
                )
                
                await interaction.response.send_message(embed=emb, view=select_ic_view)
                await select_ic_view.wait()
                try:
                    await interaction.delete_original_message()
                except:
                    pass
            
            case 64:
                slots_enabled: int = await get_server_info_value_async(guild_id=guild_id, key_name="slots_on")
                slots_table: dict[int, int] = await get_server_slots_table_async(guild_id=guild_id)
                currency: str = await get_server_currency_async(guild_id=guild_id)
                emb: Embed = Embed(description=SlotsManageView.slots_manage_view_text[lng][0].format(
                    '\n'.join("**`{0}`{2} : `{1}`**{2}".format(bet, income, currency) for bet, income in slots_table.items())
                ))
                slots_manage_view: SlotsManageView = SlotsManageView(
                    lng=lng,
                    author_id=author_id,
                    slots_enabled=slots_enabled,
                    slots_table=slots_table,
                    currency=currency
                )

                await interaction.response.send_message(embed=emb, view=slots_manage_view)
                await slots_manage_view.wait()
                try:
                    await interaction.delete_original_message()
                except:
                    pass

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return

class PollSettingsView(ViewBase):
    def __init__(self, lng: int, author_id: int, timeout: int) -> None:
        super().__init__(lng=lng, author_id=author_id, timeout=timeout)
        self.add_item(CustomButton(style=ButtonStyle.green, custom_id=f"28_{author_id}_" + urandom(4).hex(), emoji="🔎"))
        self.add_item(CustomButton(style=ButtonStyle.green, custom_id=f"29_{author_id}_" + urandom(4).hex(), emoji="📰"))
    
    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert interaction.guild is not None
        lng: int = self.lng

        guild_self_bot: Member = interaction.guild.me
        verify_permissions: Callable[[Permissions], bool] = \
            lambda permissions: permissions.read_message_history and permissions.read_messages and permissions.send_messages
        channels_options: list[tuple[str, str]] = [(c.name, c.id.__str__()) for c in interaction.guild.text_channels if verify_permissions(c.permissions_for(guild_self_bot))]

        int_custom_id: int = int(custom_id[:2])
        if int_custom_id == 28:
            v_c: PollsChannelsView = PollsChannelsView(timeout=25, lng=lng, view_id_base=1400, auth_id=self.author_id, chnls=channels_options)
        else:
            v_c: PollsChannelsView = PollsChannelsView(timeout=25, lng=lng, view_id_base=1500, auth_id=self.author_id, chnls=channels_options)

        await interaction.response.send_message(embed=Embed(description=settings_text[lng][11]), view=v_c)
        await v_c.wait()
        try:
            await interaction.delete_original_message()
        except:
            return

        new_channel_id: Optional[int] = v_c.channel_id
        if new_channel_id is None:
            return

        assert interaction.message is not None
        emb: Embed = interaction.message.embeds[0]
        assert emb.description is not None
        dsc: list[str] = emb.description.split("\n\n")

        if int_custom_id == 28:            
            if new_channel_id:
                with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                    with closing(base.cursor()) as cur:
                        cur.execute("UPDATE server_info SET value = ? WHERE settings = 'poll_v_c'", (new_channel_id,))
                        base.commit()                
                dsc[0] = poll_text[lng][0].format(f"<#{new_channel_id}>")
                emb.description = "\n\n".join(dsc)
                try:
                    await interaction.message.edit(embed=emb)
                except:
                    pass

                await interaction.send(embed=Embed(description=poll_text[lng][4].format(new_channel_id)), ephemeral=True)         
            else:
                with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                    with closing(base.cursor()) as cur:
                        cur.execute("UPDATE server_info SET value = 0 WHERE settings = 'poll_v_c'")
                        base.commit()
                dsc[0] = poll_text[lng][0].format(settings_text[lng][13])
                emb.description = "\n\n".join(dsc)
                try:
                    await interaction.message.edit(embed=emb)
                except:
                    pass

                await interaction.send(embed=Embed(description=poll_text[lng][5]), ephemeral=True)
        elif int_custom_id == 29:
            if new_channel_id:
                with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                    with closing(base.cursor()) as cur:
                        cur.execute("UPDATE server_info SET value = ? WHERE settings = 'poll_c'", (new_channel_id,))
                        base.commit()                
                dsc[1] = poll_text[lng][1].format(f"<#{new_channel_id}>")
                emb.description = "\n\n".join(dsc)
                try:
                    await interaction.message.edit(embed=emb)
                except:
                    pass

                await interaction.send(embed=Embed(description=poll_text[lng][6].format(new_channel_id)), ephemeral=True)
            else:
                with closing(connect(f"{CWD_PATH}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                    with closing(base.cursor()) as cur:
                        cur.execute("UPDATE server_info SET value = 0 WHERE settings = 'poll_c'")
                        base.commit()
                dsc[1] = poll_text[lng][1].format(settings_text[lng][13])
                emb.description = "\n\n".join(dsc)
                try:
                    await interaction.message.edit(embed=emb)
                except:
                    pass

                await interaction.send(embed=Embed(description=poll_text[lng][7]), ephemeral=True)

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return

class RankingView(ViewBase):
    def __init__(self, lng: int, author_id: int, timeout: int, g_id: int, cur_xp_pm: int, cur_xpb: int, bot: StoreBot) -> None:
        super().__init__(lng=lng, author_id=author_id, timeout=timeout)
        self.add_item(CustomButton(style=ButtonStyle.green, label="", emoji="✨", custom_id=f"21_{author_id}_" + urandom(4).hex()))
        self.add_item(CustomButton(style=ButtonStyle.grey, label="", emoji="📗", custom_id=f"22_{author_id}_" + urandom(4).hex()))
        self.add_item(CustomButton(style=ButtonStyle.red, label="", emoji="🥇", custom_id=f"24_{author_id}_" + urandom(4).hex()))
        self.cur_xp_pm: int = cur_xp_pm
        self.cur_xpb: int = cur_xpb
        self.g_id: int = g_id
        self.lvl_chnl: Optional[int] = None
        self.bot: StoreBot = bot
    
    async def xp_change(self, interaction: Interaction) -> None:
        lng: int = self.lng
        xp_m: XpSettingsModal = XpSettingsModal(timeout=80, lng=lng, auth_id=self.author_id, g_id=self.g_id, cur_xp=self.cur_xp_pm, cur_xpb=self.cur_xpb)
        await interaction.response.send_modal(modal=xp_m)
        await xp_m.wait()

        if xp_m.changed:
            self.cur_xp_pm = xp_m.new_xp
            self.cur_xpb = xp_m.new_xp_b

            assert interaction.message is not None
            emb: Embed = interaction.message.embeds[0]
            assert emb.description is not None
            dsc: list[str] = emb.description.split("\n\n")
            dsc[0] = ranking_text[lng][0].format(self.cur_xp_pm)
            dsc[1] = ranking_text[lng][1].format(self.cur_xpb)
            emb.description = "\n\n".join(dsc)
            try:
                await interaction.message.edit(embed=emb)
            except:
                pass

    async def level_channel(self, interaction: Interaction) -> None:
        assert interaction.guild is not None
        assert interaction.message is not None
        lng: int = self.lng
        
        guild_self_bot: Member = interaction.guild.me
        verify_permissions: Callable[[Permissions], bool] = \
            lambda permissions: permissions.read_message_history and permissions.read_messages and permissions.send_messages
        channels_options: list[tuple[str, str]] = [(c.name, c.id.__str__()) for c in interaction.guild.text_channels if verify_permissions(c.permissions_for(guild_self_bot))]

        level_channel_select_view: SelectChannelView = SelectChannelView(lng, self.author_id, 30, channels_options)
        await interaction.response.send_message(embed=Embed(description=settings_text[lng][11]), view=level_channel_select_view, ephemeral=True)
        await level_channel_select_view.wait()

        try:
            await interaction.delete_original_message()
        except:
            pass

        if (level_channel_id := level_channel_select_view.channel_id) is None:
            return
        
        with closing(connect(CWD_PATH + f"/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'lvl_c'", (level_channel_id,))
                base.commit()
        
        emb: Embed = interaction.message.embeds[0]
        assert emb.description is not None
        dsc: list[str] = emb.description.split("\n\n")
        dsc[2] = ranking_text[lng][2].format(f"<#{level_channel_id}>") if level_channel_id else ranking_text[lng][2].format(settings_text[lng][13])
        emb.description = "\n\n".join(dsc)

        try:
            await interaction.message.edit(embed=emb)
        except:
            return
            
    async def lvl_roles(self, interaction: Interaction) -> None:
        assert isinstance(interaction.user, Member)
        lng: int = self.lng
        with closing(connect(CWD_PATH + f"/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                lvl_rls: list[tuple[int, int]] = cur.execute("SELECT level, role_id FROM rank_roles ORDER BY level ASC").fetchall()
        if lvl_rls:
            dsc: list[str] = [f"**`{n} {ranking_text[lng][24]} - `**<@&{r}>" for n, r in lvl_rls]
            rem_b: bool = False
        else:
            dsc: list[str] = [ranking_text[lng][25]]
            rem_b: bool = True
        dsc.append(ranking_text[lng][27])
        emb: Embed = Embed(title=ranking_text[lng][26], description="\n".join(dsc))
        lr_v: LevelRolesView = LevelRolesView(
            lng=lng,
            author_id=interaction.user.id,
            timeout=80,
            g_id=self.g_id,
            disabled=rem_b
        )
        await interaction.response.send_message(embed=emb, view=lr_v)
        await lr_v.wait()
        try:
            await interaction.delete_original_message()
        except:
            return

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        match int(custom_id[:2]):
            case 21:
                await self.xp_change(interaction=interaction)
            case 22:
                await self.level_channel(interaction=interaction)
            case 24:
                await self.lvl_roles(interaction=interaction)
    
    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return


class PollsChannelsView(ViewBase):
    def __init__(self, timeout: int, lng: int, view_id_base: int, auth_id: int, chnls: list[tuple[str, str]]) -> None:
        super().__init__(lng=lng, author_id=auth_id, timeout=timeout)
        
        for i in range(min(((length := len(chnls)) + 23) // 24, 5)):
            self.add_item(CustomSelect(
                custom_id=f"{view_id_base + i}_{auth_id}_" + urandom(4).hex(), 
                placeholder=settings_text[lng][10], 
                options=[(settings_text[lng][12], "0")] + chnls[(i*24):min(length, (i + 1)*24)]
            ))

        self.select_menus_id_start: int = view_id_base // 100
        self.channel_id: Optional[int] = None
    
    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        if int(custom_id[:2]) == self.select_menus_id_start:
            self.channel_id = int(values[0])
            self.stop()

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        return


class LevelRolesView(ViewBase):
    def __init__(self, lng: int, author_id: int, timeout: int, g_id: int, disabled: bool) -> None:
        super().__init__(lng=lng, author_id=author_id, timeout=timeout)

        self.add_item(CustomButton(
            style=ButtonStyle.green,
            label="🔧",
            custom_id=f"27_{author_id}_" + urandom(4).hex(),
            emoji="<:add01:999663315804500078>"
        ))
        self.add_item(CustomButton(
            style=ButtonStyle.red,
            label="",
            custom_id=f"28_{author_id}_" + urandom(4).hex(),
            emoji="<:remove01:999663428689997844>",
            disabled=disabled
        ))

        self.g_id: int = g_id
        self.role: Optional[int] = None
    
    async def add_role(self, interaction: Interaction, lng: int, level: int) -> None:
        assert interaction.guild is not None
        rls: list[tuple[str, str]] = [(r.name, r.id.__str__()) for r in interaction.guild.roles if r.is_assignable()]
        if not rls:
            await interaction.send(embed=Embed(description = ranking_text[lng][30]), ephemeral=True)
            return
        
        for i in range(min(((length := len(rls)) + 24) // 25, 4)):
            self.add_item(CustomSelect(
                custom_id=f"{1300 + i}_{self.author_id}_" + urandom(4).hex(), 
                placeholder=settings_text[lng][2], 
                options=rls[(i*25):min(length, (i + 1)*25)]
            ))

        assert interaction.message is not None
        try:
            await interaction.message.edit(view=self)
        except:
            pass
        await interaction.send(embed=Embed(description = ranking_text[lng][29].format(level)), ephemeral=True)

        cnt: int = 0
        while self.role is None and cnt < 25:
            cnt += 1
            await sleep(1)
        
        i: int = 2
        while i < len(self.children):
            select_menu = self.children[i]
            assert isinstance(select_menu, CustomSelect)
            if select_menu.custom_id.startswith("13"):
                self.remove_item(select_menu)
            else:
                i += 1
        del i

        if self.role is None:
            try:
                await interaction.message.edit(view=self)
            except:
                pass
            await interaction.send(embed=Embed(description=ranking_text[lng][32]), ephemeral=True)
            return

        str_guild_id: str = self.g_id.__str__()
        with closing(connect(CWD_PATH + "/bases/bases_" + str_guild_id + "/" + str_guild_id + ".db")) as base:
            del str_guild_id
            with closing(base.cursor()) as cur:
                if cur.execute("SELECT role_id FROM rank_roles WHERE level = ?", (level,)).fetchone() is None:
                    cur.execute("INSERT INTO rank_roles(level, role_id) VALUES(?, ?)", (level, self.role))
                else:
                    cur.execute("UPDATE rank_roles SET role_id = ? WHERE level = ?", (self.role, level))
                base.commit()
                lvl_rls: list[tuple[int, int]] = cur.execute("SELECT level, role_id FROM rank_roles ORDER BY level ASC").fetchall()
        
        dsc: list[str] = [f"**`{n} {ranking_text[lng][24]} - `**<@&{r}>" for n, r in lvl_rls] + [ranking_text[lng][27]]
        emb: Embed = Embed(title=ranking_text[lng][26], description="\n".join(dsc))
        
        assert isinstance(self.children[1], CustomButton)
        if self.children[1].disabled:
            self.children[1].disabled = False

        try:
            await interaction.message.edit(embed=emb, view=self)
        except:
            pass
        await interaction.send(embed=Embed(description=ranking_text[lng][31].format(level, self.role)), ephemeral=True)
        self.role = None

    async def remove_role(self, interaction: Interaction, lng: int, level: int) -> None:
        str_guild_id: str = self.g_id.__str__()
        with closing(connect(CWD_PATH + "/bases/bases_" + str_guild_id + "/" + str_guild_id + ".db")) as base:
            del str_guild_id
            with closing(base.cursor()) as cur:
                if cur.execute("SELECT count() FROM rank_roles WHERE level = ?", (level,)).fetchone()[0]:
                    cur.execute("DELETE FROM rank_roles WHERE level = ?", (level,))
                    base.commit()
                    lvl_rls: list[tuple[int, int]] = cur.execute("SELECT level, role_id FROM rank_roles ORDER BY level ASC").fetchall()
                else:
                    await interaction.send(embed=Embed(description=ranking_text[lng][34].format(level)), ephemeral=True)
                    return

        if lvl_rls:
            dsc: list[str] = [f"**`{n} {ranking_text[lng][24]} - `**<@&{r}>" for n, r in lvl_rls]
            is_button_disabled: bool = False
        else:
            assert isinstance(self.children[1], CustomButton)
            self.children[1].disabled = True
            is_button_disabled: bool = True
            dsc: list[str] = [ranking_text[lng][25]]

        dsc.append(ranking_text[lng][27])
        emb: Embed = Embed(title=ranking_text[lng][26], description="\n".join(dsc))
        
        try:
            assert interaction.message is not None
            if is_button_disabled:
                await interaction.message.edit(embed=emb, view=self)
            else:
                await interaction.message.edit(embed=emb)
        except:
            pass

        await interaction.send(embed=Embed(description=ranking_text[lng][33].format(level)), ephemeral=True)

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert isinstance(interaction.user, Member)
        lng: int = self.lng
        lvl_modal: SelectLevelModal = SelectLevelModal(lng=lng, auth_id=interaction.user.id, timeout=60)
        await interaction.response.send_modal(modal=lvl_modal)
        await lvl_modal.wait()
        if not (role_level := lvl_modal.level):
            return
        
        if custom_id.startswith("27"):
            await self.add_role(interaction, lng, role_level)
        else:
            await self.remove_role(interaction, lng, role_level)                

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        if custom_id.startswith("13"):
            self.role = int(values[0])


class ManageMemberView(ViewBase):
    def __init__(self, timeout: int, lng: int, auth_id: int, memb_id: int, memb_rls: set[int], \
                rls: list[tuple[str, str]], cur_money: int, cur_xp: int, rem_dis: bool, g_id: int, member: Member) -> None:
        super().__init__(lng=lng, author_id=auth_id, timeout=timeout)

        self.add_item(CustomButton(
            style=ButtonStyle.blurple,
            label=mng_membs_text[lng][0],
            emoji="🔧",
            custom_id=f"18_{auth_id}_" + urandom(4).hex()
        ))
        self.add_item(CustomButton(
            style=ButtonStyle.green,
            label=settings_text[lng][4],
            emoji="<:add01:999663315804500078>",
            custom_id=f"19_{auth_id}_" + urandom(4).hex()
        ))
        self.add_item(CustomButton(
            style=ButtonStyle.red,
            label=settings_text[lng][5],
            emoji="<:remove01:999663428689997844>",
            custom_id=f"20_{auth_id}_" + urandom(4).hex(),
            disabled=rem_dis
        ))

        roles_count: int = len(rls)
        for i in range(min(((roles_count + 24) // 25), 4)):
            self.add_item(CustomSelect(
                custom_id=f"{300 + i}_{auth_id}_" + urandom(4).hex(),
                placeholder=settings_text[lng][2],
                options=rls[(i * 25):min(roles_count, (i + 1) * 25)]
            ))
        
        self.role_id: Optional[int] = None
        self.memb_id: int = memb_id
        self.memb_rls: set[int] = memb_rls
        self.cash: int = cur_money
        self.xp: int = cur_xp
        self.g_id: int = g_id
        self.member: Member = member

    async def add_role(self, interaction: Interaction) -> None:
        assert interaction.guild is not None
        assert self.role_id is not None
        lng: int = self.lng
        role_id: int = self.role_id
        if role_id in self.memb_rls:
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][7]), ephemeral=True)
            return
        
        self.memb_rls.add(role_id)

        str_role_id: str = role_id.__str__()
        str_guild_id: str = self.g_id.__str__()
        member_id: int = self.memb_id
        str_member_id: str = member_id.__str__()

        with closing(connect(CWD_PATH + "/bases/bases_" + str_guild_id + "/" + str_guild_id + ".db")) as base:
            del str_guild_id
            with closing(base.cursor()) as cur:
                member_owned_roles_ids: str = cur.execute("SELECT owned_roles FROM users WHERE memb_id = " + str_member_id).fetchone()[0]
                cur.execute("UPDATE users SET owned_roles = ? WHERE memb_id = ?", (member_owned_roles_ids + '#' + str_role_id, member_id))

                membs: Optional[tuple[str]] = cur.execute("SELECT members FROM salary_roles WHERE role_id = " + str_role_id).fetchone()
                if membs:
                    cur.execute("UPDATE salary_roles SET members = ? WHERE role_id = ?", (membs[0] + '#' + str_member_id, role_id))

                base.commit()

        role: Optional[Role] = interaction.guild.get_role(role_id)
        if role is not None:
            await self.member.add_roles(role)
        
        assert interaction.message is not None
        embs: list[Embed] = interaction.message.embeds
        emb3: Embed = embs[2]
        assert emb3.description is not None
        description_lines: list[str] = emb3.description.split("\n")
        
        role_id_line: str = "<@&" + str_role_id + ">**` - " + str_role_id + "`**"
        if len(description_lines) == 1:
            description_lines = [code_blocks[(lng * 5)], role_id_line]
            assert isinstance(self.children[2], CustomButton)
            self.children[2].disabled = False
            emb3.description = '\n'.join(description_lines)
            embs[2] = emb3
            try:
                await interaction.message.edit(embeds=embs, view=self)
            except:
                pass
        else:
            description_lines.append(role_id_line)
            emb3.description = '\n'.join(description_lines)
            embs[2] = emb3
            try:
                await interaction.message.edit(embeds=embs)
            except:
                pass

        await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][8].format(str_role_id, str_member_id)), ephemeral=True)
        self.role_id = None
    
    async def remove_role(self, interaction: Interaction) -> None:
        assert interaction.guild is not None
        assert self.role_id is not None
        role_id: int = self.role_id
        lng: int = self.lng
        if not role_id in self.memb_rls:
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][9]), ephemeral=True)
            return
        
        self.memb_rls.remove(role_id)

        str_role_id: str = role_id.__str__()
        str_guild_id: str = self.g_id.__str__()
        member_id: int = self.memb_id
        str_member_id: str = member_id.__str__()

        with closing(connect(CWD_PATH + "/bases/bases_" + str_guild_id + "/" + str_guild_id + ".db")) as base:
            del str_guild_id
            with closing(base.cursor()) as cur:
                m_rls: str = cur.execute("SELECT owned_roles FROM users WHERE memb_id = " + str_member_id).fetchone()[0]
                cur.execute("UPDATE users SET owned_roles = ? WHERE memb_id = ?", (m_rls.replace('#' + str_role_id, ""), member_id))

                membs: Optional[tuple[str]] = cur.execute("SELECT members FROM salary_roles WHERE role_id = " + str_role_id).fetchone()
                if membs:
                    cur.execute("UPDATE salary_roles SET members = ? WHERE role_id = ?", (membs[0].replace('#' + str_member_id, ""), role_id))

                base.commit()

        role: Optional[Role] = interaction.guild.get_role(role_id)
        assert role is not None
        await self.member.remove_roles(role)
        
        assert interaction.message is not None
        embs: list[Embed] = interaction.message.embeds
        emb3: Embed = embs[2]
        assert emb3.description is not None
        description_lines: list[str] = emb3.description.split('\n')
        
        if len(description_lines) <= 4:
            emb3.description = mng_membs_text[lng][6]
            assert isinstance(self.children[2], CustomButton)
            self.children[2].disabled = True
            embs[2] = emb3
            try:
                await interaction.message.edit(embeds=embs, view=self)
            except:
                pass
        else:
            for i, line in enumerate(description_lines):
                if str_role_id in line:
                    description_lines.pop(i)
                    break
                
            emb3.description = "\n".join(description_lines)
            embs[2] = emb3
            try:
                await interaction.message.edit(embeds=embs)
            except:
                pass
        
        await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][10].format(str_role_id, str_member_id)), ephemeral=True)
        
        self.role_id = None
    
    async def update_member_cash_or_xp(self, interaction: Interaction) -> None:
        assert interaction.message is not None
        lng: int = self.lng
        edit_modl: ManageMemberCashXpModal = ManageMemberCashXpModal(
            timeout=90,
            title=mng_membs_text[lng][19],
            lng=lng,
            memb_id=self.memb_id,
            cur_money=self.cash,
            cur_xp=self.xp,
            auth_id=self.author_id
        )

        await interaction.response.send_modal(modal=edit_modl)
        await edit_modl.wait()
        
        if edit_modl.is_changed:
            l: int = 0
            embs: list[Embed] = interaction.message.embeds
            
            str_guild_id: str = self.g_id.__str__()
            with closing(connect(CWD_PATH + "/bases/bases_" + str_guild_id + "/" + str_guild_id + ".db")) as base:
                del str_guild_id
                with closing(base.cursor()) as cur:
                    xp_b: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
                    if self.cash != edit_modl.new_cash:
                        membs_cash: list[tuple[int, int]] = cur.execute("SELECT memb_id, money FROM users ORDER BY money DESC;").fetchall()
                        l = len(membs_cash)
                    else:
                        membs_cash: list[tuple[int, int]] = []
                    if self.xp != edit_modl.new_xp:
                        membs_xp: list[tuple[int, int]] = cur.execute("SELECT memb_id, xp FROM users ORDER BY xp DESC;").fetchall()
                        l = len(membs_xp)
                    else:
                        membs_xp: list[tuple[int, int]] = []
            
            if self.cash != edit_modl.new_cash:
                self.cash = edit_modl.new_cash
                
                if membs_cash[l >> 1][1] < self.cash:
                    cnt_cash: int = 1
                    while cnt_cash < l and self.memb_id != membs_cash[cnt_cash-1][0]:
                        cnt_cash += 1
                else:
                    cnt_cash: int = l
                    while cnt_cash > 1 and self.memb_id != membs_cash[cnt_cash-1][0]:
                        cnt_cash -= 1

                embs[0].set_field_at(index=0, name=mng_membs_text[lng][1], value=code_blocks[1].format(self.cash))
                embs[0].set_field_at(index=1, name=mng_membs_text[lng][4], value=code_blocks[1].format(cnt_cash))

            if self.xp != edit_modl.new_xp:
                self.xp = edit_modl.new_xp
                if membs_xp[l >> 1][1] < self.xp:
                    cnt_xp: int = 1
                    while cnt_xp < l and self.memb_id != membs_xp[cnt_xp-1][0]:
                        cnt_xp += 1
                else:
                    cnt_xp: int = l
                    while cnt_xp > 1 and self.memb_id != membs_xp[cnt_xp-1][0]:
                        cnt_xp -= 1
                level: int = (self.xp + xp_b - 1) // xp_b

                embs[1].set_field_at(index=0, name=mng_membs_text[lng][2], value=code_blocks[2].format(f"{self.xp}/{level * xp_b + 1}"))
                embs[1].set_field_at(index=1, name=mng_membs_text[lng][3], value=code_blocks[2].format(level))
                embs[1].set_field_at(index=2, name=mng_membs_text[lng][4], value=code_blocks[2].format(cnt_xp))
            
            try:
                await interaction.message.edit(embeds=embs)
            except:
                return

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        int_custom_id: int = int(custom_id[:2])
        if int_custom_id == 18:
            await self.update_member_cash_or_xp(interaction)
            return

        if self.role_id is None:
            await interaction.response.send_message(embed=Embed(description=settings_text[self.lng][6]), ephemeral=True)
            return

        if int_custom_id == 19:
            await self.add_role(interaction)
        elif int_custom_id == 20:
            await self.remove_role(interaction)

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        assert len(values)
        assert values[0].isdigit()
        if custom_id.startswith("30"):
            self.role_id = int(values[0])


class VerifyDeleteView(ViewBase):
    def __init__(self, lng: int, role: int, m: Message, auth_id: int) -> None:
        super().__init__(lng=lng, author_id=auth_id, timeout=30)
        self.role_id: int = role
        self.m: Message = m
        self.deleted: bool = False
        self.add_item(CustomButton(style=ButtonStyle.red, label=ec_mr_text[lng][1], custom_id=f"1000_{auth_id}_" + urandom(4).hex()))
        self.add_item(CustomButton(style=ButtonStyle.green, label=ec_mr_text[lng][2], custom_id=f"1001_{auth_id}_" + urandom(4).hex()))

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert interaction.guild is not None
        assert interaction.guild_id is not None
        lng: int = self.lng
        if custom_id.startswith("1001_"):
            if interaction.message:
                try:
                    await interaction.message.delete()
                except:
                    pass
            await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][3].format(self.role_id)), ephemeral=True)
            self.stop()
        elif custom_id.startswith("1000_"):
            await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][4]), ephemeral=True)
            str_role_id: str = str(self.role_id)
            delete_role_from_db(guild_id=interaction.guild_id, str_role_id=str_role_id)
            try:
                await interaction.edit_original_message(embed=Embed(description=ec_mr_text[lng][5].format(str_role_id)))
            except:
                pass
            if interaction.message:
                try:
                    await interaction.message.delete()
                except:
                    pass

            emb: Embed = self.m.embeds[0]
            assert emb.description is not None
            dsc: list[str] = emb.description.split("\n")
            i: int = 0
            while i < len(dsc):
                if str_role_id in dsc[i]:
                    del dsc[i]
                else:
                    i += 1
            if len(dsc) == 3:
                dsc[0] = ec_text[lng][20]
            emb.description = '\n'.join(dsc)
            try:
                await self.m.edit(embed=emb)
            except:
                pass
            self.deleted = True
            self.stop()

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return
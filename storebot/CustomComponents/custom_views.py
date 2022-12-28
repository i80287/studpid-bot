from sqlite3 import connect, Connection, Cursor
from asyncio import sleep, TimeoutError
from contextlib import closing
from random import randint

from nextcord import Embed, Emoji, Interaction, ButtonStyle, Message
from nextcord.ui import View
from nextcord.ext.commands import Bot

from Tools.parse_tools import ParseTools
from Variables.vars import path_to, ignored_channels
from CustomComponents.custom_button import CustomButton
from CustomComponents.custom_select import CustomSelect
from CustomComponents.custom_modals import RoleAddModal, RoleEditModal, \
    XpSettingsModal, SelectLevelModal, ManageMemberCashXpModal


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

system_status = {
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
        2 : "Select role",
        3 : "Adding role",
        4 : "Add role",
        5 : "Remove role",
        6 : "**`You hasn't selected the role yet`**",
        7 : "Ping of the member or write member's id\n\nWrite `cancel` to cancel the menu",
        8 : "Add channel",
        9 : "Remove channel",
        10 : "Select channel",
        11 : "**`Select channel`**",
        12 : "Not selected",
        13 : "```fix\nnot selected\n```",
        14 : "**`This role not found on the server. Please try to recall the command`**"
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
        2 : "Выберите роль",
        3 : "Добавление роли",
        4 : "Добавить роль",
        5 : "Убрать роль",
        6 : "**`Вы не выбрали роль`**",
        7 : "Напишите id участника сервера или пинганите его\n\nНапишите `cancel` для отмены",
        8 : "Добавить канал",
        9 : "Убрать канал",
        10 : "Выберите канал",
        11 : "**`Выберите канал`**",
        12 : "Не выбрано",
        13 : "```fix\nне выбран\n```",
        14 : "**`Эта роль не найдена на сервере. Пожалуйста, попробуйте вызвать команду снова`**"
    }
}

gen_settings_text = {
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

mod_roles_text = {
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

ec_text = {
    0 : {
        0 : "Economy settings",
        1 : "💸 Money gained for message:\n**`{}`**",
        2 : "⏰ Cooldown for `/work`:\n**`{} seconds`**",
        3 : "💹 Salary from `/work`:\n**{}**",
        4 : "random integer from `{}` to `{}`",
        5 : "📙 Log channel for economic operations:\n{}",
        7 : "> To manage setting press button with\ncorresponding emoji",
        8 : "> To see and manage roles available for\npurchase/sale in the bot press 🛠️",
        9 : "**`Write amount of money gained for message (non negative integer number)`**",
        10 : "Amount of money gained from messages set to: `{}`",
        11 : "Write cooldown for `/work` command **in seconds** (integer at least 60)\nFor example, to make cooldown equalt to 240 seconds, write `240` in the chat",
        12 : "Cooldown for `/work` set to: `{}`",
        13 : "Write salary from `/work`:\nTwo non-negative numbers, second at least as much as first\nSalary will be random integer \
            between them\nIf you want salary to constant write one number\nFor example, if you write `1` `100` then salary \
            will be random integer from `1` to `100`\nIf you write `10`, then salary will always be `10`",
        14 : "**`Now salary is `**{}",
        15 : "Select channel",
        16 : "**`You chose channel `**{}",
        17 : "**`Timeout expired`**",
        18 : "__**role - role id - price - salary - cooldown for salary - type - how much in the store**__",
        19 : "No roles were added",
        20 : "`If role isn't shown in the menu(s) down below it means that bot can't manage this role`",
        21 : "**`You reseted log channel`**"
    },
    1 : {
        0 : "Настройки экономики",
        1 : "💸 Количество денег, получаемых за сообщение:\n**`{}`**",
        2 : "⏰ Кулдаун для команды `/work`:\n**`{} секунд`**",
        3 : "💹 Доход от команды `/work`:\n**{}**",
        4 : "рандомное целое число от `{}` до `{}`",
        5 : "📙 Канал для логов экономических операций:\n{}",
        7 : "> Для управления настройкой нажмите на кнопку с\nсоответствующим эмодзи",
        8 : "> Для просмотра и управления ролями, доступными\nдля покупки/продажи у бота, нажмите 🛠️",
        9 : "**`Укажите количество денег, получаемых за сообщение\n(неотрицательное целое число)`**",
        10 : "Количество денег, получаемых за одно сообщение, теперь равно: `{}`",
        11 : "Укажите кулдаун для команды `/work` **в секундах** (целое число не менее 60)\nНапример, чтобы поставить кулдаун 240 секунд, напишите в чат `240`",
        12 : "Кулдаун для команды `/work` теперь равен: `{}`",
        13 : "Укажите заработок от команды `/work`:\nДва неотрицательных числа, второе не менее первого\nЗаработок будет \
            рандомным целым числом между ними\nЕсли Вы хотите сделать заработок постоянным, укажите одно число\nНапример, \
            если Вы укажите `1` `100`, то заработок будет рандомным целым числом от `1` до `100`\nЕсли Вы укажите `10`, то \
            заработок всегда будет равен `10`",
        14 : "**`Теперь заработок: `**{}",
        15 : "Выберите канал",
        16 : "**`Вы выбрали канал `**{}",
        17 : "**`Время ожидания вышло`**",
        18 : "__**роль - id роли - цена - заработок - кулдаун заработка - тип - сколько в магазине**__",
        19 : "Не добавлено ни одной роли",
        20 : "`Если роль не отображается ни в одном меню снизу, значит, бот не может управлять ею`",
        21 : "**`Вы сбросили канал логов`**"
    }
}

ec_mr_text = { 
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
        10 : "Role's price",
        11 : "Write positive integer number as price of the role",
        12 : "Role's salary and cooldown for it (optional)",
        13 : "If role should bring money to its owners write salary and cooldown in hours (split numbers by space)",
        14 : "The same roles will be displayed in the store",
        15 : "Print 1 if the same roles will be separated (nonstacking) (each answer can be written in any window)",
        16 : "Print 2 if the same roles will be countable (can run out in the store) and stacking as one item",
        17 : "Print 3 if the same roles will be uncountable (can't run out in the store) and stacking as one item",
        18 : "Price must be positive integer number",
        19 : "Salary and cooldown must be two positive integer numbers separated by space, for example: `100` `24`",
        20 : "Salary should be positive integer number",
        21 : "Cooldown should be positive integer number, cooldown is time in hours. For example: `24` sets cooldown to 24 hours",
        22 : "Type of displaying of the role should be one of three numbers: `1`, `2` or `3`",
        23 : "You chose different types of displaying for the role",
        24 : "You added role <@&{}> with price **`{}`**, salary **`{}`**, cooldown for it **`{}`**, type **`{}`**",
        25 : "Editing the role",
        26 : "Print 1 if separated,nonstacking\n2 if countable,stacking\n3 if uncountable (can't run out),stacking",
        27 : "How much roles must be in the store",
        28 : "Print integer non-negative number. For uncountable roles print any non-negative number",
        29 : "Amount of the roles in the store must be non-negative integer number",
        30 : "You edited role <@&{}>. Now it's price is **`{}`**, salary is **`{}`**, cooldown for it is **`{}`**, role's type is **`{}`**, amount of roles in the store - **`{}`**",
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
        10 : "Цена роли",
        11 : "Укажите целое положительное число",
        12 : "Доход роли и кулдаун для него (необязательно)",
        13 : "Если надо, чтобы роль приносила деньги,укажите доход и его кулдаун в часах(разделите числа пробелом)",
        14 : "Одинаковые роли будут отображаться в магазине",
        15 : "Напишите 1, если одинаковые роли будут отображаться отдельно (ответ можно написать в любом поле)",
        16 : "Напишите 2, если одинаковые роли будут стакающимеся и исчисляемыми (могут закончиться в магазине)",
        17 : "Напишите 3, если одинаковые роли будут стакающимеся и бесконечными (не могут закончиться в магазине)",
        18 : "В качестве цены роли надо указать целое положительное число",
        19 : "Заработок и кулдаун должны быть двумя положительными целыми числами, разделёнными пробелом, например, `100` `24`",
        20 : "Заработок должен быть целым положительным числом",
        21 : "Кулдаун должен быть целым положительным числом, кулдаун - время в часах. Например, `24` сделать кулдаун равным 24 часам",
        22 : "В качестве типа отображения роли надо указать одно из трёх чисел: `1`, `2` или `3`",
        23 : "Вы выбрали несколько разных типов отображения для роли",
        24 : "Вы добавили роль <@&{}> с ценой **`{}`**, доходом **`{}`**, его кулдауном **`{}`**, типом **`{}`**",
        25 : "Редактирование роли",
        26 : "Напишите 1,если раздельно,нестакаются\n2,если стакающися,исчисляемые\n3,если стакающиеся,бесконечные",
        27 : "Сколько ролей должно быть в магазине",
        28 : "Напишите целое неотрицательное число.Для бесконечных ролей можно указать любое неотрицательное число",
        29 : "Количество ролей в магазине должно быть целым неотрицательным числом",
        30 : "Вы отредактировали роль <@&{}>. Теперь её цена - **`{}`**, доход - **`{}`**, его кулдаун - **`{}`**, тип роли - **`{}`**, количество в магазине - **`{}`**",
    }
}

mng_membs_text = {
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

poll_text = {
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

ranking_text = {
    0 : {
        0 : "✨ Xp gained per message:\n**`{}`**",
        1 : "✨ Amount of xp between adjacent levels:\n**`{}`**",
        2 : "📗 Channel for the notification about new levels:\n{}",
        4 : "> To manage setting press button with corresponding emoji\n",
        5 : "> Press :mute: to manage channels where members can't get xp\n",
        6 : "> Press 🥇 to manage roles given for levels",
        7 : "Managing xp settings",
        8 : "Xp per message",
        9 : "Amount of xp gained by every member from one message, non-negative integer number",
        10 : "Amount of xp between adjected levels",
        11 : "Amount of xp members need to gain to get next level, positive integer number",
        12 : "**`Xp gained per message should be non-negative integer number`**",
        13 : "**`Amount of xp between adjected levels should be positive integer number`**",
        14 : "**`You changed amount of xp gained from one message, now it's {}`**",
        15 : "**`You changed amount of xp needed to get next level, now it's {}`**",
        16 : "**`You hasn't changed anything`**",
        17 : "__**channel**__ - __**id**__",
        18 : "**`No channels were selected`**",
        19 : "**`You added channel `**<#{}>",
        20 : "**`You removed channel `**<#{}>",
        21 : "**`You hasn't selected the channel yet`**",
        22 : "**`This channel is already added`**",
        23 : "**`This channel hasn't been added yet`**",
        24 : "level",
        25 : "**`No roles matched for levels`**",
        26 : "Roles for level",
        27 : "**`Press `**<:add01:999663315804500078>🔧**`to add / change role for the level`**\n**`Press `**<:remove01:999663428689997844>**` to remove role for the level`**",
        28 : "Write the level: positive integer from 1 to 100",
        29 : "**`Select role for level {}`**",
        30 : "**`Bot can't give any role on the server`**",
        31 : "**`From now role given for the level {} is `**<@&{}>",
        32 : "**`Timeout has expired`**",
        33 : "**`You removed role for level {}`**",
        34 : "**`No roles matches level {}`**",
        35 : "Write the level: **`positive integer from 1 to 100`**",
    },
    1 : {
        0 : "✨ Опыт, получаемый за одно сообщение:\n**`{}`**",
        1 : "✨ Количество опыта между соседними уровнями:\n**`{}`**",
        2 : "📗 Канал для оповещений о получении нового уровня:\n{}",
        4 : "> Для управления настройкой нажмите на кнопку с соответствующим эмодзи\n",
        5 : "> Нажмите :mute: для управления каналами, в которых пользователи не могут получать опыт\n",
        6 : "> Нажмите 🥇 для управления ролями, выдаваемыми за уровни",
        7 : "Управление настройками опыта",
        8 : "Опыт за сообщение",
        9 : "Количество опыта, получаемого пользователем за одно сообщение, целое неотрицательное число",
        10 : "Количество опыта между уровнями",
        11 : "Количество опыта,необходимого участникам для получения следующего уровня, целове положительное число",
        12 : "**`Опыт, получаемый участником за одно сообщение, должен быть целым неотрицательным числом`**",
        13 : "**`Количество опыта, который необходимо набрать участникам для получения следующего уровня, должно быть целым положительным числом`**",
        14 : "**`Вы изменили количество опыта, получаемого участником за одно сообщение, теперь оно равно {}`**",
        15 : "**`Вы изменили количество опыта, необходимого участнику для получения следующего уровня, теперь оно равно {}`**",
        16 : "**`Вы ничего не изменили`**",
        17 : "__**канал**__ - __**id**__",
        18 : "**`Не выбрано ни одного канала`**",
        19 : "**`Вы добавили канал `**<#{}>",
        20 : "**`Вы убрали канал `**<#{}>",
        21 : "**`Вы не выбрали канал`**",
        22 : "**`Этот канал уже добавлен`**",
        23 : "**`Этот канал ещё не был добавлен`**",
        24 : "уровень",
        25 : "**`Роли за уровни не назначены`**",
        26 : "Роли за уровни",
        27 : "**`Нажмите `**<:add01:999663315804500078>🔧**`, чтобы добавить / изменить роль за уровень`**\n**`Нажмите `**<:remove01:999663428689997844>**`, чтобы убрать роль за уровень`**",
        28 : "Напишите номер уровня: положительное целое число от 1 до 100",
        29 : "**`Выберите роль для уровня {}`**",
        30 : "**`Бот не может выдать ни одной роли на сервере`**",
        31 : "**`Теперь за уровень {} выдаётся роль `**<@&{}>",
        32 : "**`Время истекло`**",
        33 : "**`Вы убрали роль за уровень {}`**",
        34 : "**`Уровню {} не соответствует ни одна роль`**",
        35 : "Напишите номер уровня: **`положительное целое число от 1 до 100`**",
    }
}

code_blocks = {
    0 : "```\nOwned roles\n```",
    5 : "```\nЛичные роли\n```",
    1 : "```fix\n{}\n```",
    2 : "```c\n{}\n```",
}


class GenSettingsView(View):
    def __init__(self, t_out: int, auth_id: int, bot: Bot, lng: int, ec_status: int, rnk_status: int):
        super().__init__(timeout=t_out)
        self.bot: Bot = bot
        self.auth_id: int = auth_id
        self.lang = None
        self.tz = None
        self.ec_status: int = ec_status
        self.rnk_status: int = rnk_status
        tzs: list[tuple[str, int]] = [(f"UTC{i}", i) for i in range(-12, 0)] + [(f"UTC+{i}", i) for i in range(0, 13)]
        self.add_item(CustomSelect(custom_id=f"100_{auth_id}_{randint(1, 100)}", placeholder=gen_settings_text[lng][20], opts=languages[2][lng]))
        self.add_item(CustomSelect(custom_id=f"101_{auth_id}_{randint(1, 100)}", placeholder=gen_settings_text[lng][21], opts=tzs))
        self.add_item(CustomButton(style=ButtonStyle.green, label=None, custom_id=f"6_{auth_id}_{randint(1, 100)}", emoji="🗣️"))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label=None, custom_id=f"7_{auth_id}_{randint(1, 100)}", emoji="⏱"))
        self.add_item(CustomButton(style=ButtonStyle.gray, label=None, custom_id=f"42_{auth_id}_{randint(1, 100)}", emoji="💵"))
        self.add_item(CustomButton(style=ButtonStyle.red, label=None, custom_id=f"43_{auth_id}_{randint(1, 100)}", emoji="💰", row=2))
        self.add_item(CustomButton(style=ButtonStyle.red, label=None, custom_id=f"44_{auth_id}_{randint(1, 100)}", emoji="📈", row=2))
        
    async def select_lng(self, interaction: Interaction, lng: int):
        s_lng = self.lang
        if s_lng is None:
            await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][22]), ephemeral=True)
            return
        g_id = interaction.guild_id
        with closing(connect(f"{path_to}/bases/bases_{g_id}/{g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                if cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0] == s_lng:
                    await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][26]), ephemeral=True)
                    return
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'lang'", (s_lng,))
                base.commit()
        
        s_lng_nm = languages[lng][s_lng]
        
        emb = interaction.message.embeds[0]
        dsc = emb.description.split("\n")
        dsc[0] = gen_settings_text[lng][0].format(s_lng_nm)
        emb.description = "\n".join(dsc)
        await interaction.message.edit(embed=emb)

        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][25].format(s_lng_nm)), ephemeral=True)
        self.lang = None
    
    async def digit_tz(self, interaction: Interaction, lng: int):
        tz = self.tz
        if tz is None:
            await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][23]), ephemeral=True)
            return
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'tz'", (tz,))
                base.commit()
        tz =  f"+{tz}" if tz >= 0 else str(tz)

        emb = interaction.message.embeds[0]
        dsc = emb.description.split("\n")
        dsc[1] = gen_settings_text[lng][1].format(tz)
        emb.description = "\n".join(dsc)
        await interaction.message.edit(embed=emb)

        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][24].format(tz)), ephemeral=True)
        self.tz = None

    async def change_currency(self, interaction: Interaction, lng: int):
        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][29]), ephemeral=True)
        try:
            user_ans: Message = await self.bot.wait_for(event="message", check=lambda m: m.channel.id == interaction.channel_id and m.author.id == self.auth_id, timeout=25)
        except TimeoutError:
            return
        else:
            user_ans_content: str = user_ans.content
            emoji = ParseTools.parse_emoji(self.bot, user_ans_content)
            if emoji is None:
                emoji_str = user_ans_content
            elif isinstance(emoji, Emoji):
                emoji_str = emoji.__str__()
            else:
                emoji_str = emoji

            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'currency'", (emoji_str,))
                    base.commit()

            emb = interaction.message.embeds[0]
            dsc = emb.description.split("\n")
            dsc[2] = gen_settings_text[lng][2].format(emoji_str)
            emb.description = "\n".join(dsc)
            await interaction.message.edit(embed=emb)

            if await interaction.original_message():
                await interaction.edit_original_message(embed=Embed(description=gen_settings_text[lng][30].format(emoji_str)))

    async def change_ec_system(self, interaction: Interaction, lng: int):
        self.ec_status = (self.ec_status + 1) % 2
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'economy_enabled'", (self.ec_status,))
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'mn_per_msg'", (self.ec_status,))
                base.commit()

        emb = interaction.message.embeds[0]
        dsc = emb.description.split("\n")
        dsc[3] = gen_settings_text[lng][3].format(system_status[lng][self.ec_status])
        dsc[8] = gen_settings_text[lng][8].format(system_status[lng][self.ec_status+2])
        emb.description = "\n".join(dsc)
        await interaction.message.edit(embed=emb)

        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][27].format(system_status[lng][self.ec_status+4])), ephemeral=True)

    async def change_rnk_system(self, interaction: Interaction, lng: int):
        self.rnk_status = (self.rnk_status + 1) % 2
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'ranking_enabled'", (self.rnk_status,))
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'xp_per_msg'", (self.rnk_status,))
                base.commit()
        
        emb = interaction.message.embeds[0]
        dsc = emb.description.split("\n")
        dsc[4] = gen_settings_text[lng][4].format(system_status[lng][self.rnk_status])
        dsc[9] = gen_settings_text[lng][9].format(system_status[lng][self.rnk_status+2])
        emb.description = "\n".join(dsc)
        await interaction.message.edit(embed=emb)
            
        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][28].format(system_status[lng][self.rnk_status+4])), ephemeral=True)

    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0        
        if c_id.startswith("6_"):
            await self.select_lng(interaction=interaction, lng=lng)
        elif c_id.startswith("7_"):
            await self.digit_tz(interaction=interaction, lng=lng)
        elif c_id.startswith("42_"):
            await self.change_currency(interaction=interaction, lng=lng)
        elif c_id.startswith("43_"):
            await self.change_ec_system(interaction=interaction, lng=lng)
        elif c_id.startswith("44_"):
            await self.change_rnk_system(interaction=interaction, lng=lng)

    async def click_menu(self, __, c_id: str, values):
        if c_id.startswith("100_"):
            self.lang = int(values[0])
        elif c_id.startswith("101_"):
            self.tz = int(values[0])
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class ModRolesView(View):
    def __init__(self, t_out: int, m_rls: set, lng: int, auth_id: int, rem_dis: bool, rls: list):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.m_rls = m_rls
        self.role = None
        for i in range((len(rls)+24)//25):
            self.add_item(CustomSelect(custom_id=f"{200+i}_{auth_id}_{randint(1, 100)}", placeholder=settings_text[lng][2], opts=rls[i*25:min(len(rls), (i+1)*25)]))
        self.add_item(CustomButton(style=ButtonStyle.green, label=settings_text[lng][4], emoji="<:add01:999663315804500078>", custom_id=f"8_{auth_id}_{randint(1, 100)}"))
        self.add_item(CustomButton(style=ButtonStyle.red, label=settings_text[lng][5], emoji="<:remove01:999663428689997844>", custom_id=f"9_{auth_id}_{randint(1, 100)}", disabled=rem_dis))
    

    async def add_role(self, interaction: Interaction, lng: int):
        rl_id = self.role
        if rl_id in self.m_rls:
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][7]), ephemeral=True)
            return       
                
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("INSERT OR IGNORE INTO mod_roles(role_id) VALUES(?)", (rl_id,))
                base.commit()

        self.m_rls.add(rl_id)
        
        emb = interaction.message.embeds[0]
        dsc = emb.description.split("\n")
        if len(self.m_rls) == 1:
            for c in self.children:
                if c.custom_id.startswith("9_"):
                    c.disabled = False
            emb.description = f"{mod_roles_text[lng][2]}\n<@&{rl_id}> - {rl_id}"
            await interaction.message.edit(view=self, embed=emb)
        else:
            dsc.append(f"<@&{rl_id}> - {rl_id}")
            emb.description = "\n".join(sorted(dsc))
            await interaction.message.edit(embed=emb)

        self.role = None
        await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][8].format(f"<@&{rl_id}>")), ephemeral=True)
    

    async def rem_role(self, interaction: Interaction, lng: int):
        rl_id = self.role
        if not rl_id in self.m_rls:
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][9]), ephemeral=True)
            return
        
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                cur.execute("DELETE FROM mod_roles WHERE role_id = ?", (rl_id,))
                base.commit()
        self.m_rls.remove(rl_id)
        emb = interaction.message.embeds[0]

        if self.m_rls:
            dsc = emb.description.split("\n")
            dsc.remove(f"<@&{rl_id}> - {rl_id}")
            emb.description = "\n".join(sorted(dsc))
            await interaction.message.edit(embed=emb)
        else:
            for c in self.children:
                if c.custom_id.startswith("9_"):
                    c.disabled = True
            emb.description = mod_roles_text[lng][1]
            await interaction.message.edit(embed=emb, view=self)

        self.role = None        
        await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][10].format(f"<@&{rl_id}>")), ephemeral=True)


    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        m = interaction.message
        if self.role is None:
            await interaction.response.send_message(embed=Embed(description=settings_text[lng][6]), ephemeral=True)
            return

        if interaction.guild.get_role(self.role):
            if c_id.startswith("8_"):
                await self.add_role(interaction=interaction, lng=lng)
            elif c_id.startswith("9_"):
                await self.rem_role(interaction=interaction, lng=lng)
        else:
            interaction.response.send_message(embed=Embed(description=settings_text[lng][14]), ephemeral=True)

    async def click_menu(self, __, c_id: str, values):
        if c_id.startswith("20") and c_id[3] == "_":
            self.role = int(values[0])
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class EconomyView(View):
    r_types = {
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

    def __init__(self, t_out: int, auth_id: int):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.channel = None
        self.add_item(CustomButton(style=ButtonStyle.blurple, label="", custom_id=f"10_{auth_id}_{randint(1, 100)}", emoji="💸"))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label="", custom_id=f"11_{auth_id}_{randint(1, 100)}", emoji="⏰"))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label="", custom_id=f"12_{auth_id}_{randint(1, 100)}", emoji="💹"))
        self.add_item(CustomButton(style=ButtonStyle.green, label="", custom_id=f"13_{auth_id}_{randint(1, 100)}", emoji="📙"))
        self.add_item(CustomButton(style=ButtonStyle.red, label="", custom_id=f"14_{auth_id}_{randint(1, 100)}", emoji="🛠️"))        

    async def msg_salary(self, interaction: Interaction, lng: int, ans: str) -> bool:
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

    async def work_cldwn(self, interaction: Interaction, lng: int, ans: str) -> bool:
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

    async def work_salary(self, interaction: Interaction, lng: int, ans: str) -> bool:
        ans = ans.split()
        fl: bool = False
        if len(ans) >= 2:
            n1 = ans[0]
            n2 = ans[1]
            if n1.isdigit() and n2.isdigit():
                n1 = int(n1); n2 = int(n2)
                if 0 <= n1 <= n2: fl = True
            
        elif len(ans):
            n1 = ans[0]
            if n1.isdigit() and int(n1) >= 0:
                n2 = n1 = int(n1)
                fl = True      
        
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
        for i in range(min((len(channels) + 23) // 24, 7)):
            opts = [(settings_text[lng][12], 0)] + channels[i*24:min((i+1)*24, len(channels))]
            self.add_item(CustomSelect(custom_id=f"{500+i}_{self.auth_id}_{randint(1, 100)}", placeholder=settings_text[lng][10], opts=opts))
            
        await interaction.message.edit(view=self)
        await interaction.response.send_message(embed=Embed(description=settings_text[lng][11]), ephemeral=True)

        cnt = 0
        while self.channel is None and cnt < 40:
            cnt += 1
            await sleep(1)

        i = 0
        while i < len(self.children):
            if self.children[i].custom_id.startswith("5"):
                self.remove_item(item=self.children[i])
            else:
                i += 1

        if cnt >= 40:
            await interaction.message.edit(view=self)
            await interaction.edit_original_message(embed=Embed(description=ec_text[lng][17]))
            self.channel = None
            return

        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'log_c'", (self.channel,))
                base.commit()
        
        emb = interaction.message.embeds[0]
        dsc = emb.description.split("\n\n")
        if self.channel != 0:
            dsc[3] = ec_text[lng][5].format(f"<#{self.channel}>")
        else:
            dsc[3] = ec_text[lng][5].format(settings_text[lng][13])
        emb.description = "\n\n".join(dsc)
        await interaction.message.edit(embed=emb, view=self)

        if self.channel != 0:
            await interaction.edit_original_message(embed=Embed(description=ec_text[lng][16].format(f"<#{self.channel}>")))
        else:
            await interaction.edit_original_message(embed=Embed(description=ec_text[lng][21]))
        
        self.channel = None

    async def manage_economy_roles(self, interaction: Interaction, lng: int):
        emb = Embed()
        s_rls = set()
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                roles: list = cur.execute('SELECT * FROM server_roles').fetchall()
                if roles:
                    descr: list[str] = [ec_text[lng][18]]
                    for role in roles:
                        s_rls.add(role[0])
                        if role[4] == 1:
                            cnt = cur.execute("SELECT count() FROM store WHERE role_id = ?", (role[0],)).fetchone()[0]
                        else:
                            cnt = cur.execute("SELECT quantity FROM store WHERE role_id = ?", (role[0],)).fetchone()
                            if not cnt:
                                cnt = 0
                            elif role[4] == 2:
                                cnt = cnt[0]
                            else:
                                cnt = "∞"
                        descr.append(f"<@&{role[0]}> - **`{role[0]}`** - **`{role[1]}`** - **`{role[2]}`** - **`{role[3]//3600}`** - **`{self.r_types[lng][role[4]]}`** - **`{cnt}`**")
                else:
                    descr: list[str] = [ec_text[lng][19]]

        descr.append("\n" + ec_text[lng][20])
        emb.description="\n".join(descr)
        
        rls = [(r.name, r.id) for r in interaction.guild.roles if r.is_assignable()]
        if len(rls): rd = False
        else: rd = True
        ec_rls_view = EconomyRolesManageView(t_out=155, lng=lng, auth_id=self.auth_id, rem_dis=rd, rls=rls, s_rls=s_rls)
        await interaction.response.send_message(embed=emb, view=ec_rls_view)
        await ec_rls_view.wait()
        for c in ec_rls_view.children:
            c.disabled = True
        await interaction.edit_original_message(view=ec_rls_view)

    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        if c_id.startswith("13"):
            await self.log_chnl(interaction=interaction, lng=lng)
        elif c_id.startswith("14"):
            await self.manage_economy_roles(interaction=interaction, lng=lng)
        elif c_id[:2] in {"10", "11", "12"}:
            await interaction.response.send_message(embed=Embed(description=ec_text[lng][9 + (int(c_id[:2]) - 10) * 2]), ephemeral=True)
            flag = True
            while flag:
                try:
                    user_ans = await interaction.client.wait_for(event="message", check=lambda m: m.author.id == self.auth_id and m.channel.id == interaction.channel_id, timeout=40)
                except TimeoutError:
                    flag = False
                else:
                    ans: str = user_ans.content
                    if c_id.startswith("10"): flag = await self.msg_salary(interaction=interaction, lng=lng, ans=ans)
                    elif c_id.startswith("11"): flag = await self.work_cldwn(interaction=interaction, lng=lng, ans=ans)
                    elif c_id.startswith("12"): flag = await self.work_salary(interaction=interaction, lng=lng, ans=ans)
                # try to delete user's ans
                try: await user_ans.delete()
                except: pass

    async def click_menu(self, _, c_id: str, values):
        if c_id.startswith("50"):
            self.channel = int(values[0])

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class EconomyRolesManageView(View):
    def __init__(self, t_out: int, lng: int, auth_id: int, rem_dis: bool, rls: list, s_rls: set):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.s_rls = s_rls
        self.role = None
        for i in range((len(rls)+24)//25):
            self.add_item(CustomSelect(custom_id=f"{800+i}", placeholder=settings_text[lng][2], opts=rls[i*25:min(len(rls), (i+1)*25)]))
        self.add_item(CustomButton(style=ButtonStyle.green, label=settings_text[lng][4], emoji="<:add01:999663315804500078>", custom_id=f"15_{auth_id}_{randint(1, 100)}"))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label=ec_mr_text[lng][0], emoji="🔧", custom_id=f"16_{auth_id}_{randint(1, 100)}", disabled=rem_dis))
        self.add_item(CustomButton(style=ButtonStyle.red, label=settings_text[lng][5], emoji="<:remove01:999663428689997844>", custom_id=f"17_{auth_id}_{randint(1, 100)}", disabled=rem_dis))


    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0

        if self.role is None:
            await interaction.response.send_message(embed=Embed(description=settings_text[lng][6]), ephemeral=True)
            return

        if c_id.startswith("17_"):
            if not self.role in self.s_rls:
                await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][7]), ephemeral=True)
                return
            v_d = VerifyDeleteView(lng=lng, role=self.role, m=interaction.message, auth_id=interaction.user.id)
            await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][6].format(self.role)), view=v_d)
            
            if await v_d.wait():
                for c in v_d.children:
                    c.disabled = True
                await interaction.edit_original_message(view=v_d)

            if v_d.deleted:
                self.s_rls.remove(self.role)
                self.role = None

        elif c_id.startswith("15_"):
            if self.role in self.s_rls:
                await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][9]), ephemeral=True)
                return
            add_mod = RoleAddModal(timeout=90, lng=lng, role=self.role, m=interaction.message, auth_id=interaction.user.id)
            await interaction.response.send_modal(modal=add_mod)
            
            await add_mod.wait()
            if add_mod.added:
                self.s_rls.add(self.role)
                self.role = None

        elif c_id.startswith("16_"):
            role_id: int = self.role
            if role_id not in self.s_rls:
                await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][8]), ephemeral=True)
                return
            
            role_type: int
            role_in_store_count: int
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    req = cur.execute("SELECT * FROM server_roles WHERE role_id = ?", (role_id,)).fetchone()
                    role_type = req[4]
                    if role_type != 2:
                        role_in_store_count = cur.execute("SELECT count() FROM store WHERE role_id = ?", (role_id,)).fetchone()[0]
                    else:
                        quantity = cur.execute("SELECT quantity FROM store WHERE role_id = ?", (role_id,)).fetchone()                        
                        role_in_store_count = quantity[0] if quantity else 0
            
            edit_mod = RoleEditModal(
                timeout=90, 
                role=role_id, 
                m=interaction.message, 
                auth_id=interaction.user.id, 
                lng=lng, 
                p=req[1], 
                s=req[2], 
                s_c=req[3]//3600, 
                r_t=role_type, 
                in_store=role_in_store_count
            )
            await interaction.response.send_modal(modal=edit_mod)
            await edit_mod.wait()
            if edit_mod.changed:
                self.role = None
            return

    async def click_menu(self, _, c_id: str, values):
        if c_id.startswith("80"):
            self.role = int(values[0])

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True
    

class SettingsView(View):
    def __init__(self, t_out: int, auth_id: int, bot: Bot):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.bot = bot
        self.add_item(CustomButton(style=ButtonStyle.red, label=None, custom_id=f"0_{auth_id}_{randint(1, 100)}", emoji="⚙️"))
        self.add_item(CustomButton(style=ButtonStyle.red, label=None, custom_id=f"1_{auth_id}_{randint(1, 100)}", emoji="<:moder:1000090629897998336>"))
        self.add_item(CustomButton(style=ButtonStyle.red, label=None, custom_id=f"2_{auth_id}_{randint(1, 100)}", emoji="<:user:1002245779089535006>"))
        self.add_item(CustomButton(style=ButtonStyle.green, label=None, custom_id=f"3_{auth_id}_{randint(1, 100)}", emoji="💰", row=2))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label=None, custom_id=f"4_{auth_id}_{randint(1, 100)}", emoji="📈", row=2))
        self.add_item(CustomButton(style=ButtonStyle.blurple, label=None, custom_id=f"5_{auth_id}_{randint(1, 100)}", emoji="📊", row=2))
    
    def check_ans(self, interaction: Interaction, ans: str):
        if ans == "cancel":
            return None, 1
        if ans.startswith("<@") and len(ans) >= 4:
            ans = ans[2:-1]
        if ans.isdigit():
            ans = int(ans)
            memb = interaction.guild.get_member(ans)
            if memb is None:
                return None, 0
            return memb, 2
        else:
            return None, 0

    def check_memb(self, base: Connection, cur: Cursor, memb_id: int):
        member = cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()
        if not member:
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

    async def click(self, interaction: Interaction, custom_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        
        if custom_id.startswith("0_"):
            with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                with closing(base.cursor()) as cur:
                    s_lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                    tz: int = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]
                    currency: str = cur.execute("SELECT value FROM server_info WHERE settings = 'currency'").fetchone()[0]
                    ec_status: int = cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]
                    rnk_status: int = cur.execute("SELECT value FROM server_info WHERE settings = 'ranking_enabled'").fetchone()[0]
                    
            emb = Embed()
            dsc = [gen_settings_text[lng][0].format(languages[lng][s_lng])]
            if tz >= 0:
                dsc.append(gen_settings_text[lng][1].format(f"+{tz}"))
            else:
                dsc.append(gen_settings_text[lng][1].format(f"{tz}"))
            dsc.append(gen_settings_text[lng][2].format(currency))
            dsc.append(gen_settings_text[lng][3].format(system_status[lng][ec_status]))
            dsc.append(gen_settings_text[lng][4].format(system_status[lng][rnk_status]))
            for i in (5, 6, 7):
                dsc.append(gen_settings_text[lng][i])
            dsc.append(gen_settings_text[lng][8].format(system_status[lng][ec_status+2]))
            dsc.append(gen_settings_text[lng][9].format(system_status[lng][rnk_status+2]))

            emb.description="\n".join(dsc)
            gen_view = GenSettingsView(t_out=50, auth_id=self.auth_id, bot=self.bot, lng=lng, ec_status=ec_status, rnk_status=rnk_status)
            await interaction.response.send_message(embed=emb, view=gen_view)
            await gen_view.wait()
            for c in gen_view.children:
                c.disabled = True
            await interaction.edit_original_message(view=gen_view)

        elif custom_id.startswith("1_"):
            with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                with closing(base.cursor()) as cur:
                    m_rls: list = cur.execute("SELECT * FROM mod_roles").fetchall()
            emb = Embed(title=mod_roles_text[lng][0])
            if m_rls:
                m_rls: set[int] = {x[0] for x in m_rls}
                emb.description = "\n".join([mod_roles_text[lng][2]] + [f"<@&{i}> - {i}" for i in m_rls])
                rem_dis = False
            else:
                emb.description=mod_roles_text[lng][1]
                m_rls = set()
                rem_dis = True

            rls = [(r.name, r.id) for r in interaction.guild.roles if not r.is_bot_managed()]
            
            m_rls_v = ModRolesView(t_out=50, m_rls=m_rls, lng=lng, auth_id=self.auth_id, rem_dis=rem_dis, rls=rls)
            await interaction.response.send_message(embed=emb, view=m_rls_v)
            await m_rls_v.wait()
            for c in m_rls_v.children:
                c.disabled = True
            await interaction.edit_original_message(view=m_rls_v)

        elif custom_id.startswith("2_"):
            await interaction.response.send_message(embed=Embed(description=settings_text[lng][7]))
            flag = 0
            while not flag:
                try:
                    m_ans = await interaction.client.wait_for(event="message", check=lambda m: m.author.id == interaction.user.id and m.channel.id == interaction.channel_id, timeout=30)
                except TimeoutError:
                    await interaction.delete_original_message()
                    flag = 1
                else:
                    ans: str = m_ans.content
                    try: await m_ans.delete()
                    except: pass
                    memb, flag = self.check_ans(interaction=interaction, ans=ans)
                    if flag == 1:
                        await interaction.delete_original_message()
            if flag != 2:
                return
            
            memb_id = memb.id
            with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                with closing(base.cursor()) as cur:
                    memb_info = self.check_memb(base=base, cur=cur, memb_id=memb_id)
                    xp_b = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
                    membs_cash = sorted(cur.execute("SELECT memb_id, money FROM users").fetchall(), key=lambda tup: tup[1], reverse=True)
                    membs_xp = sorted(cur.execute("SELECT memb_id, xp FROM users").fetchall(), key=lambda tup: tup[1], reverse=True)
                    db_roles = cur.execute("SELECT role_id FROM server_roles").fetchall()

            l = len(membs_cash)     

            # cnt_cash is a place in the rating sorded by cash
            cash = memb_info[1]
            if membs_cash[l//2][1] < cash:
                cnt_cash = 1
                while cnt_cash < l and memb_id != membs_cash[cnt_cash-1][0]:
                    cnt_cash += 1
            else:
                cnt_cash = l
                while cnt_cash > 1 and memb_id != membs_cash[cnt_cash-1][0]:
                    cnt_cash -= 1

            emb1 = Embed()
            emb1.description = mng_membs_text[lng][5].format(memb_id, memb_id)
            emb1.add_field(name=mng_membs_text[lng][1], value=code_blocks[1].format(cash), inline=True)
            emb1.add_field(name=mng_membs_text[lng][4], value=code_blocks[1].format(cnt_cash), inline=True)

            # cnt_cash is a place in the rating sorded by xp
            xp = memb_info[4]
            if membs_xp[l//2][1] < xp:
                cnt_xp = 1
                while cnt_xp < l and memb_id != membs_xp[cnt_xp-1][0]:
                    cnt_xp += 1
            else:
                cnt_xp = l
                while cnt_xp > 1 and memb_id != membs_xp[cnt_xp-1][0]:
                    cnt_xp -= 1

            level = (xp + xp_b - 1) // xp_b
            
            emb2 = Embed()
            emb2.add_field(name=mng_membs_text[lng][2], value=code_blocks[2].format(f"{xp}/{level * xp_b + 1}"), inline=True)
            emb2.add_field(name=mng_membs_text[lng][3], value=code_blocks[2].format(level), inline=True)
            emb2.add_field(name=mng_membs_text[lng][4], value=code_blocks[2].format(cnt_xp), inline=True)

            emb3 = Embed()
            if memb_info[2] != "":
                dsc = [code_blocks[lng*5]] + [f"<@&{r}>**` - {r}`**" for r in memb_info[2].split("#") if r != ""]
            else:
                dsc = [mng_membs_text[lng][6]]
            emb3.description = "\n".join(dsc)
            rem_dis = True if len(dsc) == 1 else False

            if db_roles: db_roles = {x[0] for x in db_roles}
            roles = [(rl.name, rl.id) for rl in interaction.guild.roles if rl.is_assignable() and rl.id in db_roles]

            mng_v = ManageMemberView(
                timeout=110, 
                lng=lng, 
                auth_id=interaction.user.id, 
                memb_id=memb_id, 
                memb_rls={int(r) for r in memb_info[2].split("#") if r != ""}, 
                rls=roles,
                cur_money=cash,
                cur_xp=xp,
                rem_dis=rem_dis,
                g_id=interaction.guild_id,
                member=memb
            )

            await interaction.edit_original_message(embeds=[emb1, emb2, emb3], view=mng_v)
            
            await mng_v.wait()
            for c in mng_v.children:
                c.disabled = True
            await interaction.edit_original_message(view=mng_v)

        elif custom_id.startswith("3_"):
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
                dsc.append(ec_text[lng][5].format(settings_text[lng][13]))
            else:
                dsc.append(ec_text[lng][5].format(f"<#{e_l_c}>"))
            dsc.append(ec_text[lng][7])
            dsc.append(ec_text[lng][8])
            emb.description = "\n\n".join(dsc)
            
            ec_v = EconomyView(t_out=110, auth_id=self.auth_id)
            await interaction.response.send_message(embed=emb, view=ec_v)
            await ec_v.wait()
            for c in ec_v.children:
                c.disabled = True
            await interaction.edit_original_message(view=ec_v)

        elif custom_id.startswith("4_"):   
            with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                with closing(base.cursor()) as cur:
                    xp_p_m = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_per_msg'").fetchone()[0]
                    xp_b = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
                    lvl_c_a = cur.execute("SELECT value FROM server_info WHERE settings = 'lvl_c'").fetchone()[0]

            emb = Embed()
            dsc = [ranking_text[lng][0].format(xp_p_m)]
            dsc.append(ranking_text[lng][1].format(xp_b))
            if lvl_c_a == 0:
                dsc.append(ranking_text[lng][2].format(settings_text[lng][13]))
            else:
                dsc.append(ranking_text[lng][2].format(f"<#{lvl_c_a}>"))

            dsc += [ranking_text[lng][i] for i in (4, 5, 6)]

            emb.description = "\n\n".join(dsc)
            rnk_v = RankingView(timeout=90, auth_id=interaction.user.id, g_id=interaction.guild_id, cur_xp_pm=xp_p_m, cur_xpb=xp_b)
            
            await interaction.response.send_message(embed=emb, view=rnk_v)

            await rnk_v.wait()
            for c in rnk_v.children:
                c.disabled = True
            await interaction.edit_original_message(view=rnk_v)

        elif custom_id.startswith("5_"):
            with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                with closing(base.cursor()) as cur:
                    p_v_c = cur.execute("SELECT value FROM server_info WHERE settings = 'poll_v_c'").fetchone()[0]
                    p_c = cur.execute("SELECT value FROM server_info WHERE settings = 'poll_c'").fetchone()[0]
            
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

            p_v = PollSettingsView(timeout=100, auth_id=self.auth_id)
            await interaction.response.send_message(embed=Embed(description="\n\n".join(dsc)), view=p_v)
            
            await p_v.wait()
            for c in p_v.children:
                c.disabled = True
            await interaction.edit_original_message(view=p_v)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class PollSettingsView(View):
    def __init__(self, timeout: int, auth_id: int):
        super().__init__(timeout=timeout)
        self.add_item(CustomButton(style=ButtonStyle.green, label="", custom_id=f"28_{auth_id}_{randint(1, 100)}", emoji="🔎"))
        self.add_item(CustomButton(style=ButtonStyle.green, label="", custom_id=f"29_{auth_id}_{randint(1, 100)}", emoji="📰"))
        self.auth_id = auth_id
    
    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        me = interaction.guild.me
        chnls = [(c.name, c.id) for c in interaction.guild.text_channels if c.permissions_for(me).send_messages]

        if c_id.startswith("28_"):
            v_c = PollsChannelsView(timeout=25, lng=lng, view_id_base = 1400, auth_id=self.auth_id, chnls=chnls)
            await interaction.response.send_message(embed=Embed(description=settings_text[lng][11]), view=v_c)
            
            await v_c.wait()
            await interaction.delete_original_message()
            if v_c.c is None:
                return

            if v_c.c:
                with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                    with closing(base.cursor()) as cur:
                        cur.execute("UPDATE server_info SET value = ? WHERE settings = 'poll_v_c'", (v_c.c,))
                        base.commit()
                
                emb = interaction.message.embeds[0]
                dsc = emb.description.split("\n\n")
                dsc[0] = poll_text[lng][0].format(f"<#{v_c.c}>")
                emb.description = "\n\n".join(dsc)
                await interaction.message.edit(embed=emb)

                await interaction.send(embed=Embed(description=poll_text[lng][4].format(v_c.c)), ephemeral=True)
                           
            else:
                with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                    with closing(base.cursor()) as cur:
                        cur.execute("UPDATE server_info SET value = 0 WHERE settings = 'poll_v_c'")
                        base.commit()

                emb = interaction.message.embeds[0]
                dsc = emb.description.split("\n\n")
                dsc[0] = poll_text[lng][0].format(settings_text[lng][13])
                emb.description = "\n\n".join(dsc)
                await interaction.message.edit(embed=emb)

                await interaction.send(embed=Embed(description=poll_text[lng][5]), ephemeral=True)

        elif c_id.startswith("29_"):
            v_c = PollsChannelsView(timeout=25, lng=lng, view_id_base = 1500, auth_id=self.auth_id, chnls=chnls)
            await interaction.response.send_message(embed=Embed(description=settings_text[lng][11]), view=v_c)
            
            await v_c.wait()
            await interaction.delete_original_message()
            if v_c.c is None:
                return

            if v_c.c:
                with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                    with closing(base.cursor()) as cur:
                        cur.execute("UPDATE server_info SET value = ? WHERE settings = 'poll_c'", (v_c.c,))
                        base.commit()
                
                emb = interaction.message.embeds[0]
                dsc = emb.description.split("\n\n")
                dsc[1] = poll_text[lng][1].format(f"<#{v_c.c}>")
                emb.description = "\n\n".join(dsc)
                await interaction.message.edit(embed=emb)

                await interaction.send(embed=Embed(description=poll_text[lng][6].format(v_c.c)), ephemeral=True)
                       
            else:
                with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                    with closing(base.cursor()) as cur:
                        cur.execute("UPDATE server_info SET value = 0 WHERE settings = 'poll_c'")
                        base.commit()

                emb = interaction.message.embeds[0]
                dsc = emb.description.split("\n\n")
                dsc[1] = poll_text[lng][1].format(settings_text[lng][13])
                emb.description = "\n\n".join(dsc)
                await interaction.message.edit(embed=emb)

                await interaction.send(embed=Embed(description=poll_text[lng][7]), ephemeral=True)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class RankingView(View):
    def __init__(self, timeout: int, auth_id: int, g_id: int, cur_xp_pm: int, cur_xpb: int):
        super().__init__(timeout=timeout)
        self.add_item(CustomButton(style=ButtonStyle.green, label="", emoji="✨", custom_id=f"21_{auth_id}_{randint(1, 100)}"))
        self.add_item(CustomButton(style=ButtonStyle.grey, label="", emoji="📗", custom_id=f"22_{auth_id}_{randint(1, 100)}"))
        self.add_item(CustomButton(style=ButtonStyle.grey, label="", emoji="<:ignored_channels:1003673081996378133>", custom_id=f"23_{auth_id}_{randint(1, 100)}"))
        self.add_item(CustomButton(style=ButtonStyle.red, label="", emoji="🥇", custom_id=f"24_{auth_id}_{randint(1, 100)}"))
        self.auth_id = auth_id
        self.cur_xp_pm = cur_xp_pm
        self.cur_xpb = cur_xpb
        self.g_id = g_id
        self.lvl_chnl = None
    
    async def xp_change(self, lng: int, interaction: Interaction):
        xp_m = XpSettingsModal(timeout=80, lng=lng, auth_id=self.auth_id, g_id=self.g_id, cur_xp=self.cur_xp_pm, cur_xpb=self.cur_xpb)
        await interaction.response.send_modal(modal=xp_m)
        await xp_m.wait()

        if xp_m.changed:
            self.cur_xp_pm = xp_m.old_xp
            self.cur_xpb = xp_m.old_xpb

            emb = interaction.message.embeds[0]
            dsc = emb.description.split("\n\n")
            dsc[0] = ranking_text[lng][0].format(self.cur_xp_pm)
            dsc[1] = ranking_text[lng][1].format(self.cur_xpb)
            emb.description = "\n\n".join(dsc)
            await interaction.message.edit(embed=emb)

    async def ic(self, lng: int, interaction: Interaction):
        chnls = [(c.name, c.id) for c in interaction.guild.text_channels]
        with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                db_chnls = cur.execute("SELECT chnl_id FROM ic").fetchall()
        if len(db_chnls):
            ignored_channels[self.g_id] = {r[0] for r in db_chnls}
            dsc = [ranking_text[lng][17]] + [f"<#{r}>**` - {r}`**" for r in ignored_channels[self.g_id]]
            rd = False
        else:
            ignored_channels[self.g_id] = set()
            rd = True
            dsc = [ranking_text[lng][18]]
        
        emb = Embed(description="\n".join(dsc))     
        ic_v = IgnoredChannelsView(timeout=80, lng=lng, auth_id=self.auth_id, chnls=chnls, rem_dis=rd, g_id=self.g_id)

        await interaction.response.send_message(embed=emb, view=ic_v)
        await ic_v.wait()
        await interaction.delete_original_message()

    async def level_channel(self, lng: int, interaction: Interaction):
        
        me = interaction.guild.me
        chnls = [(c.name, c.id) for c in interaction.guild.text_channels if c.permissions_for(me).send_messages]
        l = len(chnls)
        
        for i in range(min((l + 23) // 24, 20)):
            self.add_item(CustomSelect(custom_id=f"{1200+i}_{self.auth_id}_{randint(1, 100)}", placeholder=settings_text[lng][10], opts=[(settings_text[lng][12], 0)] + chnls[i*24:min((i+1)*24, l)]))
            
        await interaction.message.edit(view=self)

        await interaction.response.send_message(embed=Embed(description=settings_text[lng][11]), ephemeral=True)

        cnt = 0
        while self.lvl_chnl is None and cnt < 30:
            cnt += 1
            await sleep(1)

        i = 0
        while i < len(self.children):
            if self.children[i].custom_id.startswith("12"):
                self.remove_item(self.children[i])
            else:
                i += 1

        if cnt >= 30:
            await interaction.message.edit(view=self)
            self.lvl_chnl = None
            return
        
        with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'lvl_c'", (self.lvl_chnl,))
                base.commit()
        
        emb = interaction.message.embeds[0]
        dsc = emb.description.split("\n\n")
        if self.lvl_chnl:
            dsc[2] = ranking_text[lng][2].format(f"<#{self.lvl_chnl}>")
        else:
            dsc[2] = ranking_text[lng][2].format(settings_text[lng][13])
        emb.description = "\n\n".join(dsc)

        self.lvl_chnl = None

        await interaction.message.edit(embed=emb, view=self)
            
    async def lvl_roles(self, lng: int, interaction: Interaction):
        with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                lvl_rls = sorted(cur.execute("SELECT * FROM rank_roles").fetchall(), key=lambda tup: tup[0])
        if lvl_rls:
            dsc = [f"**`{n} {ranking_text[lng][24]} - `**<@&{r}>" for n, r in lvl_rls]
            rem_b = False
        else:
            rem_b = True
            dsc = [ranking_text[lng][25]]
        dsc.append(ranking_text[lng][27])
        emb = Embed(title=ranking_text[lng][26], description="\n".join(dsc))
        lr_v = LevelRolesView(timeout=80, auth_id=interaction.user.id, g_id=self.g_id, disabled=rem_b)
        await interaction.response.send_message(embed=emb, view=lr_v)
        await lr_v.wait()
        await interaction.delete_original_message()

    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        if c_id.startswith("21_"):
            await self.xp_change(lng=lng, interaction=interaction)
        elif c_id.startswith("22_"):
            await self.level_channel(lng=lng, interaction=interaction)
        elif c_id.startswith("23_"):
            await self.ic(lng=lng, interaction=interaction)
        elif c_id.startswith("24_"):
            await self.lvl_roles(lng=lng, interaction=interaction)
    
    async def click_menu(self, _, c_id: str, values):
        if c_id.startswith("12"):
            self.lvl_chnl = int(values[0])

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class PollsChannelsView(View):
    def __init__(self, timeout: int, lng: int, view_id_base: int,  auth_id: int, chnls: list):
        super().__init__(timeout=timeout)
        for i in range(min((len(chnls) + 23) // 24, 20)):
            self.add_item(CustomSelect(
                custom_id=f"{view_id_base+i}_{auth_id}_{randint(1, 100)}", 
                placeholder=settings_text[lng][10], 
                opts=[(settings_text[lng][12], 0)] + chnls[i*24:min(len(chnls), (i+1)*24)]
            ))
        self.auth_id = auth_id
        self.c = None
        
    async def click_menu(self, _, c_id: str, values):
        if c_id.startswith("14") or c_id.startswith("15"):
            self.c = int(values[0])
            self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class LevelRolesView(View):
    def __init__(self, timeout: int, auth_id: int, g_id: int, disabled: bool):
        super().__init__(timeout=timeout)
        self.add_item(CustomButton(style=ButtonStyle.green, label="🔧", custom_id=f"27_{auth_id}_{randint(1, 100)}", emoji="<:add01:999663315804500078>"))
        self.add_item(CustomButton(style=ButtonStyle.red, label="", custom_id=f"28_{auth_id}_{randint(1, 100)}", emoji="<:remove01:999663428689997844>", disabled=disabled))
        self.auth_id: int = auth_id
        self.g_id: int = g_id
        self.role = None
    
    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        lvl_modal = SelectLevelModal(lng=lng, auth_id=interaction.user.id, timeout=60)
        await interaction.response.send_modal(modal=lvl_modal)
        await lvl_modal.wait()
        if lvl_modal.level:
            ans = lvl_modal.level
        else:
            return
        
        if c_id.startswith("27_"):
            rls = [(r.name, r.id) for r in interaction.guild.roles if r.is_assignable()]
            if not len(rls):
                await interaction.send(embed=Embed(description = ranking_text[lng][30]), ephemeral=True)
                return
            for i in range((len(rls) + 24) // 25):
                self.add_item(CustomSelect(
                    custom_id=f"{1300+i}_{self.auth_id}_{randint(1, 100)}", 
                    placeholder=settings_text[lng][2], 
                    opts=rls[i*25:min(len(rls), (i+1) * 25)]
                ))
            await interaction.message.edit(view=self)
            await interaction.send(embed=Embed(description = ranking_text[lng][29].format(ans)), ephemeral=True)

            cnt = 0
            while self.role is None and cnt < 25:
                cnt += 1
                await sleep(1)
            if self.role is None:
                while i < len(self.children):
                    if self.children[i].custom_id.startswith("13"):
                        self.remove_item(self.children[i])
                    else:
                        i += 1
                await interaction.message.edit(view=self)
                await interaction.send(embed=Embed(description=ranking_text[lng][32]), ephemeral=True)
                return

            with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    if cur.execute("SELECT role_id FROM rank_roles WHERE level = ?", (ans,)).fetchone() is None:
                        cur.execute("INSERT INTO rank_roles(level, role_id) VALUES(?, ?)", (ans, self.role))
                    else:
                        cur.execute("UPDATE rank_roles SET role_id = ? WHERE level = ?", (self.role, ans))
                    base.commit()
                    lvl_rls = sorted(cur.execute("SELECT * FROM rank_roles").fetchall(), key=lambda tup: tup[0])

            i = 0
            while i < len(self.children):
                if self.children[i].custom_id.startswith("13"):
                    self.remove_item(self.children[i])
                else:
                    i += 1
            
            dsc = [f"**`{n} {ranking_text[lng][24]} - `**<@&{r}>" for n, r in lvl_rls]  
            dsc.append(ranking_text[lng][27])
            emb = Embed(title=ranking_text[lng][26], description="\n".join(dsc))
            
            if self.children[1].disabled:
                self.children[1].disabled = False

            await interaction.message.edit(embed=emb, view=self)
            await interaction.send(embed=Embed(description=ranking_text[lng][31].format(ans, self.role)), ephemeral=True)
            self.role = None    

        elif c_id.startswith("28_"):
            with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    if cur.execute("SELECT count() FROM rank_roles WHERE level = ?", (ans,)).fetchone()[0]:
                        cur.execute("DELETE FROM rank_roles WHERE level = ?", (ans,))
                        base.commit()
                        lvl_rls = sorted(cur.execute("SELECT * FROM rank_roles").fetchall(), key=lambda tup: tup[0])
                    else:
                        await interaction.send(embed=Embed(description=ranking_text[lng][34].format(ans)), ephemeral=True)
                        return

            if lvl_rls:
                dsc = [f"**`{n} {ranking_text[lng][24]} - `**<@&{r}>" for n, r in lvl_rls]
                fl = False
            else:
                self.children[1].disabled = True
                fl = True
                dsc = [ranking_text[lng][25]]

            dsc.append(ranking_text[lng][27])
            emb = Embed(title=ranking_text[lng][26], description="\n".join(dsc))
            
            if fl:
                await interaction.message.edit(embed=emb, view=self)
            else:
                await interaction.message.edit(embed=emb)

            await interaction.send(embed=Embed(description=ranking_text[lng][33].format(ans)), ephemeral=True)

    async def click_menu(self, _, c_id: str, values):
        if c_id.startswith("13"):
            self.role = int(values[0])
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if self.auth_id != interaction.user.id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class IgnoredChannelsView(View):
    def __init__(self, timeout: int, lng: int, auth_id: int, chnls: list, rem_dis: bool, g_id: int):
        super().__init__(timeout=timeout)
        l = len(chnls)
        for i in range(min((l + 23) // 24, 20)):
            self.add_item(CustomSelect(custom_id=f"{1100+i}_{auth_id}_{randint(1, 100)}", placeholder=settings_text[lng][10], opts=[(settings_text[lng][12], 0)] + chnls[i*24:min((i+1)*24, l)]))
        self.add_item(CustomButton(style=ButtonStyle.green, label=settings_text[lng][8], emoji="<:add01:999663315804500078>", custom_id=f"25_{auth_id}_{randint(1, 100)}"))
        self.add_item(CustomButton(style=ButtonStyle.red, label=settings_text[lng][9], emoji="<:remove01:999663428689997844>", custom_id=f"26_{auth_id}_{randint(1, 100)}", disabled=rem_dis))
        self.chnl = None
        self.g_id = g_id
        self.auth_id = auth_id

    async def add_chnl(self, interaction: Interaction, lng: int):
        with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("INSERT OR IGNORE INTO ic(chnl_id) VALUES(?)", (self.chnl,))
                base.commit()
        ignored_channels[self.g_id].add(self.chnl)

        emb = interaction.message.embeds[0]
        dsc = emb.description.split("\n")

        if len(dsc) == 1:
            dsc = [ranking_text[lng][17], f"<#{self.chnl}>**` - {self.chnl}`**"]
            emb.description = "\n".join(dsc)
            self.children[-1].disabled = False
            await interaction.message.edit(embed=emb, view=self)
        else:
            dsc.append(f"<#{self.chnl}>**` - {self.chnl}`**")
            emb.description = "\n".join(dsc)
            await interaction.message.edit(embed=emb)
        await interaction.response.send_message(embed=Embed(description=ranking_text[lng][19].format(self.chnl)), ephemeral=True)
        self.chnl = None
    
    async def rem_chnl(self, interaction: Interaction, lng: int):
        with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("DELETE FROM ic WHERE chnl_id = ?", (self.chnl,))
                base.commit()
        ignored_channels[self.g_id].remove(self.chnl)

        emb = interaction.message.embeds[0]
        dsc = emb.description.split("\n")
        if len(dsc) <= 2:
            dsc = [ranking_text[lng][18]]
            self.children[-1].disabled = True
            emb.description = "\n".join(dsc)
            await interaction.message.edit(embed=emb, view=self)
        else:
            s_c = f"{self.chnl}"
            i = 0
            while i < len(dsc):
                if s_c in dsc[i]:
                    dsc.pop(i)
                    i = len(dsc) + 2
                else:
                    i += 1
            emb.description = "\n".join(dsc)
            await interaction.message.edit(embed=emb)
        await interaction.response.send_message(embed=Embed(description=ranking_text[lng][20].format(self.chnl)), ephemeral=True)
        self.chnl = None

    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        if not self.chnl:
            await interaction.response.send_message(embed=Embed(description=ranking_text[lng][21]), ephemeral=True)
            return
        if c_id.startswith("25_"):
            if self.chnl in ignored_channels[self.g_id]:
                await interaction.response.send_message(embed=Embed(description=ranking_text[lng][22]), ephemeral=True)
                return
            await self.add_chnl(interaction=interaction, lng=lng)
        elif c_id.startswith("26_"):
            if not self.chnl in ignored_channels[self.g_id]:
                await interaction.response.send_message(embed=Embed(description=ranking_text[lng][23]), ephemeral=True)
                return
            await self.rem_chnl(interaction=interaction, lng=lng)           

    async def click_menu(self, _, c_id: str, values):
        if c_id.startswith("11"):
            self.chnl = int(values[0])

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class ManageMemberView(View):
    def __init__(self, timeout: int, lng: int, auth_id: int, memb_id: int, memb_rls: set, rls: list, cur_money: int, cur_xp: int, rem_dis: bool, g_id: int, member):
        super().__init__(timeout=timeout)
        self.add_item(CustomButton(style=ButtonStyle.blurple, label=mng_membs_text[lng][0], emoji="🔧", custom_id=f"18_{auth_id}_{randint(1, 100)}"))
        for i in range((len(rls)+24)//25):
            self.add_item(CustomSelect(custom_id=f"{300+i}_{auth_id}_{randint(1, 100)}", placeholder=settings_text[lng][2], opts=rls[i*25:min(len(rls), (i+1)*25)]))
        self.add_item(CustomButton(style=ButtonStyle.green, label=settings_text[lng][4], emoji="<:add01:999663315804500078>", custom_id=f"19_{auth_id}_{randint(1, 100)}"))
        self.add_item(CustomButton(style=ButtonStyle.red, label=settings_text[lng][5], emoji="<:remove01:999663428689997844>", custom_id=f"20_{auth_id}_{randint(1, 100)}", disabled=rem_dis))
        self.role = None
        self.memb_id = memb_id
        self.memb_rls = memb_rls
        self.cash = cur_money
        self.xp = cur_xp
        self.g_id = g_id
        self.auth_id = auth_id
        self.member=member

    async def add_r(self, lng: int, interaction: Interaction):
        if self.role in self.memb_rls:
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][7]), ephemeral=True)
            return
        self.memb_rls.add(self.role)

        with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                m_rls = cur.execute("SELECT owned_roles FROM users WHERE memb_id = ?",(self.memb_id,)).fetchone()[0]
                cur.execute("UPDATE users SET owned_roles = ? WHERE memb_id = ?", (m_rls + f"#{self.role}", self.memb_id))
                membs = cur.execute("SELECT members FROM salary_roles WHERE role_id = ?", (self.role,)).fetchone()
                if membs:
                    cur.execute("UPDATE salary_roles SET members = ? WHERE role_id = ?", (membs[0] + f"#{self.memb_id}", self.role))
                base.commit()

        await self.member.add_roles(interaction.guild.get_role(self.role))

        embs = interaction.message.embeds
        emb3 = embs[2]
        dsc = emb3.description.split("\n")
        
        if len(dsc) == 1:
            dsc = [code_blocks[lng*5], f"<@&{self.role}>**` - {self.role}`**"]
            self.children[-1].disabled = False
            emb3.description = "\n".join(dsc)
            embs[2] = emb3
            await interaction.message.edit(embeds=embs, view=self)
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][8].format(self.role, self.memb_id)), ephemeral=True)
        else:
            dsc.append(f"<@&{self.role}>**` - {self.role}`**")
            emb3.description = "\n".join(dsc)
            embs[2] = emb3
            await interaction.message.edit(embeds=embs)
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][8].format(self.role, self.memb_id)), ephemeral=True)
        self.role = None
        

    async def rem_r(self, lng: int, interaction: Interaction):
        if not self.role in self.memb_rls:
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][9]), ephemeral=True)
            return
        self.memb_rls.remove(self.role)

        with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
            with closing(base.cursor()) as cur:
                m_rls = cur.execute("SELECT owned_roles FROM users WHERE memb_id = ?",(self.memb_id,)).fetchone()[0]
                cur.execute("UPDATE users SET owned_roles = ? WHERE memb_id = ?", (m_rls.replace(f"#{self.role}", ""), self.memb_id))
                membs = cur.execute("SELECT members FROM salary_roles WHERE role_id = ?", (self.role,)).fetchone()
                if membs:
                    cur.execute("UPDATE salary_roles SET members = ? WHERE role_id = ?", (membs[0].replace(f"#{self.memb_id}", ""), self.role))
                base.commit()
        await self.member.remove_roles(interaction.guild.get_role(self.role))
        
        embs = interaction.message.embeds
        emb3 = embs[2]
        dsc = emb3.description.split("\n")
        if len(dsc) <= 4:
            emb3.description = mng_membs_text[lng][6]
            self.children[-1].disabled = True
            embs[2] = emb3
            await interaction.message.edit(embeds=embs, view=self)
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][10].format(self.role, self.memb_id)), ephemeral=True)            
        else:
            i = 0
            s_role = f"{self.role}"
            while i < len(dsc):
                if s_role in dsc[i]:
                    dsc.pop(i)
                    i = len(dsc) + 2
                i += 1
            emb3.description = "\n".join(dsc)
            embs[2] = emb3
            await interaction.message.edit(embeds=embs)
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][10].format(self.role, self.memb_id)), ephemeral=True)
        self.role = None

    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0

        if c_id.startswith("18_"):
            edit_modl = ManageMemberCashXpModal(timeout=90, title=mng_membs_text[lng][19], lng=lng, memb_id=self.memb_id, cur_money=self.cash, cur_xp=self.xp, auth_id=self.auth_id)

            await interaction.response.send_modal(modal=edit_modl)
            await edit_modl.wait()
            
            if edit_modl.is_changed:
                
                embs = interaction.message.embeds

                with closing(connect(f'{path_to}/bases/bases_{self.g_id}/{self.g_id}.db')) as base:
                    with closing(base.cursor()) as cur:
                        xp_b = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
                        if self.cash != edit_modl.new_cash:
                            membs_cash = sorted(cur.execute("SELECT memb_id, money FROM users").fetchall(), key=lambda tup: tup[1], reverse=True)
                            l = len(membs_cash)
                        if self.xp != edit_modl.new_xp:
                            membs_xp = sorted(cur.execute("SELECT memb_id, xp FROM users").fetchall(), key=lambda tup: tup[1], reverse=True)
                            l = len(membs_xp)
                
                
                if self.cash != edit_modl.new_cash:
                    self.cash = edit_modl.new_cash
                    
                    if membs_cash[l//2][1] < self.cash:
                        cnt_cash = 1
                        while cnt_cash < l and self.memb_id != membs_cash[cnt_cash-1][0]:
                            cnt_cash += 1
                    else:
                        cnt_cash = l
                        while cnt_cash > 1 and self.memb_id != membs_cash[cnt_cash-1][0]:
                            cnt_cash -= 1

                    embs[0].set_field_at(index=0, name=mng_membs_text[lng][1], value=code_blocks[1].format(self.cash))
                    embs[0].set_field_at(index=1, name=mng_membs_text[lng][4], value=code_blocks[1].format(cnt_cash))

                if self.xp != edit_modl.new_xp:
                    self.xp = edit_modl.new_xp

                    if membs_xp[l//2][1] < self.xp:
                        cnt_xp = 1
                        while cnt_xp < l and self.memb_id != membs_xp[cnt_xp-1][0]:
                            cnt_xp += 1
                    else:
                        cnt_xp = l
                        while cnt_xp > 1 and self.memb_id != membs_xp[cnt_xp-1][0]:
                            cnt_xp -= 1

                    level = (self.xp + xp_b - 1) // xp_b

                    embs[1].set_field_at(index=0, name=mng_membs_text[lng][2], value=code_blocks[2].format(f"{self.xp}/{level * xp_b + 1}"))
                    embs[1].set_field_at(index=1, name=mng_membs_text[lng][3], value=code_blocks[2].format(level))
                    embs[1].set_field_at(index=2, name=mng_membs_text[lng][4], value=code_blocks[2].format(cnt_xp))
                    
                await interaction.message.edit(embeds=embs)

            return

        if self.role is None:
            await interaction.response.send_message(embed=Embed(description=settings_text[lng][6]), ephemeral=True)
            return
        if c_id.startswith("19_"):
            await self.add_r(lng=lng, interaction=interaction)
        elif c_id.startswith("20_"):
            await self.rem_r(lng=lng, interaction=interaction)

    async def click_menu(self, __, c_id: str, values):
        if c_id.startswith("30") and c_id[3] == "_":
            self.role = int(values[0])
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class VerifyDeleteView(View):
    def __init__(self, lng: int, role: int, m, auth_id: int):
        super().__init__(timeout=30)
        self.role = role
        self.auth_id = auth_id
        self.m = m
        self.deleted = False
        self.add_item(CustomButton(style=ButtonStyle.red, label=ec_mr_text[lng][1], custom_id=f"1000_{auth_id}_{randint(1, 100)}"))
        self.add_item(CustomButton(style=ButtonStyle.green, label=ec_mr_text[lng][2], custom_id=f"1001_{auth_id}_{randint(1, 100)}"))
    
    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0
        if c_id.startswith("1001_"):
            await interaction.message.delete()
            await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][3].format(self.role)), ephemeral=True)
            self.stop()
        elif c_id.startswith("1000_"):
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
                            cur.execute("UPDATE users SET owned_roles = ? WHERE memb_id = ?", (r[2].replace(f"#{self.role}", ""), r[0]))
                            base.commit()
                            
            await interaction.edit_original_message(embed=Embed(description=ec_mr_text[lng][5].format(self.role)))
            await interaction.message.delete()
            emb = self.m.embeds[0]
            dsc = emb.description.split("\n")
            i = 0
            while i < len(dsc):
                if f"{self.role}" in dsc[i]:
                    del dsc[i]
                else:
                    i += 1

            if len(dsc) == 3:
                dsc[0] = ec_text[lng][19]

            emb.description = "\n".join(dsc)
            await self.m.edit(embed=emb)
            self.deleted = True
            self.stop()
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True

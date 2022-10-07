
from asyncio import sleep, TimeoutError
from contextlib import closing
from sqlite3 import connect, Connection, Cursor
from random import randint
from time import time

from nextcord import Embed, Locale, Interaction, slash_command, ButtonStyle, Message, SelectOption, TextInputStyle
from nextcord.ui import View, Button, Select, TextInput, Modal
from nextcord.ext import application_checks
from nextcord.ext.commands import Cog, Bot

from Variables.vars import path_to, ignored_channels

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
        29 : "**If emoji is `default discord emoji` (not from any server), print it's `name without ':'`. Otherwise print `emoji or it's id`**",
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
        29 : "**Если эмодзи является `стандартным эмодзи дискорда` (не с сервера), напишите `имя эмодзи без ':'`. Инача напишите `эмодзи или его id`**",
        30 : "**`Новое эмодзи валюты сервера: `**{}"
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
        9 : "Write amount of money gained for message (non negative integer number)",
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
        9 : "Укажите количество денег, получаемых за сообщение\n(неотрицательное целое число)",
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
        22 : "Type of displaying of the role should be one of three numbers: 1, 2 or 3",
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
        22 : "В качестве типа отображения роли надо указать одно из трёх чисел: 1, 2 или 3",
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
        34 : "**`No roles matches level {}`**"
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
        34 : "**`Уровню {} не соответствует ни одна роль`**"
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

code_blocks = {
    0 : "```\nOwned roles\n```",
    5 : "```\nЛичные роли\n```",
    1 : "```fix\n{}\n```",
    2 : "```c\n{}\n```",
}

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


class c_select(Select):

    def __init__(self, custom_id: str, placeholder: str, opts: list) -> None:
        options = [SelectOption(label=r[0], value=r[1]) for r in opts]
        super().__init__(custom_id=custom_id, placeholder=placeholder, options=options)
    
    async def callback(self, interaction: Interaction) -> None:
        await self.view.click_menu(interaction, self.custom_id, self.values)        


class c_button(Button):
    def __init__(self, style: ButtonStyle, label: str, custom_id: str, disabled: bool = False, emoji = None, row: int = None) -> None:
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row)

    async def callback(self, interaction: Interaction) -> None:
        await super().view.click(interaction, self.custom_id)


class gen_settings_view(View):

    def __init__(self, t_out: int, auth_id: int, bot: Bot, lng: int, ec_status: int, rnk_status: int) -> None:
        super().__init__(timeout=t_out)
        self.bot: Bot = bot
        self.auth_id: int = auth_id
        self.lang = None
        self.tz = None
        self.ec_status: int = ec_status
        self.rnk_status: int = rnk_status
        tzs: list[tuple[str, int]] = [(f"UTC{i}", i) for i in range(-12, 0)] + [(f"UTC+{i}", i) for i in range(0, 13)]
        self.add_item(c_select(custom_id=f"100_{auth_id}_{randint(1, 100)}", placeholder=gen_settings_text[lng][20], opts=languages[2][lng]))
        self.add_item(c_select(custom_id=f"101_{auth_id}_{randint(1, 100)}", placeholder=gen_settings_text[lng][21], opts=tzs))
        self.add_item(c_button(style=ButtonStyle.green, label=None, custom_id=f"6_{auth_id}_{randint(1, 100)}", emoji="🗣️"))
        self.add_item(c_button(style=ButtonStyle.blurple, label=None, custom_id=f"7_{auth_id}_{randint(1, 100)}", emoji="⏱"))
        self.add_item(c_button(style=ButtonStyle.gray, label=None, custom_id=f"42_{auth_id}_{randint(1, 100)}", emoji="💵"))
        self.add_item(c_button(style=ButtonStyle.red, label=None, custom_id=f"43_{auth_id}_{randint(1, 100)}", emoji="💰", row=2))
        self.add_item(c_button(style=ButtonStyle.red, label=None, custom_id=f"44_{auth_id}_{randint(1, 100)}", emoji="📈", row=2))
        
    async def select_lng(self, interaction: Interaction, lng: int) -> None:
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
    
    async def digit_tz(self, interaction: Interaction, lng: int) -> None:
        tz = self.tz
        if tz is None:
            await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][25]), ephemeral=True)
            return
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'tz'", (tz,))
                base.commit()
        if tz >= 0: tz = f"+{tz}"
        else: tz = f"{tz}"

        emb = interaction.message.embeds[0]
        dsc = emb.description.split("\n")
        dsc[1] = gen_settings_text[lng][1].format(tz)
        emb.description = "\n".join(dsc)
        await interaction.message.edit(embed=emb)

        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][24].format(tz)), ephemeral=True)
        self.tz = None

    def parse_emoji(self, ans: str) -> str:
        if ans.isdigit():
            emj = self.bot.get_emoji(int(ans))
            if emj:
                return emj.__str__()
        t1 = ans.rfind(":")
        if t1 != -1 and ans[t1+1:ans.find(">")].isdigit():
            return ans
        return f":{ans}:"
        
    async def change_currency(self, interaction: Interaction, lng: int) -> None:
        await interaction.response.send_message(embed=Embed(description=gen_settings_text[lng][29]), ephemeral=True)
        try:
            user_ans: Message = await self.bot.wait_for(event="message", check=lambda m: m.channel.id == interaction.channel_id and m.author.id == self.auth_id, timeout=25)
        except TimeoutError:
            return
        else:
            emoji_str: str = self.parse_emoji(user_ans.content)
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

    async def change_ec_system(self, interaction: Interaction, lng: int) -> None:
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

    async def change_rnk_system(self, interaction: Interaction, lng: int) -> None:
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

    async def click(self, interaction: Interaction, c_id: str) -> None:
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

    async def click_menu(self, __, c_id: str, values) -> None:
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


class mod_roles_view(View):
    def __init__(self, t_out: int, m_rls: set, lng: int, auth_id: int, rem_dis: bool, rls: list) -> None:
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.m_rls = m_rls
        self.role = None
        for i in range((len(rls)+24)//25):
            self.add_item(c_select(custom_id=f"{200+i}_{auth_id}_{randint(1, 100)}", placeholder=settings_text[lng][2], opts=rls[i*25:min(len(rls), (i+1)*25)]))
        self.add_item(c_button(style=ButtonStyle.green, label=settings_text[lng][4], emoji="<:add01:999663315804500078>", custom_id=f"8_{auth_id}_{randint(1, 100)}"))
        self.add_item(c_button(style=ButtonStyle.red, label=settings_text[lng][5], emoji="<:remove01:999663428689997844>", custom_id=f"9_{auth_id}_{randint(1, 100)}", disabled=rem_dis))
    

    async def add_role(self, interaction: Interaction, lng: int) -> None:
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
    

    async def rem_role(self, interaction: Interaction, lng: int) -> None:
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


class economy_view(View):
    def __init__(self, t_out: int, auth_id: int):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.channel = None
        self.add_item(c_button(style=ButtonStyle.blurple, label="", custom_id=f"10_{auth_id}_{randint(1, 100)}", emoji="💸"))
        self.add_item(c_button(style=ButtonStyle.blurple, label="", custom_id=f"11_{auth_id}_{randint(1, 100)}", emoji="⏰"))
        self.add_item(c_button(style=ButtonStyle.blurple, label="", custom_id=f"12_{auth_id}_{randint(1, 100)}", emoji="💹"))
        self.add_item(c_button(style=ButtonStyle.green, label="", custom_id=f"13_{auth_id}_{randint(1, 100)}", emoji="📙"))
        self.add_item(c_button(style=ButtonStyle.red, label="", custom_id=f"14_{auth_id}_{randint(1, 100)}", emoji="🛠️"))        

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

    async def log_chnl(self, interaction: Interaction, lng: int) -> None:
        channels = [(c.name, c.id) for c in interaction.guild.text_channels]
        for i in range(min((len(channels) + 23) // 24, 7)):
            opts = [(settings_text[lng][12], 0)] + channels[i*24:min((i+1)*24, len(channels))]
            self.add_item(c_select(custom_id=f"{500+i}_{self.auth_id}_{randint(1, 100)}", placeholder=settings_text[lng][10], opts=opts))
            
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

    async def manage_economy_roles(self, interaction: Interaction, lng: int) -> None:
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
                        descr.append(f"<@&{role[0]}> - **`{role[0]}`** - **`{role[1]}`** - **`{role[2]}`** - **`{role[3]//3600}`** - **`{r_types[lng][role[4]]}`** - **`{cnt}`**")
                else:
                    descr: list[str] = [ec_text[lng][19]]

        descr.append("\n" + ec_text[lng][20])
        emb.description="\n".join(descr)
        
        rls = [(r.name, r.id) for r in interaction.guild.roles if r.is_assignable()]
        if len(rls): rd = False
        else: rd = True
        ec_rls_view = economy_roles_manage_view(t_out=155, lng=lng, auth_id=self.auth_id, rem_dis=rd, rls=rls, s_rls=s_rls)
        await interaction.response.send_message(embed=emb, view=ec_rls_view)
        await ec_rls_view.wait()
        for c in ec_rls_view.children:
            c.disabled = True
        await interaction.edit_original_message(view=ec_rls_view)

    async def click(self, interaction: Interaction, c_id: str) -> None:
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

    async def click_menu(self, _, c_id: str, values) -> None:
        if c_id.startswith("50"):
            self.channel = int(values[0])

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class economy_roles_manage_view(View):
    def __init__(self, t_out: int, lng: int, auth_id: int, rem_dis: bool, rls: list, s_rls: set):
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.s_rls = s_rls
        self.role = None
        for i in range((len(rls)+24)//25):
            self.add_item(c_select(custom_id=f"{800+i}", placeholder=settings_text[lng][2], opts=rls[i*25:min(len(rls), (i+1)*25)]))
        self.add_item(c_button(style=ButtonStyle.green, label=settings_text[lng][4], emoji="<:add01:999663315804500078>", custom_id=f"15_{auth_id}_{randint(1, 100)}"))
        self.add_item(c_button(style=ButtonStyle.blurple, label=ec_mr_text[lng][0], emoji="🔧", custom_id=f"16_{auth_id}_{randint(1, 100)}", disabled=rem_dis))
        self.add_item(c_button(style=ButtonStyle.red, label=settings_text[lng][5], emoji="<:remove01:999663428689997844>", custom_id=f"17_{auth_id}_{randint(1, 100)}", disabled=rem_dis))


    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0

        if self.role is None:
            await interaction.response.send_message(embed=Embed(description=settings_text[lng][6]), ephemeral=True)
            return

        if c_id.startswith("17_"):
            if not self.role in self.s_rls:
                await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][7]), ephemeral=True)
                return
            v_d = verify_delete(lng=lng, role=self.role, m=interaction.message, auth_id=interaction.user.id)
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
            add_mod = c_modal_add(timeout=90, lng=lng, role=self.role, m=interaction.message, auth_id=interaction.user.id)
            await interaction.response.send_modal(modal=add_mod)
            
            await add_mod.wait()
            if add_mod.added:
                self.s_rls.add(self.role)
                self.role = None

        elif c_id.startswith("16_"):
            if not self.role in self.s_rls:
                await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][8]), ephemeral=True)
                return
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    r = cur.execute("SELECT * FROM server_roles WHERE role_id = ?", (self.role,)).fetchone()
                    if r[4] == 1:
                        cnt = cur.execute("SELECT count() FROM store WHERE role_id = ?", (r[0],)).fetchone()[0]
                    else:
                        cnt = cur.execute("SELECT quantity FROM store WHERE role_id = ?", (r[0],)).fetchone()
                        if not cnt:
                            cnt = 0
                        elif r[4] == 2:
                            cnt = cnt[0]
                        else:
                            cnt = "∞"
            
            edit_mod = c_modal_edit(timeout=90, role=self.role, m=interaction.message, auth_id=interaction.user.id, lng=lng, p=r[1], s=r[2], s_c=r[3]//3600, r_t=r[4], in_store=cnt)
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


class c_modal_add(Modal):

    def __init__(self, timeout: int, lng: int, role: int, m, auth_id: int):
        super().__init__(title=settings_text[lng][3], timeout=timeout, custom_id=f"6100_{auth_id}_{randint(1, 100)}")
        self.role=role
        self.m = m
        self.added = False
        self.price = TextInput(
            label=ec_mr_text[lng][10],
            min_length=1,
            max_length=8,
            placeholder=ec_mr_text[lng][11],
            required=True,
            custom_id=f"6101_{auth_id}_{randint(1, 100)}"
        )
        self.salary = TextInput(
            label=ec_mr_text[lng][12],
            min_length=1,
            max_length=9,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][13],
            required=False,
            custom_id=f"6102_{auth_id}_{randint(1, 100)}"
        )
        self.r_type1 = TextInput(
            label=ec_mr_text[lng][14],
            min_length=1,
            max_length=1,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][15],
            required=False,
            custom_id=f"6103_{auth_id}_{randint(1, 100)}"
        )
        self.r_type2 = TextInput(
            label=ec_mr_text[lng][14],
            min_length=1,
            max_length=1,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][16],
            required=False,
            custom_id=f"6104_{auth_id}_{randint(1, 100)}"
        )
        self.r_type3 = TextInput(
            label=ec_mr_text[lng][14],
            min_length=1,
            max_length=1,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][17],
            required=False,
            custom_id=f"6105_{auth_id}_{randint(1, 100)}"
        )
        self.add_item(self.price)
        self.add_item(self.salary)
        self.add_item(self.r_type1)
        self.add_item(self.r_type2)
        self.add_item(self.r_type3)
        self.r_t = set()


    def check_ans(self) -> int:
        ans = 0

        if not self.price.value.isdigit():
            ans += 1
        elif int(self.price.value) <= 0:
            ans += 1
        
        if self.salary.value:
            s_ans = self.salary.value.split()
            if len(s_ans) != 2:
                ans += 10
            else:
                s, s_c = s_ans[0], s_ans[1]
                if not s.isdigit():
                    ans += 100
                elif int(s) <= 0:
                    ans += 100

                if not s_c.isdigit():
                    ans += 1000
                elif int(s_c) <= 0:
                    ans += 1000
        
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
            ans += 10000
        elif len(self.r_t) > 1:
            ans += 100000

        return ans


    async def callback(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        ans_c = self.check_ans()
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
        if (ans_c // 100000) % 2 == 1:
            rep.append(ec_mr_text[lng][23])

        if len(rep):
            await interaction.response.send_message(embed=Embed(description="\n".join(rep)), ephemeral=True)
            self.stop()
            return

        price = int(self.price.value)
        if self.salary.value:
            s_ans = self.salary.value.split()
            salary = int(s_ans[0])
            salary_c = int(s_ans[1]) * 3600
        else:
            salary = salary_c = 0
        r_type = int(list(self.r_t)[0])

        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("INSERT OR IGNORE INTO server_roles(role_id, price, salary, salary_cooldown, type) VALUES(?, ?, ?, ?, ?)", (self.role, price, salary, salary_c, r_type))
                base.commit()
                if salary:
                    cur.execute("INSERT OR IGNORE INTO salary_roles(role_id, members, salary, salary_cooldown, last_time) VALUES(?, ?, ?, ?, ?)", (self.role, "", salary, salary_c, 0))
                    base.commit()

        emb = self.m.embeds[0]
        dsc = emb.description.split("\n")
        rls = dsc[1:-2]
        dsc = [ec_text[lng][18]]
        for r in rls:
            dsc.append(r)
        dsc.append(f"<@&{self.role}> - **`{self.role}`** - **`{price}`** - **`{salary}`** - **`{salary_c//3600}`** - **`{r_types[lng][r_type]}`** - **`0`**")
        dsc.append("\n" + ec_text[lng][20])
        emb.description = "\n".join(dsc)
        await self.m.edit(embed=emb)

        self.added = True
        await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][24].format(self.role, price, salary, salary_c//3600, r_types[lng][r_type])), ephemeral=True)
        self.stop()


class c_modal_edit(Modal):

    def __init__(self, timeout: int, role: int, m, lng: int, auth_id: int, p: int, s: int, s_c: int, r_t: int, in_store):
        super().__init__(title=ec_mr_text[lng][25], timeout=timeout, custom_id=f"7100_{auth_id}_{randint(1, 100)}")
        self.role=role
        self.m = m
        self.added = False
        self.prev_r_t = r_t
        self.s = s
        self.s_c = s_c
        self.changed = False
        self.price = TextInput(
            label=ec_mr_text[lng][10],
            min_length=1,
            max_length=8,
            placeholder=ec_mr_text[lng][11],
            default_value=f"{p}",
            required=True,
            custom_id=f"7101_{auth_id}_{randint(1, 100)}"
        )
        if s == 0:
            def_s = None
        else:
            def_s = f"{s} {s_c}"
        self.salary = TextInput(
            label=ec_mr_text[lng][12],
            min_length=1,
            max_length=9,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][13],
            default_value=def_s,
            required=False,
            custom_id=f"7102_{auth_id}_{randint(1, 100)}"
        )
        self.r_type_inp = TextInput(
            label=ec_mr_text[lng][14],
            min_length=1,
            max_length=1,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][26],
            default_value=f"{r_t}",
            required=False,
            custom_id=f"7103_{auth_id}_{randint(1, 100)}"
        )
        self.in_st = TextInput(
            label=ec_mr_text[lng][27],
            min_length=1,
            max_length=2,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][28],
            default_value=f"{in_store}",
            required=True,
            custom_id=f"7104_{auth_id}_{randint(1, 100)}"
        )
        self.add_item(self.price)
        self.add_item(self.salary)
        self.add_item(self.r_type_inp)
        self.add_item(self.in_st)

    def check_ans(self) -> int:
        ans = 0

        if not self.price.value.isdigit():
            ans += 1
        elif int(self.price.value) <= 0:
            ans += 1
        
        if self.salary.value:
            s_ans = self.salary.value.split()
            if len(s_ans) != 2:
                ans += 10
            else:
                s, s_c = s_ans[0], s_ans[1]
                if not s.isdigit():
                    ans += 100
                elif int(s) <= 0:
                    ans += 100

                if not s_c.isdigit():
                    ans += 1000
                elif int(s_c) <= 0:
                    ans += 1000
        
        if not self.r_type_inp.value.isdigit():
            ans += 10000
        elif not 1 <= int(self.r_type_inp.value) <= 3:
            ans += 10000

        if not self.in_st.value.isdigit():
            ans += 100000
        elif int(self.in_st.value) < 0:
            ans += 100000

        return ans

    async def callback(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        ans_c = self.check_ans()
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
        if (ans_c // 100000) % 2 == 1:
            rep.append(ec_mr_text[lng][29])

        if len(rep):
            await interaction.response.send_message(embed=Embed(description="\n".join(rep)), ephemeral=True)
            self.stop()
            return

        price = int(self.price.value)
        if self.salary.value:
            s_ans = self.salary.value.split()
            salary = int(s_ans[0])
            salary_c = int(s_ans[1]) * 3600
        else:
            salary = salary_c = 0
        r_type = int(self.r_type_inp.value)
        l = int(self.in_st.value)
        r = self.role

        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_roles SET price = ?, salary = ?, salary_cooldown = ?, type = ? WHERE role_id = ?", (price, salary, salary_c, r_type, r))
                if r_type != self.prev_r_t:
                    self.update_type_and_store(base=base, cur=cur, price=price, salary=salary, salary_c=salary_c, r_type=r_type, r=r, l=l)
                else:
                    self.update_store(base=base, cur=cur, r=r, price=price, salary=salary, salary_c=salary_c, r_type=r_type, l=l, l_prev = int(self.in_st.default_value))
                if salary != self.s or salary_c != self.s_c * 3600:
                    self.update_salary(base=base, cur=cur, r=r, salary=salary, salary_c=salary_c)
        
        if r_type == 3:
            l = "∞"

        emb = self.m.embeds[0]
        dsc = emb.description.split("\n")
        for i in range(1, len(dsc)-1):
            if f"{r}" in dsc[i]:
                dsc[i] = f"<@&{r}> - **`{r}`** - **`{price}`** - **`{salary}`** - **`{salary_c//3600}`** - **`{r_types[lng][r_type]}`** - **`{l}`**"
        emb.description = "\n".join(dsc)
        await self.m.edit(embed=emb)
        self.changed = True

        await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][30].format(r, price, salary, salary_c // 3600, r_types[lng][r_type], l)), ephemeral=True)
        self.stop()
    
    def update_type_and_store(self, base: Connection, cur: Cursor, price: int, salary: int, salary_c: int, r_type: int, r:int, l: int) -> None:

        t = int(time())
        cur.execute("DELETE FROM store WHERE role_id = ?", (r,))
        base.commit()
        if l == 0:
            return

        if r_type == 3:
            cur.execute("INSERT INTO store(role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES(?, ?, ?, ?, ?, ?, ?)", (r, -404, price, t, salary, salary_c, 3))
        elif r_type == 2:
            cur.execute("INSERT INTO store(role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES(?, ?, ?, ?, ?, ?, ?)", (r, l, price, t, salary, salary_c, 2))
        elif r_type == 1:
            for _ in range(l):
                cur.execute("INSERT INTO store(role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES(?, ?, ?, ?, ?, ?, ?)", (r, 1, price, t, salary, salary_c, 1))
        base.commit()
        
    def update_store(self, base: Connection, cur: Cursor, r: int, price: int, salary: int, salary_c: int, r_type: int, l: int, l_prev: int) -> None:
        if l == 0:
            cur.execute("DELETE FROM store WHERE role_id = ?", (r,))
            base.commit()
            return
        t = int(time())
        
        if r_type == 2:
            if l_prev == 0:
                cur.execute("INSERT INTO store(role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES(?, ?, ?, ?, ?, ?, ?)", (r, l, price, t, salary, salary_c, 2))
            else:
                cur.execute("UPDATE store SET quantity = ?, price = ?, last_date = ?, salary = ?, salary_cooldown = ? WHERE role_id = ?", (l, price, t, salary, salary_c, r))
        
        elif r_type == 1:
            if l_prev < l:
                cur.executemany("INSERT INTO store(role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES(?, ?, ?, ?, ?, ?, ?)", [(r, 1, price, t, salary, salary_c, 1) for _ in range(l-l_prev)])
            elif l_prev > l:
                sort_rls = sorted(cur.execute("SELECT rowid, last_date FROM store WHERE role_id = ?", (r,)).fetchall(), key=lambda tup: tup[1])
                cur.execute(f"DELETE FROM store WHERE rowid IN {tuple({x[0] for x in sort_rls[:l_prev-l]})}")
            else:
                cur.execute("UPDATE store SET price = ?, last_date = ?, salary = ?, salary_cooldown = ? WHERE role_id = ?", (price, t, salary, salary_c, r))

        elif r_type == 3 and l_prev == 0:
            cur.execute("INSERT INTO store(role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES(?, ?, ?, ?, ?, ?, ?)", (r, -404, price, t, salary, salary_c, 3))

        base.commit()   

    def update_salary(self, base: Connection, cur: Cursor, r: int, salary: int, salary_c: int) -> None:
        if salary == 0:
            cur.execute("DELETE FROM salary_roles WHERE role_id = ?", (r,))
            base.commit()
            return
        if cur.execute("SELECT role_id FROM salary_roles WHERE role_id = ?", (r,)).fetchone() == None:
            ids = set()
            s_r = f"{r}"
            for req in cur.execute("SELECT * FROM users").fetchall():
                if s_r in req[2]:
                    ids.add(f"{r[0]}")
            if len(ids):
                membs = "#".join(ids)
            else:
                membs = ""
            cur.execute("INSERT INTO salary_roles(role_id, members, salary, salary_cooldown, last_time) VALUES(?, ?, ?, ?, ?)", (r, membs, salary, salary_c, 0))
            base.commit()
            return
        cur.execute("UPDATE salary_roles SET salary = ?, salary_cooldown = ? WHERE role_id = ?", (salary, salary_c, r))
        base.commit()


class verify_delete(View):

    def __init__(self, lng: int, role: int, m, auth_id: int):
        super().__init__(timeout=30)
        self.role = role
        self.auth_id = auth_id
        self.m = m
        self.deleted = False
        self.add_item(c_button(style=ButtonStyle.red, label=ec_mr_text[lng][1], custom_id=f"1000_{auth_id}_{randint(1, 100)}"))
        self.add_item(c_button(style=ButtonStyle.green, label=ec_mr_text[lng][2], custom_id=f"1001_{auth_id}_{randint(1, 100)}"))
    
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


class c_modal_mng_memb(Modal):

    def __init__(self, timeout: int, title: str, lng: int, memb_id: int, cur_money: int, cur_xp: int, auth_id: int):
        super().__init__(title=title, timeout=timeout, custom_id=f"8100_{auth_id}_{randint(1, 100)}")
        self.is_changed = False
        self.memb_id = memb_id
        self.st_cash = cur_money,
        self.st_xp = cur_xp
        self.cash = TextInput(
            label=mng_membs_text[lng][11],
            placeholder=mng_membs_text[lng][12],
            default_value=f"{cur_money}",
            min_length=1,
            max_length=9,
            required=True,
            custom_id=f"8101_{auth_id}_{randint(1, 100)}"
        )
        self.xp = TextInput(
            label=mng_membs_text[lng][13],
            placeholder=mng_membs_text[lng][12],
            default_value=f"{cur_xp}",
            min_length=1,
            max_length=9,
            required=True,
            custom_id=f"8102_{auth_id}_{randint(1, 100)}"
        )
        self.add_item(self.cash)
        self.add_item(self.xp)
    
    def check_ans(self) -> int:
        if not(self.cash.value and self.cash.value.isdigit() and int(self.cash.value) >= 0):
            ans = 1
        else:
            ans = 0        
        if not(self.xp.value and self.xp.value.isdigit() and int(self.xp.value) >= 0):
            ans += 10
        return ans

    async def callback(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        ans = self.check_ans()
        msg = []
        if ans % 2 == 1:
            msg.append(mng_membs_text[lng][14])
        if ans // 10 == 1:
            msg.append(mng_membs_text[lng][15])
        if len(msg):
            await interaction.response.send_message(embed=Embed(description="\n".join(msg)), ephemeral=True)
            self.stop()
            return

        cash = int(self.cash.value)
        xp = int(self.xp.value)
        
        self.new_cash = cash
        self.new_xp = xp
        self.is_changed = True

        if cash != self.st_cash and xp != self.st_xp:
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:  
                    cur.execute("UPDATE users SET money = ?, xp = ? WHERE memb_id = ?", (cash, xp, self.memb_id))
                    base.commit()
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][16].format(self.memb_id, cash, xp)), ephemeral=True)

        elif cash != self.st_cash:
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:  
                    cur.execute("UPDATE users SET money = ? WHERE memb_id = ?", (cash, self.memb_id))
                    base.commit()
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][17].format(self.memb_id, cash)), ephemeral=True)

        elif xp != self.st_xp:
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:  
                    cur.execute("UPDATE users SET xp = ? WHERE memb_id = ?", (xp, self.memb_id))
                    base.commit()
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][18].format(self.memb_id, xp)), ephemeral=True)
        self.stop()


class mng_membs_view(View):

    def __init__(self, timeout: int, lng: int, auth_id: int, memb_id: int, memb_rls: set, rls: list, cur_money: int, cur_xp: int, rem_dis: bool, g_id: int, member):
        super().__init__(timeout=timeout)
        self.add_item(c_button(style=ButtonStyle.blurple, label=mng_membs_text[lng][0], emoji="🔧", custom_id=f"18_{auth_id}_{randint(1, 100)}"))
        for i in range((len(rls)+24)//25):
            self.add_item(c_select(custom_id=f"{300+i}_{auth_id}_{randint(1, 100)}", placeholder=settings_text[lng][2], opts=rls[i*25:min(len(rls), (i+1)*25)]))
        self.add_item(c_button(style=ButtonStyle.green, label=settings_text[lng][4], emoji="<:add01:999663315804500078>", custom_id=f"19_{auth_id}_{randint(1, 100)}"))
        self.add_item(c_button(style=ButtonStyle.red, label=settings_text[lng][5], emoji="<:remove01:999663428689997844>", custom_id=f"20_{auth_id}_{randint(1, 100)}", disabled=rem_dis))
        self.role = None
        self.memb_id = memb_id
        self.memb_rls = memb_rls
        self.cash = cur_money
        self.xp = cur_xp
        self.g_id = g_id
        self.auth_id = auth_id
        self.member=member

    async def add_r(self, lng: int, interaction: Interaction) -> None:
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
            self.role = None
        else:
            dsc.append(f"<@&{self.role}>**` - {self.role}`**")
            emb3.description = "\n".join(dsc)
            embs[2] = emb3
            await interaction.message.edit(embeds=embs)
            await interaction.response.send_message(embed=Embed(description=mng_membs_text[lng][8].format(self.role, self.memb_id)), ephemeral=True)       
        

    async def rem_r(self, lng: int, interaction: Interaction) -> None:
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
            self.role = None
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
            

    async def click(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0

        if c_id.startswith("18_"):
            edit_modl = c_modal_mng_memb(timeout=90, title=mng_membs_text[lng][19], lng=lng, memb_id=self.memb_id, cur_money=self.cash, cur_xp=self.xp, auth_id=self.auth_id)

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
        

class c_modal_xp(Modal):

    def __init__(self, timeout: int, lng: int, auth_id: int, g_id: int, cur_xp: int, cur_xpb: int):
        super().__init__(title=ranking_text[lng][7], timeout=timeout, custom_id=f"9100_{auth_id}_{randint(1, 100)}")

        self.xp = TextInput(
            label=ranking_text[lng][8],
            placeholder=ranking_text[lng][9],
            default_value=f"{cur_xp}",
            min_length=1,
            max_length=2,
            required=True,
            custom_id=f"9101_{auth_id}_{randint(1, 100)}"
        )
        self.xp_b = TextInput(
            label=ranking_text[lng][10],
            placeholder=ranking_text[lng][11],
            default_value=f"{cur_xpb}",
            min_length=1,
            max_length=5,
            required=True,
            custom_id=f"9102_{auth_id}_{randint(1, 100)}"
        )
        self.add_item(self.xp)
        self.add_item(self.xp_b)

        self.g_id = g_id
        self.old_xp = cur_xp
        self.old_xpb = cur_xpb
        self.changed: bool = False

    def check_ans(self):
        ans = 1 if not(self.xp.value and self.xp.value.isdigit() and int(self.xp.value) >= 0) else 0
            
        if not(self.xp_b.value and self.xp_b.value.isdigit() and int(self.xp_b.value) >= 1):
            ans += 10
        return ans

    async def callback(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        ans = self.check_ans()
        rep = []
        if ans % 2 == 1:
            rep.append(ranking_text[lng][12])
        if ans // 10 == 1:
            rep.append(ranking_text[lng][13])
        if len(rep):
            await interaction.response.send_message(embed=Embed(description="\n".join(rep)), ephemeral=True)
            self.stop()
            return

        xp = int(self.xp.value)
        xpb = int(self.xp_b.value)

        if self.old_xp != xp or self.old_xpb != xpb:
            rep = []
            with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    if self.old_xp != xp:
                        cur.execute("UPDATE server_info SET value = ? WHERE settings = 'xp_per_msg'", (xp,))
                        rep.append(ranking_text[lng][14].format(xp))
                        self.old_xp = xp
                    if self.old_xpb != xpb:
                        cur.execute("UPDATE server_info SET value = ? WHERE settings = 'xp_border'", (xpb,))
                        rep.append(ranking_text[lng][15].format(xpb))
                        self.old_xpb = xpb
                    base.commit()
            await interaction.response.send_message(embed=Embed(description="\n".join(rep)), ephemeral=True)
            self.changed = True
        else:
            await interaction.response.send_message(embed=Embed(description=ranking_text[lng][16]), ephemeral=True)
        self.stop()


class ic_view(View):

    def __init__(self, timeout: int, lng: int, auth_id: int, chnls: list, rem_dis: bool, g_id: int) -> None:
        super().__init__(timeout=timeout)
        l = len(chnls)
        for i in range(min((l + 23) // 24, 20)):
            self.add_item(c_select(custom_id=f"{1100+i}_{auth_id}_{randint(1, 100)}", placeholder=settings_text[lng][10], opts=[(settings_text[lng][12], 0)] + chnls[i*24:min((i+1)*24, l)]))
        self.add_item(c_button(style=ButtonStyle.green, label=settings_text[lng][8], emoji="<:add01:999663315804500078>", custom_id=f"25_{auth_id}_{randint(1, 100)}"))
        self.add_item(c_button(style=ButtonStyle.red, label=settings_text[lng][9], emoji="<:remove01:999663428689997844>", custom_id=f"26_{auth_id}_{randint(1, 100)}", disabled=rem_dis))
        self.chnl = None
        self.g_id = g_id
        self.auth_id = auth_id


    async def add_chnl(self, interaction: Interaction, lng: int) -> None:
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
    

    async def rem_chnl(self, interaction: Interaction, lng: int) -> None:
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


    async def click(self, interaction: Interaction, c_id: str) -> None:
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


class select_level_modal(Modal):

    def __init__(self, lng: int, auth_id: int, timeout: int) -> None:
        super().__init__(title=ranking_text[lng][24], timeout=timeout, custom_id=f"11100_{auth_id}_{randint(1, 100)}")
        self.lng = lng
        self.level = None
        self.level_selection = TextInput(
            label=ranking_text[lng][24],
            style=TextInputStyle.short,
            custom_id=f"11101_{auth_id}_{randint(1, 100)}",
            min_length=1,
            max_length=3,
            required=True,
            placeholder=ranking_text[lng][28]
        )
        self.add_item(self.level_selection)
    
    def check_level(self, value: str):
        if not value.isdigit() and int(value) > 0 and int(value) < 101:
            return None
        return int(value)

    async def callback(self, interaction: Interaction) -> None:
        ans = self.check_level(self.level_selection.value)
        if not ans:
            await interaction.response.send_message(embed=Embed(description=ranking_text[self.lng][28]))
            return
        self.level = ans
        self.stop()
        

class lvl_roles_view(View):

    def __init__(self, timeout: int, auth_id: int, g_id: int, disabled: bool):
        super().__init__(timeout=timeout)
        self.add_item(c_button(style=ButtonStyle.green, label="🔧", custom_id=f"27_{auth_id}_{randint(1, 100)}", emoji="<:add01:999663315804500078>"))
        self.add_item(c_button(style=ButtonStyle.red, label="", custom_id=f"28_{auth_id}_{randint(1, 100)}", emoji="<:remove01:999663428689997844>", disabled=disabled))
        self.auth_id: int = auth_id
        self.g_id: int = g_id
        self.role = None
    
    async def click(self, interaction: Interaction, c_id: str) -> None:
        if not (c_id.startswith("27_") or c_id.startswith("28_")):
            return
        lng = 1 if "ru" in interaction.locale else 0
        lvl_modal = select_level_modal(lng=lng, auth_id=interaction.user.id, timeout=60)
        await interaction.response.send_modal(modal=lvl_modal)
        await lvl_modal.wait()
        if lvl_modal.level:
            ans = lvl_modal.level
        else:
            return
        
        if c_id.startswith("27_"):
            
            rls = [(r.name, r.id) for r in interaction.guild.roles if r.is_assignable()]
            if not len(rls):
                await interaction.send(embed=Embed(description = ranking_text[lng][30]), delete_after=6)
                return
            for i in range((len(rls) + 24) // 25):
                self.add_item(c_select(
                    custom_id=f"{1300+i}_{self.auth_id}_{randint(1, 100)}", 
                    placeholder=settings_text[lng][2], 
                    opts=rls[i*25:min(len(rls), (i+1) * 25)]
                ))
            await interaction.message.edit(view=self)
            msg = await interaction.send(embed=Embed(description = ranking_text[lng][29].format(ans)))

            cnt = 0
            while self.role is None and cnt < 25:
                cnt += 1
                await sleep(1)
            if self.role is None:
                await msg.edit(embed=Embed(description=ranking_text[lng][32]), delete_after=6)
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
            await msg.edit(embed=Embed(description=ranking_text[lng][31].format(ans, self.role)), delete_after=6)
            self.role = None    

        else:
            with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    if cur.execute("SELECT count() FROM rank_roles WHERE level = ?", (ans,)).fetchone()[0]:
                        cur.execute("DELETE FROM rank_roles WHERE level = ?", (ans,))
                        base.commit()
                        lvl_rls = sorted(cur.execute("SELECT * FROM rank_roles").fetchall(), key=lambda tup: tup[0])
                    else:
                        await interaction.send(embed=Embed(description=ranking_text[lng][34].format(ans)), delete_after=6)
                        return

            if len(lvl_rls):
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

            await interaction.send(embed=Embed(description=ranking_text[lng][33].format(ans)), delete_after=6)


    async def click_menu(self, _, c_id: str, values):
        if c_id.startswith("13"):
            self.role = int(values[0])

    async def interaction_check(self, interaction: Interaction) -> bool:
        if self.auth_id != interaction.user.id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class ranking_view(View):

    def __init__(self, timeout: int, auth_id: int, g_id: int, cur_xp_pm: int, cur_xpb: int) -> None:
        super().__init__(timeout=timeout)
        self.add_item(c_button(style=ButtonStyle.green, label="", emoji="✨", custom_id=f"21_{auth_id}_{randint(1, 100)}"))
        self.add_item(c_button(style=ButtonStyle.grey, label="", emoji="📗", custom_id=f"22_{auth_id}_{randint(1, 100)}"))
        self.add_item(c_button(style=ButtonStyle.grey, label="", emoji="<:ignored_channels:1003673081996378133>", custom_id=f"23_{auth_id}_{randint(1, 100)}"))
        self.add_item(c_button(style=ButtonStyle.red, label="", emoji="🥇", custom_id=f"24_{auth_id}_{randint(1, 100)}"))
        self.auth_id = auth_id
        self.cur_xp_pm = cur_xp_pm
        self.cur_xpb = cur_xpb
        self.g_id = g_id
        self.lvl_chnl = None
    
    async def xp_change(self, lng: int, interaction: Interaction) -> None:
        xp_m = c_modal_xp(timeout=80, lng=lng, auth_id=self.auth_id, g_id=self.g_id, cur_xp=self.cur_xp_pm, cur_xpb=self.cur_xpb)
        await interaction.response.send_modal(modal=xp_m)
        await xp_m.wait()

        if xp_m.changed:
            self.cur_xp_pm = xp_m.old_xp
            self.cur_xpb = xp_m.old_xpb

            emb = interaction.message.embeds[0]
            dsc = emb.description.split("\n\n")
            dsc[1] = f"**`{self.cur_xp_pm}`**"
            dsc[3] = f"**`{self.cur_xpb}`**"
            emb.description = "\n\n".join(dsc)
            await interaction.message.edit(embed=emb)

    async def ic(self, lng: int, interaction: Interaction) -> None:
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
        ic_v = ic_view(timeout=80, lng=lng, auth_id=self.auth_id, chnls=chnls, rem_dis=rd, g_id=self.g_id)

        await interaction.response.send_message(embed=emb, view=ic_v)
        await ic_v.wait()
        await interaction.delete_original_message()

    async def level_channel(self, lng: int, interaction: Interaction) -> None:
        
        me = interaction.guild.me
        chnls = [(c.name, c.id) for c in interaction.guild.text_channels if c.permissions_for(me).send_messages]
        l = len(chnls)
        
        for i in range(min((l + 23) // 24, 20)):
            self.add_item(c_select(custom_id=f"{1200+i}_{self.auth_id}_{randint(1, 100)}", placeholder=settings_text[lng][10], opts=[(settings_text[lng][12], 0)] + chnls[i*24:min((i+1)*24, l)]))
            
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
        lr_v = lvl_roles_view(timeout=80, auth_id=interaction.user.id, g_id=self.g_id, disabled=rem_b)
        await interaction.response.send_message(embed=emb, view=lr_v)
        await lr_v.wait()
        await interaction.delete_original_message()

    async def click(self, interaction: Interaction, c_id: str) -> None:
        lng = 1 if "ru" in interaction.locale else 0
        if c_id.startswith("21_"):
            await self.xp_change(lng=lng, interaction=interaction)
        elif c_id.startswith("22_"):
            await self.level_channel(lng=lng, interaction=interaction)
        elif c_id.startswith("23_"):
            await self.ic(lng=lng, interaction=interaction)
        elif c_id.startswith("24_"):
            await self.lvl_roles(lng=lng, interaction=interaction)
    
    async def click_menu(self, _, c_id: str, values) -> None:
        if c_id.startswith("12"):
            self.lvl_chnl = int(values[0])

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class poll_v_c_view(View):
    def __init__(self, timeout: int, lng: int, view_id_base: int,  auth_id: int, chnls: list):
        super().__init__(timeout=timeout)
        for i in range(min((len(chnls) + 23) // 24, 20)):
            self.add_item(c_select(
                custom_id=f"{view_id_base+i}_{auth_id}_{randint(1, 100)}", 
                placeholder=settings_text[lng][10], 
                opts=[(settings_text[lng][12], 0)] + chnls[i*24:min(len(chnls), (i+1)*24)]
            ))
        self.auth_id = auth_id
        self.c = None
        
    async def click_menu(self, _, c_id: str, values) -> None:
        if c_id.startswith("14") or c_id.startswith("15"):
            self.c = int(values[0])
            self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class poll_settings_view(View):
    
    def __init__(self, timeout: int, auth_id: int):
        super().__init__(timeout=timeout)
        self.add_item(c_button(style=ButtonStyle.green, label="", custom_id=f"28_{auth_id}_{randint(1, 100)}", emoji="🔎"))
        self.add_item(c_button(style=ButtonStyle.green, label="", custom_id=f"29_{auth_id}_{randint(1, 100)}", emoji="📰"))
        self.auth_id = auth_id
    
    async def click(self, interaction: Interaction, c_id: str) -> None:
        lng = 1 if "ru" in interaction.locale else 0
        me = interaction.guild.me
        chnls = [(c.name, c.id) for c in interaction.guild.text_channels if c.permissions_for(me).send_messages]

        if c_id.startswith("28_"):

            v_c = poll_v_c_view(timeout=25, lng=lng, view_id_base = 1400, auth_id=self.auth_id, chnls=chnls)
            await interaction.response.send_message(embed=Embed(description=settings_text[lng][11]), view=v_c)
            
            await v_c.wait()
            if v_c.c is None:
                await interaction.delete_original_message()
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

                await interaction.edit_original_message(embed=Embed(description=poll_text[lng][4].format(v_c.c)), view=None)     
                           
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

                await interaction.edit_original_message(embed=Embed(description=poll_text[lng][5]), view=None)

            await interaction.delete_original_message(delay=5)


        elif c_id.startswith("29_"):

            v_c = poll_v_c_view(timeout=25, lng=lng, view_id_base = 1500, auth_id=self.auth_id, chnls=chnls)
            await interaction.response.send_message(embed=Embed(description=settings_text[lng][11]), view=v_c)
            
            await v_c.wait()
            if v_c.c is None:
                await interaction.delete_original_message()
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

                await interaction.edit_original_message(embed=Embed(description=poll_text[lng][6].format(v_c.c)), view=None)     
                           
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

                await interaction.edit_original_message(embed=Embed(description=poll_text[lng][7]), view=None)

            await interaction.delete_original_message(delay=5)
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=mod_roles_text[lng][11]), ephemeral=True)
            return False
        return True


class settings_view(View):
    def __init__(self, t_out: int, auth_id: int, bot: Bot) -> None:
        super().__init__(timeout=t_out)
        self.auth_id = auth_id
        self.bot = bot
        self.add_item(c_button(style=ButtonStyle.red, label=None, custom_id=f"0_{auth_id}_{randint(1, 100)}", emoji="⚙️"))
        self.add_item(c_button(style=ButtonStyle.red, label=None, custom_id=f"1_{auth_id}_{randint(1, 100)}", emoji="<:moder:1000090629897998336>"))
        self.add_item(c_button(style=ButtonStyle.red, label=None, custom_id=f"2_{auth_id}_{randint(1, 100)}", emoji="<:user:1002245779089535006>"))
        self.add_item(c_button(style=ButtonStyle.green, label=None, custom_id=f"3_{auth_id}_{randint(1, 100)}", emoji="💰", row=2))
        self.add_item(c_button(style=ButtonStyle.blurple, label=None, custom_id=f"4_{auth_id}_{randint(1, 100)}", emoji="📈", row=2))
        self.add_item(c_button(style=ButtonStyle.blurple, label=None, custom_id=f"5_{auth_id}_{randint(1, 100)}", emoji="📊", row=2))
    
    
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
            gen_view = gen_settings_view(t_out=50, auth_id=self.auth_id, bot=self.bot, lng=lng, ec_status=ec_status, rnk_status=rnk_status)
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
            
            m_rls_v = mod_roles_view(t_out=50, m_rls=m_rls, lng=lng, auth_id=self.auth_id, rem_dis=rem_dis, rls=rls)
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

            mng_v = mng_membs_view(
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
            
            ec_v = economy_view(t_out=110, auth_id=self.auth_id)
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
            rnk_v = ranking_view(timeout=90, auth_id=interaction.user.id, g_id=interaction.guild_id, cur_xp_pm=xp_p_m, cur_xpb=xp_b)
            
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

            p_v = poll_settings_view(timeout=100, auth_id=self.auth_id)
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


class m_cmds(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def mod_check(interaction: Interaction) -> bool:
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
        st_view = settings_view(t_out=120, auth_id=interaction.user.id, bot=self.bot)
        emb = Embed(title=settings_text[lng][0], description="\n".join(settings_text[lng][1]))
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
    bot.add_cog(m_cmds(bot))



import os
from sqlite3 import connect, Connection, Cursor
from asyncio import sleep, TimeoutError
from contextlib import closing
from datetime import datetime, timedelta
from time import time

from nextcord.ext import commands, tasks
from nextcord.ext.commands import CheckFailure
from nextcord import Embed, Colour, Guild, Role, Member, TextChannel, Locale, Interaction, slash_command, SlashOption, ButtonStyle
from nextcord.ui import View, Button, button

from config import *

guide = {
    0 : {
        0 : "The guide",
        1 : "Economic operations with the roles",
        2 : "In order to make role able to be bought and sold on the server and it could bring money you should add it to the list of roles, available for the purchase/sale via \
            commands **`{}manage_role`** or **`{}list`** (see **`/help`** -> \"⚙️\" -> **`manage_role`**, **`/help`** -> \"⚙️\" -> **`list`**). First command allows you to \
            manage role and second one allows to see list of roles, available for the purchase/sale ans add/remove roles to/from this list",
        3 : "Bot devides roles on three types:",
        4 : "0, 1 and 2",
        5 : "Type 0",
        6 : "\"Nonstacking\" roles, that are not stacking in the store (are shown as different items in the store)",
        7 : "Type 1",
        8 : "\"Stacking\" roles that are stacking in the store (are shown as one item with quantity)",
        9 : "Type 2",
        10 : "\"Infinite\" roles that can't run out in the store (you can buy them endless times)",
        11 : "Salary of the roles",
        12 : "Each role can have passive salary: once per every cooldown time (see **`/help`** -> \"⚙️\" -> **`salary_timer`**) members that have this role on their balance will \
            gain money (salary) that is selected by **`{}manage_role`** (see **`/help`** -> \"⚙️\" -> **`manage_role`**)",
        13 : "Work",
        14 : "Members can gain money by using **`/work`** command. Amount of gained money is set by **`{}work_salary`** (see **`/help`** -> \"⚙️\" -> **`work_salary`**). Cooldown \
            for the command is set by **`{}work_cooldown`** (see **`/help`** -> \"⚙️\" -> **`work_cooldown`**)",
        15 : "Rank system",
        16 : "For each message members gains xp set by **`{}xp_per_msg`** (see **`/help`** -> \"⚙️\" -> **`xp_per_msg`**) After achieving border of the level set by **`{}border`** \
            (see **`/help`** -> \"⚙️\" -> **`border`**) their level growths. For each new level bot can add (and for old - remove) role set by **`{}role_per_lvl`** \
            (see **`/help`** -> \"⚙️\" -> **`role_per_lvl`**)",
        17 : "Money for messages",
        18 : "Besides the xp members can gain money for every message. Amount of money gained from message is set by **`{}money_per_msg`** (see **`/help`** -> \"⚙️\" -> \
            **`money_per_msg`**). If you want to turn off this function you can make this value equal to 0",
        19 : "For the first setup of the bot we are strognly recommending to use {}setup"
    },
    1 : {
        0 : "Гайд",
        1 : "Экономические операции с ролями",
        2 : "Чтобы роль можно было покупать и продавать на сервере, а также она могла приносить заработок, нужно добавить её в список ролей, \
            доступных для покупки/продажи на сервере при помощи команд **`{}manage_role`** или **`{}list`** (см. **`/help`** -> \"⚙️\" -> **`manage_role`**, **`/help`** -> \"⚙️\" -> **`list`**) \
            С помощью первой команды можно управлять ролью, а с помощью второй - просматривать список доступных для покупки/продажи ролей и добавлять/убирать их",
        3 : "Бот делит роли на 3 типа:",
        4 : "0, 1 и 2",
        5 : "Тип 0",
        6 : "\"Нестакающиеся\" роли, которые не стакаются в магазине (т.е. отображаются как отдельные товары)",
        7 : "Тип 1",
        8 : "\"Стакающиеся\" роли, которые стакаются в магазине (т.е. отображаются как один товар с указанным количеством)",
        9 : "Тип 2",
        10 : "\"Бесконечные\" роли, которые не заканчиваются в магазине (т.е. их можно купить бесконечное количество раз)",
        11 : "Заработок роли",
        12 : "Каждая роль может иметь пассивный заработок: раз в некоторое установленно время (см. **`/help`** -> \"⚙️\" -> **`salary_timer`**) участники, на балансе \
            которых находится эта роль, получают заработок, установленный для каждой роли командой **`{}manage_role`** (см. **`/help`** -> \"⚙️\" -> **`manage_role`**)",
        13 : "Работа",
        14 : "Пользователи могут получать деньги за использование команды **`/work`**. Заработок определяется командой **`{}work_salary`** (см. **`/help`** -> \"⚙️\" -> **`work_salary`**). \
            Кулдаун команды определяется командой **`{}work_cooldown`** (см. **`/help`** -> \"⚙️\" -> **`work_cooldown`**)",
        15 : "Система рангов",
        16 : "За каждое сообщение на сервере пользователь получает xp, установленное командов **`{}xp_per_msg`** (см. **`/help`** -> \"⚙️\" -> **`xp_per_msg`**) По достижении границы уровня, \
            установленной командой **`{}border`** (см. **`/help`** -> \"⚙️\" -> **`border`**), уровень пользователя повышается. За каждый новый уровень бот может выдавать (а за пройденный - снимать) \
            роль, установленную командой **`{}role_per_lvl`** (см. **`/help`** -> \"⚙️\" -> **`role_per_lvl`**) для каждого уровня.",
        17 : "Деньги за сообщения",
        18 : "За каждое сообщение пользователь получает не только опыт, но и деньги. Количество денег, получаемое за сообщение, определяется командой **`{}money_per_msg`** \
            (см. **`/help`** -> \"⚙️\" -> **`money_per_msg`**). Если Вы хотите отключить эту функцию, Вы можете установить это значение равным нулю",
        19 : "Для начальной настройки бота мы настоятельно рекомендуем вызвать команду {}setup"
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
    "EDT" : -4,
    "CDT" : -5,
    "MDT" : -6,
    "MST" : -7,
    "PDT" : -7,
    "AKDT" : -8,
    "HDT" : -9,
    "HST" : -10
}
zone_text = {
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
    "EDT" :	"Eastern Daylight, Time UT-4",
    "CDT" : "Central Daylight, Time UTC-5",
    "MDT" : "Mountain Daylight, Time UTC-6",
    "MST" :	"Mountain Standard, Time UTC-7",
    "PDT" :	"Pacific Daylight, Time UTC-7",
    "AKDT" : "Alaska Daylight, Time UTC-8",
    "HDT" : "Hawaii-Aleutian, Daylight UTC-9",           
    "HST" :	"Hawaii Standard, Time UTC-10"
}
set_text = {
    0 : {
        0 : "**`Server settings`**",
        1 : "Server language:",
        2 : "Server log channel id:",
        3 : "Server economic mod role id:",
        4 : "Server time zone:",
        5 : "Server cooldown for `/work`:",
        6 : "Salary from `/work`:",
        7 : "Server cooldown for unique roles salary:",
        8 : "```fix\nChannel not selected```",
        9 : "```fix\nRole not selected```"
    },
    1 : {
        0 : "**`Настройки сервера`**",
        1 : "Язык сервера:",
        2 : "Id канала для логов:",
        3 : "Id роли модератора экономики:",
        4 : "Часовой пояс сервера:",
        5 : "Кулдаун команды `/work`:",
        6 : "Заработок от команды `/work`:",
        7 : "Кулдаун заработка уникальных ролей:",
        8 : "```fix\nКанал не выбран```",
        9 : "```fix\nРоль не выбрана```"
    }
}
questions = {
    0 : {
        1 : "1. Select server's language: **`eng`** for English or **`rus`** for Russian",
        2 : "2. Select log channel: **`id`** of text channel or **`0`** if not change current setting",
        3 : "3. Select economic mode role: **`id`** of role or **`0`** if not change current setting",
        4 : "4. Select server's time zone: integer number from **`-12`** to **`12`** (format UTC±X, X Є {-12; -11; ...; 11; 12})",
        5 : "5. Select cooldown for `/work` command (in seconds, must be integer positive number). Members will able to \
        use `/work` once per this time. **`0`** if not change current setting",
        6 : "6. Select salary for `/work` command: two integer positive numbers, second one must be at least as \
        large as the first.\n Salary will be random integer number є [first; second]. **`0`** **`0`** if not change current setting",
        7 : "7. Select cooldown for gaining money from unique roles (in seconds, must be positive integer number). Members with unique roles will gain money once per this time. \
        **`0`** if not change current setting",
        8 : "8. You finished setup. To check chosen settings use **`{}settings`**",
        9 : "Print cancel to stop setup"
    },
    1 : {
        1 : "1. Укажите язык сервера: **`eng`** для английского или **`rus`** для русского",
        2 : "2. Укажите канал для логов: **`id`** текстового канала или **`0`**, если оставить без изменений",
        3 : "3. Укажите роль модератора экономики: **`id`** роли или **`0`**, если оставить без изменений",
        4 : "4. Укажите часовой пояс сервера: целое число от **`-12`** до **`12`** (формат UTC±X, X Є {-12; -11; ...; 11; 12})",
        5 : "5. Укажите кулдаун (время в секундах, должно быть целым положительным числом) для команды `/work`. Пользователи смогут \
        использовать команду `/work` один раз в это время. **`0`**, если оставить без изменений",
        6 : "6. Укажите заработок от команды `/work`: два целых положительных числа, где второе не менее первого. \nЗаработок \
        будет рандомным целым числом из отрезка [первое; второе]. **`0`** **`0`**, если оставить без изменений",
        7 : "7. Укажите кулдаун (время в секундах, должно быть целым положительным числом) для заработка от уникальных ролей. Пользователи с \
        уникальными ролями будут получать деньги от них один раз в это время. **`0`**, если оставить без изменений",
        8 : "8. Вы завершили настройку сервера. Чтобы посмотреть выбранные настройки, используйте **`{}settings`**",
        9 : "Напишите cancel для остановки настроек"
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
        7 : "General",
        8 : "Economy",
        9 : "Rank system"
    },
    1 : {
        0 : "Команды пользователей",
        1 : "Команды модераторов",
        2 : "**`Извините, но Вы не можете управлять меню, которое вызвано другим пользователем`**",
        3 : "**`Извините, но у Вас нет прав для просмотра команд для модераторов`**",
        4 : "Экономика",
        5 : "Персональные",
        6 : "Остальные",
        7 : "Основные",
        8 : "Экономика",
        9 : "Система рангов"
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

m_general_cmds = {
    0 : [
        ("`{}guide`", "Show guide about bot's settings"),
        ("`{}setup`", "Start setup of all bot's settings"),
        ("`{}settings`", "Show menu with current bot's settings"),
        ("`{}language` `language`", "Select language"),
        ("`{}zones`", "Show available pre-named time zones"),
        ("`{}time_zone` `time_zone`", "Select timezone for the server"), 
        ("`{}mod_role`", "Show menu to manage mod roles"), 
        ("`{}money_per_msg` `amount`", "Set amount of money gained by member from message"),
        ("`{}reset`", "Reset bot's settings")
    ],
    1 : [
        ("`{}guide`", "Показать гайд о настройках бота"),
        ("`{}setup`", "Начать настройки параметров бота"),
        ("`{}settings`", "Показать текущие настройки бота"),
        ("`{}language` `язык`", "Выбрать язык"),
        ("`{}zones`", "Показать именные часовые поясв"),
        ("`{}time_zone` `часовой пояс`", "Установить часовой пояс сервера"), 
        ("`{}mod_role`", "Вызывет меню управления ролями модераторов"), 
        ("`{}money_per_msg` `количество`", "Установить количество денег, получаемое пользователем за сообщение"),
        ("`{}reset`", "Сбросить настройки бота")
    ]
}
m_ec_cmds = {
    0 : [
        ("`{}available_roles`", "Call menu to manage roles available for purchase/sale (see guide)"), 
        ("`{}manage_role` `role`", "Call menu to manage role in the economic system"), 
        ("`{}salary_timer` `cooldown`", "Set cooldown for salary for roles with it"), 
        ("`{}work_salary` `left_border` `right_border`", "Set amount of money gained from `/work`"), 
        ("`{}work_cooldown` `cooldown`", "Set cooldown for `/work` command"), 
        ("`{}log_economy`", "Call menu to manage log channel for economy")
    ],
    1 : [
        ("`{}available_roles`", "Вызвать меню управления ролями, доступными для покупки/продажи на сервере (см. гайд)"), 
        ("`{}manage_role` `роль`", "Вызвать меню для управления ролью в экономической системе бота"), 
        ("`{}salary_timer` `кулдаун`", "Установить кулдаун для зараплат ролей, которые приносят деньги"), 
        ("`{}work_salary` `левая_граница` `правая_граница`", "Установить доход, получаемый от команды `/work`"), 
        ("`{}work_cooldown` `кулдаун`", "Установить кулдаун для команды `/work`"), 
        ("`{}log_economy`", "Вызвать меню управления каналом для логов экономики")
    ]
}
m_rnk_cmds = {
    0 : [
        ("`{}border` `amount_of_xp`", "Set xp border that members need to get for new level"), 
        ("`{}xp_per_msg` `amount_of_xp`", "Set xp gained from 1 message"), 
        ("`{}ic`", "Call menu to manage ignored channels, where members can't gain xp from message"), 
        ("`{}alert_channel`", "Call menu to manage alert channel where members are notificated about new level"), 
        ("`{}roles_per_lvl`", "Call menu to manage levels and roles gained for them"), 
        ("`{}manage_member` `member`", "Call menu to manage member")
    ],
    1 : [
        ("`{}border` `опыт`", "Установить опыт, который необходимо набрать для получения нового уровня"), 
        ("`{}xp_per_msg` `опыт`", "Установить опыт, получаемый за 1 сообщение"), 
        ("`{}ic`", "Вызвать меню управления игнорируемыми каналами, в которых пользователи не получают опыт за сообщения"), 
        ("`{}alert_channel`", "Вызвать меню управления каналом оповещения пользователей о получении нового уровня"), 
        ("`{}roles_per_lvl`", "Вызвать меню управления уровнями и соответствующими им ролями"), 
        ("`{}manage_member` `пользователь`", "Вызывает меню управления пользователем")
    ]
}

help_menu = {
    0 : {
        "guide" : "`{}guide` show guide about bot's settings",
        
        "setup" : "`{}setup` start setup of all bot's settings",

        "settings" : "`{}settings` show menu with current bot's settings",

        "language" : "`{}language` `lang` select language for the mod commands and names and descriptions of the slash commands. Can be **`Eng`** (no matter Eng, eng, \
                    eNg etc.) for English and **`Rus`** (no matter Rus, rus, rUs etc.) for Russian.\n\n**Example:**\n**`{}language`** **`eng`** will select English language",

        "zones" : "`{}zones` show available pre-named time zones",

        "time_zone" : "`{}time_zone` `name_of_time_zone_from_{}zones or \nhour_difference_with_'-'_if_needed` selects **`UTC`**±**`X`**, **`X`** Є {}-12; -11; ...; 11; 12{}, \
                    format for the server. \n\n**Example:**\n**`{}time_zone`** **`EDT`** will set time zone of Eastern Daylight Time UTC-4, **`{}time_zone`** **`-7`** \
                    will set time zone UTC-7",

        "mod_roles" : "`{}mod_roles` show menu to manage mod roles. Members with this roles will be able to use change bot's settings",
        
        "money_per_msg" : "`{}money_per_msg` `amount` set amount of money gained by member from message\n\n**Example:**\n**`{}money_per_msg`** **`2`** set amount equal to 2 \
                    so for every message member will gain 2 units of currency",
        
        "reset" : "`{}reset` reset current bot's settings",

        "available_roles" : "`{}available_roles` сall menu to manage roles available for purchase/sale (see guide)",

        "manage_role" : "`{}manage_role` `role` сall menu to manage role in the economic system\n\n**Example:**\n**`{}manage_role`** **`972494065088200745`** \
                    will call menu to manage role with id 972494065088200745 (you can use mention with @ instead of id)",

        "salary_timer" : "`{}salary_timer` `time_in_seconds` sets cooldown for accruing money from roles with salary\n\n**Example:**\n**`{}salary_timer`** **`10800`** \
                    will set 3 hours cooldown (10800 seconds = 3 hours)",

        "work_salary" : "`{}work_salary` `left_border` `right_border` sets borders for amount of money gained from command `/work`. This amount will be random integer number \
                    Є [left; right]. Both are integer non-negative numbers, right one must be at least as large as the left\n\n**Example:**\n**`{}work_salary`** **`10`** \
                    **`100`** changes amount of cash gained from `/work`, and this amount will be random integer from 10 to 100 (amount Є [10; 100])",

        "work_cooldown" : "`{}work_cooldown` `time_in_seconds` sets cooldown for command `/work`\n\n**Example:**\n**`{}work_cooldown`** **`10800`** will set 3 hours \
                    cooldown (10800 seconds = 3 hours) for command `/work`",
        
        "log_economy" : "`{}log_economy` `text_channel` selects log channel for economic operations\n\n**Example:**\n**`{}log_economy`** **`863462268934422540`** \
                    will select **text** channel with id 863462268934422540 (you can use mention with # instead of id) as log channel",


        "border" : "`{}border` `amount_of_xp` set amount of xp that members need to get for the new level\n\n**Example:**\n**`{}border`** **`1000`** set border equal to 1000 xp, so \
                    after achieving level 2 member need 1000 more xp to achieve level 3",

        "xp_per_msg" : "`{}xp_per_msg` `amount_of_xp` set amount of xp gained from one message\n\n**Example:**\n**`{}xp_per_msg`** **`2`** set this amount equal to 2 so\
                    for each message member will gain 2 xp",

        "ic" : "`{}ic` call menu to manage ignored channels, where members can't gain xp from message",

        "alert_channel" : "`{}alert_channel` call menu to manage alert channel where members are notificated about new level",

        "roles_per_lvl" : "`{}roles_per_lvl` call menu to manage levels and roles gained for them",

        "manage_member" : "`{}manage_member` `member` сall menu to manage member (his balance and xp)\n\n**Example:**\n**`{}manage_member`** **`931273285268832326`** \
                    will call menu to manage member with id 931273285268832326 ((you can use mention with @ instead of id)",
    },
    1 : {
        "guide" : "`{}guide` показывает гайд о системе бота",

        "setup" : "`{}setup` начинает настройку параметров бота",

        "settings" : "`{}settings` вызывает меню, в котором отображены текущие настройки бота",

        "language" : "`{}language` `язык` устанавливает выбранный язык для команд модераторов и названия и описания слэш команды. Доступны: **`Eng`** \
                    (регистр не важен) - для английского и **`Rus`** (регистр не важен) - для русского.\n\n**Пример:**\n**`{}language`** **`rus`** установит русский язык",

        "zones" : "`{}zones` показывет доступные именные часовые пояса",

        "time_zone" : "`{}time_zone` `имя_часового_пояса_из_списка или часовой_сдвиг_от_UTC_со_знаком_'-'_при_необходимости` устанавливает формат времени **`UTC`**±**`X`**, \
                    **`X`** Є {}-12; -11; ...; 11; 12{}, для сервера. \n\n**Пример:**\n**`{}time_zone`** **`YAKT`** установит часовой пояс Якутска UTC+9, а **`{}time_zone`** \
                    **`-7`** установит часовой пояс UTC-7",

        "mod_roles" : "`{}mod_roles` вызывает меню управления ролями модераторов. Пользователи с этими ролями смогу управлять настройками бота",

        "money_per_msg" : "`{}money_per_msg` `количество` устанавливает количество денег, получаемое пользователем за одно сообщение\n\n**Пример:**\n**`{}money_per_msg`** \
                    **`2`** сделает так, что за каждое сообщение пользователь будет получать 2 единицы валюты",

        "reset" : "`{}reset` сбрасывает текущие настройки бота",

        "available_roles" : "`{}available_roles` вызывает меню управления ролями, доступными для покупки/продажи на сервере (см. гайд)",

        "manage_role" : "`{}manage_role` `роль` вызывает меню для управления ролью в экономической системе бота\n\n**Пример:**\n**`{}manage_role`** \
                    **`972494065088200745`** вызовет меню управления ролью с id 972494065088200745 (Вы можете упомянуть роль при помощи @ вместо id) ",
        
        "salary_timer" : "`{}salary_timer` `время_в_секундах` устанавливает перерыв между начислением денег участникам с ролями, которые приносят деньги.\n\n**Пример:**\n\
                    **`{}salary_timer`** **`10800`** установит перерыв, равный 3 часам (10800 секунд = 3 часа)",
        
        "work_salary" : "`{}work_salary` `левая_граница` `правая_граница` устанавливает количество денег, получаемое после использования команды /work. Это количество будет целым \
                    числом Є [левая_граница; правая_граница]. Оба числа должны быть целыми неотрицательными числами, правая граница должна быть не меньше левой.\n\n**Пример:**\n\
                    **`{}work_salary`** **`10`** **`100`** изменяет заработок, получаемый после использования команды `/work`, этот заработок будет рандомным целым числом от 10 до \
                    100 (заработок Є [10; 100])",

        "work_cooldown" : "`{}work_cooldown` `время_в_секундах` устанавливает кулдаун для использования команды `/work`\n\n**Пример:**\n**`{}work_cooldown`** **`10800`** \
                    установит кулдаун, равный 3 часам (10800 секунд = 3 часа), для команды `/work`",

        "log_economy" : "`{}log_economy` `текстовый_канал` устанавливает выбранный для хранения логов об экономических операциях\n\n**Пример:**\n**`{}log_economy`** \
                    **`863462268934422540`** установит канал с id 863462268934422540 (Вы можете упомянуть канал при помощи #, а не id) в качестве канала для логов бота",

        "border" : "`{}border` `граница` устанавливает количество опыта, которое нужно пользователям для достижения нового уровня\n\n**Пример:**\n**`{}border`** **`1000`** установит \
                    границу в 1000 xp, и теперь, чтобы достичь второго уровня после получения первого, пользователю понадобидся ещё 1000 xp",

        "xp_per_msg" : "`{}xp_per_msg` `опыт` устанавливает количество опыта, получаемое за каждое сообщение\n\n**Пример:**\n**`{}xp_per_msg`** **`2`** сделает так, что за \
                    каждое сообщение пользователь будет получать 2 опыта",

        "ic" : "`{}ic` вызывает меню управления игнорируемыми каналами, в которых пользователи не получают опыт за сообщения",

        "alert_channel" : "`{}alert_channel` вызывает меню управления каналом оповещения пользователей о достижении нового уровня",

        "roles_per_lvl" : "`{}roles_per_lvl` вызывает меню уровнями и соответствующими им ролями",

        "manage_member" : "`{}manage_member` `member` вызывает меню управления пользователем (его балансом и опытом)\n\n**Пример:**\n**`{}manage_member`** **`931273285268832326`** \
                    вызовет меню управления пользователем с id 931273285268832326 (Вы можете упомянуть пользователя при помощи @ вместо id)"
    }
}

class custom_b(Button):
    def __init__(self, label: str, style: ButtonStyle, emoji, c_id: str):
        super().__init__(style=style, label=label, emoji=emoji, custom_id=c_id)
    async def callback(self, interaction: Interaction):
        return await self.view.click(interaction=interaction, c_id=self.custom_id)

class help_view(View):
    def __init__(self, t_out: int, auth_id: int, m_rls: set, lng: int, pref: str):
        super().__init__(timeout=t_out)
        self.m_rls = m_rls
        self.auth_id = auth_id
        self.lng = lng
        self.pref = pref
        self.add_item(custom_b(label=text_help_view[lng][0], style=ButtonStyle.green, emoji="👤", c_id="0"))
        self.add_item(custom_b(label=text_help_view[lng][1], style=ButtonStyle.red, emoji="⚙️", c_id="1"))
        
    
    async def click(self, interaction: Interaction, c_id: str):
        if interaction.user.id != self.auth_id:
            await interaction.response.send_message(embed=Embed(description=text_help_view[self.lng][2]), ephemeral=True)
        elif c_id == "0":
            emb1 = Embed(title=text_help_view[self.lng][0], description=text_help_view[self.lng][4])
            emb2 = Embed(description=text_help_view[self.lng][5])
            emb3 = Embed(description=text_help_view[self.lng][6])
            for n, v in u_ec_cmds[self.lng]:
                emb1.add_field(name=n, value=v, inline=False)
            for n, v in u_pers_cmds[self.lng]:
                emb2.add_field(name=n, value=v, inline=False)
            for n, v in u_other_cmds[self.lng]:
                emb3.add_field(name=n, value=v, inline=False)
            await interaction.response.edit_message(embeds=[emb1, emb2, emb3])
        elif interaction.user.guild_permissions.administrator or any(role.id in self.m_rls for role in interaction.user.roles):
            emb1 = Embed(title=text_help_view[self.lng][1], description=text_help_view[self.lng][7])
            emb2 = Embed(description=text_help_view[self.lng][8])
            emb3 = Embed(description=text_help_view[self.lng][9])
            for n, v in m_general_cmds[self.lng]:
                emb1.add_field(name=n.format(self.pref), value=v, inline=False)
            for n, v in m_ec_cmds[self.lng]:
                emb2.add_field(name=n.format(self.pref), value=v, inline=False)
            for n, v in m_rnk_cmds[self.lng]:
                emb3.add_field(name=n.format(self.pref), value=v, inline=False)
            await interaction.response.edit_message(embeds=[emb1, emb2, emb3])
        else:
            await interaction.response.send_message(embed=Embed(description=text_help_view[self.lng][3]), ephemeral=True)


class mod_commands(commands.Cog):
    def __init__(self, bot: commands.Bot, prefix: str, in_row):
        self.bot = bot
        self.prefix = prefix
        
        global bot_guilds
        global bot_guilds_e
        global bot_guilds_r
        global help_menu
        
        self.currency = currency
        global languages
        languages = {
            "eng" : 0,
            "rus" : 1
        }
        global text
        text = {
            0 : {
                0 : 'Role',
                1 : 'Commands',
                2 : '**For more information about command use**:',
                3 : 'name_of_the_command',
                4 : 'Information about command:',
                404 : 'Error',
                5 : f'Please, use command like **`{prefix}help_m`** or\n**`{prefix}help_m`** **`name_of_the_command`**', #
                6 : 'Please, select command from list of command', #
                7 : '**This role is unavailable for the purchase/sale on the server. Change it via the command**',
                8 : 'Role type must be integer number belongs to the segment [0; 2]',
                9 : '**`Salary of unique role must be non-negative integer number`**',
                10 : '**`was added to the list of roles available for the purchase/sale on the server`**',
                11 : 'You cant change type of the existing role. To do it, you should recreate role.\n**All information about the role will be lost!**',
                12 : 'Role was successfully updated',
                13 : "has been withdrawn from server store, unavailable for the purchase/sale and doesnt bring money to it's owners from now",
                14 : 'From now the price of the role',
                15 : f'role - id - price - type (look {prefix}help_m add)',
                16 : 'This role is not unique',
                17 : 'added to the balance of',
                18 : "**`This user not found on the server.`**",
                19 : '**`Please, use correct arguments for command. More info via \n{}help_m {}`**',
                20 : '**`This command not found`**',
                21 : '**`This user not found`**',
                22 : '**`Please, wait before reusing this command`**',
                23 : "**`Sorry, but you don't have enough permissions for using this command`**",
                24 : f"**Economic moderator role is not chosen! User with administrator or manage server permission should do it via `{prefix}mod_role` `role_id`**",
                25 : f"**`was set as economic moderator role. Commands from {prefix}help_m are available for users with this role`**",
                26 : "was set as log channel",
                27 : "**`English language was set as main`**",
                28 : "Please, select language from the list:",
                29 : "`Eng` - for English language",
                30 : "`Rus` - for Russian language",
                31 : f"Please, use command in format **`{prefix}time_zone`** **`name_of_time_zone_from_{prefix}zones or hour_difference_with_'-'_if_needed`**",
                32 : "Time zone **`UTC{}`** was set on the server",
                33 : "**`This server has time zone UTC",
                34 : "**`List of available named time zones:`**",
                35 : "**`Time (in seconds) must be integer positive number (without any additional symbols)`**",
                36 : "**`From now to reuse command /work members should wait at least {} seconds`**",
                37 : "**Left and right borders must be `integer non-negative` numbers and the `right must be at least as large as the left`**",
                38 : "**`{} и {} selected as borders for amount of money gained after using /work`**",
                39 : "**`From now members with unique roles (type of roles - 0) will gain money once every {} seconds`**",
                40 : "**`This role not found`**",
                41 : "**`This channel not found`**",
                42 : "**`This amount of role already in the store`**",
                43 : "**`Amount of roles {} was made equal to {}`**",
                44 : "**`Now cash of the {} is equal to {}`** {}",
                45 : "**Time for answer has expired**",
                46 : "Balance of the member:",
                47 : "**`Language is changing, please, wait a bit...`**",
                48 : "**`Selected language already set as main`**"
                
            },
            1 : {
                0 : 'Role',
                1 : 'Команды:',
                2 : '**Для уточнения работы команды напишите**:',
                3 : 'название_команды',
                4 : 'Информация о команде',
                404 : 'Ошибка',
                5 : f'Пожалуйста, укажите команду в формате`{prefix}help_m` или\n`{prefix}help_m` `название_команды`',
                6 : 'Пожалуйста, укажите команду из списка команды',
                7 : '**Эта роль не находится в списке ролей, доступных для покупки/на сервере. Измените это с помощью команды**',
                8 : "Тип роли должен быть целым числом, принадлежащим отрезку [0; 2]",
                9 : "**`Пассивный заработок уникальной роли должен быть целым неотрицательным числом`**",
                10 : '**`была добавлена в список ролей, разрешённых для покупки/продажи на сервере`**',
                11 : 'Вы не можете изменять тип существующе роли. Чтобы сделать это, Вам нужно пересоздать роль.\n**Вся информация о роли будет потеряна!**',
                12 : 'Роль была успешно обновлена',
                13 : 'изъята из обращения на сервере и больше не доступна для покупки/продажи, а также не приносит доход',
                14 : 'Теперь цена роли',
                15 : f"Роль - id - цена - тип (см. {prefix}help_m add)",
                16 : "Эта роль не уникальная",
                17 : 'записана на личный счёт пользователя',
                18 : "**`На сервере не найден такой пользователь`**",
                19 : "**`Пожалуйста, укажите верные аргументы команды. Подробнее - {}help_m {}`**",
                20 : "**`Такая команда не найдена`**",
                21 : "**`Такой пользователь не найден`**",
                22 : "**`Пожалуйста, подождите перед повторным использованием команды`**",
                23 : "**`У Ваc недостаточно прав для использования этой команды`**",
                24 : f"**Роль модератора экономики не выбрана! Пользователь с правами админитратора или управляющего сервером должен сделать это при помощи `{prefix}mod_role` `role_id`**",
                25 : f"**`установлена в качестве роли модератора экономики. Этой роли доступны команды из списка {prefix}help_m`**",
                26 : "установлен в качестве канала для логов",
                27 : "**`Русский язык установлен в качестве языка интерфейса`**",
                28 : "Пожалуйста, выберите язык из списка:",
                29 : "`Eng` - для английского языка",
                30 : "`Rus` - для русского языка",
                31 : f"Пожалуйста, укажите команду в формате **`{prefix}time_zone`** **`имя_пояса_из_списка или часовой_сдвиг_со_знаком_'-'_при необходимости`**",
                32 : "На сервере был установлен часовой пояс **`UTC{}`**",
                33 : "**`На этом сервере установлен часовой пояс UTC",
                34 : "**`Список именных часовых поясов:`**",
                35 : "**`Время (в секундах) должно быть целым положительным числом (только число, без дополнительных символов)`**",
                36 : "**`В качестве перерыва между использованием /work установлено время {} секунд(а, ы)`**",
                37 : "**Границы заработка должны быть `целыми неотрицательными` числами, причём `правая граница` (в команде указывается второй) \
                **`должна быть не меньше левой`** (в команде указывается первой)**",
                38 : "**`{} и {} установлены в качестве границ заработка от команды /work`**",
                39 : "**`В качестве перерыва между начислением денег участникам с уникальными ролями (тип ролей - 0) установлено время {} секунд(а, ы)`**",
                40 : "**`Такая роль не найдена`**",
                41 : "**`Такой канал не найден`**",
                42 : "**`Нужное количество ролей уже находится в магазине`**",
                43 : "**`Количество ролей {} в магазине установлено равным {}`**",
                44 : "**`Теперь баланс пользователя {} равен {}`** {}",
                45 : "**Время ответа истекло**",
                46 : "Баланс пользователя:",
                47 : "**`Язык изменяется, пожалуйста, подождите немного...`**",
                48 : "**`Выбранный язык уже установлен в качестве основного`**"
            }
        }
        

    def mod_role_set(self, ctx: commands.Context):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                r = cur.execute("SELECT value FROM server_info WHERE settings = 'mod_role'").fetchone()
                if r == None or r[0] == 0:
                    return 0
                return 1

    def lang(self, ctx: commands.Context):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                return cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]

    def needed_role(ctx: commands.Context):
        
        if any(role.permissions.administrator or role.permissions.manage_guild for role in ctx.author.roles) or ctx.guild.owner == ctx.author:
            return 1

        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                mod_id = cur.execute("SELECT value FROM server_info WHERE settings = 'mod_role'").fetchone()
                if mod_id != None and mod_id[0] != 0:
                    return any(role.id == mod_id[0] for role in ctx.author.roles)
                return 0
          
    def check(self, base: Connection, cur: Cursor, memb_id: int):
            member = cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()
            if member == None:
                cur.execute('INSERT INTO users(memb_id, money, owned_roles, work_date) VALUES(?, ?, ?, ?)', (memb_id, 0, "", 0))
                base.commit()
            else:
                if member[1] == None or member[1] < 0:
                    cur.execute('UPDATE users SET money = ? WHERE memb_id = ?', (0, memb_id))
                    base.commit()
                if member[2] == None:
                    cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', ("", memb_id))
                    base.commit()
                if member[3] == None:
                    cur.execute('UPDATE users SET work_date = ? WHERE memb_id = ?', (0, memb_id))
                    base.commit()
            return cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()

    async def insert_uniq(self, base: Connection, cur: Cursor, nums: int, role_id: int, outer: list, price: int, time_now: int, ctx, lng: int):
        l = 0 if outer == None or outer == [] else len(outer)
        if nums > l:
            items = cur.execute('SELECT item_id FROM outer_store').fetchall()
            if items == None or items == []:
                free_ids = [i for i in range(1, nums-l+1)]
                r = [(x, role_id, 1, price, time_now, 0) for x in free_ids]
                cur.executemany('INSERT INTO outer_store(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', r)
                base.commit()
            else:
                item_ids = set([x[0] for x in items])
                free_ids = []
                for i in range(1, max(item_ids) + 1):
                    if i not in item_ids:
                        free_ids.append(i)
                if len(free_ids) >= nums - l:
                    r = [(free_ids[i], role_id, 1, price, time_now, 0) for i in range(nums-l)]
                    cur.executemany('INSERT INTO outer_store(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', r)
                    base.commit()
                else:
                    r = [(x, role_id, 1, price, time_now, 0) for x in free_ids]
                    cur.executemany('INSERT INTO outer_store(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', r)
                    base.commit()
                    r = [(x, role_id, 1, price, time_now, 0) for x in range(max(item_ids)+1, max(item_ids) + nums - l- len(free_ids) + 1)]
                    cur.executemany('INSERT INTO outer_store(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', r)
                    base.commit()
            await ctx.reply(text[lng][43].format(role_id, nums), mention_author=False)

        elif nums < l:
            to_delete = cur.execute("SELECT item_id FROM outer_store WHERE role_id = ? ORDER BY last_date LIMIT ?", (role_id, l-nums)).fetchall()
            for item in to_delete:
                cur.execute("DELETE FROM outer_store WHERE item_id = ?", (item[0],))
            base.commit()
            await ctx.reply(text[lng][43].format(role_id, nums), mention_author=False)

        elif nums == l:
            await ctx.reply(text[lng][42], mention_author=False)


    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        if not os.path.exists(f"{path_to}/bases/bases_{guild.id}/"):
            try:
                os.mkdir(f"{path_to}/bases/bases_{guild.id}/")
            except Exception:
                with open("error.log", "a+", encoding="utf-8") as f:
                    f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [can't create folder] [{guild.id}] [{guild.name}] [{str(Exception)}]\n")
                return
        
        bot_guilds.add(guild.id)
        with closing(connect(f'{path_to}/bases/bases_{guild.id}/{guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                cur.execute('CREATE TABLE IF NOT EXISTS users(memb_id INTEGER PRIMARY KEY, money INTEGER, owned_roles TEXT, work_date INTEGER)')
                base.commit()
                cur.execute('CREATE TABLE IF NOT EXISTS server_roles(role_id INTEGER PRIMARY KEY, price INTEGER, salary INTEGER, type INTEGER)')
                base.commit()
                cur.execute('CREATE TABLE IF NOT EXISTS store(item_id INTEGER PRIMARY KEY, role_id INTEGER, quantity INTEGER, price INTEGER, last_date INTEGER, salary INTEGER, type INTEGER)')
                base.commit()
                cur.execute('CREATE TABLE IF NOT EXISTS salary_roles(role_id INTEGER PRIMARY KEY, members TEXT, salary INTEGER NOT NULL, last_time INTEGER)')
                base.commit()
                cur.execute("CREATE TABLE IF NOT EXISTS server_info(settings TEXT PRIMARY KEY, value INTEGER)")
                base.commit()
                cur.execute("CREATE TABLE IF NOT EXISTS rank_roles(level INTEGER PRIMARY KEY, role_id INTEGER)")
                base.commit()
                cur.execute("CREATE TABLE IF NOT EXISTS rank(memb_id INTEGER PRIMARY KEY, xp INTEGER, c_xp INTEGER)")
                base.commit()
                cur.execute("CREATE TABLE IF NOT EXISTS ic(chn_id INTEGER PRIMARY KEY)")
                base.commit()
                cur.execute("CREATE TABLE IF NOT EXISTS mod_roles(role_id INTEGER PRIMARY KEY)")
                base.commit()

                lng = 1 if "ru" in guild.preferred_locale else 0

                r = [
                    ('lang', lng), ("0>>", -1), ('xp_step', 1), ('tz', 0), 
                    ('w_cd', 14400), ('sal_t', 0), ('sal_l', 1), ('sal_r', 250),
                    ('lvl_c', 0), ('log_c', 0), ('poll_v_c', 0), ('poll_c', 0)
                ]
                    
                cur.executemany("INSERT OR IGNORE INTO server_info(settings, value) VALUES(?, ?)", r)
                base.commit()

        with open("guild.log", "a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [guild_join] [{guild.id}] [{guild.name}] \n")


    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        bot_guilds.remove(guild.id)
        with open("guild.log", "a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [guild_remove] [{guild.id}] [{guild.name}]\n")

    
    @tasks.loop(seconds=30)
    async def salary_roles(self):
        for g in bot_guilds: 
            with closing(connect(f'{path_to}/bases/bases_{g}/{g}.db')) as base:
                with closing(base.cursor()) as cur:
                    r = cur.execute("SELECT * FROM salary_roles").fetchall()
                    if r:
                        t = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_t'").fetchone()[0]
                        for role, members, salary, last_time in r:
                            flag = 0

                            if last_time == 0 or last_time == None:
                                flag = 1
                            elif last_time - int(time()) >= t:
                                flag = 1

                            if flag:
                                cur.execute("UPDATE money_roles SET last_time = ? WHERE role_id = ?", (int(time()), role))
                                base.commit()
                                for member in members.split('#'):
                                    if member != "":
                                        member = int(member)
                                        self.check(base=base, cur=cur, memb_id=member)
                                        cur.execute("UPDATE users SET money = money + ? WHERE memb_id = ?", (salary, member))
                                        base.commit()
            await sleep(0.5)

    
    @salary_roles.before_loop
    async def before_timer(self):
        await self.bot.wait_until_ready()

    @commands.command(name="guide")
    @commands.check(needed_role)
    async def _guide(self, ctx: commands.Context, pr: str):
        with closing(connect(f'{path_to}/bases/bases_{ctx. guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
        emb = Embed(title=guide[lng][0])
        emb.add_field(name=guide[lng][1], value=guide[lng][2].format(pr, pr), inline=False)
        for i in range(3, 10, 2):
            emb.add_field(name=guide[lng][i], value=guide[lng][i+1], inline=False)
        emb.add_field(name=guide[lng][11], value=guide[lng][12].format(pr), inline=False)
        emb.add_field(name=guide[lng][13], value=guide[lng][14].format(pr, pr), inline=False)
        emb.add_field(name=guide[lng][15], value=guide[lng][16].format(pr, pr, pr), inline=False)
        emb.add_field(name=guide[lng][17], value=guide[lng][18].format(pr), inline=False)
        print(guide[lng][19].format(pr))
        #emb.set_footer()
        await ctx.reply(embed=emb, mention_author=False)
  
    @commands.command(name="log_economy")
    @commands.check(needed_role)
    async def _log_economy(self, ctx: commands.Context, channel: TextChannel):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'log_channel'", (channel.id,))
                base.commit()
                await ctx.reply(f"{channel.mention} {text[lng][26]}", mention_author=False)


    async def help(self, interaction: Interaction, command: str):
        lng = 1 if "ru" in interaction.locale else 0
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild.id}/{interaction.guild.id}.db")) as base:
            with closing(base.cursor()) as cur:
                m_rls = cur.execute("SELECT * FROM mod_roles").fetchall()
                pref = cur.execute("SELECT settings FROM server_info WHERE value = -1").fetchone()[0][1:]
                if m_rls:
                    m_rls = {x[0] for x in m_rls}
                else:
                    m_rls = set()
                if command == "":
                    view_h = help_view(t_out=60, auth_id=interaction.user.id, m_rls=m_rls, lng=lng, pref=pref)
                    emb = Embed(
                        title=help_text[lng][0],
                        description=help_text[lng][1],
                        colour=Colour.dark_purple()
                    )
                    await interaction.response.send_message(embed=emb, view=view_h)
                    msg = await interaction.original_message()
                    chk = await view_h.wait()
                    if chk:
                        for button in view_h.children:
                            button.disabled = True
                        await msg.edit(view=view_h)
                else:
                    pass
                    

    @slash_command(
        name="help", 
        description="Calls menu with commands",
        description_localizations={
            Locale.ru : "Вызывает меню команд"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    async def help_e(
        self, 
        interaction: Interaction,
        command: str = SlashOption(
            name = "command",
            description="type command if you want to see more info about it (optional, not necessary)",
            description_localizations={
                Locale.ru: "напишите команду, если хотите узнать больше информации о ней (не обязательно)"
            },
            required=False,
            default=""
        )
    ):
        await self.help(interaction=interaction, command=command)
    

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
    async def help_r(
        self, 
        interaction: Interaction,
        command: str = SlashOption(
            name = "command",
            description="напишите команду, если хотите узнать больше информации о ней (не обязательно)",
            description_localizations={
                Locale.en_GB: "type command if you want to see more info about it (optional, not necessary)",
                Locale.en_US: "type command if you want to see more info about it (optional, not necessary)"
            },
            required=False,
            default=""
        )
    ):
        await self.help(interaction=interaction, command=command)

    

    """ @commands.command(aliases = ["help_m"])
    @commands.check(needed_role)
    async def _help_m(self, ctx: commands.Context, *args):
        msg = []
        lng = self.lang(ctx=ctx)
        if len(args) == 0:
            for command in self.cmds_list:
                msg.append(command)
            emb = Embed(
                colour=Colour.dark_purple(),
                title=text[lng][1],
                description = '\n'.join(msg)
            )
            emb.add_field(name=text[lng][2], value = f'\n**`{self.prefix}help_m`** **`{text[lng][3]}`**')

        elif len(args) == 1:
            arg = args[0].replace(self.prefix, '')
            if not arg in help_menu[lng]:
                await ctx.reply(
                    embed=Embed(
                        title=text[lng][404],
                        description=f'{text[lng][6]} `{self.prefix}help_m`',
                        colour=Colour.red()
                    ),
                    mention_author=False
                )
                return

            msg.append(f"{help_menu[lng][arg]}")
            emb = Embed(
                colour=Colour.dark_purple(),
                title=text[lng][4],
                description='\n'.join(msg)
            )
        
        else:
            emb = Embed(colour=Colour.red(), title=text[lng][404], description=text[lng][5])

        await ctx.reply(embed=emb, mention_author=False) """

    """ @_help_m.error
    async def _help_m_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandInvokeError):
            lng = self.lang(ctx=ctx) """
      

    @commands.command(hidden=True, aliases=['set'])
    @commands.check(needed_role)
    async def _set(self, ctx: commands.Context, role: Role, nums: int):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur: 
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
                if role_info == None:
                    await ctx.reply(embed=Embed(title=text[lng][404],description=f"{text[lng][7]} `{self.prefix}add`",colour=Colour.red()), mention_author=False)
                    return
                is_special = role_info[2]
                outer = cur.execute('SELECT * FROM outer_store WHERE role_id = ?', (role.id,)).fetchall()
                if nums > 0:
                    #time_now = (datetime.utcnow()+timedelta(hours=3)).strftime('%S/%M/%H/%d/%m/%Y')
                    time_now = int(time()) #inside of the bot without time zone
                    if is_special == 0:
                        await self.insert_uniq(base=base, cur=cur, nums=nums, role_id=role.id, outer=outer, price=role_info[1], time_now=time_now, ctx=ctx, lng=lng)
                        return

                    elif is_special == 1:
                        if outer == None or outer == []:
                            items = cur.execute('SELECT item_id FROM outer_store').fetchall()
                            free_id = 1
                            if items != None:
                                item_ids = [x[0] for x in items]
                                item_ids.sort()
                                while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                                    free_id += 1
                            cur.execute('INSERT INTO outer_store(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, nums, role_info[1], time_now, 1))
                            base.commit()
                        else:
                            cur.execute('UPDATE outer_store SET quantity = ?, last_date = ? WHERE role_id = ?', (nums, time_now, role.id))
                            base.commit()
                    elif is_special == 2:
                        if outer == None or outer == []:
                            items = cur.execute('SELECT item_id FROM outer_store').fetchall()
                            free_id = 1
                            if items != None:
                                item_ids = [x[0] for x in cur.execute('SELECT item_id FROM outer_store').fetchall()]
                                item_ids.sort()
                                while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                                    free_id += 1
                            cur.execute('INSERT INTO outer_store(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, -404, role_info[1], time_now, 2))
                            base.commit()     
                else:
                    nums = 0
                    cur.execute('DELETE FROM outer_store WHERE role_id = ?', (role.id,))
                    base.commit()

                await ctx.reply(content=text[lng][43].format(role.id, nums), mention_author=False)


    @commands.command(hidden=True, aliases=['update_cash'])
    @commands.check(needed_role)
    async def _update_cash(self, ctx: commands.Context, member: Member, value: int):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                memb_id = member.id
                self.check(base=base, cur=cur, memb_id=memb_id)
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                if value < 0:
                    cur.execute('UPDATE users SET money = ? WHERE memb_id = ?', (0, memb_id))
                    base.commit()
                    value = 0
                else:
                    cur.execute('UPDATE users SET money = ? WHERE memb_id = ?', (value, memb_id))
                    base.commit()

                await ctx.reply(content=text[lng][44].format(member.name, value, self.currency), mention_author = False)


    @commands.command(hidden=True, aliases=['add'])
    @commands.check(needed_role)
    async def _add(self, ctx: commands.Context, role: Role, price: int, is_special: int, salary: int = None):
        
        lng = self.lang(ctx=ctx)
        if not is_special in [0, 1, 2]:
            await ctx.reply(embed=Embed(title=text[lng][404], description=text[lng][8], colour=Colour.red()), mention_author=False)
            return
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                rls = cur.execute('SELECT role_id FROM server_roles').fetchall()
                role_ids = [] if rls == None else [x[0] for x in rls]
                if not role.id in role_ids:
                    if is_special == 0:
                        if salary == None or salary < 0:
                            await ctx.reply(embed=Embed(title=text[lng][404], description=text[lng][9], colour=Colour.red()), mention_author=False)
                            return
                        cur.execute("INSERT INTO money_roles(role_id, members, salary, last_time) VALUES(?, ?, ?, ?)", (role.id, "", salary, 0))
                        base.commit()
                    await ctx.reply(embed=Embed(description=f"{role.mention} {text[lng][10]}"), mention_author=False)
                    cur.execute('INSERT INTO server_roles(role_id, price, special) VALUES(?, ?, ?)', (role.id, price, is_special))
                    base.commit()
                else:
                    is_special_shop = cur.execute("SELECT special FROM server_roles WHERE role_id = ?", (role.id,)).fetchone()[0]
                    if is_special != is_special_shop:
                        await ctx.reply(content = text[lng][11], mention_author=False)
                        return
                    cur.execute("UPDATE server_roles SET price = ? WHERE role_id = ?", (price, role.id))
                    base.commit()
                    cur.execute("UPDATE money_roles SET salary = ? WHERE role_id = ?", (salary, role.id))
                    base.commit()
                    await ctx.reply(content = text[lng][12], mention_author=False)

              
    @commands.command(hidden=True, aliases=['remove'])
    @commands.check(needed_role)
    async def _remove(self, ctx: commands.Context, role: Role):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                cur.execute('DELETE FROM server_roles WHERE role_id = ?', (role.id,))
                base.commit()
                cur.execute('DELETE FROM outer_store WHERE role_id = ?', (role.id,))
                base.commit()
                cur.execute("DELETE FROM money_roles WHERE role_id = ?", (role.id,))
                base.commit()
                await ctx.reply(content=f"{text[lng][0]} {role} {text[lng][13]}", mention_author=False)


    @commands.command(hidden=True, aliases=['update_price'])
    @commands.check(needed_role)
    async def _update_price(self, ctx: commands.Context, role: Role, price: int):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                is_in = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
                if is_in == None:
                        emb = Embed(colour=Colour.red(), title=text[lng][404], description=f"{text[lng][7]} `{self.prefix}add`")
                        await ctx.reply(embed=emb, mention_author=False)
                        return
                cur.execute('UPDATE server_roles SET price = ? WHERE role_id = ?', (price, role.id))
                base.commit()
                await ctx.reply(content=f"{text[lng][14]} {role} - {price}{self.currency}", mention_author=False)


    @commands.command(hidden=True, aliases=['list'])
    @commands.check(needed_role)
    async def _list(self, ctx: commands.Context):
        try:
            with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
                with closing(base.cursor()) as cur:
                    lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                    roles = cur.execute('SELECT * FROM server_roles').fetchall()
        except Exception as E:
            with open("d.log", "a+", encoding="utf-8") as f:
                f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [{ctx.guild.id}] [{ctx.guild.name}] [{str(E)}]\n")
            return
        descr = []
        for role in roles:
            descr.append(f"<@&{role[0]}> - {role[0]} - {role[1]} - {role[2]}")
        emb = Embed(title=text[lng][15], description="\n".join(descr))
        await ctx.reply(embed=emb, mention_author=False)


    @commands.command(hidden=True, aliases=['give_unique'])
    @commands.check(needed_role)
    async def _give_unique(self, ctx: commands.Context, member: Member, role: Role):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                memb = self.check(base=base, cur=cur, memb_id=member.id)
                role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
                if role_info == None:
                    emb = Embed(colour=Colour.red(), title=text[lng][404], description=f"{text[lng][7]} `{self.prefix}add`")
                    await ctx.reply(embed=emb, mention_author=False)
                    return
                elif role_info[2] != 0:
                    emb = Embed(colour=Colour.red(), title=text[lng][404], description=text[lng][16])
                    await ctx.reply(content=emb, mention_author=False)
                    return

                owned_roles = memb[2]
                if not str(role.id) in owned_roles.split('#'):
                    owned_roles += f"#{role.id}"                        
                cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', (owned_roles, member.id))
                base.commit()

                try:
                    membs = cur.execute("SELECT members FROM money_roles WHERE role_id = ?", (role.id,)).fetchone()
                    if membs == None:
                        cur.execute("INSERT INTO money_roles(role_id, members, salary, last_time) VALUES(?, ?, ?, ?)", (role.id, "", 0, 0))
                        membs = ""
                    elif membs[0] == None:
                        membs = ""
                    else:
                        membs = membs[0]

                    if not str(member.id) in membs.split('#'):
                        membs += f"#{member.id}"                 
                    cur.execute('UPDATE money_roles SET members = ? WHERE role_id = ?', (membs, role.id))
                    base.commit()
                except Exception as E:
                    base.rollback()
                    with open("d.log", "a+", encoding="utf-8") as f:
                        f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [_give_unique] [{ctx.guild.id}] [{ctx.guild.name}] [{str(E)}]\n")

                await ctx.reply(content=f"{text[lng][0]} {role} {text[lng][17]} {member}", mention_author=False)

    
    

    
  

    @commands.command(hidden=True, aliases=["language"])
    @commands.check(needed_role)
    async def _language(self, ctx: commands.Context, language: str):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                if language.lower() not in languages:
                    emb = Embed(
                        title=text[lng][28],
                        description="\n".join([text[lng][29], text[lng][30]]), 
                        colour=Colour.red(),
                    )
                    await ctx.reply(embed=emb, mention_author=False)
                    return
                
                if languages[language.lower()] == lng:
                    emb = Embed(
                        title=text[lng][404],
                        description=text[lng][48],
                        colour=Colour.red(),
                    )
                    await ctx.reply(embed=emb, mention_author=False)
                    return

                g_id = ctx.guild.id
                emb = Embed(
                    colour=Colour.dark_purple(),
                )
                if not languages[language.lower()]:   
                    if not g_id in bot_guilds_e:
                        bot_guilds_e.add(g_id)
                    if g_id in bot_guilds_r:
                        bot_guilds_r.remove(g_id)
                    #print(f"Update: Eng: {bot_guilds_e}; Rus: {bot_guilds_r}")
                    lng = 0
                    emb.description=text[lng][47]
                    msg = await ctx.reply(embed=emb, mention_author=False)

                    self.bot.unload_extension(f"commands.slash_shop")
                    self.bot.load_extension(f"commands.slash_shop", extras={"prefix": prefix, "in_row": in_row, "currency": currency})
                    await sleep(1)
                    await self.bot.discover_application_commands()
                    await sleep(10)
                    await self.bot.sync_all_application_commands()
                    
                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'lang'", (0,))

                elif language.lower() == "rus":
                    if not g_id in bot_guilds_r:
                        bot_guilds_r.add(g_id)
                    if g_id in bot_guilds_e:
                        bot_guilds_e.remove(g_id)
                    lng = 1
                    emb.description=text[lng][47]
                    msg = await ctx.reply(embed=emb, mention_author=False)

                    self.bot.unload_extension(f"commands.slash_shop")
                    self.bot.load_extension(f"commands.slash_shop", extras={"prefix": prefix, "in_row": in_row, "currency": currency})
                    await sleep(1)
                    await self.bot.discover_application_commands()
                    await sleep(10)
                    await self.bot.sync_all_application_commands()

                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'lang'", (1,))
                    
                
                base.commit()
                emb.description=text[lng][27]
                await msg.edit(embed=emb)
                


    @commands.command(hidden=True, aliases=["time_zone", "tz"])
    @commands.check(needed_role)
    async def _time_zone(self, ctx: commands.Context, tz: str):
        tz = tz.upper()
        if not tz in zones:
            lng = self.lang(ctx=ctx)
            emb = Embed(colour=Colour.red(), title=text[lng][404], description=text[lng][31])
            await ctx.reply(embed=emb, mention_author=False)
            return
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'tz'", (zones[tz],))
                base.commit()
                if zones[tz] >= 0:
                    await ctx.reply(content=text[lng][32].format(f"+{zones[tz]}"), mention_author=False)
                else:
                    await ctx.reply(content=text[lng][32].format(zones[tz]), mention_author=False)


    @commands.command(hidden=True, aliases=["zones"])
    @commands.check(needed_role)
    async def _zones_list(self, ctx: commands.Context):
        try:
            with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
                with closing(base.cursor()) as cur:
                    lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                    tz = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]
        except Exception as E:
            with open("d.log", "a+", encoding="utf-8") as f:
                f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [{ctx.guild.id}] [{ctx.guild.name}] [{str(E)}]\n")
            return

        msg = []
        for i in zone_text:
            msg.append(f" **`{i}`** - **`{zone_text[i]}`**")
        if tz >= 0:
            msg.append("\n" + text[lng][33] + f"+{tz}`**")
        else:
            msg.append("\n" + text[lng][33] + f"{tz}`**")
        emb = Embed(
            title=text[lng][34],
            description="\n".join(msg),
            colour=Colour.dark_purple()
        )
        await ctx.reply(embed=emb, mention_author=False)


    @commands.command(hidden=True, aliases=['work_timer'])
    @commands.check(needed_role)
    async def _work_timer(self, ctx: commands.Context, timer: int):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                if timer <= 0:
                    emb = Embed(colour=Colour.red(), title=text[lng][404], description=text[lng][35])
                    await ctx.reply(embed=emb, mention_author=False)
                    return
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'time_r'", (timer,))
                base.commit()
                await ctx.reply(content=text[lng][36].format(timer), mention_author=False)


    @commands.command(hidden=True, aliases=['salary'])
    @commands.check(needed_role)
    async def _salary(self, ctx: commands.Context, a: int, b: int):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                if min(a, b) < 0 or a > b:
                    emb = Embed(colour=Colour.red(), title=text[lng][404], description=text[lng][37])
                    await ctx.reply(embed=emb, mention_author=False)
                    return
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'sal_l'", (a,))
                base.commit()
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'sal_r'", (b,))
                base.commit()
                await ctx.reply(content=text[lng][38].format(a, b), mention_author=False)


    @commands.command(hidden=True, aliases=['uniq_timer'])
    @commands.check(needed_role)
    async def _uniq_timer(self, ctx: commands.Context, timer: int):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                if timer <= 0:
                    emb = Embed(colour=Colour.red(), title=text[lng][404], description=text[lng][35])
                    await ctx.reply(embed=emb, mention_author=False)
                    return
                cur.execute("UPDATE server_info SET value = ? WHERE settings = 'uniq_timer'", (timer,))
                base.commit()
                await ctx.reply(content=text[lng][39].format(timer), mention_author=False)


    @commands.command(hidden=True, aliases=['settings'])
    @commands.check(needed_role)
    async def _settings(self, ctx: commands.Context):
        try:
            with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
                with closing(base.cursor()) as cur:
                    sets = cur.execute("SELECT * FROM server_info").fetchall()
        except Exception as E:
            with open("d.log", "a+", encoding="utf-8") as f:
                f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [{ctx.guild.id}] [{ctx.guild.name}] [{str(E)}]\n")
            return
        lng = sets[0][1]
        log_c = sets[1][1]
        m_r = sets[3][1]
        tz = sets[4][1]
        t_r = sets[5][1]
        s_l = sets[6][1]
        s_r = sets[7][1]
        u_t = sets[8][1]
        emb = Embed(title=set_text[lng][0])
        if lng == 0:
            emb.add_field(name=set_text[0][1], value="`English`", inline=False)
        else:
            emb.add_field(name=set_text[1][1], value="`Русский`", inline=False)
        if log_c != 0:
            emb.add_field(name=set_text[lng][2], value=log_c, inline=False)
        else:
            emb.add_field(name=set_text[lng][2], value=set_text[lng][8], inline=False)
        if m_r != 0:
            emb.add_field(name=set_text[lng][3], value=m_r, inline=False)
        else:
            emb.add_field(name=set_text[lng][3], value=set_text[lng][9], inline=False)
        if tz >= 0:
            emb.add_field(name=set_text[lng][4], value=f"`UTC+{tz}`", inline=False)
        else:
            emb.add_field(name=set_text[lng][4], value=f"`UTC{tz}`", inline=False)
        if lng == 0:
            emb.add_field(name=set_text[0][5], value=f"`{t_r} seconds`", inline=False)
            emb.add_field(name=set_text[0][6], value=f"`From {s_l} to {s_r}`", inline=False)
            emb.add_field(name=set_text[0][7], value=f"`{u_t} seconds`", inline=False)
        else:
            emb.add_field(name=set_text[1][5], value=f"`{t_r} секунд(а, ы)`", inline=False)
            emb.add_field(name=set_text[1][6], value=f"`От {s_l} до {s_r}`", inline=False)
            emb.add_field(name=set_text[1][7], value=f"`{u_t} секунд(а, ы)`", inline=False)
        await ctx.reply(embed=emb, mention_author=False)


    @commands.command(hidden=True, aliases=['reset'])
    @commands.check(needed_role)
    async def _reset(self, ctx: commands.Context):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                cur.execute("DROP TABLE IF EXISTS server_info")
                base.commit()
                cur.execute("CREATE TABLE server_info(settings TEXT PRIMARY KEY, value INTEGER)")
                base.commit()
                r = [
                    ('lang', 0), ('log_channel', 0), ('error_log', 0), 
                    ('mod_role', 0), ('tz', 0), ('time_r', 14400), 
                    ('sal_l', 1), ('sal_r', 250), ('uniq_timer', 14400)
                ]
                cur.executemany("INSERT INTO server_info(settings, value) VALUES(?, ?)", r)
                base.commit()
                if lng == 1:       
                    await ctx.reply("**`Setting were reseted. Настройки были сброшены.`**", mention_author=False)
                else:
                    await ctx.reply("**`Setting were reseted.`**", mention_author=False)

  
    @commands.command(hidden=True, aliases=["quick", "setup", "qs"])
    @commands.check(needed_role)
    async def _quick(self, ctx: commands.Context):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                flag = 1
                msg_ans = None
                while flag and flag < 8:
                    try:
                        if msg_ans == None:
                            emb = Embed(title = questions[lng][9], description=questions[lng][flag])
                            msg_ans = await ctx.reply(embed=emb, mention_author=False)
                        else:
                            emb.description = questions[lng][flag]
                            await msg_ans.edit(embed=emb)
                        message = await self.bot.wait_for(event="message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=20.0)
                    except TimeoutError:
                        emb = Embed(title=text[lng][404], description=text[lng][45], colour=Colour.red())
                        await msg_ans.edit(embed=emb)
                        return
                    else:
                        ans: str = message.content.lower()
                        if ans == "cancel":
                            flag = 0
                        elif flag == 1:
                            if ans in ["eng", "rus"]:
                                flag += 1
                                if ans == "eng":
                                    cur.execute("UPDATE server_info SET value = 0 WHERE settings = 'lang'")
                                    base.commit()
                                    lng = 0
                                else:
                                    cur.execute("UPDATE server_info SET value = 1 WHERE settings = 'lang'")
                                    base.commit()
                                    lng = 1
                                emb.title = questions[lng][9]
                        elif flag == 2:
                            try:
                                ans = int(ans)
                                if ans == 0:
                                    flag += 1
                                elif ans in [x.id for x in ctx.guild.text_channels]:
                                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'log_channel'", (ans,))
                                    base.commit()
                                    flag += 1
                            except:
                                pass
                        elif flag == 3:
                            try:
                                ans = int(ans)
                                if ans == 0:
                                    flag += 1
                                elif ans in [x.id for x in ctx.guild.roles]:
                                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'mod_role'", (ans,))
                                    base.commit()
                                    flag += 1
                            except:
                                pass
                        elif flag == 4:
                            try:
                                ans = int(ans)
                                if -12 <= ans <= 12:
                                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'tz'", (ans,))
                                    base.commit()
                                    flag += 1
                            except:
                                pass
                        elif flag == 5:
                            try:
                                ans = int(ans)
                                if ans == 0:
                                    flag += 1
                                elif ans > 0:
                                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'time_r'", (ans,))
                                    base.commit()
                                    flag += 1
                            except:
                                pass
                        elif flag == 6:
                            try:
                                a, b = map(int, ans.split(" "))
                                if a == 0 and b == 0:
                                    flag += 1
                                elif 0 < a <= b:
                                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'sal_l'", (a,))
                                    base.commit()
                                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'sal_r'", (b,))
                                    base.commit()
                                    flag += 1
                            except:
                                pass
                        elif flag == 7:
                            try:
                                ans = int(ans)
                                if ans == 0:
                                    flag += 1
                                elif ans > 0:
                                    cur.execute("UPDATE server_info SET value = ? WHERE settings = 'uniq_timer'", (ans,))
                                    base.commit()
                                    flag += 1
                            except:
                                pass
                emb.title = None
                emb.description = questions[lng][8].format(self.prefix)
                await msg_ans.edit(embed=emb)


    @commands.command(hidden=True, aliases=["balance_of"])
    @commands.check(needed_role)
    async def _balance_of(self, ctx: commands.Context, member: Member):
        with closing(connect(f'{path_to}/bases/bases_{ctx.guild.id}/{ctx.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]            
                memb = self.check(base=base, cur=cur,memb_id=member.id)
                emb = Embed(title=text[lng][46], description=f"{memb[1]} {self.currency}")
                await ctx.reply(embed=emb, mention_author=False)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        lng = self.lang(ctx=ctx)
        emb=Embed(title=text[lng][404],colour=Colour.red())
        if isinstance(error, commands.MemberNotFound):
            emb.description = text[lng][18]
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            try:
                emb.description = text[lng][19].format(self.prefix, str(ctx.command)[1:])
            except:
                emb.description = text[lng][19].format(self.prefix, "name_of_the_command")
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
            if not self.mod_role_set(ctx=ctx):
                emb.description = text[lng][24]
            else:
                emb.description = text[lng][23]
        else:
            #raise error
            with open("d.log", "a+", encoding="utf-8") as f:
                f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [{ctx.guild.id}] [{ctx.guild.name}] [{str(error)}]\n")
            return
        await ctx.reply(embed=emb, mention_author=False)
  
def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(mod_commands(bot, **kwargs))
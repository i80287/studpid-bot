import asyncio, os
from contextlib import closing
import sqlite3, nextcord
from datetime import datetime, timedelta
from time import time
from nextcord.ext import commands
from nextcord.ext.commands import CheckFailure
from nextcord import Embed, Colour
from config import path, bot_guilds

class mod_commands(commands.Cog):
  def __init__(self, bot: commands.Bot, prefix: str, in_row: int, currency: str):
    self.bot = bot
    self.prefix = prefix
    self.cmds_list = [
        f"`{prefix}guide`",
        f"`{prefix}quick`",
        f"`{prefix}language`",
        f"`{prefix}add`", 
        f"`{prefix}remove`", 
        f"`{prefix}list`", 
        f"`{prefix}set`",
        f"`{prefix}update_price`", 
        f"`{prefix}balance_of`",
        f"`{prefix}update_cash`", 
        f"`{prefix}give_unique`",
        f"`{prefix}mod_role`", 
        f"`{prefix}log`", 
        f"`{prefix}time_zone`", 
        f"`{prefix}zones`",
        f"`{prefix}work_timer`",
        f"`{prefix}salary`",
        f"`{prefix}uniq_timer`",
        f"`{prefix}settings`",
        f"`{prefix}reset`"      
    ]
    ryad = "{-12; -11; ...; 11; 12}"
    global bot_guilds
    global help_menu
    help_menu = {
        0 : {
            "guide" : f"`{prefix}guide` shows guide about bot's economic system",
            
            "quick" : f"`{prefix}quick` starts quick setup of all bot's settings",

            "set" : f"`{prefix}set` `role` `quantity` - sets the quantity of selected role for selling in store. If quantity <= 0, then role will be removed from store. If \
              role not in the list of roles available for the purchase/sale, add it via the `{prefix}add` command\n\n**Example:**\n**`{prefix}set`** **`972494065088200745`** \
              **`5`** sets 5 roles with id 972494065088200745 (you can use mention with @ instead of id) selling in the store",

            "update_cash" : f"`{prefix}update_cash` `member` `value` sets cash of the member **equal** to selected value. \n\n**Example:**\n**`{prefix}update_cash`** \
              **`931273285268832326`** **`100`** will set user's cash **equal** to 100 {currency} (you can mention user with @ instead of him id)",

            "add" : f"`{prefix}add` `role` `price` `type_of_role` `salary (for unique roles)` adds role to the list of roles available for the purchase/sale.\
              Types of role:\n**`0`** is for unique, which has salary;\n**`1`** is for common, has quantity in the store;\n**`2`** is for infinite (can't run out in the store).\
              \nMore info via **`{prefix}guide`**\n\n**Example:**\n**`{prefix}add`** **`972494065088200745`** **`100`** **`0`** **`10`** adds role with id 972494065088200745 \
              (you can use mention with @ instead of id) to the list, it costs 100 {currency}, unique and brigns it's owner 10 {currency} one per every unique's roles cooldown \
              (see **`{prefix}help_m`** **`uniq_timer`**)",

            "remove" : f"`{prefix}remove` `role` - removes role from list of available for the purchase/sale. Also removes this role from the store. **All information about \
              the role will be lost!**\n\n**Example:**\n**`{prefix}remove`** **`972494065088200745`** will remove role with id 972494065088200745 (you can use mention with \
              @ instead of id) from list of roles available for the purchase/sale on the server, also all information about the role will be deleted",

            "update_price" : f"`{prefix}update_price` `role` `price` changes role's price and makes it **equal** to the selected price\n\n**Example:**\n**`{prefix}update_price`** \
              **`972494065088200745`** **`100`** sets price of role with id 972494065088200745 (you can use mention with @ instead of id) **equal** to 100 {currency}",

            "list" : f"`{prefix}list` - shows the list of roles available for the purchase/sale",

            "give_unique" : f"`{prefix}give_unique` `member` `role` adds unique role to the balance of member so he could start getting money from this role (also role can \
              be added if user calls command `/balance`)\n\n**Example:**\n**`{prefix}give_unique`** **`931273285268832326`** **`972494065088200745`** will add role with id \
              972494065088200745 (you can use mention with @ instead of id) to the balance of user with id 931273285268832326 (you can use mention with @ instead of id) so \
              he could start getting money from that role",

            "mod_role" : f"`{prefix}mod_role` `role` gives permissions to use commands from `{prefix}help_m` for the selected role. Server can only have one role selected for \
              this\n\n**Example:**\n**`{prefix}mod_role`** **`972494065088200745`** will select role with id 972494065088200745 (you can use mention with @ instead of id) as \
              economic mod role, so users with this role will be able to use commands from `{prefix}help_m`",
            
            "log" : f"`{prefix}log` `text_channel` selects log channel for economic operations\n\n**Example:**\n**`{prefix}log`** **`863462268934422540`** will select **text** \
              channel with id 863462268934422540 (you can use mention with # instead of id) as log channel",

            "language" : f"`{prefix}language` `lang` selects language for interface. Can be **`Eng`** (no matter Eng, eng, eNg etc.) for English and **`Rus`** (no matter Rus, \
              rus, rUs etc.) for Russian.\n\n**Example:**\n**`{prefix}language`** **`eng`** will select English language for bot interface",

            "time_zone" : f"`{prefix}time_zone` `name_of_time_zone_from_{prefix}zones or \nhour_difference_with_'-'_if_needed` selects **`UTC`**±**`X`**, **`X`** Є {ryad}, \
              format for the server. \n\n**Example:**\n**`{prefix}time_zone`** **`EDT`** will set time zone of Eastern Daylight Time UTC-4, **`{prefix}time_zone`** **`-7`** \
              will set time zone UTC-7",

            "zones" : f"`{prefix}zones` shows available pre-named time zones",

            "work_timer" : f"`{prefix}work_timer` `time_in_seconds` sets cooldown for command `/work`\n\n**Example:**\n**`{prefix}work_timer`** **`10800`** will set 3 hours \
              cooldown (10800 seconds = 3 hours) for command `/work`",

            "salary" : f"`{prefix}salary` `left_border` `right_border` sets borders for amount of money gained from command `/work`. This amount will be random integer number \
              Є [left; right]. Both are integer non-negative numbers, right one must be at least as large as the left\n\n**Example:**\n**`{prefix}salary`** **`10`** \
              **`100`** changes amount of cash gained from `/work`, and this amount will be random integer from 10 to 100 (amount Є [10; 100])",

            "uniq_timer" : f"`{prefix}uniq_timer` `time_in_seconds` sets cooldown for accruing money from unique roles (type of roles - 0).\n\n**Example:**\n\
              **`{prefix}uniq_timer`** **`10800`** will set 3 hours cooldown (10800 seconds = 3 hours)",

            "settings" : f"`{prefix}settings` shows menu with current bot's settings",

            "reset" : f"`{prefix}reset` resets current bot's settings",

            "balance_of" : f"`{prefix}balance_of` `member` shows balance of the selected member\n\n**Пример:**\n**`{prefix}balance_of`** **`931273285268832326`** will show balance \
              of user with id 931273285268832326 (you can use mention with @ instead of id)"

        },
        1 : {
            "guide" : f"`{prefix}guide` показывает гайд об экономической системе бота",

            "quick" : f"`{prefix}quick` начинает быструю настройку параметров бота",

            "set" : f"`{prefix}set` `роль` `количество` устанавливает количество продаваемых в магазине ролей. Если количество <= 0, то роль будет убрана из магазина. Если роли \
              нет в списке ролей, доступных для покупки/продажи на сервере , добавьте её при помощи команды `{prefix}add`. Для количества бесконечных ролей можно указать любое \
              целое число.\n\n**Пример:**\n**`{prefix}set`** **`972494065088200745`** **`5`** сделает так, что в магазине будут продаваться 5 ролей с id 972494065088200745 \
              (Вы можете упомянуть роль при помощи @ вместо id)",

            "update_cash" : f"`{prefix}update_cash` `участник` `сумма` изменяет баланс учатсника и делает его **равным** указанной сумме.\
              \n\n**Пример:**\n**`{prefix}update_cash`** **`931273285268832326`** **`100`** сделает баланс пользователя с id 931273285268832326 (Вы можете упомянуть пользователя при \
              помощи @ вместо id) **равным** 100 {currency}",

            "add" : f"`{prefix}add` `роль` `цена` `тип_роли` `зарплата (для уникальных ролей)` добавляет роль в список ролей, доступных для покупки/продажи на сервере. \
              Тип роли:\n**`0`**, если уникальная, т.е. имеющая пассивный заработок;\n**`1`**, если обычная, то есть конечная;\n**`2`**, если бесконечная (не может закончиться \
              в магазине)\nПодробнее - **`{prefix}guide`**\n\n**Пример:**\n**`{prefix}add`** **`972494065088200745`** **`100`** **`0`** **`10`** добавит роль с id \
              972494065088200745 (Вы можете упомянуть роль при помощи @ вместо id) в список, она будет уникальной, будет стоить 100 {currency} и приносить своему владельцу \
              10 {currency} один раз за время кулдауна (см. **`{prefix}help_m`** **`uniq_timer`**)",

            "remove" : f"`{prefix}remove` `роль` - убирает роль из списка ролей, доступных для покупки/продажи на сервере. Также удаляет эту роль из магазина. **Вся информация о роли \
              будет потеряна!**\n\n**Пример:**\n**`{prefix}remove`** **`972494065088200745`** удалит роль с id 972494065088200745 (Вы можете упомянуть роль при помощи @ вместо id) из \
              списка ролей, доступных для покупки/продажи на сервере, и из магазина, а также удалит информацию о роли (её цена, тип и заработок)",

            "update_price" : f"`{prefix}update_price` `роль` `цена` изменяет цену роли и делает её **равной** указанной цене\n\n**Пример:**\n**`{prefix}update_price`** \
              **`972494065088200745`** **`100`** сделает цену роли с id 972494065088200745 (Вы можете упомянуть роль при помощи @ вместо id) **равной** 100 {currency}",

            "list" : f"`{prefix}list` показывет список ролей, доступных для покупки/продажи на сервере",

            "give_unique" : f"`{prefix}give_unique` `участник` `роль`- добавляет уникальную роль на личный баланс пользователя, чтобы он начал получать пассивный заработок \
              (также это можно сделать, если пользователь вызовет команду `/balance`)\n\n**Пример:**\n**`{prefix}give_unique`** **`931273285268832326`** **`972494065088200745`** запишет \
              роль c id 972494065088200745 (Вы можете упомянуть роль при помощи @ вместо id) на баланс пользователя с id 931273285268832326 (Вы можете упомянуть пользователя при помощи @ вместо id), \
              чтобы он смог получать пассивный заработок с этой роли",

            "mod_role" : f"`{prefix}mod_role` `роль` выбирает роль в качестве роли модератора экономики для доступа к командам из `{prefix}help_m`. На сервере может быть только \
              одна такая роль.\n\n**Пример:**\n**`{prefix}mod_role`** **`972494065088200745`** выберет роль с id 972494065088200745 (Вы можете упомянуть роль при помощи @ вместо id) \
              в качестве роли модератора экономики. Юзеры с этой ролью смогу использовать команды из списка команды `{prefix}help_m` и управлять настройками бота",

            "log" : f"`{prefix}log` `текстовый_канал` устанавливает выбранный для хранения логов об операциях\n\n**Пример:**\n**`{prefix}log`** **`863462268934422540`** установит \
              канал с id 863462268934422540 (Вы можете упомянуть канал при помощи #, а не id) в качестве канала для логов бота",

            "language" : f"`{prefix}language` `язык` устанавливает выбранный язык в качестве языка интерфейса. Доступны: **`Eng`** (регист не важен) - для английского и **`Rus`** \
              (регистр не важен) - для русского.\n\n**Пример:**\n**`{prefix}language`** **`rus`** установит русский язык для интерфейса бота",

            "time_zone" : f"`{prefix}time_zone` `имя_часового_пояса_из_списка или часовой_сдвиг_от_UTC_со_знаком_'-'_при_необходимости` устанавливает формат времени **`UTC`**±**`X`**, \
              **`X`** Є {ryad}, для сервера. \n\n**Пример:**\n**`{prefix}time_zone`** **`YAKT`** установит часовой пояс Якутска UTC+9, а **`{prefix}time_zone`** **`-7`** установит \
              часовой пояс UTC-7",

            "zones" : f"`{prefix}zones` показывет доступные именные часовые пояса",

            "work_time" : f"`{prefix}work_time` `время_в_секундах` устанавливает кулдаун для использования команды `/work`\n\n**Пример:**\n**`{prefix}work_timer`** **`10800`** \
              установит кулдаун, равный 3 часам (10800 секунд = 3 часа), для команды `/work`",

            "salary" : f"`{prefix}salary` `левая_граница` `правая_граница` устанавливает количество денег, получаемое после использования команды /work. Это количество будет целым \
              числом Є [левая_граница; правая_граница]. Оба числа должны быть целыми неотрицательными числами, правая граница должна быть не меньше левой.\n\n**Пример:**\n\
              **`{prefix}salary`** **`10`** **`100`** изменяет заработок, получаемый после использования команды `/work`, этот заработок будет рандомным целым числом от 10 до 100 (заработок Є [10; 100])",
            
            "uniq_timer" : f"`{prefix}uniq_timer` `время_в_секундах` устанавливает перерыв между начислением денег участникам с уникальными ролями (тип ролей - 0).\n\n**Пример:**\n\
              **`{prefix}uniq_timer`** **`10800`** установит перерыв, равный 3 часам (10800 секунд = 3 часа)",

            "settings" : f"`{prefix}settings` вызывает меню, в котором отображены текущие настройки бота",
            
            "reset" : f"`{prefix}reset` сбрасывает текущие настройки бота",

            "balance_of" : f"`{prefix}balance_of` `участник` показывает баланс выбранного участника\n\n**Пример:**\n**`{prefix}balance_of`** **`931273285268832326`** покаже баланс \
              пользователя с id 931273285268832326 (Вы можете упомянуть пользователя при помощи @ вместо id)"

        }
    }
    self.currency = currency
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
            22 : '**`Please, wait before reusing this command.`**',
            23 : "**Sorry, but you don't have enough permissions for using this comamnd.**",
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
            46 : "Balance of the member:"
            
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
            46 : "Баланс пользователя:"
        }
    }
    global zones
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
    global zone_text
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
    global set_text
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
    global questions
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
    global guide
    guide = {
        0 : {
            0 : "The guide",
            1 : "The basis of trade",
            2 : f"In order to make role able to be bought and sold on the server you should add it to the list of roles, available for the purchase/sale via command \
              **`{prefix}add`** \n(more info via **`{prefix}help_m`** **`add`**)",
            3 : "List of roles, available for the purchase/sale on the server",
            4 : f"To see this list you should use command **`{prefix}list`**",
            5 : "Bot devides roles on three types:",
            6 : "0, 1 and 2",
            7 : "Type 0",
            8 : '"Unique" ' + f"roles, that are not stacking in the store (are shown as different items in the store) and have salary: once per evety cooldown time \
              (more info via \n**`{prefix}help_m`** **`uniq_timer`**) members that have this role on their balance will gain money (salary) that has been selected by \
              command **`{prefix}add`**",
            9 : "Type 1",
            10 : '"Common" ' + "roles that are stacking in the store (are shown as one item with quantity). Don't have salary",
            11 : "Type 2",
            12 : '"Infinite" ' + f"roles that can't run out in the store (you can buy them endless times), can be added and removed to/from the store via command \
              **`{prefix}set`** (more info via **`{prefix}help_m`** **`set`**). Don't have salary"
        },
        1 : {
            0 : "Гайд",
            1 : "Базис торговли",
            2 : f"Чтобы роль можно было покупать и продавать на сервере, а также она могла приносить заработок, нужно добавить её в список ролей, \
              доступных для покупки/продажи на сервере при помощи команды **`{prefix}add`** (см. **`{prefix}help_m`** **`add`**)",
            3 : "Список ролей, доступных для покупки/продажи на сервере",
            4 : f"Посмотреть список добавленных ролей можно при помощи команды **`{prefix}list`**",
            5 : "Бот делит роли на 3 типа:",
            6 : "0, 1 и 2",
            7 : "Тип 0",
            8 : '"Уникальные" ' + f"роли, которые не стакаются в магазине (т.е. отображаются как отдельные товары), а также имеют пассивный заработок: раз в \
              некоторое установленно время (см. **`{prefix}help_m`**  **`uniq_timer`**) участники, на балансе которых находится эта роль, получают заработок, \
                установленный для каждой роли при её добавлении (см. **`{prefix}help_m`** **`add`**)",
            9 : "Тип 1",
            10 : '"Обычные" ' + "роли, которые стакаются в магазине (т.е. отображаются как один товар с указанным количеством). Не имеют пассивного заработка",
            11 : "Тип 2",
            12 : '"Бесконечные" ' + f"роли, которые не заканчиваются в магазине (т.е. их можно купить бесконечное количество раз), добавляются и убираются в \
              магазин при помощи команды **`{prefix}set`** (см. **`{prefix}help_m`** **`set`**). Не имеют пассивного заработка"
        }
    }

  def mod_role_set(self, ctx: commands.Context):
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
          with closing(base.cursor()) as cur:
              r = cur.execute("SELECT value FROM server_info WHERE settings = 'mod_role'").fetchone()
              if r == None or r[0] == 0:
                  return 0
              return 1

  def lang(self, ctx: commands.Context):
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
          with closing(base.cursor()) as cur:
              return cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]

  def needed_role(ctx: commands.Context):
    
      if any(role.permissions.administrator or role.permissions.manage_guild for role in ctx.author.roles) or ctx.guild.owner == ctx.author:
          return 1

      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
          with closing(base.cursor()) as cur:
              mod_id = cur.execute("SELECT value FROM server_info WHERE settings = 'mod_role'").fetchone()
              if mod_id != None and mod_id[0] != 0:
                  return any(role.id == mod_id[0] for role in ctx.author.roles)
              return 0
          
  def check(self, base: sqlite3.Connection, cur: sqlite3.Cursor, memb_id: int):
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

  async def insert_uniq(self, base: sqlite3.Connection, cur: sqlite3.Cursor, nums: int, role_id: int, outer: list, price: int, time_now: int, ctx, lng: int):
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
  async def on_guild_join(self, guild: nextcord.Guild):
      if not os.path.exists(f'{path}bases_{guild.id}'):
          try:
              os.mkdir(f'{path}bases_{guild.id}/')
              bot_guilds.append(guild.id)
          except Exception as E:
              with open("d.log", "a+", encoding="utf-8") as f:
                  f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [{guild.id}] [{str(E)}]\n")
                  f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [{guild.id}] [{guild.name}] [{str(E)}]\n")
      else:
          bot_guilds.append(guild.id)

      with closing(sqlite3.connect(f'{path}bases_{guild.id}/{guild.id}_store.db')) as base:
          with closing(base.cursor()) as cur:
              cur.execute('CREATE TABLE IF NOT EXISTS users(memb_id INTEGER PRIMARY KEY, money INTEGER, owned_roles TEXT, work_date INTEGER)')
              base.commit()
              cur.execute('CREATE TABLE IF NOT EXISTS server_roles(role_id INTEGER PRIMARY KEY, price INTEGER, special INTEGER)')
              base.commit()
              cur.execute('CREATE TABLE IF NOT EXISTS outer_store(item_id INTEGER PRIMARY KEY, role_id INTEGER, quantity INTEGER, price INTEGER, last_date INTEGER, special INTEGER)')
              base.commit()
              cur.execute('CREATE TABLE IF NOT EXISTS money_roles(role_id INTEGER NOT NULL PRIMARY KEY, members TEXT, salary INTEGER NOT NULL, last_time INTEGER)')
              base.commit()
              cur.execute("CREATE TABLE IF NOT EXISTS server_info(settings TEXT PRIMARY KEY, value INTEGER)")
              base.commit()
              
              if cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone() == None:
                  cur.execute("INSERT INTO server_info(settings, value) VALUES('lang', 0)")
                  base.commit()
              
              if cur.execute("SELECT value FROM server_info WHERE settings = 'log_channel'").fetchone() == None:
                  cur.execute("INSERT INTO server_info(settings, value) VALUES('log_channel', 0)")
                  base.commit()

              if cur.execute("SELECT value FROM server_info WHERE settings = 'error_log'").fetchone() == None:
                  cur.execute("INSERT INTO server_info(settings, value) VALUES('error_log', 0)")
                  base.commit()

              if cur.execute("SELECT value FROM server_info WHERE settings = 'mod_role'").fetchone() == None:
                  cur.execute("INSERT INTO server_info(settings, value) VALUES('mod_role', 0)")
                  base.commit()
              
              if cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone() == None:
                  cur.execute("INSERT INTO server_info(settings, value) VALUES('tz', 0)")
                  base.commit()

              if cur.execute("SELECT value FROM server_info WHERE settings = 'time_r'").fetchone() == None:
                  cur.execute("INSERT INTO server_info(settings, value) VALUES('time_r', 14400)")
                  base.commit()
              
              if cur.execute("SELECT value FROM server_info WHERE settings = 'sal_l'").fetchone() == None:
                  cur.execute("INSERT INTO server_info(settings, value) VALUES('sal_l', 1)")
                  base.commit()
              
              if cur.execute("SELECT value FROM server_info WHERE settings = 'sal_r'").fetchone() == None:
                  cur.execute("INSERT INTO server_info(settings, value) VALUES('sal_r', 250)")
                  base.commit()

              if cur.execute("SELECT value FROM server_info WHERE settings = 'uniq_timer'").fetchone() == None:
                  cur.execute("INSERT INTO server_info(settings, value) VALUES('uniq_timer', 14400)")
                  base.commit()
      with open("guild.log", "a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [guild_join] [{guild.id}]\n")
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [guild_join] [{guild.name}] [{guild.id}]\n")

  @commands.Cog.listener()
  async def on_guild_remove(self, guild: nextcord.Guild):
    bot_guilds.remove(guild.id)
    with open("guild.log", "a+", encoding="utf-8") as f:
        f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [guild_remove] [{guild.id}]\n")
        f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [guild_remove] [{guild.name}] [{guild.id}]\n")

  @commands.Cog.listener()
  async def on_ready(self):
      await self.passive()


  async def passive(self):
    while True:
      for g in bot_guilds: 
        with closing(sqlite3.connect(f'{path}bases_{g}/{g}_store.db')) as base:
          with closing(base.cursor()) as cur:
            r = cur.execute("SELECT * FROM money_roles").fetchall()
            if r != None:
              for role, members, salary, last_time in r:
                #print(g, role, members, salary, last_time)
                flag = 0
                if last_time == 0 or last_time == None:
                  flag = 1
                else:
                  #lasted_time = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") + \
                  #    timedelta(hours=3) - datetime.strptime(last_time, '%S/%M/%H/%d/%m/%Y')
                  #if lasted_time >= timedelta(hours=4):
                  #    flag = 1
                  if last_time - int(time()) >= 14400:
                    flag = 1
                if flag:
                  #cur.execute("UPDATE money_roles SET last_time = ? WHERE role_id = ?", (datetime.utcnow().strftime('%S/%M/%H/%d/%m/%Y'), role))
                  cur.execute("UPDATE money_roles SET last_time = ? WHERE role_id = ?", (int(time()), role))
                  base.commit()
                  for member in members.split('#'):
                    if member != "":
                      member = int(member)
                      self.check(base=base, cur=cur, memb_id=member)
                      #print(user)
                      cur.execute("UPDATE users SET money = money + ? WHERE memb_id = ?", (salary, member))
                      base.commit()

        await asyncio.sleep(0.5)

      await asyncio.sleep(20)
  
  
  @commands.command(aliases = ["guide"])
  @commands.check(needed_role)
  async def _guide(self, ctx: commands.Context):
      lng = self.lang(ctx=ctx)
      emb = Embed(title=guide[lng][0])
      for i in range(1, 12, 2):
          emb.add_field(name=guide[lng][i], value=guide[lng][i+1], inline=False)
      await ctx.reply(embed=emb, mention_author=False)
  
  
  @commands.command(aliases = ["help_m"])
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

      await ctx.reply(embed=emb, mention_author=False)

  """ @_help_m.error
  async def _help_m_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.CommandInvokeError):
        lng = self.lang(ctx=ctx) """
      

  @commands.command(hidden=True, aliases=['set'])
  @commands.check(needed_role)
  async def _set(self, ctx: commands.Context, role: nextcord.Role, nums: int):
    with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
  async def _update_cash(self, ctx: commands.Context, member: nextcord.Member, value: int):
    with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
  async def _add(self, ctx: commands.Context, role: nextcord.Role, price: int, is_special: int, salary: int = None):
    lng = self.lang(ctx=ctx)
    if not is_special in [0, 1, 2]:
        await ctx.reply(embed=Embed(title=text[lng][404], description=text[lng][8], colour=Colour.red()), mention_author=False)
        return
    with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
  async def _remove(self, ctx: commands.Context, role: nextcord.Role):
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
  async def _update_price(self, ctx: commands.Context, role: nextcord.Role, price: int):
    with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
    with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
        with closing(base.cursor()) as cur:
          lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
          roles = cur.execute('SELECT * FROM server_roles').fetchall()
          descr = []
          for role in roles:
            descr.append(f"<@&{role[0]}> - {role[0]} - {role[1]} - {role[2]}")
          emb = Embed(title=text[lng][15], description="\n".join(descr))
          await ctx.reply(embed=emb, mention_author=False)


  @commands.command(hidden=True, aliases=['give_unique'])
  @commands.check(needed_role)
  async def _give_unique(self, ctx: commands.Context, member: nextcord.Member, role: nextcord.Role):
    with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
                with open("d.log", "a+", encoding="utf-8") as f:
                    f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [{ctx.guild.id}] [{str(E)}]\n")
                    f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [{ctx.guild.id}] [{ctx.guild.name}] [{str(E)}]\n")

          await ctx.reply(content=f"{text[lng][0]} {role} {text[lng][17]} {member}", mention_author=False)

    
  @commands.command(hidden=True, aliases=["mod_role"])
  @commands.check(needed_role)
  async def _mod_role(self, ctx: commands.Context, role: nextcord.Role):
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
          with closing(base.cursor()) as cur:
              lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
              cur.execute("UPDATE server_info SET value = ? WHERE settings = 'mod_role'", (role.id,))
              base.commit()
              await ctx.reply(f"**`{text[lng][0]}`** {role.name} {text[lng][25]}", mention_author=False)


  @commands.command(hidden=True, aliases=["log"])
  @commands.check(needed_role)
  async def _log(self, ctx: commands.Context, channel: nextcord.TextChannel):
      with closing(sqlite3.connect(f'{path}bases_{ctx. guild.id}/{ctx.guild.id}_store.db')) as base:
          with closing(base.cursor()) as cur:
              lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
              cur.execute("UPDATE server_info SET value = ? WHERE settings = 'log_channel'", (channel.id,))
              base.commit()
              await ctx.reply(f"{channel.mention} {text[lng][26]}", mention_author=False)
  

  @commands.command(hidden=True, aliases=["language"])
  @commands.check(needed_role)
  async def _language(self, ctx: commands.Context, language: str):
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
          with closing(base.cursor()) as cur:
              if language.lower() == "eng":
                  cur.execute("UPDATE server_info SET value = ? WHERE settings = 'lang'", (0,))
                  lng = 0
              elif language.lower() == "rus":
                  cur.execute("UPDATE server_info SET value = ? WHERE settings = 'lang'", (1,))
                  lng = 1
              else:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                emb = Embed(
                    title=text[lng][28],
                    description="\n".join([text[lng][29], text[lng][30]]), 
                    colour=Colour.red(),
                )
                await ctx.reply(embed=emb, mention_author=False)
                return
              base.commit()
              await ctx.reply(text[lng][27], mention_author=False)


  @commands.command(hidden=True, aliases=["time_zone", "tz"])
  @commands.check(needed_role)
  async def _time_zone(self, ctx: commands.Context, tz: str):
      tz = tz.upper()
      if not tz in zones:
          lng = self.lang(ctx=ctx)
          emb = Embed(colour=Colour.red(), title=text[lng][404], description=text[lng][31])
          await ctx.reply(embed=emb, mention_author=False)
          return
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
          with closing(base.cursor()) as cur:
              lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
              tz = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]
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
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
          with closing(base.cursor()) as cur:
              sets = cur.execute("SELECT * FROM server_info").fetchall()
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
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
                      message = await self.bot.wait_for(event="message", check= lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=20.0)
                  except asyncio.TimeoutError:
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
  async def _balance_of(self, ctx: commands.Context, member: nextcord.Member):
      with closing(sqlite3.connect(f'{path}bases_{ctx.guild.id}/{ctx.guild.id}_store.db')) as base:
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
                    f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [{ctx.guild.id}] [{str(error)}]\n")
                    f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [{ctx.guild.id}] [{ctx.guild.name}] [{str(error)}]\n")
                return
        await ctx.reply(embed=emb, mention_author=False)
  
def setup(bot: commands.Bot, **kwargs):
  bot.add_cog(mod_commands(bot, **kwargs))
import asyncio, os
from contextlib import closing
import sqlite3, nextcord
from datetime import datetime
from time import time
from nextcord.ext import commands
from nextcord.ext.commands import CheckFailure
from nextcord import Embed, Colour

class mod_commands(commands.Cog):
  def __init__(self, bot: commands.Bot, prefix: str, in_row: int, currency: str):
    self.bot = bot
    self.prefix = prefix
    self.cmds_list = [
        f"`{prefix}set`",
        f"`{prefix}update_cash`", 
        f"`{prefix}add`", 
        f"`{prefix}remove`", 
        f"`{prefix}update_price`", 
        f"`{prefix}list`", 
        f"`{prefix}give_unique`",
        f"`{prefix}mod_role`", 
        f"`{prefix}log`", 
        f"`{prefix}language`", 
        f"`{prefix}time_zone`", 
        f"`{prefix}zones`"
    ]
    ryad = "{-12; -11; ...; 11; 12}"
    self.help_menu = {
        0 : {
            "set" : f"`{prefix}set` `<role>` `<quantity>` - sets the quantity of selected role for selling in shop. If role not in the list of roles available for buying/selling, add it via the `{prefix}add` command",
            "update_cash" : f"`{prefix}update_cash` `<member>` `<value>` sets cash of the member **equal** to selected value",
            "add" : f"`{prefix}add` `<role>` `<price>` `<type_of_role>` `<salary (for unique roles)>` adds role to the list of roles available for buying/selling. Types of role: 0 is for unique, which has salary; 1 is for common, has quantity in the shop; 2 is for infinite (can't run out in the shop)",
            "remove" : f"`{prefix}remove` `<role>` - removes role from list of available for buying/selling. Also removes this role from the shop. **All information about the role will be lost!**",
            "update_price" : f"`{prefix}update_price` `<role>` `<price>` changes role's price and makes it equal to the selected price",
            "list" : f"`{prefix}list` - shows the list of roles avaailable for buying/selling",
            "give_unique" : f"`{prefix}give_unique` `<member>` `<role>` adds unique role to the balance of member so he could start getting money (also role can be added if user calls command `/balance`)",
            "mod_role" : f"`{prefix}mod_role` `<role>` gives role permissions to use commands from `{prefix}help_mod`. Server can only have one role selected for this",
            "log" : f"`{prefix}log` `<text_channel>` selects log channel for economic operations",
            "language" : f"`{prefix}language` `<lang>` selects language for interface. Can be **`Eng`** (no matter Eng, eng, eNg etc.) for English and **`Rus`** (no matter Rus, rus, rUs etc.) for Russian",
            "time_zone" : f"`{prefix}time_zone` `<name_of_time_zone_from_{prefix}zones or \nhour_difference_with_'-'_if_needed>` selects **`UTC`**±**`X`**, **`X`** Є {ryad}, format for the server",
            "zones" : f"`{prefix}zones` shows available pre-named time zones"
        },
        1 : {
            "set" : f"`{prefix}set` `<роль>` `<количество>` устанавливает количество продаваемых в магазине ролей. Если роли нет в списке доступных для продажи на сервере ролей, добавьте её при помощи команды `{prefix}add`. Для количества бесконечных ролей можно указать любое целое число",
            "update_cash" : f"`{prefix}update_cash` `<участник>` `<сумма>` изменяет баланс учатсника и делает его **равным** указанной сумме",
            "add" : f"`{prefix}add` `<роль>` `<цена>` `<тип_роли>` `<зарплата (для уникальных ролей)>` добавляет роль в список разрешённых для продажи на сервере ролей. Тип роли: 0, если уникальная, т.е. имеющая пассивный заработок; 1, если обычная, то есть конечная; 2, если бесконечная (не может закончиться в магазине)",
            "remove" : f"`{prefix}remove` `<роль>` - убирает роль из списка разрешённых для продажи на сервере ролей. Также удаляет эту роль из магазина. **Вся информация о роли будет потеряна!**",
            "update_price" : f"`{prefix}update_price` `<роль>` `<цена>` изменяет цену роли и делает её **равной** указанной цене",
            "list" : f"`{prefix}list` показывет список ролей, доступных для продажи на сервере",
            "give_unique" : f"`{prefix}give_unique` `<участник>` `<роль>`- добавляет уникальную роль на личный баланс пользователя, чтобы он начал получать пассивный заработок (также это можно сделать, если пользователь вызовет команду `/balance`)",
            "mod_role" : f"`{prefix}mod_role` `<роль>` выбирает роль в качестве роли модератора экономики для доступа к командам из `{prefix}help_mod`. На сервере может быть только одна такая роль",
            "log" : f"`{prefix}log` `<текстовый_канал>` устанавливает выбранный для хранения логов об операциях",
            "language" : f"`{prefix}language` `<язык>` устанавливает выбранный язык в качестве языка интерфейса. Доступны: **`Eng`** (регист не важен) - для английского и **`Rus`** (регистр не важен) - для русского",
            "time_zone" : f"`{prefix}time_zone` `<имя_часового_пояса_из_списка или часовой_сдвиг_от_UTC_со_знаком_'-'_при_необходимости>` устанавливает формат времени **`UTC`**±**`X`**, **`X`** Є {ryad}, для сервера",
            "zones" : f"`{prefix}zones` показывет доступные именные часовые пояса"
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
            5 : f'Please, use command like `{prefix}help_mod` or\n`{prefix}help_mod <name_of_the_command>`',
            6 : 'Please, select command from list of command',
            7 : 'Error: this role is unavailable for buying/selling on the server. Change it via the command',
            8 : 'Third argument of the command must belong to the segment [0; 2]',
            9 : 'Error: salary must be non-negative integer number',
            10 : 'was added to the list',
            11 : 'Error: you cant change type of the existing role. To do it, you should recreate role.\n**All information about the role will be lost!**',
            12 : 'Role was successfully updated',
            13 : 'has been withdrawn from server shop, not available for buying/selling  and doesnt bring money from now,',
            14 : 'From now the price of the role',
            15 : f'role - id - price - type (look {prefix}help_mod add)',
            16 : 'Error: this role is not unique',
            17 : 'added to the balance of',
            18 : '**`This user was not found on the server.`**',
            19 : f'**`Please, use correct arguments for command. More info via {prefix}help_mod <name_of_the_command>`**',
            20 : '**`This command not found.`**',
            21 : '**`This user was not found.`**',
            22 : '**`Please, wait before reusing this command.`**',
            23 : "**`Sorry, but you don't have enough permissions for using this comamnd.`**",
            24 : f"**`Economic moderation role is not chosen! User with administrator or manage server permission should do it via {prefix}mod_role`**",
            25 : f"**`was set as economic moderation role. Commands from {prefix}help_mod are available for users with this role`**",
            26 : "was set as log channel",
            27 : "**`English language was set as main`**",
            28 : "Please, select language from list:",
            29 : "`Eng` - for English language",
            30 : "`Rus` - for Russian language",
            31 : f"Please, use command in format **`{prefix}time_zone`** **`<name_of_time_zone_from_{prefix}zones or hour_difference_with_'-'_if_needed>`**",
            32 : "Time zone **`UTC{}`** was set on the server",
            33 : "**`This server has time zone UTC",
            34 : "**`List of available named time zones:`**",
            35 : "Time (in seconds) must be integer positive number (without any additional symbols)"
        },
        1 : {
            0 : 'Role',
            1 : 'Команды:',
            2 : '**Для уточнения работы команды напишите**:',
            3 : 'название_команды',
            4 : 'Информация о команде',
            404 : 'Ошибка',
            5 : f'Пожалуйста, укажите команду в формате`{prefix}help_mod` или\n`{prefix}help_mod <название_команды>`',
            6 : 'Пожалуйста, укажите команду из списка команды',
            7 : 'Ошибка: эту роль нельзя продавать и покупать на сервере. Измените это с помощью команды',
            8 : "Третий аргумент команды должен принадлежать отрезку [0; 2]",
            9 : "Ошибка: укажите неотрицательное целое число в качестве зарплаты для этой роли",
            10 : 'добавлена в список',
            11 : 'Ошибка: Вы не можете изменять тип существующе роли. Чтобы сделать это, Вам нужно пересоздать роль.\n**Вся информация о роли будет потеряна!**',
            12 : 'Роль была успешно обновлена',
            13 : 'изъята из обращения на сервере и больше не доступна для продажи/покупки, а также не приносит доход.',
            14 : 'Теперь цена роли',
            15 : f"Роль - id - цена - тип (см. {prefix}help_mod add)",
            16 : "Ошибка: это не уникальная роль",
            17 : 'записана на личный счёт пользователя',
            18 : "**`На сервере не найден такой пользователь`**",
            19 : f"**`Пожалуйста, укажите верные аргументы команды. Больше информации - {prefix}help_mod <название_команды>`**",
            20 : "**`Такая команда не найдена`**",
            21 : "**`Такой пользователь не найден`**",
            22 : "**`Пожалуйста, подождите перед повторным использованием команды`**",
            23 : "**`У Ваc недостаточно прав для использования этой команды`**",
            24 : f"**`Роль модератора экономики не выбрана! Пользователь с правами админитратора или управляющего сервером должен сделать это при помощи {prefix}mod_role`**",
            25 : f"**`установлена в качестве роли модератора экономики. Этой роли доступны команды из списка {prefix}help_mod`**",
            26 : "установлен в качестве канала для логов",
            27 : "**`Русский язык установлен в качестве языка интерфейса`**",
            28 : "Пожалуйста, выберите язык из списка:",
            29 : "`Eng` - для английского языка",
            30 : "`Rus` - для русского языка",
            31 : f"Пожалуйста, укажите команду в формате **`{prefix}time_zone`** **`<имя_пояса_из_списка или часовой_сдвиг_со_знаком_'-'_при необходимости>`**",
            32 : "На сервере был установлен часовой пояс **`UTC{}`**",
            33 : "**`На этом сервере установлен часовой пояс UTC",
            34 : "**`Список именных часовых поясов:`**",
            35 : "Время (в секундах) должно быть целым положительным числом (только число, без дополнительных символов)"
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
  def mod_role_set(self, ctx: commands.Context):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
      with closing(base.cursor()) as cur:
        r = cur.execute("SELECT value FROM server_info WHERE settings = 'mod_role'").fetchone()
        if r == None or r[0] == 0:
          return 0
        return 1

  def lang(self, ctx: commands.Context):
      with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
          with closing(base.cursor()) as cur:
              return cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]

  def needed_role(ctx: commands.Context):
    
      if any(role.permissions.administrator or role.permissions.manage_guild for role in ctx.author.roles) or ctx.guild.owner == ctx.author:
          return 1

      with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
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

  @commands.Cog.listener()
  async def on_guild_join(self, guild: nextcord.Guild):
      if not os.path.exists(f'./bases_{guild.id}'):
          try:
              os.mkdir(f'./bases_{guild.id}/')
          except Exception as e:
              open("report.txt", "a").write(f"\n{datetime.utcnow()}: {str(e)}")

      with closing(sqlite3.connect(f'./bases_{guild.id}/{guild.id}_shop.db')) as base:
          with closing(base.cursor()) as cur:
              cur.execute('CREATE TABLE IF NOT EXISTS users(memb_id INTEGER PRIMARY KEY, money INTEGER, owned_roles TEXT, work_date INTEGER)')
              base.commit()
              cur.execute('CREATE TABLE IF NOT EXISTS server_roles(role_id INTEGER PRIMARY KEY, price INTEGER, special INTEGER)')
              base.commit()
              cur.execute('CREATE TABLE IF NOT EXISTS outer_shop(item_id INTEGER PRIMARY KEY, role_id INTEGER, quantity INTEGER, price INTEGER, last_date INTEGER, special INTEGER)')
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
              


  @commands.Cog.listener()
  async def on_ready(self):
      await self.passive()

  async def passive(self):
    while True:
      for g in self.bot.guilds: 
        with closing(sqlite3.connect(f'./bases_{g.id}/{g.id}_shop.db')) as base:
          with closing(base.cursor()) as cur:
            r = cur.execute("SELECT * FROM money_roles").fetchall()
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
                  
      await asyncio.sleep(20)

  @commands.command(aliases = ["help_mod"])
  @commands.check(needed_role)
  async def _help_mod(self, ctx: commands.Context, *args):
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
      emb.add_field(name=text[lng][2], value = f'\n`{self.prefix}help_mod <{text[lng][3]}>`')

    elif len(args) == 1:
      arg = args[0].replace(self.prefix, '')
      if not arg in self.help_menu[lng]:
          await ctx.reply(
            embed=Embed(
              title=text[lng][404],
              description=f'{text[lng][6]} `{self.prefix}help_mod`',
              colour=Colour.red()
            ),
            mention_author=False
          )
          return

      msg.append(f"{self.help_menu[lng][arg]}")
      emb = Embed(
        colour=Colour.dark_purple(),
        title=text[lng][4],
        description='\n'.join(msg)
      )
    
    else:
      emb = Embed(colour=Colour.red(), title=text[lng][404], description=text[lng][5])

    await ctx.reply(embed=emb, mention_author=False)

  @_help_mod.error
  async def _help_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.CommandInvokeError):
      lng = self.lang(ctx=ctx)
      

  @commands.command(hidden=True, aliases=['set'])
  @commands.check(needed_role)
  async def _set(self, ctx: commands.Context, role: nextcord.Role, nums: int):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
      with closing(base.cursor()) as cur: 
        lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
        role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
        if role_info == None:
            await ctx.reply(content=f"{text[lng][7]} {self.prefix}add", mention_author=False)
            return
        is_special = role_info[2]
        if nums > 0:
          #time_now = (datetime.utcnow()+timedelta(hours=3)).strftime('%S/%M/%H/%d/%m/%Y')
          time_now = int(time())
          if is_special == 0:
            for _ in range(nums):                
              item_ids = [x[0] for x in cur.execute('SELECT item_id FROM outer_shop').fetchall()]
              item_ids.sort()
              free_id = 1
              while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                  free_id += 1
              cur.execute('INSERT INTO outer_shop(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, 1, role_info[1], time_now, 0))
              base.commit()
          elif is_special == 1:
              outer = cur.execute('SELECT * FROM outer_shop WHERE role_id = ?', (role.id,)).fetchone()
              if outer == None:
                  item_ids = [x[0] for x in cur.execute('SELECT item_id FROM outer_shop').fetchall()]
                  item_ids.sort()
                  free_id = 1
                  while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                      free_id += 1
                  cur.execute('INSERT INTO outer_shop(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, nums, role_info[1], time_now, 1))
                  base.commit()            
              else:
                  cur.execute('UPDATE outer_shop SET quantity = ?, last_date = ? WHERE role_id = ?', (nums, time_now, role.id))
                  base.commit()
          elif is_special == 2:
            outer = cur.execute('SELECT * FROM outer_shop WHERE role_id = ?', (role.id,)).fetchone()
            if outer == None:
              item_ids = [x[0] for x in cur.execute('SELECT item_id FROM outer_shop').fetchall()]
              item_ids.sort()
              free_id = 1
              while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                  free_id += 1
              cur.execute('INSERT INTO outer_shop(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, -404, role_info[1], time_now, 2))
              base.commit()      
        else:
          item_id = cur.execute('SELECT item_id FROM outer_shop WHERE role_id = ?', (role.id,)).fetchone()[0]
          cur.execute('DELETE FROM outer_shop WHERE item_id = ?', (item_id,))
          base.commit()

        await ctx.reply(content=f"{nums} role(s) {role.name} was(ere) added to database", mention_author=False)

  @commands.command(hidden=True, aliases=['update_cash'])
  @commands.check(needed_role)
  async def _update(self, ctx: commands.Context, member: nextcord.Member, value: int):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
      with closing(base.cursor()) as cur:
        memb_id = member.id
        self.check(base=base, cur=cur, memb_id=memb_id)
        if value < 0:
          cur.execute('UPDATE users SET money = ? WHERE memb_id = ?', (0, memb_id))
          base.commit()
        else:
          cur.execute('UPDATE users SET money = ? WHERE memb_id = ?', (value, memb_id))
          base.commit()
  
  @commands.command(hidden=True, aliases=['add'])
  @commands.check(needed_role)
  async def _add(self, ctx: commands.Context, role: nextcord.Role, price: int, is_special: int, salary: int = None):
    lng = self.lang(ctx=ctx)
    if not is_special in [0, 1, 2]:
        await ctx.reply(text[lng][8], mention_author=False)
        return
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
        with closing(base.cursor()) as cur:
          rls = cur.execute('SELECT role_id FROM server_roles').fetchall()
          role_ids = [x[0] for x in rls]
          if not role.id in role_ids:
            if is_special == 0:
              if salary == None or salary < 0:
                await ctx.reply(content=text[lng][9], mention_author=False)
                return
              cur.execute("INSERT INTO money_roles(role_id, members, salary, last_time) VALUES(?, ?, ?, ?)", (role.id, "", salary, 0))
              base.commit()
            await ctx.reply(content=f"{role} {text[lng][10]}", mention_author=False)
            cur.execute('INSERT INTO server_roles(role_id, price, special) VALUES(?, ?, ?)', (role.id, price, is_special))
            base.commit()
          else:
            is_special_shop = cur.execute("SELECT special FORM server_roles WHERE role_id = ?", (role.id,)).fetchone()[0]
            if is_special != is_special_shop:
              await ctx.reply(content = text[lng][11], mention_author=False)
            cur.execute("UPDATE server_roles SET price = ? WHERE role_id = ?", (price, role.id))
            base.commit()
            cur.execute("UPDATE money_roles SET salary = ? WHERE role_id = ?", (salary, role.id))
            base.commit()
            await ctx.reply(content = text[lng][12], mention_author=False)
                 
  @commands.command(hidden=True, aliases=['remove'])
  @commands.check(needed_role)
  async def _remove(self, ctx: commands.Context, role: nextcord.Role):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
        with closing(base.cursor()) as cur:
          lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
          cur.execute('DELETE FROM server_roles WHERE role_id = ?', (role.id,))
          base.commit()
          cur.execute('DELETE FROM outer_shop WHERE role_id = ?', (role.id,))
          base.commit()
          cur.execute("DELETE FROM money_roles WHERE role_id = ?", (role.id,))
          base.commit()
          await ctx.reply(content=f"{text[lng][0]} {role} {text[lng][13]}", mention_author=False)

  @commands.command(hidden=True, aliases=['update_price'])
  @commands.check(needed_role)
  async def _update_price(self, ctx: commands.Context, role: nextcord.Role, price: int):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
        with closing(base.cursor()) as cur:
          lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
          is_in = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
          if is_in == None:
            await ctx.reply(f"{text[lng][7]} {self.prefix}add", mention_author=False)
            return
          cur.execute('UPDATE server_roles SET price = ? WHERE role_id = ?', (price, role.id))
          base.commit()
          await ctx.reply(content=f"{text[lng][14]} {role} - {price}{self.currency}", mention_author=False)

  @commands.command(hidden=True, aliases=['list'])
  @commands.check(needed_role)
  async def _list(self, ctx: commands.Context):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
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
  async def _unique(self, ctx: commands.Context, member: nextcord.Member, role: nextcord.Role):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
        with closing(base.cursor()) as cur:
          lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
          memb = self.check(base=base, cur=cur, memb_id=member.id)
          role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
          if role_info == None:
              await ctx.reply(content=f"{text[lng][7]} {self.prefix}add", mention_author=False)
              return
          elif role_info[2] != 0:
            await ctx.reply(content=text[lng][16], mention_author=False)
            return

          try:
            owned_roles = memb[2]
            if not str(role.id) in owned_roles.split('#'):
              owned_roles += f"#{role.id}"                        
            cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', (owned_roles, member.id))
            base.commit()
          except:
            pass

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
          except Exception as e:
            open("report.txt", "a").write(f"{datetime.utcnow()}: {str(e)}\n")

          await ctx.reply(content=f"{text[lng][0]} {role} {text[lng][17]} {member}", mention_author=False)
          
  @commands.command(hidden=True, aliases=["mod_role"])
  @commands.check(needed_role)
  async def _mod_role(self, ctx: commands.Context, role: nextcord.Role):
      with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
          with closing(base.cursor()) as cur:
              lng = cur.execute("SELECT lang FROM server_info").fetchone()[0]
              cur.execute("UPDATE server_info SET mod_role = ?", (role.id,))
              base.commit()
              await ctx.reply(f"**`{text[lng][0]}`** {role.name} {text[lng][25]}", mention_author=False)

  @commands.command(hidden=True, aliases=["log"])
  @commands.check(needed_role)
  async def _log(self, ctx: commands.Context, channel: nextcord.TextChannel):
      with closing(sqlite3.connect(f'./bases_{ctx. guild.id}/{ctx.guild.id}_shop.db')) as base:
          with closing(base.cursor()) as cur:
              lng = cur.execute("SELECT lang FROM server_info").fetchone()[0]
              cur.execute("UPDATE server_info SET log = ?", (channel.id,))
              base.commit()
              await ctx.reply(f"{channel.mention} {text[lng][26]}", mention_author=False)
  
  @commands.command(hidden=True, aliases=["language"])
  @commands.check(needed_role)
  async def _language(self, ctx: commands.Context, language: str):
      with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
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
                    colour=Colour.dark_purple(),
                )
                await ctx.reply(embed=emb, mention_author=False)
                return
              base.commit()
              await ctx.reply(text[lng][27], mention_author=False)

  @commands.command(hidden=True, aliases=["time_zone", "tz"])
  @commands.check(needed_role)
  async def _tz(self, ctx: commands.Context, tz: str):
      tz = tz.upper()
      if not tz in zones:
          lng = self.lang(ctx=ctx)
          await ctx.reply(content=text[lng][31], mention_author=False)
          return
      with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
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
      with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
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
      with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
          with closing(base.cursor()) as cur:
              lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
              if timer <= 0:
                  await ctx.reply(content=text[lng][35], mention_author=False)
                  return
              cur.execute("UPDATE server_info SET value = ? WHERE settings = ?", (timer, 'time_reload'))
              base.commit()


  @commands.Cog.listener()
  async def on_command_error(self, ctx: commands.Context, error):
      lng = self.lang(ctx=ctx)
      if isinstance(error, commands.MemberNotFound):
        await ctx.reply(text[lng][18], mention_author=False)
      elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(text[lng][19], mention_author=False)
      elif isinstance(error, commands.CommandNotFound):
        await ctx.reply(text[lng][20], mention_author=False)
      elif isinstance(error, commands.UserNotFound):
        await ctx.reply(text[lng][21], mention_author=False)
      elif isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(text[lng][22], mention_author=False)
      elif isinstance(error, CheckFailure):
        if not self.mod_role_set(ctx=ctx):
          await ctx.reply(text[lng][24], mention_author=False)
        else:
          await ctx.reply(text[lng][23], mention_author=False)
      else:
        open("report.txt", "a").write(f"{datetime.utcnow()}: {str(error)}\n")
  
def setup(bot: commands.Bot, **kwargs):
  bot.add_cog(mod_commands(bot, **kwargs))
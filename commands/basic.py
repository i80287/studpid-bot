from contextlib import closing
from posixpath import split
import sqlite3, nextcord
from datetime import datetime, timedelta
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions, CheckFailure
from nextcord import Embed, Colour
from sqlalchemy import desc

class basic_commands(commands.Cog):
  def __init__(self, bot: commands.Bot, prefix: str, in_row: int, currency: str):
    self.bot = bot
    self.prefix = prefix
    self.cmds_list = [f'`{prefix}set`', f'`{prefix}update_cash`', f'`{prefix}add`', f'`{self.prefix}remove`', f'`{self.prefix}update_price`', f'`{self.prefix}list`', f'`{self.prefix}update_unique`']
    self.help_menu = {
      'set' : f'`{self.prefix}set` `<роль>` `<количество>` - устанавливает количество продаваемых в магазине ролей. Если роли нет в списке доступных для продажи на сервере ролей, добавьте её командой `{self.prefix}add`. Для количества бесконечных ролей можно указать любое целое число',
      'update_cash' : f'`{self.prefix}update_cash` `<участник>` `<сумма>` - изменяет баланс учатсника и делает его **равным** указанной сумме',
      'add' : f'`{self.prefix}add` `<роль>` `<цена>` `<тип_роли>` - добавляет роль в список разрешённых для продажи на сервере ролей. Тип роли: 0, если уникальная; 1, если обычная, то есть конечная; 2, если бесконечная',
      'remove' : f'`{self.prefix}remove` `<роль>` - убирает роль из списка разрешённых для продажи на сервере ролей. Также удаляет эту роль из магазина',
      'update_price' : f'`{self.prefix}update_price` `<роль>` `<цена>` - изменяет цену роли и делает её **равной** указанной цене',
      'list' : f'`{self.prefix}list` - показывет список ролей, доступных для продажи на сервере',
      'update_unique' : f'`{self.prefix}update_unique` `<участник>` `<роль>`- добавляет уникальную роль на личный баланс пользователя'
    }
    self.currency = currency

  def check(self, base: sqlite3.Connection, cur: sqlite3.Cursor, memb_id: int):
        member = cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()
        if member == None:
            cur.execute('INSERT INTO users(memb_id, money, owned_roles, work_date) VALUES(?, ?, ?, ?)', (memb_id, 0, "", "0"))
            base.commit()
        else:
            if member[1] == None or member[1] < 0:
                cur.execute('UPDATE users SET money = ? WHERE memb_id = ?', (0, memb_id))
                base.commit()
            if member[2] == None:
                cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', ("", memb_id))
                base.commit()
            if member[3] == None:
                cur.execute('UPDATE users SET work_date = ? WHERE memb_id = ?', ("0", memb_id))
                base.commit()
        return cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()

  """ def adding(ctx: commands.Context):
    return 1
    roles = [863463514542309407, 879139230201294868]
    for role in ctx.author.roles:
      if role.id in roles:
        return 1
    return 0 """

  @commands.command(aliases = ["help", "commands"])
  @has_permissions(administrator=True)
  async def _help(self, ctx: commands.Context, *args):
    msg = []

    if len(args) == 0:
      for command in self.cmds_list:
        msg.append(command)
      emb = Embed(
        colour=Colour.dark_purple(),
        title='Команды:',
        description = '\n'.join(msg)
      )
      emb.add_field(name=f'**Для уточнения работы команды напишите**:', value = f'\n`{self.prefix}help название_команды`')

    elif len(args) == 1:
      msg.append(f"{self.help_menu[args[0].replace('>', '')]}")
      emb = Embed(
        colour=Colour.dark_purple(),
        title='Информация о команде:',
        description='\n'.join(msg)
      )
    
    else:
      emb = Embed(color=Colour.red(), title='Ошибка', description=f'Пожалуйста, укажите команду в формате `{self.prefix}help` или\n`{self.prefix}help название_команды`')

    await ctx.reply(embed=emb, mention_author = False)

  @_help.error
  async def _help_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.CommandInvokeError):
      await ctx.reply(
        embed=Embed(
          title='Ошибка',
          description=f'Пожалуйста, укажите команду из списка команды `{self.prefix}help`',
          colour=Colour.red()
        ),
        mention_author=False
      )
      return
    else:
      raise error

  """@commands.command(hidden=True)
  async def load(self, ctx, extension):
      if ctx.author == self.bot.user:
          return
      self.bot.load_extension(f"commands.{extension}", extras={"prefix": self.prefix})
      await ctx.send("cog is loaded")

  @commands.command(hidden=True)
  async def unload(self, ctx, extension):
      if ctx.author == self.bot.user:
          return
      self.bot.unload_extension(f"commands.{extension}")
      await ctx.send("cog is unloaded")

  @commands.command(hidden=True)
  async def reload(self, ctx, extension):
      if ctx.author == self.bot.user:
          return
      self.bot.unload_extension(f"commands.{extension}")
      self.bot.load_extension(f"commands.{extension}", extras={"prefix": self.prefix})
      await ctx.send("cog is loaded")"""

  @commands.command(hidden=True, aliases=['set'])
  #@commands.check(adding)
  @has_permissions(administrator=True)
  async def _set(self, ctx: commands.Context, role: nextcord.Role, nums: int):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
      with closing(base.cursor()) as cur: 

        role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
        if role_info == None:
            await ctx.reply(content=f"Ошибка: эту роль нельзя продавать и покупать на сервере. Измените это с помощью команды {self.prefix}add", mention_author=False)
            return
        is_special = role_info[2]
        if nums > 0:
          time_now = (datetime.utcnow()+timedelta(hours=3)).strftime('%S/%M/%H/%d/%m/%Y')
          if is_special == 0:
            await ctx.reply(content=f"Ошибка: эту роль нельзя покупать на сервере.", mention_author=False)
            return
            """ for _ in range(nums):                
              item_ids = [x[0] for x in cur.execute('SELECT item_id FROM outer_shop').fetchall()]
              item_ids.sort()
              free_id = 1
              while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                  free_id += 1
              cur.execute('INSERT INTO outer_shop(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, 1, role_info[1], time_now, 0))
              base.commit() """
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
  @has_permissions(administrator=True)
  async def _update(self, ctx: commands.Context, member: nextcord.Member, value: int):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
      with closing(base.cursor()) as cur:
        memb_id = member.id
        user = self.check(base=base, cur=cur, memb_id=memb_id)
        if user[1] + value < 0:
          cur.execute('UPDATE users SET money = ? WHERE memb_id = ?', (0, memb_id))
          base.commit()
        else:
          cur.execute('UPDATE users SET money = ? WHERE memb_id = ?', (value, memb_id))
          base.commit()
  
  @commands.command(hidden=True, aliases=['add'])
  @has_permissions(administrator=True)
  async def _add(self, ctx: commands.Context, role: nextcord.Role, price: int, is_special: int):
    if not is_special in [0, 1, 2]:
      await ctx.reply("Третий параметр должен принадлежать отрезку [0, 1, 2]", mention_author=False)
      return
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
        with closing(base.cursor()) as cur:
          #сначала добавляем роль в информацию о ролях сервера
          rls = cur.execute('SELECT role_id FROM server_roles').fetchall()
          role_ids = [x[0] for x in rls]
          if not role.id in role_ids:
            cur.execute('INSERT INTO server_roles(role_id, price, special) VALUES(?, ?, ?)', (role.id, price, is_special))
            base.commit()
            await ctx.reply(content=f"Роль {role} добавлена в список", mention_author=False)
          else:
            await ctx.reply(content=f"Ошибка: эта роль уже есть в списке разрешённых для продажи на сервере ролей", mention_author=False)

  @commands.command(hidden=True, aliases=['remove'])
  @has_permissions(administrator=True)
  async def _remove(self, ctx: commands.Context, role: nextcord.Role):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
        with closing(base.cursor()) as cur:
          cur.execute('DELETE FROM server_roles WHERE role_id = ?', (role.id,))
          base.commit()
          cur.execute('DELETE FROM outer_shop WHERE role_id = ?', (role.id,))
          base.commit()
          await ctx.reply(content=f"Роль {role} изъята из обращения на сервере", mention_author=False)

  @commands.command(hidden=True, aliases=['update_price'])
  @has_permissions(administrator=True)
  async def _update_price(self, ctx: commands.Context, role: nextcord.Role, price: int):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
        with closing(base.cursor()) as cur:
          is_in = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
          if is_in == None:
            await ctx.reply('Этой роли нет в списке разрешённых для продажи на сервере ролей', mention_author=False)
            return
          cur.execute('UPDATE server_roles SET price = ? WHERE role_id = ?', (price, role.id))
          base.commit()
          await ctx.reply(content=f"Цена роли {role} теперь - {price}{self.currency}", mention_author=False)

  @commands.command(hidden=True, aliases=['list'])
  @has_permissions(administrator=True)
  async def _list(self, ctx: commands.Context):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
        with closing(base.cursor()) as cur:
          roles = cur.execute('SELECT * FROM server_roles').fetchall()
          descr = []
          for role in roles:
            descr.append(f"<@&{role[0]}> - {role[0]} - {role[1]} - {role[2]}")
          emb = Embed(title="Роль - id - цена - тип (см. >help add)", description="\n".join(descr))
          await ctx.reply(embed=emb, mention_author=False)

  @commands.command(hidden=True, aliases=['update_unique'])
  @has_permissions(administrator=True)
  async def _unique(self, ctx: commands.Context, member: nextcord.Member, role: nextcord.Role):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
        with closing(base.cursor()) as cur:
          memb = self.check(base=base, cur=cur, memb_id=member.id)
          role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
          if role_info == None:
              await ctx.reply(content=f"Ошибка: эту роль нельзя продавать и покупать на сервере. Измените это с помощью команды {self.prefix}add", mention_author=False)
              return
          elif role_info[2] != 0:
            await ctx.reply(content=f"Ошибка: это не уникальная роль", mention_author=False)
            return
          owned_roles = memb[2]
          if not str(role.id) in owned_roles.split('#'):
            owned_roles += f"#{role.id}"                        
          cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', (owned_roles, member.id))
          base.commit()
          await ctx.reply(content=f"Роль {role} записана на личный счёт пользователя {member}", mention_author=False)
          

  @commands.Cog.listener()
  async def on_command_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MemberNotFound):
      await ctx.reply("На сервере не найден такой пользователь", mention_author = False)
    elif isinstance(error, commands.MissingRequiredArgument):
      await ctx.reply("Пожалуйста, укажите верные аргументы команды", mention_author = False)
    elif isinstance(error, commands.CommandNotFound):
      await ctx.reply("Такая команда не найдена", mention_author=False)
    elif isinstance(error, commands.UserNotFound):
      await ctx.reply('Такой пользователь не найден', mention_author=False)
    elif isinstance(error, commands.CommandOnCooldown):
      await ctx.reply("Пожалуйста, подождите перед повторным использованием команды", mention_author=False)
    elif isinstance(error, CheckFailure):
        await ctx.reply("У Ваc недостаточно прав для использования этой команды", mention_author=False)
    else:
      pass
      raise error
  
def setup(bot: commands.Bot, **kwargs):
  bot.add_cog(basic_commands(bot, **kwargs))
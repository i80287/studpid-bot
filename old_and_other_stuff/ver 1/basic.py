from contextlib import closing
import sqlite3, nextcord
from datetime import datetime, timedelta
from nextcord.ext import commands
from nextcord import Embed, Colour

class basic_commands(commands.Cog):
  def __init__(self, bot: commands.Bot, prefix: str, in_row: int, currency: str):
    self.bot = bot
    self.prefix = prefix
    self.cmds_list = [f'`{prefix}help` aka `{prefix}commands`', f'`{prefix}shop` aka `{prefix}list`', f'`{prefix}buy`', f'`{prefix}sell`', f'`{self.prefix}balance`']
    self.help_menu = {
      'help' : f'`{self.prefix}help` - вызывает меню команд, аналогична `{self.prefix}commands`',
      'commands' : f'`{self.prefix}commands` - вызывает меню команд, аналогична `{self.prefix}help`',
      'shop' : f'`{self.prefix}shop` - вызывает меню с товарами, аналогична `{self.prefix}list`',
      'list' : f'`{self.prefix}list` - вызывает меню с товарами, аналогична `{self.prefix}shop`',
      'buy' : f'`{self.prefix}buy <id>` - вызывает меню покупки выбранной роли в магазине\nПример: `{self.prefix}buy 1` вызывает меню покупки роли, у которой `id` в магазине\nравен `1`',
      'sell' : f'`{self.prefix}sell <role> <price>` - выставляет указанную роль на продажу. Её можно указать через `упомянание` или `id`\nПример: `{self.prefix}sell @example_role 100` выставит роль `@example_role` на продажу за `100` валюты',
      'balance' : f'`{self.prefix}balance` - показывает Ваш баланс'
    }

  def adding(ctx: commands.Context):
    return 1
    roles = [863463514542309407, 879139230201294868]
    for role in ctx.author.roles:
      if role.id in roles:
        return 1
    return 0

  @commands.command(aliases = ["help", "commands"])
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

  @commands.command(hidden=True)
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
      await ctx.send("cog is loaded")

  @commands.command(hidden=True, aliases=['add'])
  @commands.check(adding)
  async def _add(self, ctx: commands.Context, role: nextcord.Role, price: int, nums: int):
    with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
      with closing(base.cursor()) as cur:
        item_ids = [x[0] for x in cur.execute('SELECT item_id FROM shop').fetchall()]
        item_ids.sort()
        free_id = 1
        while(free_id < len(item_ids) and free_id == item_ids[free_id-1]):
            free_id += 1
        if free_id == len(item_ids):
            free_id += 1

        cur.execute('INSERT INTO shop(item_id, role_id, seller_id, price, date) VALUES(?, ?, ?, ?, ?)', (free_id, role.id, (404*100000+nums), price, (datetime.utcnow()+timedelta(hours=3)).strftime('%S/%M/%H/%d/%m/%Y')))
        base.commit()
        
        rls = cur.execute('SELECT roles FROM server_roles').fetchall()
        roles = [x[0] for x in rls]
        if not role.id in roles:
          cur.execute('INSERT INTO server_roles(roles) VALUES(?)', (role.id,))
          base.commit()
        await ctx.reply(content=f"Added {nums} {role.name} to database", mention_author=False)

  @commands.Cog.listener()
  async def on_command_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MemberNotFound):
      await ctx.reply("На сервере не найден такой пользователь", mention_author = False)
    elif isinstance(error, commands.MissingRequiredArgument):
      #await ctx.reply("Пожалуйста, укажите верные аргументы команды", mention_author = False)
      pass
    elif isinstance(error, commands.CommandNotFound):
      print(f"user {ctx.author.name} tried to call {error}")
      await ctx.reply("Такая команда не найдена", mention_author=False)
    elif isinstance(error, commands.UserNotFound):
      await ctx.reply('Такой пользователь не найден', mention_author=False)
    elif isinstance(error, commands.CommandOnCooldown):
      await ctx.reply("Пожалуйста, подождите перед повторным использованием команды", mention_author=False)
    else:
      raise error
      pass
  
def setup(bot: commands.Bot, **kwargs):
  bot.add_cog(basic_commands(bot, **kwargs))
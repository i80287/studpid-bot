import sqlite3, nextcord
from nextcord.ui import Button, View
from nextcord.ext import commands
from nextcord.ext.commands import Context
from nextcord import Embed, Colour, ButtonStyle, Interaction
from contextlib import closing
from datetime import datetime, timedelta
""" 
class Myview_buy(View):

        def __init__(self, timeout, ctx: Context):
            super().__init__(timeout=timeout)
            self.ctx = ctx
            self.value = 0

        @nextcord.ui.button(label='Нет, отменить покупку', style=ButtonStyle.red, emoji="❌")
        async def decl_callback(self, button: Button, interaction: Interaction):
            button.disabled = True
            button1 = [x for x in self.children if x.custom_id == "second"][0]
            button1.disabled=True
            emb = interaction.message.embeds[0]
            emb.description='**`Покупка отмена пользователем`**'
            await interaction.response.edit_message(embed = emb, view=self)
            self.stop()
        
        @nextcord.ui.button(label='Да', style=ButtonStyle.green, emoji="✅", custom_id = "second")
        async def agr_callback(self, button: Button, interaction: Interaction):
            self.value = 1
            self.stop()
            
        async def interaction_check(self, interaction):
            if interaction.user != self.ctx.author:
                await interaction.response.send_message('Вы не можете управлять чужой покупкой', ephemeral=True)
                return False
            return True
            
class Myview_shop(View):
    def __init__(self, timeout: int, rls, ctx: Context, in_row: int):
        super().__init__(timeout=timeout)
        self.rls = rls
        self.ctx = ctx
        self.in_row = in_row
        self.sort_d = 0 #by default - price
        self.sort_grad = 0 #возрастание / убывание, от gradation, 0 - возрастание
    
    def sort_by(self):
        rls = self.rls
        sort_d = self.sort_d
        sort_grad = self.sort_grad
        if sort_d == 0:
            #price
            array = [rr[3] for rr in rls]
        elif sort_d == 1:
            array = [datetime.strptime(rr[4], '%S/%M/%H/%d/%m/%Y') for rr in rls]
            
        for i in range(len(array)-1):
            for j in range(i+1, len(array)):
                if sort_d == 0:
                    if (sort_grad == 0 and array[i] > array[j]) or (sort_grad == 1 and array[i] < array[j]):
                        temp = array[j]
                        array[j] = array[i]
                        array[i] = temp
                        temp = rls[j]
                        rls[j] = rls[i]
                        rls[i] = temp
                    elif array[i] == array[j]:
                        if datetime.strptime(rls[i][4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y') < datetime.strptime(rls[j][4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y'):        
                            temp = array[j]
                            array[j] = array[i]
                            array[i] = temp
                            temp = rls[j]
                            rls[j] = rls[i]
                            rls[i] = temp
                elif sort_d == 1:
                    if (sort_grad == 0 and array[i] < array[j]) or (sort_grad == 1 and array[i] > array[j]):
                        temp = array[j]
                        array[j] = array[i]
                        array[i] = temp
                        temp = rls[j]
                        rls[j] = rls[i]
                        rls[i] = temp
                    elif array[i] == array[j]:
                        if rls[i][3] > rls[j][3]:
                            temp = array[j]
                            array[j] = array[i]
                            array[i] = temp
                            temp = rls[j]
                            rls[j] = rls[i]
                            rls[i] = temp
        self.rls = rls
        return

        
    def click(self, interaction: Interaction, click: int, in_row: int):
        text = interaction.message.embeds[0].description
        t1 = text.find('Страница **`')
        t2 = text.find('из', t1)
        counter = int(text[t1+12:t2-4])
        counter = (counter - 1) * in_row
        rls = self.rls
        if click == 0:
            if counter == 0:
                return ["-1"]
            counter -= in_row
        elif click == 1:
            if counter == (len(rls) + in_row - 1) // in_row * in_row - in_row:
                return ["-1"]
            counter += in_row
        elif click == 2:
            counter = 0
        elif click == 3:
            counter = (len(rls) + in_row - 1) // in_row * in_row - in_row

        shop_list = []
        if counter + in_row < len(rls):
            for r in rls[counter:counter+in_row]:
                date = datetime.strptime(r[4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y')
                shop_list.append(f"**•** <@&{r[1]}>\n`id товара в магазине` - `{r[0]}`\n`Цена` - `{r[3]}`\n`Продавец` - <@{r[2]}>\n`Выставлено на продажу:`\n*{date}*\n")
        else:
            for r in rls[counter:]:
                date = datetime.strptime(r[4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y')
                shop_list.append(f"**•** <@&{r[1]}>\n`id товара в магазине` - `{r[0]}`\n`Цена` - `{r[3]}`\n`Продавец` - <@{r[2]}>\n`Выставлено на продажу:`\n*{date}*\n")
        shop_list.append(f'\nСтраница **`{(counter // in_row) + 1}`** из **`{(len(self.rls)+in_row-1)//in_row}`**')
        
        return shop_list
        
    @nextcord.ui.button(emoji="⏮️")
    async def callback_l_end(self, button: Button, interaction: Interaction):
        shop_list=self.click(interaction=interaction, click=2, in_row=self.in_row)
        if shop_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', color=Colour.dark_gray(), description='\n'.join(shop_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="◀️")
    async def callback_l(self, button: Button, interaction: Interaction):
        shop_list=self.click(interaction=interaction, click=0, in_row=self.in_row)
        if shop_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', color=Colour.dark_gray(), description='\n'.join(shop_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="▶️")
    async def callback_r(self, button: Button, interaction: Interaction):
        shop_list=self.click(interaction=interaction, click=1, in_row=self.in_row)
        if shop_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', color=Colour.dark_gray(), description='\n'.join(shop_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="⏭")
    async def callback_r_end(self, button: Button, interaction: Interaction):
        shop_list=self.click(interaction=interaction, click=3, in_row=self.in_row)
        if shop_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', color=Colour.dark_gray(), description='\n'.join(shop_list))
            await interaction.response.edit_message(embed=emb)
        

    @nextcord.ui.select(
        placeholder='Сортировать по...',
        options=[
            nextcord.SelectOption(
                label="Сортировать по цене",
                emoji="💰",
                default=True
            ),
            nextcord.SelectOption(
                label="Сортировать по дате",
                emoji="📅"
            )

        ], 
        min_values=1, 
        max_values=1
    )
    async def callback_select_value(self, menu: nextcord.ui.Select, interaction: Interaction):

        if menu._selected_values[0] == "Сортировать по цене":
            self.sort_d = 0
            self.children[4].options[0].default=True
            self.children[4].options[1].default=False
        else:
            self.sort_d = 1
            self.children[4].options[0].default=False
            self.children[4].options[1].default=True
        self.sort_by()

        shop_list=self.click(interaction=interaction, click=4, in_row=self.in_row)
        if shop_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', color=Colour.dark_gray(), description='\n'.join(shop_list))
            await interaction.response.edit_message(embed=emb, view=self)

    @nextcord.ui.select(
        placeholder='Сортировать от...',
        options=[
            nextcord.SelectOption(
                label="От меньшей цены (более свежого товара)",
                emoji="↗️",
                default=True
            ),
            nextcord.SelectOption(
                label="От большей цены (более старого товара)",
                emoji="↘️"
            )
        ], 
        min_values=1, 
        max_values=1
    )
    async def callback_select_how(self, menu: nextcord.ui.Select, interaction: Interaction):
        
        if menu._selected_values[0].startswith("От меньшей"):
            self.sort_grad = 0
            self.children[5].options[0].default = True
            self.children[5].options[1].default = False
        else:
            self.sort_grad = 1
            self.children[5].options[0].default = False
            self.children[5].options[1].default = True
        self.sort_by()
        
        shop_list=self.click(interaction=interaction, click=4, in_row=self.in_row)
        if shop_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', color=Colour.dark_gray(), description='\n'.join(shop_list))
            await interaction.response.edit_message(embed=emb, view=self)

    async def interaction_check(self, interaction):
            if interaction.user != self.ctx.author:
                await interaction.response.send_message('Вы не можете управлять меню, которое вызвано другим человеком', ephemeral=True)
                return False
            return True
 """
class shop_commands(commands.Cog):

    def __init__(self, bot: commands.Bot, prefix: str, in_row: int, currency: str):
        self.bot = bot
        self.prefix = prefix
        self.in_row = in_row

    """ @commands.cooldown(rate=1, per=100, type=commands.BucketType.user)
    @commands.command(aliases=['shop', 'list'])
    async def _merch(self, ctx: Context):
        with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                in_row = self.in_row
                counter = 0
                shop_list = []
                rls = cur.execute('SELECT * FROM shop').fetchall()
                
                for i in range(len(rls)):
                    if str(type(rls[i][0])) == "<class 'NoneType'>":
                        rls.pop(i)

                for i in range(len(rls)-1):
                    for j in range(i+1, len(rls)):
                        if rls[i][3] > rls[j][3]:
                            temp = rls[j]
                            rls[j] = rls[i]
                            rls[i] = temp
                        elif rls[i][3] == rls[j][3]:
                            if datetime.strptime(rls[i][4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y') < datetime.strptime(rls[j][4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y'):
                                temp = rls[j]
                                rls[j] = rls[i]
                                rls[i] = temp

                for r in rls[counter:counter+in_row]:
                    date = datetime.strptime(r[4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y')
                    shop_list.append(f"**•** <@&{r[1]}>\n`id товара в магазине` - `{r[0]}`\n`Цена` - `{r[3]}`\n`Продавец` - <@{r[2]}>\n`Выставлено на продажу:`\n*{date}*\n")

                shop_list.append(f'\nСтраница **`1`** из **`{(len(rls)+in_row-1)//in_row}`**')
                emb = Embed(title='Роли на продажу:', color=Colour.dark_gray(), description='\n'.join(shop_list))
                myview_shop = Myview_shop(timeout=140, rls=rls, ctx=ctx, in_row=3)
                msg = await ctx.reply(
                    view=myview_shop,
                    embed=emb,
                    mention_author=False
                )

                chk = await myview_shop.wait()
                if chk:
                    for button in myview_shop.children:
                        button.disabled = True
                    await msg.edit(view=myview_shop)
    

    @commands.command(aliases=['buy'])
    async def _buy(self, ctx: Context, id: int):
        with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                r = cur.execute('select * from shop where item_id = ?', (id,)).fetchone()

                if r == [] or r == None:
                    await ctx.reply(embed=Embed(title = 'Ошибка', description='**`Такой товар не найден. Пожалуйста, проверьте правильность указанного id`**', color=Colour.red()), mention_author=False)

                else:
                    role = ctx.guild.get_role(r[1])
                    if role in ctx.author.roles:
                        emb = Embed(title='Ошибка', description='**`У Вас уже есть эта роль`**', color=Colour.red())
                        await ctx.reply(embed=emb, mention_author=False)
                        return
                        
                    buyer = cur.execute('select * from users where memb_id = ?', (ctx.author.id,)).fetchone()
                    buyer_cash = None
                    if buyer != None:
                        buyer_cash = buyer[1]

                    if buyer == None:
                        cur.execute('insert into users(memb_id, money) values(?, ?)', (ctx.author.id, 0))
                        base.commit()
                        emb = Embed(title='Ошибка', color=Colour.red(), description=f'**`У Вас недостаточно денег: в вашем распоряжении 0, а для покупки роли необходимо {r[3]}`**')
                        await ctx.reply(embed=emb, mention_author=False)
                        return

                    elif buyer_cash == None:
                        cur.execute('update users set money = ? where memb_id = ?', (0, ctx.author.id))
                        base.commit()
                        emb = Embed(title='Ошибка', color=Colour.red(), description=f'**`У Вас недостаточно денег: в вашем распоряжении 0, а для покупки роли необходимо {r[3]}`**')
                        await ctx.reply(embed=emb, mention_author=False)
                        return

                    elif buyer_cash < r[3]:
                        emb = Embed(title='Ошибка', color=Colour.red(), description=f'**`У Вас недостаточно денег: в вашем распоряжении {buyer_cash}, а для покупки роли необходимо {r[3]}`**')
                        await ctx.reply(embed=emb, mention_author=False)
                        return


                    emb = Embed(title='Подтверждение покупки', description=f'**`Вы уверены, что хотите купить роль`** <@&{r[1]}>**`?\nС Вас будет списано {r[3]}`**')
                    view = Myview_buy(30, ctx)
                    msg = await ctx.reply(embed=emb, view=view, mention_author=False)

                    chk = await view.wait()
                    if chk:
                        for button in view.children:
                            button.disabled = True
                        emb.description = '**`Истекло время подтверждения покупки`**'
                        await msg.edit(embed = emb, view=view)
                        return
                    
                    if view.value:

                        seller = cur.execute('select * from users where memb_id = ?', (r[2],)).fetchone()
                        if seller == None:
                            cur.execute('insert into users(memb_id, money) values(?, ?)',(r[2], 0))
                            seller = (r[2], 0)
                        seller_cash = seller[1]
                        if seller_cash == None:
                            seller_cash = 0

                        cur.execute('update users set money = ? where memb_id = ?', (seller_cash + r[3], r[2]))
                        base.commit()
                        cur.execute('update users set money = ? where memb_id = ?', (buyer_cash - r[3], ctx.author.id))
                        base.commit()
                        cur.execute('delete from shop where item_id = ?', (id,))
                        base.commit()
                        
                        member_seller = await ctx.guild.fetch_member(r[2])
                        member_byer = ctx.author

                        await member_byer.add_roles(role)
                        await member_seller.remove_roles(role)

                        own_roles_seller = str(cur.execute('select spec_roles from users where memb_id = ?', (r[2],)).fetchone()[0])
                        own_roles_buyer = cur.execute('select spec_roles from users where memb_id = ?', (ctx.author.id,)).fetchone()
                       
                        if own_roles_buyer == None:
                            own_roles_buyer = ""
                        elif own_roles_buyer[0] == None:
                            own_roles_buyer = ""
                        else:
                            own_roles_buyer = str(own_roles_buyer[0])

                        own_roles_seller = own_roles_seller.replace(f"#{role.id}", "")
                        own_roles_buyer += f"#{role.id}"

                        cur.execute('update users set spec_roles = ? where memb_id = ?', (own_roles_seller, r[2]))
                        base.commit()
                        cur.execute('update users set spec_roles = ? where memb_id = ?', (own_roles_buyer, ctx.author.id))
                        base.commit()
                        emb.title, emb.description = 'Покупка совершена', '**`Если у Вас включена возможность получения личных сообщений от участников серверов, то подтверждение покупки будет выслано Вам в личные сообщения`**'
                        
                        await msg.edit(embed=emb, view=None)
                        try:
                            emb = Embed(title='Подтверждение оплаты', description=f'Вы успешно купили роль `{role.name}` на сервере `{ctx.guild.name}` за `{r[3]}`', color=Colour.green())
                            await ctx.author.send(embed=emb)
                        except:
                            pass
                        try:
                            emb = Embed(title='Подтверждение оплаты', description=f'Ваша роль роль `{role.name}` на сервере `{ctx.guild.name}` была куплена {ctx.author.mention} за `{r[3]}`', color=Colour.green())
                            member = await ctx.guild.fetch_member(r[2])
                            await member.send(embed=emb)
                        except:
                            pass 

    @_buy.error
    async def _buy_error(self, ctx: Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                embed=Embed(
                    color=Colour.red(),
                    title='Ошибка',
                    description=f'**Пожалуйста, укажите id товара в команде в формате\n`{self.prefix}buy id_товара_в_магазине`**'
                ),
                mention_author=False
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.reply(
                embed=Embed(
                    color=Colour.red(),
                    title='Ошибка',
                    description=f'**Пожалуйста, укажите id товара в виде натурального числа,\nнапример, `1, 5, 10`**'
                ),
                mention_author=False
            )
        else:
            raise error

    @commands.command(aliases=['sell'])
    async def _sell(self, ctx: Context, role: nextcord.Role, price: int):
        if price < 0:
            await ctx.reply(
                embed=Embed(
                    color=Colour.red(),
                    title='Ошибка',
                    description='**`Вы не можете выставить отрицательную цену за роль`**'
                ),
                mention_author=False
            )
            return
        elif not role in ctx.author.roles:
            await ctx.reply(
                embed=Embed(
                    color=Colour.red(),
                    title='Ошибка',
                    description='**`Вы не можете выставить на продажу роль, которой у Вас нет`**'
                ),
                mention_author=False
            )
            return

        with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                item_ids = [x[0] for x in cur.execute('select item_id from shop').fetchall()]
                item_ids.sort()
                free_id = 1
                while(free_id < len(item_ids) and free_id == item_ids[free_id-1]):
                    free_id += 1
                if free_id == len(item_ids):
                    free_id += 1

                cur.execute('insert into shop(item_id, role_id, seller_id, price, date) values(?, ?, ?, ?, ?)', (free_id, role.id, ctx.author.id, price, (datetime.utcnow()+timedelta(hours=3)).strftime('%S/%M/%H/%d/%m/%Y')))
                base.commit()

                emb = Embed(title='Подтверждение', description=f'Вы успешно выставили роль **`{role}`** за **`{price}`**')
                await ctx.reply(embed=emb, mention_author=False)
             
    @_sell.error
    async def _sell_error(self, ctx: Context, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.reply(
                embed=Embed(
                    color=Colour.red(),
                    title='Ошибка',
                    description='**`Такая роль не найдена. Пожалуйста, проверьте правильность написания указанной роли`**'
                ),
                mention_author=False
            ) 
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                embed=Embed(
                    color=Colour.red(),
                    title='Ошибка',
                    description=f'**Пожалуйста, укажите Ваши роль и цену в формате\n`{self.prefix}sell id_или_упомянание_роли цена`**'
                ),
                mention_author=False
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.reply(
                embed=Embed(
                    color=Colour.red(),
                    title='Ошибка',
                    description=f'**Пожалуйста, укажите Вашу цену в виде целого неотрицательного числа, например, `0, 1, 100, 1000`**'
                ),
                mention_author=False
            )
        else:
            #pass
            raise error
            
    #@commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @commands.command(aliases=['balance'])
    async def _balance(self, ctx: Context):
        with closing(sqlite3.connect(f'./bases_{ctx.guild.id}/{ctx.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                r = cur.execute('select * from users where memb_id = ?', (ctx.author.id,)).fetchone()
                emb = Embed(title='Личный счёт')
                if r == None or r == [] or r[0] == None:
                    cur.execute('insert into users(memb_id, money) values(?, ?)', (ctx.author.id, 0))
                    base.commit()
                    emb.description='Ваш баланс: `0`'
                elif r[1] == None:
                    cur.execute('update users set money = ? where memb_id = ?', (0, ctx.author.id))
                    base.commit()
                    emb.description='Ваш баланс: `0` '
                else:
                    emb.description=f'Ваш баланс: `{r[1]}`'
                await ctx.reply(
                    embed=emb,
                    mention_author=False
                ) """

def setup(bot: commands.Bot, **kwargs):
  bot.add_cog(shop_commands(bot, **kwargs))
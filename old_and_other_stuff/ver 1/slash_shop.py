import sqlite3, nextcord
from random import choice
from nextcord.ui import Button, View
from nextcord.ext import commands
from nextcord import Embed, Colour, ButtonStyle, SlashOption, Interaction
from contextlib import closing
from datetime import datetime, timedelta

class Bet_view(View):
    def __init__(self, timeout: int, ctx: Interaction, base: sqlite3.Connection, cur: sqlite3.Cursor, symbol: str, bet: int, function: filter):
        super().__init__(timeout=timeout)
        self.base = base
        self.cur = cur
        self.ctx = ctx
        self.symbol = symbol
        self.bet = bet
        self.check_user = function
        self.dueler = None

    @nextcord.ui.button(label="Сделать ставку", style=ButtonStyle.green, emoji="💰", custom_id="Make")
    async def callback_make(self, button: Button, interaction: Interaction):
        if interaction.user == self.ctx.user:
            await interaction.response.send_message('Вы не можете делать встречную ставку самому себе', ephemeral=True)
            return

        member = self.check_user(self.base, self.cur, interaction.user.id)
        if member[1] < self.bet:
            emb = Embed(title="Ошибка", description=f"**`Вы не можете сделать встречную ставку, так как Вам не хватает {self.bet-member[1]}`**{self.symbol}", colour=Colour.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        self.dueler = member
        self.stop()   

    @nextcord.ui.button(label="Отменить ставку", style=ButtonStyle.red, emoji="❌", custom_id="Deny")
    async def callback_deny(self, button: Button, interaction: Interaction):
        if interaction.user != self.ctx.user:
            await interaction.response.send_message('Вы не можете управлять чужой ставкой', ephemeral=True)
            return

        emb = Embed(title="Отмена ставки", description="**`Ставка была отменена пользователем`**")
        for button in self.children:
            button.disabled = True
        await interaction.response.edit_message(embed=emb, view=self)
        self.stop()


class Myview_shop_slash(View):
    def __init__(self, timeout: int, rls, ctx: Interaction, in_row: int, coin: str):
        super().__init__(timeout=timeout)
        self.rls = rls
        self.ctx = ctx
        self.in_row = in_row
        self.sort_d = 0 #by default - price
        self.sort_grad = 0 #возрастание / убывание, от gradation, 0 - возрастание
        self.coin = coin
    
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
        if counter < 0 or counter >= len(rls):
            return ["-1"]
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
            last = counter+in_row
        else:
            last = len(rls)
                
        for r in rls[counter:last]:
            date = datetime.strptime(r[4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y') 
            if r[2] // 100000 != 404:
                shop_list.append(f"**•** <@&{r[1]}>\n`id товара в магазине` - `{r[0]}`\n`Цена` - `{r[3]}`{self.coin}\n`Продавец` - <@{r[2]}>\n`Выставлено на продажу:`\n*{date}*\n")
            elif r[2] // 100000 == 404 and (r[2] % 100000 > 0):
                shop_list.append(f"**•** <@&{r[1]}>\n`id товара в магазине` - `{r[0]}`\n`Цена` - `{r[3]}`{self.coin}\n`Продавец` - `{interaction.guild.name}`\n`Количество` - `{r[2] % 100000}`\n`Выставлено на продажу:`\n*{date}*\n")
        
        shop_list.append(f'\nСтраница **`{(counter // in_row) + 1}`** из **`{(len(self.rls)+in_row-1)//in_row}`**')
        
        return shop_list

    @nextcord.ui.button(emoji="⏮️")
    async def callback_l_end(self, button: Button, interaction: Interaction):
        shop_list=self.click(interaction=interaction, click=2, in_row=self.in_row)
        if shop_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(shop_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="◀️")
    async def callback_l(self, button: Button, interaction: Interaction):
        shop_list=self.click(interaction=interaction, click=0, in_row=self.in_row)
        if shop_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(shop_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="▶️")
    async def callback_r(self, button: Button, interaction: Interaction):
        shop_list=self.click(interaction=interaction, click=1, in_row=self.in_row)
        if shop_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(shop_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="⏭")
    async def callback_r_end(self, button: Button, interaction: Interaction):
        shop_list=self.click(interaction=interaction, click=3, in_row=self.in_row)
        if shop_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(shop_list))
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
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(shop_list))
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
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(shop_list))
            await interaction.response.edit_message(embed=emb, view=self)

    async def interaction_check(self, interaction):
            if interaction.user != self.ctx.user:
                await interaction.response.send_message('Вы не можете управлять меню, которое вызвано другим человеком', ephemeral=True)
                return False
            return True

class Myview_buy_slash(View):

        def __init__(self, timeout, ctx: Interaction):
            super().__init__(timeout=timeout)
            self.ctx = ctx
            self.value = 0

        @nextcord.ui.button(label='Да', style=ButtonStyle.green, emoji="✅", custom_id = "second")
        async def agr_callback(self, button: Button, interaction: Interaction):
            self.value = 1
            self.stop()

        @nextcord.ui.button(label='Нет, отменить покупку', style=ButtonStyle.red, emoji="❌")
        async def decl_callback(self, button: Button, interaction: Interaction):
            button.disabled = True
            button1 = [x for x in self.children if x.custom_id == "second"][0]
            button1.disabled=True
            emb = interaction.message.embeds[0]
            emb.description='**`Покупка отмена пользователем`**'
            await interaction.response.edit_message(embed = emb, view=self)
            self.stop()
            
        async def interaction_check(self, interaction):
            if interaction.user != self.ctx.user:
                await interaction.response.send_message('Вы не можете управлять чужой покупкой', ephemeral=True)
                return False
            return True

class shop_commands_slash(commands.Cog):

    def __init__(self, bot: commands.Bot, prefix: str, in_row: int, currency: str):
        self.bot = bot
        self.prefix = prefix
        self.in_row = in_row
        self.currency = currency
    
    def check_user(self, base: sqlite3.Connection, cur: sqlite3.Cursor, memb_id: int):
        member = cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()
        if member == None:
            cur.execute('INSERT INTO users(memb_id, money, owned_roles, sale_roles, work_date) VALUES(?, ?, ?, ?, ?)', (memb_id, 0, "", "", "0"))
            base.commit()
        else:
            if member[1] == None or member[1] < 0:
                cur.execute('UPDATE users SET money = ? WHERE memb_id = ?', (0, memb_id))
                base.commit()
            if member[2] == None:
                cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', ("", memb_id))
                base.commit()
            if member[3] == None:
                cur.execute('UPDATE users SET sale_roles = ? WHERE memb_id = ?', ("", memb_id))
                base.commit()
            if member[4] == None:
                cur.execute('UPDATE users SET work_date = ? WHERE memb_id = ?', ("0", memb_id))
                base.commit()
        return cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()

    @nextcord.slash_command(name="buy", description="Вызывает меню покупки роли в магазине", guild_ids=[863462268402532363, 934139154290339881])
    async def buy(self, interaction: Interaction, id: int = SlashOption(name="id", description="id товара в магазине", min_value=1, required=True)):
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                r = cur.execute('SELECT * FROM shop WHERE item_id = ?', (id,)).fetchone()

                if r == [] or r == None:
                    await interaction.response.send_message(embed=Embed(title = 'Ошибка', description='**`Такой товар не найден. Пожалуйста, проверьте правильность указанного id`**', colour=Colour.red()))

                else:
                    role = interaction.guild.get_role(r[1])
                    if role in interaction.user.roles:
                        emb = Embed(title='Ошибка', description='**`У Вас уже есть эта роль`**', colour=Colour.red())
                        await interaction.response.send_message(embed=emb)
                        return
                    
                    memb_id = interaction.user.id
                    buyer = self.check_user(base=base, cur=cur, memb_id=memb_id)
                    buyer_cash = buyer[1]
                    
                    if buyer_cash < r[3]:
                        emb = Embed(title='Ошибка', colour=Colour.red(), description=f'**`У Вас недостаточно денег: в вашем распоряжении {buyer_cash}`{self.currency}`, а для покупки роли необходимо {r[3]}`**{self.currency}')
                        await interaction.response.send_message(embed=emb)
                        return

                    
                    emb = Embed(title='Подтверждение покупки', description=f'**`Вы уверены, что хотите купить роль`** <@&{r[1]}>**`?\nС Вас будет списано {r[3]}`**{self.currency}')
                    view = Myview_buy_slash(timeout=30, ctx=interaction)
                    await interaction.response.send_message(embed=emb, view=view)
                    msg = await interaction.original_message()

                    chk = await view.wait()
                    if chk:
                        for button in view.children:
                            button.disabled = True
                        emb.description = '**`Истекло время подтверждения покупки`**'
                        await msg.edit(embed = emb, view=view)
                        return
                    
                    if view.value:
                        root = 0
                        if r[2] // 100000 == 404:
                             root = 1

                        if not root: 
                            seller = self.check_user(base=base, cur=cur, memb_id=r[2])
                            cur.execute('UPDATE users SET money = money + ? WHERE memb_id = ?', (r[3], r[2]))
                            base.commit()
                            
                        cur.execute('UPDATE users SET money = money - ? WHERE memb_id = ?', (r[3], memb_id))
                        base.commit()

                        if not root:
                            cur.execute('DELETE FROM shop WHERE item_id = ?', (id,))
                            base.commit()
                        else:
                            n = r[2] % 100000
                            if n <= 1:
                                cur.execute('DELETE FROM shop WHERE item_id = ?', (id,))
                            else:
                                cur.execute('UPDATE shop SET seller_id = seller_id - ? where item_id = ?', (1, id))
                            base.commit()

                        if not root: 
                            member_seller = await interaction.guild.fetch_member(r[2])
                            await member_seller.remove_roles(role)

                        member_buyer = interaction.user
                        await member_buyer.add_roles(role)                            

                        buyer_owned_roles = buyer[2]
                        buyer_owned_roles += f"#{role.id}"
                        
                        cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', (buyer_owned_roles, memb_id))
                        base.commit()

                        if not root: 
                            
                            seller_owned_roles = seller[2]
                            seller_owned_roles = seller_owned_roles.replace(f"#{role.id}", "")
                            seller_sale_roles = seller[3]
                            seller_sale_roles = seller_sale_roles.replace(f"#{role.id}", "")
                        
                            cur.execute('UPDATE users SET owned_roles = ?, sale_roles = ? WHERE memb_id = ?', (seller_owned_roles, seller_sale_roles, r[2]))
                            base.commit()

                        emb.title, emb.description = 'Покупка совершена', '**`Если у Вас включена возможность получения личных сообщений от участников серверов, то подтверждение покупки будет выслано Вам в личные сообщения`**'
                        
                        await msg.edit(embed=emb, view=None)

                        try:
                            emb = Embed(title='Подтверждение оплаты', description=f'Вы успешно купили роль `{role.name}` на сервере `{interaction.guild.name}` за `{r[3]}`{self.currency}', colour=Colour.green())
                            await member_buyer.send(embed=emb)
                        except:
                            pass
                        
                        if not root:    
                            try:
                                emb = Embed(title='Подтверждение оплаты', description=f'Ваша роль роль `{role.name}` на сервере `{interaction.guild.name}` была куплена {interaction.user.mention} за `{r[3]}`{self.currency}', colour=Colour.green())
                                await member_seller.send(embed=emb)
                            except:
                                pass

    @nextcord.slash_command(name="shop", description="Вызывает меню с товарами", guild_ids=[863462268402532363, 934139154290339881])
    async def shop(self, interaction: Interaction):
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
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
                    if r[2] // 100000 != 404:
                        shop_list.append(f"**•** <@&{r[1]}>\n`id товара в магазине` - `{r[0]}`\n`Цена` - `{r[3]}`{self.currency}\n`Продавец` - <@{r[2]}>\n`Выставлено на продажу:`\n*{date}*\n")
                    elif r[2] // 100000 == 404 and (r[2] % 100000 > 0):
                        shop_list.append(f"**•** <@&{r[1]}>\n`id товара в магазине` - `{r[0]}`\n`Цена` - `{r[3]}`{self.currency}\n`Продавец` - `{interaction.guild.name}`\n`Количество` - `{r[2] % 100000}`\n`Выставлено на продажу:`\n*{date}*\n")
                shop_list.append(f'\nСтраница **`1`** из **`{(len(rls)+in_row-1)//in_row}`**')
                emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(shop_list))
                myview_shop = Myview_shop_slash(timeout=60, rls=rls, ctx=interaction, in_row=3, coin=self.currency)
                await interaction.response.send_message(embed=emb, view=myview_shop)
                msg = await interaction.original_message()
                chk = await myview_shop.wait()
                if chk:
                    for button in myview_shop.children:
                        button.disabled = True
                    await msg.edit(view=myview_shop)
    
    @nextcord.slash_command(name="sell", description="Выставляет указанную роль на продажу", guild_ids=[863462268402532363, 934139154290339881])
    async def sell(
        self,
        interaction: Interaction,
        role: nextcord.Role = SlashOption(name="role", description="Ваша роль, которую Вы хотите выставить на продажу", required=True),
        price: int = SlashOption(name="price", description="Цена, за которую Вы хотите выставить роль", required=True, min_value=0)
    ):
        if not role in interaction.user.roles:
            await interaction.response.send_message(embed=Embed(
                colour=Colour.red(),
                title='Ошибка',
                description='**`Вы не можете выставить на продажу роль, которой у Вас нет`**'
            ))
            return
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                allowed_roles = cur.execute('SELECT * FROM server_roles').fetchall()
                allowed_roles = [x[0] for x in allowed_roles]
                if not role.id in allowed_roles:
                    await interaction.response.send_message(embed=Embed(title='Ошибка', description='Вы не можете выставить эту роль на продажу', colour=Colour.red()))
                    return

                memb_id = interaction.user.id
                user = self.check_user(base=base, cur=cur, memb_id=memb_id)
                
                owned_roles = user[2]
                sale_roles = user[3]
                if owned_roles.find(f"{role.id}") == -1:
                    owned_roles += f"#{role.id}"
                    cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', (owned_roles, memb_id))
                    base.commit()

                if str(role.id) in sale_roles:
                    await interaction.response.send_message(embed=Embed(title='Ошибка', description='Вы не можете выставить на продажу роль, которую уже продаёте', colour=Colour.red()))
                    return

                sale_roles += f"#{role.id}"
                cur.execute('UPDATE users SET sale_roles = ? WHERE memb_id = ?', (sale_roles, memb_id))
                base.commit()
                item_ids = [x[0] for x in cur.execute('SELECT item_id FROM shop').fetchall()]
                item_ids.sort()
                free_id = 1
                while(free_id < len(item_ids) and free_id == item_ids[free_id-1]):
                    free_id += 1
                if free_id == len(item_ids):
                    free_id += 1

                cur.execute('INSERT INTO shop(item_id, role_id, seller_id, price, date) VALUES(?, ?, ?, ?, ?)', (free_id, role.id, interaction.user.id, price, (datetime.utcnow()+timedelta(hours=3)).strftime('%S/%M/%H/%d/%m/%Y')))
                base.commit()

                emb = Embed(title='Подтверждение', description=f'Вы успешно выставили роль **`{role}`** за **`{price}`**{self.currency}')
                await interaction.response.send_message(embed=emb)

    @nextcord.slash_command(name="balance", description="Показывает Ваш баланс", guild_ids=[863462268402532363, 934139154290339881])
    async def balance(self, interaction: Interaction):
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                member = self.check_user(base=base, cur=cur, memb_id=interaction.user.id)
                emb = Embed(title='Личный счёт')
                emb.description=f'Ваш баланс: `{member[1]}`{self.currency}'
                await interaction.response.send_message(embed=emb)

    @nextcord.slash_command(name="work", description="Поработать", guild_ids=[863462268402532363, 934139154290339881])
    async def work(self, interaction: Interaction):
        memb_id = interaction.user.id
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                member = self.check_user(base=base, cur=cur, memb_id=memb_id)
                flag = 0
                
                """ print(lasted_time)
                print(timedelta(hours=4))
                print(lasted_time < timedelta(hours=4)) """

                if member[4] == "0":
                    flag = 1
                else:
                    lasted_time = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") + \
                        timedelta(hours=3) - datetime.strptime(member[4], '%S/%M/%H/%d/%m/%Y')
                    if lasted_time >= timedelta(hours=4):
                        flag = 1
                if not flag:
                    time_l = timedelta(hours=4) - lasted_time                    
                    await interaction.response.send_message(embed=Embed(title="Ошибка", description=f"Пожалуйста, подождите {time_l} перед тем, как снова вызвать команду работы"))
                    return 
                
                salary = choice(range(50, 201))
                cur.execute('UPDATE users SET money = money + ?, work_date = ? WHERE memb_id = ?', (salary, (datetime.utcnow() + timedelta(hours=3)).strftime("%S/%M/%H/%d/%m/%Y"), memb_id))
                base.commit()
                await interaction.response.send_message(embed=Embed(title="Успех", description=f"**`Вы заработали {salary}`**{self.currency}", colour=Colour.gold()))
                return

    @nextcord.slash_command(name="duel", description="Сделать ставку", guild_ids=[863462268402532363, 934139154290339881])
    async def duel(self, interaction: Interaction, bet: int = SlashOption(name="bet", description="Делает ставку указанной суммы", required=True, min_value=1)): 

        memb_id = interaction.user.id
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                member = self.check_user(base=base, cur=cur, memb_id=memb_id)
                if bet > member[1]:
                    await interaction.response.send_message(embed=Embed(title='Ошибка', description='**`Вы не можете поставить больше, чем есть у Вас на балансе`**', colour=Colour.red()), ephemeral=True)
                    return
                betview = Bet_view(timeout=30, ctx=interaction, base=base, cur=cur, symbol=self.currency, bet=bet, function=self.check_user)
                emb = Embed(title='Ставка', description=f'**`Вы `**{self.currency}')
                await interaction.response.send_message(embed=emb, view=betview)
                msg = await interaction.original_message()

                chk = await betview.wait()

                if chk:
                    for button in betview.children:
                        button.disabled = True
                    emb.description = '**`Истекло время ожидания встречной ставки`**'
                    await msg.edit(embed = emb, view=betview)
                    return
                
                if betview.dueler == None:
                    return

                msg = await interaction.original_message()
                dueler = betview.dueler

                winner = choice([0, 1])
                emb = Embed(title='У нас победитель!', colour=Colour.gold())
                if winner:
                    loser_id = dueler[0]
                    winner_id = interaction.user.id
                    emb.description = f"{interaction.user.mention} выиграл `{bet}`{self.currency}"
                else:
                    winner_id = dueler[0]
                    loser_id = interaction.user.id
                    emb.description = f"<@{dueler[0]}> выиграл `{bet}`{self.currency}"
                
                cur.execute('UPDATE users SET money = money - ? WHERE memb_id = ?', (bet, loser_id))
                base.commit()
                cur.execute('UPDATE users SET money = money + ? WHERE memb_id = ?', (bet, winner_id))
                base.commit()
                for button in betview.children:
                    button.disabled = True
                await msg.edit(embed=emb, view=betview)
                
    """ @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(error) """

def setup(bot: commands.Bot, **kwargs):
  bot.add_cog(shop_commands_slash(bot, **kwargs))
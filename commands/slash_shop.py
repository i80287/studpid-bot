import sqlite3, nextcord, pytz
from time import time
from random import randint
from nextcord.ui import Button, View
from nextcord.ext import commands
from nextcord import Embed, Colour, ButtonStyle, SlashOption, Interaction
from contextlib import closing
from datetime import datetime, timedelta, timezone


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
    
""" class view_sell(View):
    def __init__(self, timeout: int, ctx: Interaction):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.is_sold = 0
    @nextcord.ui.button(label='Да', style=ButtonStyle.green, emoji="✅", custom_id = "goodbye")
    async def goodbye_role(self, button: Button, interaction: Interaction):
        self.is_sold = 1
        self.stop()

    @nextcord.ui.button(label='Нет, отменить продажу', style=ButtonStyle.red, emoji="❌")
    async def decline_sell(self, button: Button, interaction: Interaction):
        button.disabled = True
        button1 = [x for x in self.children if x.custom_id == "goodbye"][0]
        button1.disabled=True
        emb = interaction.message.embeds[0]
        emb.description='**`Продажа отмена пользователем`**'
        emb.title="Изменение статуса продажи"
        await interaction.response.edit_message(embed = emb, view=self)
        self.stop()
        
    async def interaction_check(self, interaction):
        if interaction.user != self.ctx.user:
            await interaction.response.send_message('Вы не можете управлять чужой продажей', ephemeral=True)
            return False
        return True """

class Myview_shop_slash(View):
    def __init__(self, timeout: int, outer_shop: list, ctx: Interaction, in_row: int, coin: str, tz: int):
        super().__init__(timeout=timeout)
        self.outer_shop = outer_shop
        self.ctx = ctx
        self.in_row = in_row
        self.sort_d = 0 #by default - sort by price, 1 - sort by date (time)
        self.sort_grad = 0 #возрастание / убывание, от gradation, 0 - возрастание
        self.coin = coin
        self.tz = tz #time zone of the guild
    
    def sort_by(self):
        outer = self.outer_shop
        sort_d = self.sort_d
        sort_grad = self.sort_grad
        if sort_d == 0:
            #price
            array = [rr[3] for rr in outer]
        elif sort_d == 1:
            #time
            array = [rr[4] for rr in outer]
            
        for i in range(len(array)-1):
            for j in range(i+1, len(array)):
                if sort_d == 0:
                    if (sort_grad == 0 and array[i] > array[j]) or (sort_grad == 1 and array[i] < array[j]):
                        temp = array[j]
                        array[j] = array[i]
                        array[i] = temp
                        temp = outer[j]
                        outer[j] = outer[i]
                        outer[i] = temp
                    elif array[i] == array[j]:
                        #if datetime.strptime(outer[i][4], '%S/%M/%H/%d/%m/%Y') < datetime.strptime(outer[j][4], '%S/%M/%H/%d/%m/%Y'):
                        #if prices are equal, at first select позже выставленную роль
                        if outer[i][4] < outer[j][4]:
                            temp = array[j]
                            array[j] = array[i]
                            array[i] = temp
                            temp = outer[j]
                            outer[j] = outer[i]
                            outer[i] = temp

                elif sort_d == 1:
                    if (sort_grad == 0 and array[i] < array[j]) or (sort_grad == 1 and array[i] > array[j]):
                        temp = array[j]
                        array[j] = array[i]
                        array[i] = temp
                        temp = outer[j]
                        outer[j] = outer[i]
                        outer[i] = temp
                    elif array[i] == array[j]:
                        #if dates are equal, at first select role with lower price
                        if outer[i][3] > outer[j][3]:
                            temp = array[j]
                            array[j] = array[i]
                            array[i] = temp
                            temp = outer[j]
                            outer[j] = outer[i]
                            outer[i] = temp

        self.outer_shop = outer
        return

        
    def click(self, interaction: Interaction, click: int, in_row: int):
        text = interaction.message.embeds[0].description
        t1 = text.find('Страница **`')
        t2 = text.find('из', t1)
        counter = int(text[t1+12:t2-4])
        counter = (counter - 1) * in_row
        outer = self.outer_shop
        if counter < 0 or counter >= len(outer):
            return ["-1"]
        if click == 0:
            if counter == 0:
                return ["-1"]
            counter -= in_row
        elif click == 1:
            if counter == (len(outer) + in_row - 1) // in_row * in_row - in_row:
                return ["-1"]
            counter += in_row
        elif click == 2:
            counter = 0
        elif click == 3:
            counter = (len(outer) + in_row - 1) // in_row * in_row - in_row

        shop_list = []

        if counter + in_row < len(outer):
            last = counter + in_row
        else:
            last = len(outer)
                
        for r in outer[counter:last]:
            #date = datetime.strptime(r[4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y')
            tzinfo = timezone(timedelta(hours=self.tz))
            date = datetime.fromtimestamp(r[4], tz=tzinfo).strftime("%H:%M %d-%m-%Y")
            if r[5] == 1:
                shop_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}`{self.coin}\n`Осталось` - `{r[2]}`\n`Последний раз выставленa на продажу:`\n*{date}*\n")
            elif r[5] == 2:
                shop_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}`{self.coin}\n`Осталось` - `∞`\n`Последний раз выставленa на продажу:`\n*{date}*\n")
            elif r[5] == 0:
                shop_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}`{self.coin}\n`Выставленa на продажу:`\n*{date}*\n")
                
        
        shop_list.append(f'\nСтраница **`{(counter // in_row) + 1}`** из **`{(len(outer)+in_row-1)//in_row}`**')
        
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

    @nextcord.slash_command(name="buy", description="Вызывает меню покупки роли в магазине", guild_ids=[863462268402532363, 934139154290339881])
    async def buy(self, interaction: Interaction, role: nextcord.Role = SlashOption(name="role", description="Роль, которую Вы хотите купить", required=True)):
        member_buyer = interaction.user
        if role in member_buyer.roles:
            emb = Embed(title='Ошибка', description='**`У Вас уже есть эта роль`**', colour=Colour.red())
            await interaction.response.send_message(embed=emb)
            return
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:            
                outer = cur.execute('SELECT * FROM outer_shop WHERE role_id = ?', (role.id,)).fetchone()
                if outer == [] or outer == None:
                    await interaction.response.send_message(embed=Embed(title = 'Ошибка', description='**`Такой товар не найден. Пожалуйста, проверьте правильность выбранной роли`**', colour=Colour.red()))
                    return

                role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()

                memb_id = member_buyer.id
                buyer = self.check_user(base=base, cur=cur, memb_id=memb_id)
                buyer_cash = buyer[1]
                cost = role_info[1]
                if buyer_cash < cost:
                    emb = Embed(title='Ошибка', colour=Colour.red(), description=f'**`Для покупки роли Вам не хватает {cost - buyer_cash}`**{self.currency}')
                    await interaction.response.send_message(embed=emb)
                    return

                emb = Embed(title='Подтверждение покупки', description=f'**`Вы уверены, что хотите купить роль`** {role.mention}?\nС Вас будет списано **`{cost}`**{self.currency}')
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
                    
                    is_special = role_info[2]
                    if is_special == 0:
                        outer = None
                        special_roles = cur.execute('SELECT * FROM outer_shop WHERE role_id = ?', (role.id,)).fetchall()
                        #min_time = datetime.utcnow() + timedelta(hours=4)
                        min_time = int(time()) + 57600
                        for i in range(len(special_roles)):
                            #if datetime.strptime(special_roles[i][4], "%S/%M/%H/%d/%m/%Y") < min_time:
                            if special_roles[i][4] < min_time:
                                outer = special_roles[i]
                                #min_time = datetime.strptime(special_roles[i][4], "%S/%M/%H/%d/%m/%Y")
                                min_time = special_roles[i][4]

                    await member_buyer.add_roles(role)                            
                    buyer_owned_roles = buyer[2]
                    buyer_owned_roles += f"#{role.id}"                        
                    cur.execute('UPDATE users SET money = money - ?, owned_roles = ? WHERE memb_id = ?', (cost, buyer_owned_roles, memb_id))
                    base.commit()
                    
                    if (outer[2] <= 1 and outer[2] != -404) or is_special == 0:
                        item_id = cur.execute('SELECT item_id FROM outer_shop WHERE role_id = ?', (role.id,)).fetchone()[0]
                        cur.execute('DELETE FROM outer_shop WHERE item_id = ?', (item_id,))
                        base.commit()
                    elif is_special == 1:
                        cur.execute('UPDATE outer_shop SET quantity = quantity - ? WHERE role_id = ?', (1, role.id))
                        base.commit()

                    emb.title = 'Покупка совершена'
                    emb.description = '**`Если у Вас включена возможность получения личных сообщений от участников серверов, то подтверждение покупки будет выслано Вам в личные сообщения`**'
                    await msg.edit(embed=emb, view=None)

                    try:
                        emb = Embed(title='Подтверждение оплаты', description=f'Вы успешно купили роль `{role.name}` на сервере `{interaction.guild.name}` за `{cost}`{self.currency}', colour=Colour.green())
                        await member_buyer.send(embed=emb)
                    except:
                        pass
                    
    @nextcord.slash_command(name="shop", description="Вызывает меню с товарами", guild_ids=[863462268402532363, 934139154290339881])
    async def shop(self, interaction: Interaction):
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                in_row = self.in_row
                counter = 0
                shop_list = []
                tz = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]
                outer_list = cur.execute('SELECT * FROM outer_shop').fetchall()
                for i in range(len(outer_list)-1):
                    for j in range(i+1, len(outer_list)):
                        if outer_list[i][3] > outer_list[j][3]:
                            temp = outer_list[j]
                            outer_list[j] = outer_list[i]
                            outer_list[i] = temp
                        elif outer_list[i][3] == outer_list[j][3]:
                            #if datetime.strptime(outer_list[i][4], "%S/%M/%H/%d/%m/%Y") < datetime.strptime(outer_list[j][4], "%S/%M/%H/%d/%m/%Y"):
                            if outer_list[i][4] < outer_list[j][4]:
                                temp = outer_list[j]
                                outer_list[j] = outer_list[i]
                                outer_list[i] = temp
                
                for r in outer_list[counter:counter+in_row]:
                    #date = datetime.strptime(r[4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y')
                    tzinfo = timezone(timedelta(hours=tz))
                    date = datetime.fromtimestamp(r[4], tz=tzinfo).strftime("%H:%M %d-%m-%Y")
                    if r[5] == 1:
                        shop_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}`{self.currency}\n`Осталось` - `{r[2]}`\n`Последний раз выставленa на продажу:`\n*{date}*\n")
                    elif r[5] == 2:
                        shop_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}`{self.currency}\n`Осталось` - `∞`\n`Последний раз выставленa на продажу:`\n*{date}*\n")
                    elif r[5] == 0:
                        shop_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}`{self.currency}\n`Выставленa на продажу:`\n*{date}*\n")
                        

                shop_list.append(f'\nСтраница **`1`** из **`{(len(outer_list)+in_row-1)//in_row}`**')

                emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(shop_list))
                myview_shop = Myview_shop_slash(timeout=60, outer_shop=outer_list, ctx=interaction, in_row=3, coin=self.currency, tz=tz)
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
        role: nextcord.Role = SlashOption(name="role", description="Ваша роль, которую Вы хотите продать", required=True),
    ):
        if not role in interaction.user.roles:
            await interaction.response.send_message(embed=Embed(
                colour=Colour.red(),
                title='Ошибка',
                description='**`Вы не можете продать роль, которой у Вас нет`**'
            ))
            return
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()

                if role_info == None:
                    await interaction.response.send_message(embed=Embed(title='Ошибка', description='Вы не можете продать эту роль', colour=Colour.red()))
                    return

                memb_id = interaction.user.id
                user = self.check_user(base=base, cur=cur, memb_id=memb_id)

                #time_now = (datetime.utcnow() + timedelta(hours=3)).strftime('%S/%M/%H/%d/%m/%Y')
                
                role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
                owned_roles = user[2]
                cur.execute('UPDATE users SET owned_roles = ?, money = money + ? WHERE memb_id = ?', (owned_roles.replace(f"#{role.id}", ""), role_info[1], memb_id))
                base.commit()
                outer  = cur.execute('SELECT * FROM outer_shop WHERE role_id = ?', (role.id,)).fetchone()      
                time_now = int(time())
                tz = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]     
                if role_info[2] == 1:                   
                    if outer == None:
                        item_ids = [x[0] for x in cur.execute('SELECT item_id FROM outer_shop').fetchall()]
                        item_ids.sort()
                        free_id = 1
                        while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                            free_id += 1
                        cur.execute('INSERT INTO outer_shop(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, 1, role_info[1], time_now, 1))
                        base.commit()            
                    else:
                        cur.execute('UPDATE outer_shop SET quantity = quantity + ?, last_date = ? WHERE role_id = ?', (1, time_now + tz * 3600, role.id))
                        base.commit()
                elif role_info[2] == 2:
                    if outer == None:
                        item_ids = [x[0] for x in cur.execute('SELECT item_id FROM outer_shop').fetchall()]
                        item_ids.sort()
                        free_id = 1
                        while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                            free_id += 1
                        cur.execute('INSERT INTO outer_shop(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, -404, role_info[1], time_now + tz * 3600, 2))
                        base.commit()

                elif role_info[2] == 0:
                    
                    item_ids = [x[0] for x in cur.execute('SELECT item_id FROM outer_shop').fetchall()]
                    item_ids.sort()
                    free_id = 1
                    while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                        free_id += 1
                    cur.execute('INSERT INTO outer_shop(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, 1, role_info[1], time_now + tz * 3600, 0))
                    base.commit()

                    membs = cur.execute("SELECT members FROM money_roles WHERE role_id = ?", (role.id,)).fetchone()
                    if membs != None and membs[0] != None:
                        cur.execute("UPDATE money_roles SET members = ? WHERE role_id = ?", (membs[0].replace(f"#{memb_id}", ""), role.id))
                        base.commit()

                await interaction.user.remove_roles(role)
                emb = Embed(title='Продажа совершена', description=f'Вы продали роль {role.mention} за **`{role_info[1]}`**{self.currency}\nЕсли у Вас включена возможность получения личных сообщений от участников серверов, то подтверждение покупки будет выслано Вам в личные сообщения', colour=Colour.gold())
                await interaction.response.send_message(embed=emb)

                try:
                    emb = Embed(title='Подтверждение продажи', description=f'Вы продали роль {role.mention} за **`{role_info[1]}`**{self.currency}', colour=Colour.green())
                    await interaction.user.send(embed=emb)
                except:
                    pass

    @nextcord.slash_command(name="profile", description="Показывает Ваш профиль", guild_ids=[863462268402532363, 934139154290339881])
    async def profile(self, interaction: Interaction):
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                memb_id = interaction.user.id
                member = self.check_user(base=base, cur=cur, memb_id=memb_id)
                server_roles = cur.execute('SELECT role_id FROM server_roles').fetchall()
                server_roles = set([x[0] for x in server_roles]) #ids of roles that user might has, set for quick searching in
                emb = Embed(title='Ваш профиль')
                roles = ""
                uniq_roles = []
                descr = []
                descr.append(f'**Ваш баланс:** `{member[1]}`{self.currency}\n')
                flag = 0
                for role_g in interaction.user.roles:
                    id = role_g.id
                    if id in server_roles:
                        if flag == 0:
                            descr.append('**Ваши личные роли:**')
                            descr.append("**Роль** - **Цена** - **Доход** (для уникальных ролей)")
                        flag = 1
                        role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (id,)).fetchone()
                        price = role_info[1]
                        is_special = role_info[2]
                        if is_special == 0:
                            salary = cur.execute("SELECT salary FROM money_roles WHERE role_id = ?", (id,)).fetchone()[0]
                            descr.append(f"**•** {role_g.mention} - `{price}`{self.currency} - `{salary}`{self.currency}")
                            uniq_roles.append(id)
                        else:
                            descr.append(f"**•** {role_g.mention} - `{price}`{self.currency}")
                        roles += f"#{id}"
                try:
                    # for each uniq user's role check if system knows that user has this role
                    for role in uniq_roles:
                        membs = cur.execute("SELECT members FROM money_roles WHERE role_id = ?", (role,)).fetchone()[0]
                        if membs == None:
                            cur.execute("UPDATE money_roles SET members = ? WHERE role_id = ?", (f"#{memb_id}", role))
                            base.commit()
                        else:
                            if not str(memb_id) in membs:
                                membs += f"#{memb_id}"
                                cur.execute("UPDATE money_roles SET members = ? WHERE role_id = ?", (membs, role))
                                base.commit()

                except Exception as E:
                    with open("d.log", "a+", encoding="utf-8") as f:
                        f.write(f"[{datetime.now(pytz.utc).__add__(timedelta(hours=3))}] [ERROR] [command /profile] [user: {memb_id}] [{str(E)}]\n")

                if flag:
                    cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', (roles, interaction.user.id))
                    base.commit()
                emb.description = "\n".join(descr)
                await interaction.response.send_message(embed=emb)

    @nextcord.slash_command(name="work", description="Поработать", guild_ids=[863462268402532363, 934139154290339881])
    async def work(self, interaction: Interaction):
        memb_id = interaction.user.id
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                tz = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]
                time_reload = cur.execute("SELECT value FROM server_info WHERE settings = 'time_r'").fetchone()[0]
                member = self.check_user(base=base, cur=cur, memb_id=memb_id)
                flag = 0
                if member[3] == 0:
                    flag = 1
                else:
                    #lasted_time = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") + \
                    #    timedelta(hours=3) - datetime.strptime(member[3], '%S/%M/%H/%d/%m/%Y')
                    lasted_time = int(time()) + tz * 3600 - member[3]
                    if lasted_time >= time_reload:
                        flag = 1
                if not flag:
                    time_l = time_reload - lasted_time                    
                    await interaction.response.send_message(embed=Embed(title="Ошибка", description=f"Пожалуйста, подождите **`{time_l}`** перед тем, как снова вызвать команду работы"))
                    return 
                sal_l = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_l'").fetchone()[0]
                sal_r = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_r'").fetchone()[0]
                salary = randint(sal_l, sal_r)
                cur.execute('UPDATE users SET money = money + ?, work_date = ? WHERE memb_id = ?', (salary, int(time()) + tz * 3600, memb_id))
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
                    await interaction.response.send_message(embed=Embed(title='Ошибка', description=f'Вы не можете сделать ставку, так как Вам не хватает **`{bet - member[1]}`**{self.currency}', colour=Colour.red()), ephemeral=True)
                    return
                betview = Bet_view(timeout=30, ctx=interaction, base=base, cur=cur, symbol=self.currency, bet=bet, function=self.check_user)
                emb = Embed(title='Ставка', description=f'Вы сделали ставку в размере **`{bet}`**{self.currency}\nТеперь кто-то должен принять Ваш вызов')
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

                winner = randint(0, 1)
                emb = Embed(title='У нас победитель!', colour=Colour.gold())
                if winner:
                    loser_id = dueler[0]
                    winner_id = interaction.user.id
                    emb.description = f"{interaction.user.mention} выиграл(a) `{bet}`{self.currency}"
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

    @nextcord.slash_command(name="transfer", description="Перадать валюту другому участнику", guild_ids=[863462268402532363, 934139154290339881])
    async def transfer(
        self,
        interaction: Interaction, 
        value: int = SlashOption(name="value", description="Передаваемая сумма денег", required=True, min_value=1),
        target: nextcord.Member = SlashOption(name="target", description="Кому Вы хотите передать валюту", required=True)
    ):
        memb_id = interaction.user.id
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_shop.db')) as base:
            with closing(base.cursor()) as cur:
                act = self.check_user(base=base, cur=cur, memb_id=memb_id)
                self.check_user(base=base, cur=cur, memb_id=target.id)
                if value > act[1]:
                    emb=Embed(title="Ошибка", description=f"Для совершения перевода Вам не хватает **`{value - act[1]}`**{self.currency}", colour=Colour.red())
                    await interaction.response.send_message(embed=emb)
                else:
                    cur.execute('UPDATE users SET money = money - ? WHERE memb_id = ?', (value, memb_id))
                    base.commit()
                    cur.execute('UPDATE users SET money = money + ? WHERE memb_id = ?', (value, target.id))
                    base.commit()
                    emb=Embed(title="Перевод совершён", description=f"Вы успешно перевели **`{value}`**{self.currency} пользователю {target.mention}", colour=Colour.green())
                    await interaction.response.send_message(embed=emb)
    
    
    """ @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(error) """

def setup(bot: commands.Bot, **kwargs):
  bot.add_cog(shop_commands_slash(bot, **kwargs))
import sqlite3, nextcord
from time import time
from random import randint
from nextcord.ui import Button, View
from nextcord.ext import commands
from nextcord import Embed, Colour, ButtonStyle, SlashOption, Interaction
from contextlib import closing
from datetime import datetime, timedelta, timezone

class bet_slash_r(View):

    def __init__(self, timeout: int, ctx: Interaction, base: sqlite3.Connection, cur: sqlite3.Cursor, symbol: str, bet: int, function: filter):
        super().__init__(timeout=timeout)
        self.base = base
        self.cur = cur
        self.ctx = ctx
        self.symbol = symbol
        self.bet = bet
        self.check_user = function
        self.dueler = None

    @nextcord.ui.button(label="Сделать встречную ставку", style=ButtonStyle.green, emoji="💰", custom_id="Make")
    async def callback_make(self, button: Button, interaction: Interaction):
        if interaction.user == self.ctx.user:
            await interaction.response.send_message("**`Извините, но Вы не можете делать встречную ставку самому себе`**", ephemeral=True)
            return

        member = self.check_user(self.base, self.cur, interaction.user.id)
        if member[1] < self.bet:
            emb = Embed(title="Ошибка", description=f"**`Извините, но Вы не можете сделать встречную ставку, так как Вам не хватает {self.bet-member[1]}`** {self.symbol}", colour=Colour.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        self.dueler = member
        self.stop()   

    @nextcord.ui.button(label="Отменить ставку", style=ButtonStyle.red, emoji="❌", custom_id="Deny")
    async def callback_deny(self, button: Button, interaction: Interaction):
        if interaction.user != self.ctx.user:
            await interaction.response.send_message("**`Извините, но Вы не можете управлять чужой ставкой`**", ephemeral=True)
            return

        emb = Embed(title="Отмена ставки", description="**`Ставка была отменена пользователем`**")
        for button in self.children:
            button.disabled = True
        await interaction.response.edit_message(embed=emb, view=self)
        self.stop()

class bet_slash_e(View):

    def __init__(self, timeout: int, ctx: Interaction, base: sqlite3.Connection, cur: sqlite3.Cursor, symbol: str, bet: int, function: filter):
        super().__init__(timeout=timeout)
        self.base = base
        self.cur = cur
        self.ctx = ctx
        self.symbol = symbol
        self.bet = bet
        self.check_user = function
        self.dueler = None

    @nextcord.ui.button(label="Make a counter bet", style=ButtonStyle.green, emoji="💰", custom_id="Make")
    async def callback_make(self, button: Button, interaction: Interaction):
        if interaction.user == self.ctx.user:
            await interaction.response.send_message("**`Sorry, but you can't make counter bet for yourself`**", ephemeral=True)
            return

        member = self.check_user(self.base, self.cur, interaction.user.id)
        if member[1] < self.bet:
            emb = Embed(title="Error", description=f"**`Sorry, but you can't make counter bet, because you need at least {self.bet-member[1]}`** {self.symbol}", colour=Colour.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        self.dueler = member
        self.stop()   

    @nextcord.ui.button(label="Cancel bet", style=ButtonStyle.red, emoji="❌", custom_id="Deny")
    async def callback_deny(self, button: Button, interaction: Interaction):
        if interaction.user != self.ctx.user:
            await interaction.response.send_message("**`Sorry, but you can't control bet made by another user`**", ephemeral=True)
            return

        emb = Embed(title="Cancelling bet", description="**`Bet was cancelled by user`**")
        for button in self.children:
            button.disabled = True
        await interaction.response.edit_message(embed=emb, view=self)
        self.stop()

""" class view_sell(View):
    def __init__(self, timeout: int, ctx: Interaction):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.is_sold = 0
        global text_sl
        text_sl = {
            'eng' : {
                0 : 'Yes',
                1 : "No, decline sale",
                2 : "**`The sale has been canceled by user`**",
                3 : "**`Sale status has changed`**",
                4 : "You can't manage other's sale"
            },
            'rus' : {
                1 : 'Да',
                2 : "Нет, отменить продажу",
                2 : '**`Продажа отмена пользователем`**',
                3 : "Изменение статуса продажи",
                4 : 'Вы не можете управлять чужой продажей'
            }
        }
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

class store_slash_r(View):
    def __init__(self, timeout: int, outer_store: list, ctx: Interaction, in_row: int, coin: str, tz: int):
        super().__init__(timeout=timeout)
        self.outer_store = outer_store
        self.ctx = ctx
        self.in_row = in_row
        self.sort_d = 0 #by default - sort by price, 1 - sort by date (time)
        self.sort_grad = 0 #возрастание / убывание, от gradation, 0 - возрастание
        self.coin = coin
        self.tz = tz #time zone of the guild
    
    def sort_by(self):
        outer = self.outer_store
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

        self.outer_store = outer
        return

        
    def click(self, interaction: Interaction, click: int, in_row: int):
        text = interaction.message.embeds[0].description
        t1 = text.find('Страница **`')
        t2 = text.find('из', t1)
        counter = int(text[t1+12:t2-4])
        counter = (counter - 1) * in_row
        outer = self.outer_store
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

        store_list = []

        if counter + in_row < len(outer):
            last = counter + in_row
        else:
            last = len(outer)

        tzinfo = timezone(timedelta(hours=self.tz))                
        for r in outer[counter:last]:
            #date = datetime.strptime(r[4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y')
            date = datetime.fromtimestamp(r[4], tz=tzinfo).strftime("%H:%M %d-%m-%Y")
            if r[5] == 1:
                store_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}` {self.coin}\n`Осталось` - `{r[2]}`\n`Последний раз выставленa на продажу:`\n*{date}*\n")
            elif r[5] == 2:
                store_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}` {self.coin}\n`Осталось` - `∞`\n`Последний раз выставленa на продажу:`\n*{date}*\n")
            elif r[5] == 0:
                store_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}` {self.coin}\n`Выставленa на продажу:`\n*{date}*\n")
                
        
        store_list.append(f'\nСтраница **`{(counter // in_row) + 1}`** из **`{(len(outer)+in_row-1)//in_row}`**')
        
        return store_list

    @nextcord.ui.button(emoji="⏮️")
    async def callback_l_end(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=2, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="◀️")
    async def callback_l(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=0, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="▶️")
    async def callback_r(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=1, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="⏭")
    async def callback_r_end(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=3, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(store_list))
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

        store_list=self.click(interaction=interaction, click=4, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(store_list))
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
        
        store_list=self.click(interaction=interaction, click=4, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title='Роли на продажу:', colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb, view=self)

    async def interaction_check(self, interaction):
            if interaction.user != self.ctx.user:
                await interaction.response.send_message('**`Извините, но Вы не можете управлять меню, которое вызвано другим человеком`**', ephemeral=True)
                return False
            return True

class store_slash_e(View):
    def __init__(self, timeout: int, outer_store: list, ctx: Interaction, in_row: int, coin: str, tz: int):
        super().__init__(timeout=timeout)
        self.outer_store = outer_store
        self.ctx = ctx
        self.in_row = in_row
        self.sort_d = 0 #by default - sort by price, 1 - sort by date (time)
        self.sort_grad = 0 #возрастание / убывание, от gradation, 0 - возрастание
        self.coin = coin
        self.tz = tz #time zone of the guild
    
    def sort_by(self):
        outer = self.outer_store
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

        self.outer_store = outer
        return

        
    def click(self, interaction: Interaction, click: int, in_row: int):
        text = interaction.message.embeds[0].description
        t1 = text.find('Page **`')
        t2 = text.find('from', t1)
        counter = int(text[t1+8:t2-4])
        counter = (counter - 1) * in_row
        outer = self.outer_store
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

        store_list = []

        if counter + in_row < len(outer):
            last = counter + in_row
        else:
            last = len(outer)
        tzinfo = timezone(timedelta(hours=self.tz))    
        for r in outer[counter:last]:
            #date = datetime.strptime(r[4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y')
            date = datetime.fromtimestamp(r[4], tz=tzinfo).strftime("%H:%M %d-%m-%Y")
            if r[5] == 1:
                store_list.append(f"**•** <@&{r[1]}>\n`Price` - `{r[3]}` {self.coin}\n`Left` - `{r[2]}`\n`Last listed for sale:`\n*{date}*\n")
            elif r[5] == 2:
                store_list.append(f"**•** <@&{r[1]}>\n`Price` - `{r[3]}` {self.coin}\n`Left` - `∞`\n`Last listed for sale:`\n*{date}*\n")
            elif r[5] == 0:
                store_list.append(f"**•** <@&{r[1]}>\n`Price` - `{r[3]}` {self.coin}\n`Listed for sale:`\n*{date}*\n")
                
        
        store_list.append(f'\Page **`{(counter // in_row) + 1}`** from **`{(len(outer)+in_row-1)//in_row}`**')
        
        return store_list

    @nextcord.ui.button(emoji="⏮️")
    async def callback_l_end(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=2, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title="Roles for sale:", colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="◀️")
    async def callback_l(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=0, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title="Roles for sale:", colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="▶️")
    async def callback_r(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=1, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title="Roles for sale:", colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb)

    @nextcord.ui.button(emoji="⏭")
    async def callback_r_end(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=3, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title="Roles for sale:", colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb)
        

    @nextcord.ui.select(
        placeholder="Sort by...",
        options=[
            nextcord.SelectOption(
                label="Sort by price",
                emoji="💰",
                default=True
            ),
            nextcord.SelectOption(
                label="Sort by date",
                emoji="📅"
            )

        ], 
        min_values=1, 
        max_values=1
    )
    async def callback_select_value(self, menu: nextcord.ui.Select, interaction: Interaction):

        if menu._selected_values[0] == "Sort by price":
            self.sort_d = 0
            self.children[4].options[0].default=True
            self.children[4].options[1].default=False
        else:
            self.sort_d = 1
            self.children[4].options[0].default=False
            self.children[4].options[1].default=True
        self.sort_by()

        store_list=self.click(interaction=interaction, click=4, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title="Roles for sale:", colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb, view=self)

    @nextcord.ui.select(
        placeholder="Sort from...",
        options=[
            nextcord.SelectOption(
                label="From the lower price / newer role",
                emoji="↗️",
                default=True
            ),
            nextcord.SelectOption(
                label="From the higher price / older role",
                emoji="↘️"
            )
        ], 
        min_values=1, 
        max_values=1
    )
    async def callback_select_how(self, menu: nextcord.ui.Select, interaction: Interaction):
        
        if menu._selected_values[0].startswith("From the lower"):
            self.sort_grad = 0
            self.children[5].options[0].default = True
            self.children[5].options[1].default = False
        else:
            self.sort_grad = 1
            self.children[5].options[0].default = False
            self.children[5].options[1].default = True
        self.sort_by()
        
        store_list=self.click(interaction=interaction, click=4, in_row=self.in_row)
        if store_list[0] != "-1":
            emb = Embed(title="Roles for sale:", colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb, view=self)

    async def interaction_check(self, interaction):
            if interaction.user != self.ctx.user:
                await interaction.response.send_message("**`Sorry, but you can't manage menu called by another user`**", ephemeral=True)
                return False
            return True

class buy_slash_r(View):

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
                await interaction.response.send_message('**`Извините, но Вы не можете управлять чужой покупкой`**', ephemeral=True)
                return False
            return True

class buy_slash_e(View):

        def __init__(self, timeout, ctx: Interaction):
            super().__init__(timeout=timeout)
            self.ctx = ctx
            self.value = 0

        @nextcord.ui.button(label='Yes', style=ButtonStyle.green, emoji="✅", custom_id = "second")
        async def agr_callback(self, button: Button, interaction: Interaction):
            self.value = 1
            self.stop()

        @nextcord.ui.button(label="No, cancel purchase", style=ButtonStyle.red, emoji="❌")
        async def decl_callback(self, button: Button, interaction: Interaction):
            button.disabled = True
            button1 = [x for x in self.children if x.custom_id == "second"][0]
            button1.disabled=True
            emb = interaction.message.embeds[0]
            emb.description='**`Purchase was cancelled by user`**'
            await interaction.response.edit_message(embed = emb, view=self)
            self.stop()
            
        async def interaction_check(self, interaction):
            if interaction.user != self.ctx.user:
                await interaction.response.send_message("**`Sorry, but you can't manage other's purchase`**", ephemeral=True)
                return False
            return True

class slash(commands.Cog):

    def __init__(self, bot: commands.Bot, prefix: str, in_row: int, currency: str):
        self.bot = bot
        self.prefix = prefix
        self.in_row = in_row
        self.currency = currency
        global cmds
        cmds = {
            0 : [
                    ("`/store`", "Shows store"), ("`/buy`", "Makes a role purchase"), \
                    ("`/sell`", "Sells the role"), ("`/profile`", "Shows your profile"), \
                    ("`/work`", "Starts working, so you get salary"), ("`/duel`", "Makes a bet"), \
                    ("`/transfer`", "Transfers money to another member"), ("`>>moderation`", "Calls menu with bot's settings")
            ],
            1 : [
                    ("`/store`", "Открывает меню магазина"), ("`/buy`", "Совершает покупку роли"), \
                    ("`/sell`", "Совершает продажу роли"), ("`/profile`", "Показывает меню Вашего профиля"), \
                    ("`/work`", "Начинает работу, за которую Вы полчите заработок"), ("`/duel`", "Делает ставку"), \
                    ("`/transfer`", "Совершает перевод валюты другому пользователю"), ("`>>moderation`", "Вызывает меню команд настройки бота")
            ],
        }

        global text_slash
        text_slash = {
            0 : {
                0 : "Error",
                1 : "I don't have permission to manage roles on the server.",
                2 : "I don't have permission to manage this role. My role should be higher than this role",
                3 : "Commands",
                4 : "**`You already have this role`**",
                5 : "**`This item not found. Please, check if you selected right role`**",
                6 : "**`For purchasing this role you need {} {} more`**",
                7 : "Purchase confirmation",
                8 : "**`Are you sure that you want to buy`** {}?\n{} {} will be debited from your balance",
                9 : "**`Purchase has expired`**",
                10 : "Purchase completed",
                11 : "**`If your DM are open, then purchase confirmation will be message you`**",
                12 : "You successfully bought role `{}` on the server `{}` for `{}` {}",
                13 : "Role purchase",
                14 : "{} bought role {} for {} {}",
                15 : "Roles for sale:",
                16 : "You can't sell the role that you don't have",
                17 : "**`You can't sell that role because it isn't in the list of roles available for purchase/sale on the server`**",
                18 : "The sale is completed",
                19 : "**`You sold role {} for {}`** {}\n**`If your DM are open, then confirmation of sale will be message you`**",
                20 : "Confirmation of sale",
                21 : "**`You sold role {} for {}`** {}",
                22 : "Role sale",
                23 : "{} sold role {} for {} {}",
                24 : "Your balance",
                25 : "**Your personal roles:**\n**Role** --- **Price** --- **Salary** (if it has)",
                26 : "**`Please, wait {} before using this command`**",
                27 : "Success",
                28 : "**`You gained {}`** {}",
                29 : "Work",
                30 : "{} gained {} {}",
                31 : "**`You can't make a bet, because you need {}`** {} **`more`**",
                32 : "Bet",
                33 : "**`You bet {}`** {}\n**`Now another user must make a counter bet`**",
                34 : "**`Time for the counter bet has expired`**",
                35 : "We have a winner!",
                36 : "won",
                37 : "Duel",
                38 : "<@{}> gained {} {}, <@{}> lost",
                39 : "**`Sorry, but for money transfering you need {}`** {} **`more`**",
                40 : "Transaction completed", #title
                41 : "**`You successfully transfered {}`** {} **`to`** {}",
                42 : "Transaction",
                43 : "{} transfered {} {} to {}"
            },
            1 : {
                0 : "Ошибка", #title
                1 : "У меня нет прав управлять ролями на сервере.",
                2 : "У меня нет прав управлять этой ролью. Моя роль должна быть выше, чем указанная Вами роль.",
                3 : "Команды", #title
                4 : "**`У Вас уже есть эта роль`**",
                5 : "**`Такой товар не найден. Пожалуйста, проверьте правильность выбранной роли`**",
                6 : "**`Для покупки роли Вам не хватает {} {}`**",
                7 : "Подтверждение покупки",
                8 : "**`Вы уверены, что хотите купить роль`** {}?\nС Вас будет списано **`{}`** {}",
                9 : '**`Истекло время подтверждения покупки`**',
                10 : "Покупка совершена", #title
                11 : "**`Если у Вас включена возможность получения личных сообщений от участников серверов, то подтверждение покупки будет выслано Вам в личные сообщения`**",
                12 : "Вы успешно купили роль `{}` на сервере `{}` за `{}` {}",
                13 : "Покупка роли",
                14 : "{} купил роль {} за {} {}",
                15 : "Роли на продажу:",
                16 : "**`Вы не можете продать роль, которой у Вас нет`**",
                17 : "**`Продажа этой роли невозможна, т.к. она не находится в списке ролей, доступных для покупки/продажи на сервере`**",
                18 : "Продажа совершена", #title
                19 : "**`Вы продали роль {} за {}`** {}\n**`Если у Вас включена возможность получения личных сообщений от участников серверов, \
                    то подтверждение покупки будет выслано Вам в личные сообщения`**",
                20 : "Подтверждение продажи",
                21 : "**`Вы продали роль {} за {}`** {}",
                22 : "Продажа роли",
                23 : "{} продал роль {} за {} {}",
                24 : "Ваш баланс",
                25 : "**Ваши личные роли:**\n**Роль** --- **Цена** --- **Доход** (если есть)",
                26 : "**`Пожалуйста, подождите {} перед тем, как снова использовать эту команду`**",
                27 : "Успех",
                28 : "**`Вы заработали {}`** {}",
                29 : "Работа",
                30 : "{} заработал {} {}",
                31 : "**`Вы не можете сделать ставку, так как Вам не хватает {}`** {}",
                32 : "Ставка",
                33 : "**`Вы сделали ставку в размере {}`** {}\n**`Теперь кто-то должен принять Ваш вызов`**",
                34 : "**`Истекло время ожидания встречной ставки`**",
                35 : "У нас победитель!",
                36 : "выиграл(a)",
                37 : "Дуэль",
                38 : "<@{}> заработал(a) {} {}, <@{}> - проиграл(a)",
                39 : "**`Извините, но для совершения перевода Вам не хватает {}`** {}",
                40 : "Перевод совершён",
                41 : "**`Вы успешно перевели {}`** {} **`пользователю`** {}",
                42 : "Транзакция",
                43 : "{} передал {} {} пользователю {}"


            }
        }
    
    async def can_role(self, interaction: Interaction, role: nextcord.Role, lng: int):
        
        if not interaction.guild.me.guild_permissions.manage_roles:
            emb = Embed(title=text_slash[lng][0], colour=Colour.red(), description=text_slash[lng][1])
            await interaction.response.send_message(embed=emb)
            return 0

        elif not role.is_assignable():
            emb = Embed(title=text_slash[lng][0], colour=Colour.red(), description=text_slash[lng][2])
            await interaction.response.send_message(embed=emb)
            return 0
        
        return 1


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
    

    @nextcord.slash_command(name="help", description="Calls menu with commands | Вызывает меню команд")
    async def help(self, interaction: Interaction):
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_store.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                emb = Embed(title=text_slash[lng][3], colour=Colour.dark_purple())
                for n, v in cmds[lng]:
                    emb.add_field(name=n, value=v, inline=False)
                await interaction.response.send_message(embed=emb)
    
    
    @nextcord.slash_command(name="buy", description="Makes a role purchase from the store | Совершает покупку роли из магазина", guild_ids=[])
    async def buy(self, interaction: Interaction, role: nextcord.Role = SlashOption(name="role", description="Role that you want to buy | Роль, которую Вы хотите купить", required=True)):
        
        if not await self.can_role(interaction=interaction, role=role):
            return

        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_store.db')) as base:
            with closing(base.cursor()) as cur:

                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                member_buyer = interaction.user
                if role in member_buyer.roles:
                    emb = Embed(title=text_slash[lng][0], description=text_slash[lng][4], colour=Colour.red())
                    await interaction.response.send_message(embed=emb)
                    return
                
                outer = cur.execute('SELECT * FROM outer_store WHERE role_id = ?', (role.id,)).fetchone()
                if outer == [] or outer == None:
                    await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], description=text_slash[lng][5], colour=Colour.red()))
                    return

                role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()

                memb_id = member_buyer.id
                buyer = self.check_user(base=base, cur=cur, memb_id=memb_id)
                buyer_cash = buyer[1]
                cost = role_info[1]
                if buyer_cash < cost:
                    emb = Embed(title=text_slash[lng][0], colour=Colour.red(), description=f"{text_slash[lng][6].format(cost - buyer_cash, self.currency)}")
                    await interaction.response.send_message(embed=emb)
                    return

                emb = Embed(title=text_slash[lng][7], description=text_slash[lng][8].format(role.mention, cost, self.currency))
                if lng == 0:
                    view = buy_slash_e(timeout=30, ctx=interaction)
                else:
                    view = buy_slash_r(timeout=30, ctx=interaction)
                await interaction.response.send_message(embed=emb, view=view)
                msg = await interaction.original_message()

                chk = await view.wait()
                if chk:
                    for button in view.children:
                        button.disabled = True
                    emb.description = text_slash[lng][9]
                    await msg.edit(embed = emb, view=view)
                    return
                
                if view.value:
                    
                    is_special = role_info[2]
                    if is_special == 0:
                        outer = None
                        special_roles = cur.execute('SELECT * FROM outer_store WHERE role_id = ?', (role.id,)).fetchall()
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
                        item_id = cur.execute('SELECT item_id FROM outer_store WHERE role_id = ?', (role.id,)).fetchone()[0]
                        cur.execute('DELETE FROM outer_store WHERE item_id = ?', (item_id,))
                        base.commit()
                    elif is_special == 1:
                        cur.execute('UPDATE outer_store SET quantity = quantity - ? WHERE role_id = ?', (1, role.id))
                        base.commit()

                    emb.title = text_slash[lng][10]
                    emb.description = text_slash[lng][11]
                    await msg.edit(embed=emb, view=None)

                    try:
                        emb = Embed(title=text_slash[lng][7], description=text_slash[lng][12].format(role.name, interaction.guild.name, cost, self.currency), colour=Colour.green())
                        await member_buyer.send(embed=emb)
                    except:
                        pass

                    chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'log_channel'").fetchone()[0]
                    if chnl_id != 0:
                        try:
                            channel = interaction.guild.get_channel(chnl_id)
                            await channel.send(embed=Embed(title=text_slash[lng][13], description=text_slash[lng][14].format(interaction.user.mention, role.mention, cost, self.currency)))
                        except:
                            pass
                    
                    
    @nextcord.slash_command(name="store", description="Shows store | Открывает меню магазина", guild_ids=[])
    async def store(self, interaction: Interaction):
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_store.db')) as base:
            with closing(base.cursor()) as cur:
                in_row = self.in_row
                counter = 0
                store_list = []
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                tz = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]
                outer_list = cur.execute('SELECT * FROM outer_store').fetchall()
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
                tzinfo = timezone(timedelta(hours=tz))
                if lng == 0:
                    for r in outer_list[counter:counter+in_row]:
                        #date = datetime.strptime(r[4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y')
                        date = datetime.fromtimestamp(r[4], tz=tzinfo).strftime("%H:%M %d-%m-%Y")
                        if r[5] == 1:
                            store_list.append(f"**•** <@&{r[1]}>\n`Price` - `{r[3]}` {self.currency}\n`Left` - `{r[2]}`\n`Last listed for sale:`\n*{date}*\n")
                        elif r[5] == 2:
                            store_list.append(f"**•** <@&{r[1]}>\n`Price` - `{r[3]}` {self.currency}\n`Left` - `∞`\n`Last listed for sale:`\n*{date}*\n")
                        elif r[5] == 0:
                            store_list.append(f"**•** <@&{r[1]}>\n`Price` - `{r[3]}` {self.currency}\n`Listed for sale:`\n*{date}*\n")
                    store_list.append(f'\nСтраница **`1`** из **`{(len(outer_list)+in_row-1)//in_row}`**')
                else:
                    for r in outer_list[counter:counter+in_row]:
                        #date = datetime.strptime(r[4], '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y')
                        date = datetime.fromtimestamp(r[4], tz=tzinfo).strftime("%H:%M %d-%m-%Y")
                        if r[5] == 1:
                            store_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}` {self.currency}\n`Осталось` - `{r[2]}`\n`Последний раз выставленa на продажу:`\n*{date}*\n")
                        elif r[5] == 2:
                            store_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}` {self.currency}\n`Осталось` - `∞`\n`Последний раз выставленa на продажу:`\n*{date}*\n")
                        elif r[5] == 0:
                            store_list.append(f"**•** <@&{r[1]}>\n`Цена` - `{r[3]}` {self.currency}\n`Выставленa на продажу:`\n*{date}*\n")
                    store_list.append(f'\nPage **`1`** from **`{(len(outer_list)+in_row-1)//in_row}`**')

                emb = Embed(title=text_slash[lng][15], colour=Colour.dark_gray(), description='\n'.join(store_list))
                if lng == 0:
                    myview_store = store_slash_e(timeout=60, outer_store=outer_list, ctx=interaction, in_row=3, coin=self.currency, tz=tz)
                else:
                    myview_store = store_slash_r(timeout=60, outer_store=outer_list, ctx=interaction, in_row=3, coin=self.currency, tz=tz)
                await interaction.response.send_message(embed=emb, view=myview_store)
                msg = await interaction.original_message()
                chk = await myview_store.wait()
                if chk:
                    for button in myview_store.children:
                        button.disabled = True
                    await msg.edit(view=myview_store)
    
    
    @nextcord.slash_command(name="sell", description="Sells the role | Совершает продажу роли", guild_ids=[])
    async def sell(
        self,
        interaction: Interaction,
        role: nextcord.Role = SlashOption(name="role", description="Your role that you want to sell | Ваша роль, которую Вы хотите продать", required=True),
    ):
        if not role in interaction.user.roles:
            await interaction.response.send_message(embed=Embed(
                colour=Colour.red(),
                title=text_slash[lng][0],
                description=text_slash[lng][16]
            ))
            return
        
        if not await self.can_role(interaction=interaction, role=role):
            return

        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_store.db')) as base:
            with closing(base.cursor()) as cur:
                role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()
                if role_info == None:
                    await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], description=text_slash[lng][17], colour=Colour.red()))
                    return

                memb_id = interaction.user.id
                user = self.check_user(base=base, cur=cur, memb_id=memb_id)

                #time_now = (datetime.utcnow() + timedelta(hours=3)).strftime('%S/%M/%H/%d/%m/%Y')
                
                role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()
                owned_roles = user[2]
                cur.execute('UPDATE users SET owned_roles = ?, money = money + ? WHERE memb_id = ?', (owned_roles.replace(f"#{role.id}", ""), role_info[1], memb_id))
                base.commit()
                outer  = cur.execute('SELECT * FROM outer_store WHERE role_id = ?', (role.id,)).fetchone()      
                time_now = int(time())
                if role_info[2] == 1:                   
                    if outer == None:
                        item_ids = [x[0] for x in cur.execute('SELECT item_id FROM outer_store').fetchall()]
                        item_ids.sort()
                        free_id = 1
                        while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                            free_id += 1
                        cur.execute('INSERT INTO outer_store(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, 1, role_info[1], time_now, 1))
                        base.commit()            
                    else:
                        cur.execute('UPDATE outer_store SET quantity = quantity + ?, last_date = ? WHERE role_id = ?', (1, time_now, role.id))
                        base.commit()
                elif role_info[2] == 2:
                    if outer == None:
                        item_ids = [x[0] for x in cur.execute('SELECT item_id FROM outer_store').fetchall()]
                        item_ids.sort()
                        free_id = 1
                        while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                            free_id += 1
                        cur.execute('INSERT INTO outer_store(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, -404, role_info[1], time_now, 2))
                        base.commit()

                elif role_info[2] == 0:
                    
                    item_ids = [x[0] for x in cur.execute('SELECT item_id FROM outer_store').fetchall()]
                    item_ids.sort()
                    free_id = 1
                    while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
                        free_id += 1
                    cur.execute('INSERT INTO outer_store(item_id, role_id, quantity, price, last_date, special) VALUES(?, ?, ?, ?, ?, ?)', (free_id, role.id, 1, role_info[1], time_now, 0))
                    base.commit()

                    membs = cur.execute("SELECT members FROM money_roles WHERE role_id = ?", (role.id,)).fetchone()
                    if membs != None and membs[0] != None:
                        cur.execute("UPDATE money_roles SET members = ? WHERE role_id = ?", (membs[0].replace(f"#{memb_id}", ""), role.id))
                        base.commit()

                await interaction.user.remove_roles(role)
                emb = Embed(title=text_slash[lng][18], description=text_slash[lng][19].format(role.mention, role_info[1], self.currency), colour=Colour.gold())
                await interaction.response.send_message(embed=emb)

                try:
                    emb = Embed(title=text_slash[lng][20], description=text_slash[lng][20].format(role.id, role_info[1], self.currency), colour=Colour.green())
                    await interaction.user.send(embed=emb)
                except:
                    pass

                chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'log_channel'").fetchone()[0]
                if chnl_id != 0:
                    try:
                        channel = interaction.guild.get_channel(chnl_id)
                        await channel.send(embed=Embed(title=text_slash[lng][22], description=text_slash[lng][23].format(interaction.user.mention, role.mention, role_info[1])))
                    except:
                        pass


    @nextcord.slash_command(name="profile", description="Show your profile | Показывает меню Вашего профиля", guild_ids=[])
    async def profile(self, interaction: Interaction):
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_store.db')) as base:
            with closing(base.cursor()) as cur:
                memb_id = interaction.user.id
                member = self.check_user(base=base, cur=cur, memb_id=memb_id)
                server_roles = cur.execute('SELECT role_id FROM server_roles').fetchall()
                server_roles = set([x[0] for x in server_roles]) #ids of roles that user might has, set for quick searching in
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                emb = Embed(title=text_slash[lng][24])
                roles = ""
                uniq_roles = []
                descr = []
                descr.append(f'**{text_slash[lng][24]}** `{member[1]}`{self.currency}\n')
                flag = 0
                for role_g in interaction.user.roles:
                    id = role_g.id
                    if id in server_roles:
                        if flag == 0:
                            descr.append(text_slash[lng][25])
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
                        f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [command /profile] [user: {memb_id}] [{str(E)}]\n")

                if flag:
                    cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', (roles, interaction.user.id))
                    base.commit()
                emb.description = "\n".join(descr)
                await interaction.response.send_message(embed=emb)


    @nextcord.slash_command(name="work", description="Allows to gain money | Позволяет заработать деньги", guild_ids=[])
    async def work(self, interaction: Interaction):
        memb_id = interaction.user.id
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_store.db')) as base:
            with closing(base.cursor()) as cur:
                time_reload = cur.execute("SELECT value FROM server_info WHERE settings = 'time_r'").fetchone()[0]
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                member = self.check_user(base=base, cur=cur, memb_id=memb_id)
                flag = 0
                if member[3] == 0:
                    flag = 1
                else:
                    #lasted_time = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") + \
                    #    timedelta(hours=3) - datetime.strptime(member[3], '%S/%M/%H/%d/%m/%Y')
                    lasted_time = int(time()) - member[3]
                    if lasted_time >= time_reload:
                        flag = 1
                if not flag:
                    time_l = time_reload - lasted_time
                    t_l = f"{time_l // 3600}:{(time_l % 3600)//60}:{time_l % 60}"
                    await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], description=text_slash[lng][26].format(t_l)))
                    return 
                sal_l = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_l'").fetchone()[0]
                sal_r = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_r'").fetchone()[0]
                salary = randint(sal_l, sal_r)
                cur.execute('UPDATE users SET money = money + ?, work_date = ? WHERE memb_id = ?', (salary, int(time()), memb_id))
                base.commit()
                await interaction.response.send_message(embed=Embed(title=text_slash[lng][27], description=text_slash[lng][28].format(salary, self.currency), colour=Colour.gold()))

                chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'log_channel'").fetchone()[0]
                if chnl_id != 0:
                    try:
                        channel = interaction.guild.get_channel(chnl_id)
                        await channel.send(embed=Embed(title=text_slash[lng][29], description=text_slash[lng][30].format(interaction.user.mention, salary)))
                    except:
                        pass


    @nextcord.slash_command(name="duel", description="Make a bet | Сделать ставку", guild_ids=[])
    async def duel(self, interaction: Interaction, amount: int = SlashOption(name="amount", description="Bet amount | Сумма ставки", required=True, min_value=1)): 

        memb_id = interaction.user.id
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_store.db')) as base:
            with closing(base.cursor()) as cur:
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                member = self.check_user(base=base, cur=cur, memb_id=memb_id)
                if amount > member[1]:
                    await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], description=text_slash[lng][31].format(amount - member[1], self.currency), colour=Colour.red()), ephemeral=True)
                    return
                if lng == 0:
                    betview = bet_slash_e(timeout=30, ctx=interaction, base=base, cur=cur, symbol=self.currency, bet=amount, function=self.check_user)
                else:
                    betview = bet_slash_r(timeout=30, ctx=interaction, base=base, cur=cur, symbol=self.currency, bet=amount, function=self.check_user)
                emb = Embed(title=text_slash[lng][32], description=text_slash[lng][33].format(amount, self.currency))
                await interaction.response.send_message(embed=emb, view=betview)
                msg = await interaction.original_message()

                chk = await betview.wait()

                if chk:
                    for button in betview.children:
                        button.disabled = True
                    emb.description = text_slash[lng][34]
                    await msg.edit(embed = emb, view=betview)
                    return
                
                if betview.dueler == None:
                    return

                msg = await interaction.original_message()
                dueler = betview.dueler

                winner = randint(0, 1)
                emb = Embed(title=text_slash[lng][35], colour=Colour.gold())
                if winner:
                    loser_id = dueler[0]
                    winner_id = interaction.user.id
                    emb.description = f"{interaction.user.mention} {text_slash[lng][36]} `{amount}`{self.currency}"
                    
                else:
                    winner_id = dueler[0]
                    loser_id = interaction.user.id
                    emb.description = f"<@{dueler[0]}> {text_slash[lng][36]} `{amount}`{self.currency}"        

                cur.execute('UPDATE users SET money = money - ? WHERE memb_id = ?', (amount, loser_id))
                base.commit()
                cur.execute('UPDATE users SET money = money + ? WHERE memb_id = ?', (amount, winner_id))
                base.commit()
                for button in betview.children:
                    button.disabled = True
                await msg.edit(embed=emb, view=betview)

                chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'log_channel'").fetchone()[0]
                if chnl_id != 0:
                    try:
                        channel = interaction.guild.get_channel(chnl_id)
                        await channel.send(embed=Embed(title=text_slash[lng][37], description=text_slash[lng][38].format(winner_id, amount, self.currency, loser_id)))
                    except:
                        pass


    @nextcord.slash_command(name="transfer", description="Transfers money to another member | Совершает перевод валюты другому пользователю", guild_ids=[])
    async def transfer(
        self,
        interaction: Interaction, 
        value: int = SlashOption(name="value", description="Amount of money to transfer | Переводимая сумма денег", required=True, min_value=1),
        target: nextcord.Member = SlashOption(name="target", description="The member you want to transfer money to | Пользователь, которому Вы хотите перевести деньги", required=True)
    ):
        memb_id = interaction.user.id
        with closing(sqlite3.connect(f'./bases_{interaction.guild.id}/{interaction.guild.id}_store.db')) as base:
            with closing(base.cursor()) as cur:
                act = self.check_user(base=base, cur=cur, memb_id=memb_id)
                self.check_user(base=base, cur=cur, memb_id=target.id)
                lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                if value > act[1]:
                    emb=Embed(title=text_slash[lng][0], description=text_slash[lng][39].format(value - act[1], self.currency), colour=Colour.red())
                    await interaction.response.send_message(embed=emb)
                else:
                    cur.execute('UPDATE users SET money = money - ? WHERE memb_id = ?', (value, memb_id))
                    base.commit()
                    cur.execute('UPDATE users SET money = money + ? WHERE memb_id = ?', (value, target.id))
                    base.commit()
                    emb=Embed(title=text_slash[lng][40], description=text_slash[lng][41].format(value, self.currency, target.mention), colour=Colour.green())
                    await interaction.response.send_message(embed=emb)

                    chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'log_channel'").fetchone()[0]
                    if chnl_id != 0:
                        try:
                            channel = interaction.guild.get_channel(chnl_id)
                            await channel.send(embed=Embed(title=text_slash[lng][42], description= text_slash[lng][43].format(interaction.user.mention, value, self.currency, target.mention)))
                        except:
                            pass
    
    
    @commands.Cog.listener()
    async def on_application_command_error(self, interaction, exception):
        with open("d.log", "a+", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().__add__(timedelta(hours=3))}] [ERROR] [slash command] [{str(exception)}]\n")

def setup(bot: commands.Bot, **kwargs):
  bot.add_cog(slash(bot, **kwargs))
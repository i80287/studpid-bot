
from sqlite3 import Connection, Cursor, connect
from contextlib import closing
from datetime import datetime, timedelta, timezone
from time import time
from random import randint

from nextcord.ext import commands
from nextcord import Embed, Colour, ButtonStyle, SlashOption, Interaction, Locale, ui, SelectOption, slash_command, Role, Member
from nextcord.ui import Button, View, Select

from config import path_to, bot_guilds_e, bot_guilds_r, currency, in_row

common_text = {
    0 : {
        0 : "**`Sorry, but you can't manage menu called by another member`**"
    },
    1 : {
        0 : "**`Извините, но Вы не можете управлять чужой покупкой`**"
    }
}

text_slash = {
    0 : {
        0 : "Error",
        1 : "**`I don't have permission to manage roles on the server`**",
        2 : "**`I don't have permission to manage this role. My role should be higher than this role`**",
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
        16 : "**`You can't sell the role that you don't have`**",
        17 : "**`You can't sell that role because it isn't in the list of roles available for purchase/sale on the server`**",
        18 : "The sale is completed",
        19 : "**`You sold role `**{}**` for {}`** {}\n**`If your DM are open, then confirmation of sale will be message you`**",
        20 : "Confirmation of sale",
        21 : "**`You sold role {} for {}`** {}",
        22 : "Role sale",
        23 : "{} sold role {} for {} {}",
        24 : "Your balance",
        25 : "**Your personal roles:**\n--- **Role** --- **Price** --- **Salary** (if it has)",
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
        1 : "**`У меня нет прав управлять ролями на сервере`**",
        2 : "**`У меня нет прав управлять этой ролью. Моя роль должна быть выше, чем указанная Вами роль`**",
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
        19 : "**`Вы продали роль `**{}**` за {}`** {}\n**`Если у Вас включена возможность получения личных сообщений от участников серверов, \
            то подтверждение покупки будет выслано Вам в личные сообщения`**",
        20 : "Подтверждение продажи",
        21 : "**`Вы продали роль {} за {}`** {}",
        22 : "Продажа роли",
        23 : "{} продал роль {} за {} {}",
        24 : "Ваш баланс",
        25 : "**Ваши личные роли:**\n--- **Роль** --- **Цена** --- **Доход** (если есть)",
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

buy_approve_text = {
    0 : {
        0 : "Yes",
        1 : "No, cancel purchase"
    },
    1 : {
        0 : "Да",
        1 : "Нет, отменить покупку"
    }
}

store_text = {
    0 : {
        0 : "**•** <@&{}>\n`Price` - `{}` {}\n`Listed for sale:`\n*{}*\n",
        1 : "**•** <@&{}>\n`Price` - `{}` {}\n`Left` - `{}`\n`Last listed for sale:`\n*{}*\n",
        2 : "`Average salary per week` - `{}` {}\n",
        3 : "Page **`{}`** from **`{}`**",
        4 : "Sort by...",
        5 : "Sort by price",
        6 : "Sort by date",
        7 : "Sort from...",
        8 : "From the lower price / newer role",
        9 : "From the higher price / older role",
        10 : "Roles for sale:"

    },
    1 : {
        0 : "**•** <@&{}>\n`Цена` - `{}` {}\n`Выставленa на продажу:`\n*{}*\n",
        1 : "**•** <@&{}>\n`Цена` - `{}` {}\n`Осталось` - `{}`\n`Последний раз выставленa на продажу:`\n*{}*\n",
        2 : "`Средний доход за неделю` - `{}` {}\n",
        3 : "Страница **`{}`** из **`{}`**",
        4 : "Сортировать по...",
        5 : "Сортировать по цене",
        6 : "Сортировать по дате",
        7 : "Сортировать от...",
        8 : "От меньшей цены / более свежого товара",
        9 : "От большей цены / более старого товара",
        10 : "Роли на продажу:"
    }
}

class c_button(Button):

    def __init__(self, label: str, custom_id: str, style = ButtonStyle.secondary, emoji = None):
        super().__init__(style=style, label=label, custom_id=custom_id, emoji=emoji)
    
    async def callback(self, interaction: Interaction) -> None:
        await self.view.click_b(interaction, self.custom_id)


class c_select(Select):

    def __init__(self, custom_id: str, placeholder: str, opts: list) -> None:
        super().__init__(custom_id=custom_id, placeholder=placeholder, options=opts)
    
    async def callback(self, interaction: Interaction):
        await self.view.click_menu(interaction, self.custom_id, self.values)     


class bet_slash_r(View):

    def __init__(self, timeout: int, ctx: Interaction, base: Connection, cur: Cursor, symbol: str, bet: int, function: filter):
        super().__init__(timeout=timeout)
        self.base = base
        self.cur = cur
        self.ctx = ctx
        self.symbol = symbol
        self.bet = bet
        self.check_user = function
        self.dueler = None

    @ui.button(label="Сделать встречную ставку", style=ButtonStyle.green, emoji="💰", custom_id="Make")
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

    @ui.button(label="Отменить ставку", style=ButtonStyle.red, emoji="❌", custom_id="Deny")
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

    def __init__(self, timeout: int, ctx: Interaction, base: Connection, cur: Cursor, symbol: str, bet: int, function: filter):
        super().__init__(timeout=timeout)
        self.base = base
        self.cur = cur
        self.ctx = ctx
        self.symbol = symbol
        self.bet = bet
        self.check_user = function
        self.dueler = None

    @ui.button(label="Make a counter bet", style=ButtonStyle.green, emoji="💰", custom_id="Make")
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

    @ui.button(label="Cancel bet", style=ButtonStyle.red, emoji="❌", custom_id="Deny")
    async def callback_deny(self, button: Button, interaction: Interaction):
        if interaction.user != self.ctx.user:
            await interaction.response.send_message("**`Sorry, but you can't control bet made by another user`**", ephemeral=True)
            return

        emb = Embed(title="Cancelling bet", description="**`Bet was cancelled by user`**")
        for button in self.children:
            button.disabled = True
        await interaction.response.edit_message(embed=emb, view=self)
        self.stop()


class store_slash_view(View):

    def __init__(self, timeout: int, db_store: list, auth_id: int, lng: int, in_row: int, coin: str, tz: int):
        super().__init__(timeout=timeout)
        self.db_store = db_store
        self.l = len(db_store)
        self.auth_id = auth_id
        self.in_row = in_row
        self.coin = coin
        self.tz = tz # time zone of the guild
        self.sort_by = True # True - sort by price, False - sort by date (time)
        self.reversed = False # возрастание / убывание при сортировке, False - возрастание
        

        self.add_item(c_button(label="", custom_id=f"32_{auth_id}_{randint(1, 100)}", emoji="⏮️"))
        self.add_item(c_button(label="", custom_id=f"33_{auth_id}_{randint(1, 100)}", emoji="◀️"))
        self.add_item(c_button(label="", custom_id=f"34_{auth_id}_{randint(1, 100)}", emoji="▶️"))
        self.add_item(c_button(label="", custom_id=f"35_{auth_id}_{randint(1, 100)}", emoji="⏭"))

        opts = [
            SelectOption(
                label=store_text[lng][5],
                value=0,
                emoji="💰",
                default=True
            ),
            SelectOption(
                label=store_text[lng][6],
                value=1,
                emoji="📅",
                default=False
            )
        ]
        self.add_item(c_select(custom_id=f"102_{auth_id}_{randint(1, 100)}", placeholder=store_text[lng][4], opts=opts))
        opts = [
            SelectOption(
                label=store_text[lng][8],
                value=0,
                emoji="↗️",
                default=True
            ),
            SelectOption(
                label=store_text[lng][9],
                value=1,
                emoji="↘️",
                default=False
            )
        ]
        self.add_item(c_select(custom_id=f"103_{auth_id}_{randint(1, 100)}", placeholder=store_text[lng][7], opts=opts))
        

    def sort_store(self) -> None:
        
        sort_by = self.sort_by

        if self.reversed:
            if sort_by:
                # Reversed sort by price, from higher to lower. 
                # If prices are equal sort by date from higher to lower (latest is higher, early date is lower)
                # tup[2] - price of the role, tup[3] - last date of adding role to the store
                self.db_store.sort(key=lambda tup: (tup[2], tup[3]), reverse=True)
            else:
                # Reversed sort by date from lower to higher (early date is lower, goes first) 
                # If dates are equal then item with lower price goes first
                # tup[2] - price of the role, tup[3] - last date of adding role to the store. If dates are equal
                self.db_store.sort(key=lambda tup: (tup[3], tup[2]), reverse=False)
            return
        
        # If sort is not reversed
        store = self.db_store
        l = self.l // 2

        if sort_by:
            # Sort by price from lower to higher 
            # If prices are equal sort by date from higher to lower (latest is higher, early date is lower)
            
            # Shell sort
            while l:
                for i in range(l, self.l):
                    moving_item = store[i]
                    while i >= l and (store[i-l][2] > store[i][2] or (store[i-l][2] == store[i][2] and store[i-l][3] < store[i][3])):
                        store[i] = store[i - l]
                        i -= l
                        store[i] = moving_item
                l //= 2
            self.db_store = store
        else:
            # Sort by date from higher to lower (latest is higher, early date is lower)
            # If dates are equal then item with lower price goes first
            
            # Shell sort
            while l:
                for i in range(l, self.l):
                    moving_item = store[i]
                    while i >= l and (store[i-l][3] < store[i][3] or (store[i-l][3] == store[i][3] and store[i-l][2] > store[i][2])):
                        store[i] = store[i - l]
                        i -= l
                        store[i] = moving_item
                l //= 2
            self.db_store = store


    def update_menu(self, interaction: Interaction, lng: int, click: int, in_row: int) -> list:
        text = interaction.message.embeds[0].description

        if lng == 0:
            t1 = text.find('Page **`')
            t2 = text.find('from', t1)
            counter = int(text[t1+8:t2-4])
        elif lng == 1:
            t1 = text.find('Страница **`')
            t2 = text.find('из', t1)
            counter = int(text[t1+12:t2-4])
        
        counter = (counter - 1) * in_row
        db_store = self.db_store

        if counter < 0 or counter >= self.l:
            return []
        if click == 1:
            if counter == 0:
                return []
            counter -= in_row
        elif click == 2:
            if counter == (self.l + in_row - 1) // in_row * in_row - in_row:
                return []
            counter += in_row
        elif click == 0:
            counter = 0
        elif click == 3:
            counter = (self.l + in_row - 1) // in_row * in_row - in_row

        store_list = []
        tzinfo = timezone(timedelta(hours=self.tz))

        for r, q, p, d, s, s_t, tp in db_store[counter:min(counter + in_row, self.l)]:
            date = datetime.fromtimestamp(d, tz=tzinfo).strftime("%H:%M %d-%m-%Y")
            if tp == 1:
                r_inf = store_text[lng][0].format(r, p, currency, date)
            elif tp == 2:
                r_inf = store_text[lng][0].format(r, p, currency, q, date)
            elif tp == 3:
                r_inf = store_text[lng][0].format(r, p, currency, "∞", date)
            if s:
                r_inf += store_text[lng][2].format(s * 604800 // s_t, currency)
            store_list.append(r_inf)
        
        if self.l:
            store_list.append(store_text[lng][3].format((counter // in_row) + 1, (self.l + in_row - 1) // in_row))
        else:
            store_list.append(store_text[lng][3].format(1, 1))
        
        return store_list


    async def click_b(self, interaction: Interaction, c_id: str):
        lng = 1 if "ru" in interaction.locale else 0

        click = 4
        if c_id.startswith("32_"):
            click = 0
        elif c_id.startswith("33_"):
            click = 1
        elif c_id.startswith("34_"):
            click = 2
        elif c_id.startswith("35_"):
            click = 3

        store_list=self.update_menu(interaction=interaction, lng=lng, click=click, in_row=self.in_row)
        if store_list:
            emb = Embed(title=store_text[lng][10], colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb)


    async def click_menu(self, interaction: Interaction, c_id: str, value):
        lng = 1 if "ru" in interaction.locale else 0

        if c_id.startswith("102_"):
            if int(value[0]):
                self.sort_by = False
                self.children[4].options[0].default=False
                self.children[4].options[1].default=True
            else:
                self.sort_by = True
                self.children[4].options[0].default=True
                self.children[4].options[1].default=False

        elif c_id.startswith("103_"):
            if int(value[0]):
                self.reversed = True
                self.children[5].options[0].default=False
                self.children[5].options[1].default=True
            else:
                self.reversed = False
                self.children[5].options[0].default=True
                self.children[5].options[1].default=False
        
        self.sort_store()
        store_list = self.update_menu(interaction=interaction, lng=lng, click=4, in_row=self.in_row)
        if store_list:
            emb = Embed(title=store_text[lng][10], colour=Colour.dark_gray(), description='\n'.join(store_list))
            await interaction.response.edit_message(embed=emb, view=self)


class buy_slash(View):

        def __init__(self, timeout: int, auth_id: int, lng: int):
            super().__init__(timeout=timeout)
            self.auth_id = auth_id
            self.value = False
            self.add_item(c_button(label=buy_approve_text[lng][0], custom_id=f"30_{auth_id}_{randint(1, 100)}", style=ButtonStyle.green, emoji="✅"))
            self.add_item(c_button(label=buy_approve_text[lng][1], custom_id=f"31_{auth_id}_{randint(1, 100)}", style=ButtonStyle.red, emoji="❌"))

        async def click_b(self, _, c_id: str):
            if c_id.startswith("30_"):
                self.value = True
                self.stop()
            elif c_id.startswith("31_"):
                self.stop()
            
        async def interaction_check(self, interaction) -> bool:
            if interaction.user.id != self.auth_id:
                lng = 1 if "ru" in interaction.locale else 0
                await interaction.response.send_message(common_text[lng][0], ephemeral=True)
                return False
            return True

class rating_slash_r(View):
    def __init__(self, timeout, membs: list, in_row: int, curr: str, auth_id: int):
        super().__init__(timeout=timeout)
        self.membs = membs
        self.pages = (len(membs) + in_row - 1) // in_row
        self.curr = curr
        self.in_row = in_row
        self.auth_id = auth_id
    
    def click(self, interaction: Interaction, click: int, in_row: int):
        text = interaction.message.embeds[0].footer.text
        t1 = text.find("Страница ")
        t2 = text.find(" из")
        page = int(text[t1+9:t2])
        if click <= 1 and page == 1:
            return []
        elif click >= 2 and page == self.pages:
            return []
        if click == 0:
            page = 1
        elif click == 3:
            page = self.pages
        elif click == 1:
            page -= 1
        elif click == 2:
            page += 1
        msg = []
        counter = (page-1) * in_row + 1
        for r in self.membs[(page-1) * in_row:min(page * in_row, len(self.membs))]:
            msg.append((f"{counter} место", f"<@{r[0]}>\n{r[1]} {self.curr}"))
            counter += 1
        msg.append((f"Страница {page} из {self.pages}", ""))
        return msg


    @ui.button(emoji="⏮️")
    async def callback_l_top(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=0, in_row=self.in_row)
        if store_list != []:
            emb = Embed(title="Топ пользователей по балансу", colour=Colour.dark_gray())
            emb.set_footer(text=store_list[-1][0])
            for r in store_list[:-1]:
                emb.add_field(name=r[0], value=r[1], inline=False)
            await interaction.response.edit_message(embed=emb)

    @ui.button(emoji="◀️")
    async def callback_l(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=1, in_row=self.in_row)
        if store_list != []:
            emb = Embed(title="Топ пользователей по балансу", colour=Colour.dark_gray())
            emb.set_footer(text=store_list[-1][0])
            for r in store_list[:-1]:
                emb.add_field(name=r[0], value=r[1], inline=False)
            await interaction.response.edit_message(embed=emb)

    @ui.button(emoji="▶️")
    async def callback_r(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=2, in_row=self.in_row)
        if store_list != []:
            emb = Embed(title="Топ пользователей по балансу", colour=Colour.dark_gray())
            emb.set_footer(text=store_list[-1][0])
            for r in store_list[:-1]:
                emb.add_field(name=r[0], value=r[1], inline=False)
            await interaction.response.edit_message(embed=emb)

    @ui.button(emoji="⏭")
    async def callback_r_top(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=3, in_row=self.in_row)
        if store_list != []:
            emb = Embed(title="Топ пользователей по балансу", colour=Colour.dark_gray())
            emb.set_footer(text=store_list[-1][0])
            for r in store_list[:-1]:
                emb.add_field(name=r[0], value=r[1], inline=False)
            await interaction.response.edit_message(embed=emb)

    async def interaction_check(self, interaction):
            if interaction.user.id != self.auth_id:
                await interaction.response.send_message('**`Извините, но Вы не можете управлять меню, которое вызвано другим пользователем`**', ephemeral=True)
                return False
            return True

    """ async def on_timeout(self):
        #return await super().on_timeout()
        '''for child in self.children:
            child.disabled = True'''
        pass """
        
class rating_slash_e(View):
    def __init__(self, timeout, membs: list, in_row: int, curr: str, auth_id: int):
        super().__init__(timeout=timeout)
        self.membs = membs
        self.pages = (len(membs) + in_row - 1) // in_row
        self.curr = curr
        self.in_row = in_row
        self.auth_id = auth_id
    
    def click(self, interaction: Interaction, click: int, in_row: int):
        text = interaction.message.embeds[0].footer.text
        t1 = text.find("Page ")
        t2 = text.find(" from")
        page = int(text[t1+5:t2])
        if click <= 1 and page == 1:
            return []
        elif click >= 2 and page == self.pages:
            return []
        if click == 0:
            page = 1
        elif click == 3:
            page = self.pages
        elif click == 1:
            page -= 1
        elif click == 2:
            page += 1
        msg = []
        counter = (page-1) * in_row + 1

        for r in self.membs[(page-1) * in_row:min(page * in_row, len(self.membs))]:
            msg.append((f"{counter} place", f"<@{r[0]}>\n{r[1]} {self.curr}"))
            counter += 1
        msg.append((f"Page {page} from {self.pages}", ""))
        print(msg)
        return msg


    @ui.button(emoji="⏮️")
    async def callback_l_top(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=0, in_row=self.in_row)
        if store_list != []:
            emb = Embed(title="Top members by balance", colour=Colour.dark_gray())
            emb.set_footer(text=store_list[-1][0])
            for r in store_list[:-1]:
                emb.add_field(name=r[0], value=r[1], inline=False)
            await interaction.response.edit_message(embed=emb)

    @ui.button(emoji="◀️")
    async def callback_l(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=1, in_row=self.in_row)
        if store_list != []:
            emb = Embed(title="Top members by balance", colour=Colour.dark_gray())
            emb.set_footer(text=store_list[-1][0])
            for r in store_list[:-1]:
                emb.add_field(name=r[0], value=r[1], inline=False)
            await interaction.response.edit_message(embed=emb)

    @ui.button(emoji="▶️")
    async def callback_r(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=2, in_row=self.in_row)
        if store_list != []:
            emb = Embed(title="Top members by balance", colour=Colour.dark_gray())
            emb.set_footer(text=store_list[-1][0])
            for r in store_list[:-1]:
                emb.add_field(name=r[0], value=r[1], inline=False)
            await interaction.response.edit_message(embed=emb)

    @ui.button(emoji="⏭")
    async def callback_r_top(self, button: Button, interaction: Interaction):
        store_list=self.click(interaction=interaction, click=3, in_row=self.in_row)
        if store_list != []:
            emb = Embed(title="Top members by balance", colour=Colour.dark_gray())
            emb.set_footer(text=store_list[-1][0])
            for r in store_list[:-1]:
                emb.add_field(name=r[0], value=r[1], inline=False)
            await interaction.response.edit_message(embed=emb)

    async def interaction_check(self, interaction):
            if interaction.user.id != self.auth_id:
                await interaction.response.send_message("**`Sorry, but you can't manage menu called by another member`**", ephemeral=True)
                return False
            return True

class slash(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.in_row = in_row
        self.currency = currency
        
        global bot_guilds_e
        global bot_guilds_r        

    
    async def can_role(self, interaction: Interaction, role: Role, lng: int) -> bool:
        
        if not interaction.permissions.manage_roles:
            await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], colour=Colour.red(), description=text_slash[lng][1]))
            return False

        elif not role.is_assignable():
            await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], colour=Colour.red(), description=text_slash[lng][2]))
            return False
        
        return True


    def check_user(self, base: Connection, cur: Cursor, memb_id: int):
        member = cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()
        if not member:
            cur.execute('INSERT INTO users(memb_id, money, owned_roles, work_date, xp) VALUES(?, ?, ?, ?, ?)', (memb_id, 0, "", 0, 0))
            base.commit()
            return (memb_id, 0, "", 0, 0)
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
    

    async def buy(self, interaction: Interaction, role: Role) -> None:
        lng = 1 if "ru" in interaction.locale else 0
        if not await self.can_role(interaction=interaction, role=role, lng=lng):
            return
        member_buyer = interaction.user
        r_id = role.id
        rls = {x[0] for x in member_buyer.roles}
        if r_id in rls:
            await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], description=text_slash[lng][4], colour=Colour.red()))
            return
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                store = cur.execute('SELECT * FROM store WHERE role_id = ?', (r_id,)).fetchone()
                if not store:
                    await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], description=text_slash[lng][5], colour=Colour.red()))
                    return

                role_info = cur.execute('SELECT price, type FROM server_roles WHERE role_id = ?', (r_id,)).fetchone()
                memb_id = member_buyer.id
                buyer = self.check_user(base=base, cur=cur, memb_id=memb_id)
                buyer_cash = buyer[1]
                cost = role_info[0]

                if buyer_cash < cost:
                    await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], colour=Colour.red(), description=text_slash[lng][6].format(cost - buyer_cash, currency)))
                    await interaction.delete_original_message(delay=10)
                    return

                emb = Embed(title=text_slash[lng][7], description=text_slash[lng][8].format(role.mention, cost, currency))
                
                view = buy_slash(timeout=30, auth_id=memb_id, lng=lng)
                await interaction.response.send_message(embed=emb, view=view)

                c = await view.wait()
                if c or not view.value:
                    await interaction.delete_original_message()
                    return                    
                    
                role_type = role_info[1]
                await member_buyer.add_roles(role)                                                
                cur.execute('UPDATE users SET money = money - ?, owned_roles = ? WHERE memb_id = ?', (cost, buyer[2]+f"#{r_id}" , memb_id))
                base.commit()
                
                if role_type == 1:
                    rowid_to_delete = sorted(cur.execute("SELECT rowid, last_date FROM store WHERE role_id = ?", (r_id,)).fetchall(), key=lambda tup: tup[1])[0][0]
                    cur.execute("DELETE FROM store WHERE rowid = ?", (rowid_to_delete,))                        
                elif role_type == 2:
                    if store[1] > 1:
                        cur.execute('UPDATE store SET quantity = quantity - ? WHERE role_id = ?', (1, r_id))
                    else:
                        cur.execute("DELETE FROM store WHERE role_id = ?", (r_id,))
                base.commit()
                chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]

        emb.title = text_slash[lng][10]
        emb.description = text_slash[lng][11]
        await interaction.edit_original_message(embed=emb, view=None)

        try: await member_buyer.send(embed=Embed(title=text_slash[lng][7], description=text_slash[lng][12].format(role.name, interaction.guild.name, cost, self.currency), colour=Colour.green()))
        except: pass
        
        if chnl_id:
            try: await interaction.guild.get_channel(chnl_id).send(embed=Embed(title=text_slash[lng][13], description=text_slash[lng][14].format(f"<@{memb_id}>", f"<@&{r_id}>", cost, self.currency)))
            except: pass


    async def store(self, interaction: Interaction) -> None:
        
        lng = 1 if "ru" in interaction.locale else 0
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild.id}/{interaction.guild.id}.db")) as base:
            with closing(base.cursor()) as cur:        
                tz = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]
                db_store = cur.execute('SELECT * FROM store').fetchall()

        for i in range(len(db_store)-1):
            for j in range(i+1, len(db_store)):
                if db_store[i][2] > db_store[j][2]:
                    temp = db_store[j]
                    db_store[j] = db_store[i]
                    db_store[i] = temp
                elif db_store[i][2] == db_store[j][2] and db_store[i][3] < db_store[j][3]:
                    temp = db_store[j]
                    db_store[j] = db_store[i]
                    db_store[i] = temp

        store_list = []
        tzinfo = timezone(timedelta(hours=tz))
        
        for r, q, p, d, s, s_t, tp in db_store[:in_row]:
            date = datetime.fromtimestamp(d, tz=tzinfo).strftime("%H:%M %d-%m-%Y")
            if tp == 1:
                r_inf = store_text[lng][0].format(r, p, currency, date)
            elif tp == 2:
                r_inf = store_text[lng][0].format(r, p, currency, q, date)
            elif tp == 3:
                r_inf = store_text[lng][0].format(r, p, currency, "∞", date)
            if s:
                r_inf += store_text[lng][2].format(s * 604800 // s_t, currency)
            store_list.append(r_inf)               

        if len(db_store):
            store_list.append(store_text[lng][3].format(1, (len(db_store) + in_row - 1) // in_row))
        else:
            store_list.append(store_text[lng][3].format(1, 1))

        emb = Embed(title=text_slash[lng][15], colour=Colour.dark_gray(), description='\n'.join(store_list))        
        myview_store = store_slash_view(timeout=60, db_store=db_store, auth_id=interaction.user.id, lng=lng, in_row=in_row, coin=currency, tz=tz)

        await interaction.response.send_message(embed=emb, view=myview_store)
        
        await myview_store.wait()
        for button in myview_store.children:
            button.disabled = True
        await interaction.edit_original_message(view=myview_store)               


    async def sell(self, interaction: Interaction, role: Role) -> None:
        lng = 1 if "ru" in interaction.locale else 0
        if not role in interaction.user.roles:
            await interaction.response.send_message(
                embed=Embed(
                    colour=Colour.red(),
                    title=text_slash[lng][0],
                    description=text_slash[lng][16]
                )
            )
            return
        if not await self.can_role(interaction=interaction, role=role, lng=lng):
            return
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild.id}/{interaction.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                #lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (role.id,)).fetchone()      
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
                    emb = Embed(title=text_slash[lng][20], description=text_slash[lng][21].format(role.id, role_info[1], self.currency), colour=Colour.green())
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
    
    
    async def profile(self, interaction: Interaction) -> None:
        lng = 1 if "ru" in interaction.locale else 0
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild.id}/{interaction.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                memb_id = interaction.user.id
                member = self.check_user(base=base, cur=cur, memb_id=memb_id)
                server_roles = cur.execute('SELECT role_id FROM server_roles').fetchall()
                #lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                #emb = Embed(title=text_slash[lng][24])
                roles = ""
                uniq_roles = []
                descr = []
                descr.append(f'**{text_slash[lng][24]}** `{member[1]}`{self.currency}\n')
                flag = 0
                if server_roles != None:
                    server_roles = set([x[0] for x in server_roles]) #ids of roles that user might has, set for quick searching in
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
                if uniq_roles != None:
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

                if flag:
                    cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', (roles, interaction.user.id))
                    base.commit()
                await interaction.response.send_message(embed=Embed(description="\n".join(descr)))
    
    
    async def work(self, interaction: Interaction) -> None:
        memb_id = interaction.user.id
        lng = 1 if "ru" in interaction.locale else 0
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild.id}/{interaction.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                time_reload = cur.execute("SELECT value FROM server_info WHERE settings = 'time_r'").fetchone()[0]
                #lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
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
    

    async def bet(self, interaction: Interaction, amount: int) -> None:
        lng = 1 if "ru" in interaction.locale else 0
        memb_id = interaction.user.id
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild.id}/{interaction.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                #lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
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
    

    async def transfer(self, interaction: Interaction, value: int, target: Member) -> None:
        memb_id = interaction.user.id
        lng = 1 if "ru" in interaction.locale else 0
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild.id}/{interaction.guild.id}.db')) as base:
            with closing(base.cursor()) as cur:
                act = self.check_user(base=base, cur=cur, memb_id=memb_id)
                self.check_user(base=base, cur=cur, memb_id=target.id)
                #lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
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

    
    async def leaders(self, interaction: Interaction) -> None:
        lng = 1 if "ru" in interaction.locale else 0
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild.id}/{interaction.guild.id}.db")) as base:
            with closing(base.cursor()) as cur:
                #lng = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                self.check_user(base=base, cur=cur, memb_id=interaction.user.id)
                membs = cur.execute("SELECT * FROM users ORDER BY money DESC").fetchall()
                counter = 1
                 
                if lng == 0:
                    emb = Embed(title="Top members by balance", colour=Colour.dark_gray())
                    emb.set_footer(text=f"Page 1 from {(len(membs) + self.in_row - 1) // self.in_row}")
                    for r in membs[0:min(self.in_row, len(membs))]:
                        emb.add_field(name=f"{counter} place", value=f"<@{r[0]}>\n{r[1]} {self.currency}", inline=False)
                        counter += 1 
                    view_r = rating_slash_e(timeout=30, membs=membs, in_row=self.in_row, curr=self.currency, auth_id=interaction.user.id)
                else:
                    emb = Embed(title="Топ пользователей по балансу", colour=Colour.dark_gray())
                    emb.set_footer(text=f"Страница 1 из {(len(membs) + self.in_row - 1) // self.in_row}")
                    for r in membs[0:min(self.in_row, len(membs))]:
                        emb.add_field(name=f"{counter} место", value=f"<@{r[0]}>\n{r[1]} {self.currency}", inline=False)
                        counter += 1 
                    view_r = rating_slash_r(timeout=30, membs=membs, in_row=self.in_row, curr=self.currency, auth_id=interaction.user.id)
                await interaction.response.send_message(embed=emb, view=view_r)
                end = await view_r.wait()
                if end:
                    for child in view_r.children:
                        child.disabled = True
                    msg = await interaction.original_message()
                    await msg.edit(view=view_r)
    
    
    @slash_command(
        name="buy", 
        description="Makes a role purchase from the store",
        description_localizations={
            Locale.ru : "Совершает покупку роли из магазина"
        },
        guild_ids=bot_guilds_e,
    )
    async def buy_e(
        self, 
        interaction: Interaction, 
        role: Role = SlashOption(
            name="role",
            name_localizations={
                Locale.ru: "роль"
            },
            description="Role that you want to buy", 
            description_localizations={
                Locale.ru: "Роль, которую Вы хотите купить"
            },
            required=True
        )
    ):
        await self.buy(interaction=interaction, role=role)
                    

    @slash_command(
        name="buy", 
        description="Совершает покупку роли из магазина",
        description_localizations={
            Locale.en_GB : "Makes a role purchase from the store",
            Locale.en_US : "Makes a role purchase from the store",
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    async def buy_r(
        self, 
        interaction: Interaction, 
        role: Role = SlashOption(
            name="роль",
            name_localizations={
                Locale.en_GB: "role",
                Locale.en_US: "role"
            },
            description="Роль, которую Вы хотите купить", 
            description_localizations={
                Locale.en_GB: "Role that you want to buy",
                Locale.en_US: "Role that you want to buy"
            },
            required=True
        )
    ):
        await self.buy(interaction=interaction, role=role)

    
    @slash_command(
        name="store",
        description="Shows store",
        description_localizations={
            Locale.ru : "Открывает меню магазина"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    async def store_e(self, interaction: Interaction):
        await self.store(interaction=interaction)
    
    
    @slash_command(
        name="store",
        description="Открывает меню магазина",
        description_localizations={
            Locale.en_GB: "Shows store",
            Locale.en_US: "Shows store"
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    async def store_r(self, interaction: Interaction):
        await self.store(interaction=interaction)
    

    @slash_command(
        name="sell", 
        description="Sells the role",
        description_localizations={
            Locale.ru: "Совершает продажу роли"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    async def sell_e(
        self,
        interaction: Interaction,
        role: Role = SlashOption(
            name="role",
            name_localizations={
                Locale.ru: "роль"
            },
            description="Your role that you want to sell",
            description_localizations={
                Locale.ru: "Ваша роль, которую Вы хотите продать"
            },
            required=True
        )
    ):
        await self.sell(interaction=interaction, role=role)


    @slash_command(
        name="sell", 
        description="Совершает продажу роли",
        description_localizations={
            Locale.en_GB: "Sells the role",
            Locale.en_US: "Sells the role"
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    async def sell_r(
        self,
        interaction: Interaction,
        role: Role = SlashOption(
            name="роль",
            name_localizations={
                Locale.en_GB: "role",
                Locale.en_US: "role"
            },
            description="Ваша роль, которую Вы хотите продать",
            description_localizations={
                Locale.en_GB: "Your role that you want to sell",
                Locale.en_US: "Your role that you want to sell"
            },
            required=True
        )
    ):
        await self.sell(interaction=interaction, role=role)


    @slash_command(
        name="profile", 
        description="Shows your profile",
        description_localizations={
            Locale.ru: "Показывает меню Вашего профиля"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    async def profile_e(self, interaction: Interaction):
        await self.profile(interaction=interaction)


    @slash_command(
        name="profile", 
        description="Показывает меню Вашего профиля",
        description_localizations={
            Locale.en_GB: "Shows your profile",
            Locale.en_US: "Shows your profile"
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    async def profile_r(self, interaction: Interaction):
        await self.profile(interaction=interaction)


    @slash_command(
        name="work", 
        description="Allows to gain money",
        description_localizations={
            Locale.ru: "Позволяет заработать деньги"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    async def work_e(self, interaction: Interaction):
        await self.work(interaction=interaction)
    

    @slash_command(
        name="work", 
        description="Позволяет заработать деньги",
        description_localizations={
            Locale.en_GB: "Allows to gain money",
            Locale.en_US: "Allows to gain money"
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    async def work_r(self, interaction: Interaction):
        await self.work(interaction=interaction)
    
    
    @slash_command(
        name="duel", 
        description="Make a bet",
        description_localizations={
            Locale.ru: "Сделать ставку"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    async def duel_e(
        self, 
        interaction: Interaction, 
        amount: int = SlashOption(
            name="amount", 
            name_localizations={
                Locale.ru: "количество"
            },
            description="Bet amount",
            description_localizations={
                Locale.ru: "Сумма ставки"
            },
            required=True, 
            min_value=1
        )
    ): 
        await self.bet(interaction=interaction, amount=amount)

    
    @slash_command(
        name="duel", 
        description="Сделать ставку",
        description_localizations={
            Locale.en_GB: "Make a bet",
            Locale.en_US: "Make a bet"
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    async def duel_r(
        self, 
        interaction: Interaction, 
        amount: int = SlashOption(
            name="количество", 
            name_localizations={
                Locale.en_GB: "amount",
                Locale.en_US: "amount"
            },
            description="Сумма ставки",
            description_localizations={
                Locale.en_GB: "Bet amount",
                Locale.en_US: "Bet amount"
            },
            required=True, 
            min_value=1
        )
    ): 
        await self.bet(interaction=interaction, amount=amount)

    
    @slash_command(
        name="transfer", 
        description="Transfers money to another member",
        description_localizations={
            Locale.ru: "Совершает перевод валюты другому пользователю"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    async def transfer_e(
        self,
        interaction: Interaction, 
        value: int = SlashOption(
            name="value", 
            name_localizations={
                Locale.ru: "сумма"
            },
            description="Amount of money to transfer", 
            description_localizations={
                Locale.ru: "Переводимая сумма денег"
            },
            required=True, 
            min_value=1
        ),
        target: Member = SlashOption(
            name="target", 
            name_localizations={
                Locale.ru: "кому"
            },
            description="The member you want to transfer money to", 
            description_localizations={
                Locale.ru : "Пользователь, которому Вы хотите перевести деньги"
            },
            required=True
        )
    ):
        await self.transfer(interaction=interaction, value=value, target=target)
    

    @slash_command(
        name="transfer", 
        description="Совершает перевод валюты другому пользователю",
        description_localizations={
            Locale.en_GB: "Transfers money to another member",
            Locale.en_US: "Transfers money to another member"
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    async def transfer_r(
        self,
        interaction: Interaction, 
        value: int = SlashOption(
            name="сумма", 
            name_localizations={
                Locale.en_GB: "value",
                Locale.en_US: "value"
            },
            description="Переводимая сумма денег", 
            description_localizations={
                Locale.en_GB: "Amount of money to transfer",
                Locale.en_US: "Amount of money to transfer"
            },
            required=True, 
            min_value=1
        ),
        target: Member = SlashOption(
            name="кому", 
            name_localizations={
                Locale.en_US: "target",
                Locale.en_GB: "target"
            },
            description= "Пользователь, которому Вы хотите перевести деньги",
            description_localizations={
                Locale.en_GB: "The member you want to transfer money to",
                Locale.en_US: "The member you want to transfer money to"
            },
            required=True
        )
    ):
        await self.transfer(interaction=interaction, value=value, target=target)

    
    @slash_command(
        name="leaders", 
        description="Shows top members by balance",
        description_localizations={
            Locale.ru: "Показывет топ пользователей по балансу"
        },
        guild_ids=bot_guilds_e,
        force_global=False
    )
    async def leaders_e(self, interaction: Interaction):
        await self.leaders(interaction=interaction)
    

    @slash_command(
        name="leaders", 
        description="Показывет топ пользователей по балансу",
        description_localizations={
            Locale.en_GB: "Shows top members by balance",
            Locale.en_US: "Shows top members by balance"
        },
        guild_ids=bot_guilds_r,
        force_global=False
    )
    async def leaders_r(self, interaction: Interaction):
        await self.leaders(interaction=interaction)
    

def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(slash(bot, **kwargs))
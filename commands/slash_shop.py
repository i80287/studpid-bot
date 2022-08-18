
from sqlite3 import Connection, Cursor, connect
from contextlib import closing
from datetime import datetime, timedelta, timezone
from time import time
from random import randint

from nextcord.ext import commands
from nextcord import Embed, Colour, ButtonStyle, SlashOption, Interaction, Locale, ui, SelectOption, slash_command, Role, Member
from nextcord.ui import Button, View, Select

from config import path_to, currency, in_row

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
        19 : "**`Вы продали роль `**{}**` за {}`** {}\n**`Если у Вас включена возможность получения личных сообщений от участников серверов, то \
            подтверждение продажи будет выслано Вам в личные сообщения`**",
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
        0 : "**•** <@&{}>\n`Price` - `{}` {}\n`Left` - `1`\n`Listed for sale:`\n*{}*\n",
        1 : "**•** <@&{}>\n`Price` - `{}` {}\n`Left` - `{}`\n`Last listed for sale:`\n*{}*\n",
        2 : "`Average salary per week` - `{}` {}\n",
        3 : "Page {} from {}",
        4 : "Sort by...",
        5 : "Sort by price",
        6 : "Sort by date",
        7 : "Sort from...",
        8 : "From the lower price / newer role",
        9 : "From the higher price / older role",
        10 : "Roles for sale:"

    },
    1 : {
        0 : "**•** <@&{}>\n`Цена` - `{}` {}\n`Осталось` - `1`\n`Выставленa на продажу:`\n*{}*\n",
        1 : "**•** <@&{}>\n`Цена` - `{}` {}\n`Осталось` - `{}`\n`Последний раз выставленa на продажу:`\n*{}*\n",
        2 : "`Средний доход за неделю` - `{}` {}\n",
        3 : "Страница {} из {}",
        4 : "Сортировать по...",
        5 : "Сортировать по цене",
        6 : "Сортировать по дате",
        7 : "Сортировать от...",
        8 : "От меньшей цены / более свежого товара",
        9 : "От большей цены / более старого товара",
        10 : "Роли на продажу:"
    }
}


profile_text = {
    0 : {
        1 : "Cash",
        2 : "Xp",
        3 : "Level",
        4 : "Place in the rating",
        5 : "**`Information about member:`**\n<@{}>",
        6 : "**`You don't have any roles from the bot's store`**",    
    },
    1 : {
        1 : "Кэш",
        2 : "Опыт",
        3 : "Уровень",
        4 : "Место в рейтинге",
        5 : "**`Информация о пользователе:`**\n<@{}>",
        6 : "**`У Вас нет ролей из магазина бота`**",
    }
}


code_blocks = {
    0 : "```\nMember's personal roles\n```",
    5 : "```\nЛичные роли пользователя\n```",
    1 : "```fix\n{}\n```",
    2 : "```c\n{}\n```",
}

bet_text = {
    0 : {
        0 : "Make a counter bet",
        1 : "Cancel bet",
        2 : "**`Sorry, but you can't make counter bet for yourself`**",
        3 : "**`Sorry, but you can't make counter bet, because you need at least {}`** {}",
        4 : "**`Sorry, but you can't control bet made by another user`**",
        5 : "**`Bet was cancelled by user`**"
    },
    1 : {
        0 : "Сделать встречную ставку",
        1 : "Отменить ставку",
        2 : "**`Извините, но Вы не можете делать встречную ставку самому себе`**",
        3 : "**`Извините, но Вы не можете сделать встречную ставку, так как Вам не хватает {}`** {}",
        4 : "**`Извините, но Вы не можете управлять чужой ставкой`**",
        5 : "**`Ставка была отменена пользователем`**"
    }
}


rating_text = {
    0 : {
        0 : "Top members by balance",
        1 : "Page {} from {}",
        2 : "{} place",
        3 : "{} level",
        4 : "Sort by...",
        5 : "Sort by cash",
        6 : "Sort by xp",
    },
    1 : {
        0 : "Топ пользователей по балансу",
        1 : "Страница {} из {}",
        2 : "{} место",
        3 : "{} уровень",
        4 : "Сортировать по...",
        5 : "Сортировать по кэшу",
        6 : "Сортировать по опыту",     
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


class bet_slash_view(View):

    def __init__(self, timeout: int, lng: int, auth_id: int, bet: int):
        super().__init__(timeout=timeout)
        self.bet = bet
        self.auth_id = auth_id
        self.dueler = None
        self.declined = False
        self.currency = currency
        self.add_item(c_button(label=bet_text[lng][0], custom_id=f"36_{auth_id}_{randint(1, 100)}", style=ButtonStyle.green, emoji="💰"))
        self.add_item(c_button(label=bet_text[lng][1], custom_id=f"37_{auth_id}_{randint(1, 100)}", style=ButtonStyle.red, emoji="❌"))

    async def click_b(self, interaction: Interaction, c_id: str):
        memb_id =  interaction.user.id
        lng = 1 if "ru" in interaction.locale else 0

        if c_id.startswith("36_"):

            if memb_id == self.auth_id:
                await interaction.response.send_message(embed=Embed(description=bet_text[lng][2]), ephemeral=True)
                return
            
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    db_cash = cur.execute('SELECT money FROM users WHERE memb_id = ?', (memb_id,)).fetchone()
                    if not db_cash:
                        cur.execute('INSERT INTO users(memb_id, money, owned_roles, work_date, xp) VALUES(?, ?, ?, ?, ?)', (memb_id, 0, "", 0, 0))
                        base.commit()
                        cash = 0
                    elif db_cash[0] is None:
                        cur.execute("UPDATE users SET money = 0 WHERE memb_id = ?", (memb_id,))
                        base.commit()
                        cash = 0
                    else:
                        cash = db_cash[0]
                                    
            if cash < self.bet:
                emb = Embed(description=bet_text[lng][3].format(self.bet-cash, self.currency), colour=Colour.red())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
            
            self.dueler = memb_id
            self.stop()

        else:

            if interaction.user.id != self.auth_id:
                await interaction.response.send_message(embed=Embed(description=bet_text[lng][4]), ephemeral=True)
                return

            self.declined = True            
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
        self.lng = lng
        self.pages = max(1, (self.l + in_row - 1) // in_row)

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


    async def update_menu(self, interaction: Interaction, click: int) -> list:
        text = interaction.message.embeds[0].footer.text

        if not self.lng:
            t1 = text.find('Pa')
            t2 = text.find('fr', t1)
            page = int(text[t1+5:t2-1])
        else:
            t1 = text.find('Ст')
            t2 = text.find('из', t1)
            page = int(text[t1+9:t2-1])
        
        db_store = self.db_store

        if click in (1, 2) and page <= 1:
            return
        elif click in (3, 4) and page >= self.pages:
            return

        if click == 1:
            page = 1
        elif click == 2:
            page -= 1
        elif click == 3:
            page += 1
        elif click == 4:
            page = self.pages

        store_list = []
        tzinfo = timezone(timedelta(hours=self.tz))

        for r, q, p, d, s, s_t, tp in db_store[(page - 1) * self.in_row:min(page * self.in_row, self.l)]:
            date = datetime.fromtimestamp(d, tz=tzinfo).strftime("%H:%M %d-%m-%Y")
            if tp == 1:
                r_inf = store_text[self.lng][0].format(r, p, currency, date)
            elif tp == 2:
                r_inf = store_text[self.lng][1].format(r, p, currency, q, date)
            elif tp == 3:
                r_inf = store_text[self.lng][1].format(r, p, currency, "∞", date)
            if s:
                r_inf += store_text[self.lng][2].format(s * 604800 // s_t, currency)
            store_list.append(r_inf)
        
        if store_list:

            emb = Embed(title=store_text[self.lng][10], colour=Colour.dark_gray(), description='\n'.join(store_list))
            emb.set_footer(text=store_text[self.lng][3].format(page, self.pages))

            if click == 0:
                await interaction.response.edit_message(embed=emb, view=self)
            else:
                await interaction.response.edit_message(embed=emb)


    async def click_b(self, interaction: Interaction, c_id: str):

        click = 0
        if c_id.startswith("32_"):
            click = 1
        elif c_id.startswith("33_"):
            click = 2
        elif c_id.startswith("34_"):
            click = 3
        elif c_id.startswith("35_"):
            click = 4

        await self.update_menu(interaction=interaction, click=click)


    async def click_menu(self, interaction: Interaction, c_id: str, value):

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
        await self.update_menu(interaction=interaction, click=0)


class buy_slash_view(View):

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
                await interaction.response.send_message(embed=Embed(description=common_text[lng][0]), ephemeral=True)
                return False
            return True


class rating_slash_view(View):

    def __init__(self, timeout: int, lng: int, auth_id: int, cash_list: list, xp_list: list, xp_b: int, in_row: int):
        super().__init__(timeout=timeout)
        self.xp_b = xp_b
        self.cash_list = cash_list
        self.xp_list = xp_list
        self.pages = max(1, (len(cash_list) + in_row - 1) // in_row)
        self.currency = currency
        self.in_row = in_row
        self.auth_id = auth_id
        self.lng = lng
        self.sort_value = True # True - show ranking by cash, False - by xp
        self.add_item(c_button(label="", custom_id=f"38_{auth_id}_{randint(1, 100)}", emoji="⏮️"))
        self.add_item(c_button(label="", custom_id=f"39_{auth_id}_{randint(1, 100)}", emoji="◀️"))
        self.add_item(c_button(label="", custom_id=f"40_{auth_id}_{randint(1, 100)}", emoji="▶️"))
        self.add_item(c_button(label="", custom_id=f"41_{auth_id}_{randint(1, 100)}", emoji="⏭"))
        opts = [
            SelectOption(
                label=rating_text[lng][5],
                value=0,
                emoji="💰",
                default=True
            ),
            SelectOption(
                label=rating_text[lng][6],
                value=1,
                emoji="✨",
                default=False
            )
        ]
        self.add_item(c_select(custom_id=f"104_{auth_id}_{randint(1, 100)}", placeholder=rating_text[lng][4], opts=opts))

    async def update_menu(self, interaction: Interaction, click: int):
        
        page_text = interaction.message.embeds[0].footer.text

        if not self.lng:
            t1 = page_text.find("Pa")
            t2 = page_text.find("fr", t1)
            page = int(page_text[t1+5:t2-1])
        else:
            t1 = page_text.find("Ст")
            t2 = page_text.find("из", t1)
            page = int(page_text[t1+9:t2-1])

        if click in (1, 2) and page <= 1:
            return
        elif click in (3, 4) and page >= self.pages:
            return
        
        if click == 1:
            page = 1
        elif click == 2:
            page -= 1
        elif click == 3:
            page += 1
        elif click == 4:
            page = self.pages

        emb = Embed(title=rating_text[self.lng][0], colour=Colour.dark_gray())
        
        counter = (page - 1) * self.in_row + 1

        if self.sort_value:
            for r in self.cash_list[(page-1) * self.in_row:min(page*self.in_row, len(self.cash_list))]:
                emb.add_field(name=rating_text[self.lng][2].format(counter), value=f"<@{r[0]}>\n{r[1]} {self.currency}", inline=False)
                counter += 1
        else:
            for r in self.xp_list[(page-1) * self.in_row:min(page*self.in_row, len(self.xp_list))]:
                level = (r[1] - 1) // self.xp_b + 1
                emb.add_field(name=rating_text[self.lng][2].format(counter), value=f"<@{r[0]}>\n{rating_text[self.lng][3].format(level)}", inline=False)
                counter += 1

        emb.set_footer(text=rating_text[self.lng][1].format(page, self.pages))   
        if not click:
            await interaction.response.edit_message(embed=emb, view=self)
        else:
            await interaction.response.edit_message(embed=emb)

    async def click_b(self, interaction: Interaction, c_id: str):
        
        if c_id.startswith("38_"):
            click = 1
        elif c_id.startswith("39_"):
            click = 2
        elif c_id.startswith("39_"):
            click = 3
        else:
            click = 4

        await self.update_menu(interaction=interaction, click=click)
        

    async def click_menu(self, interaction: Interaction, c_id: str, value):  

        if c_id.startswith("104_"):
            if int(value[0]):
                self.sort_value = False
                self.children[4].options[0].default=False
                self.children[4].options[1].default=True
            else:
                self.sort_value = True
                self.children[4].options[0].default=True
                self.children[4].options[1].default=False

        await self.update_menu(interaction=interaction, click=0)


    async def interaction_check(self, interaction):
        if interaction.user.id != self.auth_id:
            lng = 1 if "ru" in interaction.locale else 0
            await interaction.response.send_message(embed=Embed(description=common_text[lng][0]), ephemeral=True)
            return False
        return True


class slash_commands(commands.Cog):


    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.in_row = in_row
        self.currency = currency 

    
    async def can_role(self, interaction: Interaction, role: Role, lng: int) -> bool:
        
        if not interaction.permissions.manage_roles:
            await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], colour=Colour.red(), description=text_slash[lng][1]), ephemeral=True)
            return False

        elif not role.is_assignable():
            await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], colour=Colour.red(), description=text_slash[lng][2]), ephemeral=True)
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
        memb_id = member_buyer.id
        r_id = role.id    

        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                store = cur.execute('SELECT * FROM store WHERE role_id = ?', (r_id,)).fetchone()
                if not store:
                    await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], description=text_slash[lng][5], colour=Colour.red()))
                    return
                buyer = self.check_user(base=base, cur=cur, memb_id=memb_id)
        
        if r_id in {int(x) for x in buyer[2].split("#") if x != ""}:
            await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], description=text_slash[lng][4], colour=Colour.red()), ephemeral=True)
            return

        buyer_cash = buyer[1]
        cost = store[2]

        if buyer_cash < cost:
            await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], colour=Colour.red(), description=text_slash[lng][6].format(cost - buyer_cash, currency)))
            await interaction.delete_original_message(delay=10)
            return

        emb = Embed(title=text_slash[lng][7], description=text_slash[lng][8].format(role.mention, cost, currency))
        
        view = buy_slash_view(timeout=30, auth_id=memb_id, lng=lng)
        await interaction.response.send_message(embed=emb, view=view)

        c = await view.wait()
        if c or not view.value:
            await interaction.delete_original_message()
            return          

        role_type = store[6]
        await member_buyer.add_roles(role)                                                

        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:   
                
                cur.execute('UPDATE users SET money = money - ?, owned_roles = ? WHERE memb_id = ?', (cost, buyer[2]+f"#{r_id}" , memb_id))
                base.commit()
                
                if role_type == 1:
                    rowid_to_delete = sorted(cur.execute("SELECT rowid, last_date FROM store WHERE role_id = ?", (r_id,)).fetchall(), key=lambda tup: tup[1])[0][0]
                    cur.execute("DELETE FROM store WHERE rowid = ?", (rowid_to_delete,))                        
                elif role_type == 2:
                    if store[1] > 1:
                        cur.execute('UPDATE store SET quantity = quantity - 1 WHERE role_id = ?', (r_id,))
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
        
        db_l = len(db_store)
        l = db_l // 2
        while l:
            for i in range(l, db_l):
                moving_item = db_store[i]
                while i >= l and (db_store[i-l][2] > db_store[i][2] or (db_store[i-l][2] == db_store[i][2] and db_store[i-l][3] < db_store[i][3])):
                    db_store[i] = db_store[i - l]
                    i -= l
                    db_store[i] = moving_item
            l //= 2

        store_list = []
        tzinfo = timezone(timedelta(hours=tz))
        
        for r, q, p, d, s, s_t, tp in db_store[:min(in_row, db_l)]:
            date = datetime.fromtimestamp(d, tz=tzinfo).strftime("%H:%M %d-%m-%Y")
            if tp == 1:
                r_inf = store_text[lng][0].format(r, p, currency, date)
            elif tp == 2:
                r_inf = store_text[lng][1].format(r, p, currency, q, date)
            elif tp == 3:
                r_inf = store_text[lng][1].format(r, p, currency, "∞", date)
            if s:
                r_inf += store_text[lng][2].format(s * 604800 // s_t, currency)
            store_list.append(r_inf)               

        emb = Embed(title=text_slash[lng][15], colour=Colour.dark_gray(), description='\n'.join(store_list))        

        if db_l:
            emb.set_footer(text=store_text[lng][3].format(1, (db_l + in_row - 1) // in_row))
        else:
            emb.set_footer(text=store_text[lng][3].format(1, 1))

        
        myview_store = store_slash_view(timeout=60, db_store=db_store, auth_id=interaction.user.id, lng=lng, in_row=in_row, coin=currency, tz=tz)

        await interaction.response.send_message(embed=emb, view=myview_store)
        
        await myview_store.wait()
        for button in myview_store.children:
            button.disabled = True
        await interaction.edit_original_message(view=myview_store)               


    async def sell(self, interaction: Interaction, role: Role) -> None:
        lng = 1 if "ru" in interaction.locale else 0
        r_id = role.id
        
        if not await self.can_role(interaction=interaction, role=role, lng=lng):
            return
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                
                role_info = cur.execute('SELECT * FROM server_roles WHERE role_id = ?', (r_id,)).fetchone()      
                if not role_info:
                    await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], description=text_slash[lng][17], colour=Colour.red()))
                    return

                memb_id = interaction.user.id
                user = self.check_user(base=base, cur=cur, memb_id=memb_id)
                owned_roles = user[2]

                if not r_id in {int(x) for x in owned_roles.split("#") if x != ""}:
                    await interaction.response.send_message(embed=Embed(colour=Colour.red(), title=text_slash[lng][0], description=text_slash[lng][16]), ephemeral=True)
                    return

                r_price = role_info[1]
                r_sal = role_info[2]
                r_sal_c = role_info[3]
                r_type = role_info[4]

                await interaction.user.remove_roles(role)
                
                cur.execute('UPDATE users SET owned_roles = ?, money = money + ? WHERE memb_id = ?', (owned_roles.replace(f"#{r_id}", ""), r_price, memb_id))
                base.commit()

                db_store = cur.execute('SELECT count() FROM store WHERE role_id = ?', (r_id,)).fetchone()      
                time_now = int(time())

                if r_type == 1:
                    cur.execute("INSERT INTO store(role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES(?, ?, ?, ?, ?, ?, ?)", 
                            (r_id, 1, r_price, time_now, r_sal, r_sal_c, 1))
                    membs = cur.execute("SELECT members FROM salary_roles WHERE role_id = ?", (r_id,)).fetchone()
                    if membs and membs[0]:
                        cur.execute("UPDATE money_roles SET members = ? WHERE role_id = ?", (membs[0].replace(f"#{memb_id}", ""), r_id))

                elif r_type == 2:                   
                    if db_store:
                        cur.execute("UPDATE store SET quantity = quantity + ?, last_date = ? WHERE role_id = ?", (1, time_now, r_id))      
                    else:
                        cur.execute("INSERT INTO store(role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES(?, ?, ?, ?, ?, ?, ?)", 
                            (r_id, 1, r_price, time_now, r_sal, r_sal_c, 2))

                elif r_type == 3:
                    if db_store:
                        cur.execute("UPDATE store SET last_date = ? WHERE role_id = ?", (time_now, r_id))
                    else:
                        cur.execute('INSERT INTO store(role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES(?, ?, ?, ?, ?, ?, ?)', 
                        (r_id, -404, r_price, time_now, r_sal, r_sal_c, 3))

                base.commit()
                
                chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]
                
        emb = Embed(title=text_slash[lng][18], description=text_slash[lng][19].format(role.mention, role_info[1], self.currency), colour=Colour.gold())
        await interaction.response.send_message(embed=emb)

        try: await interaction.user.send(embed=Embed(title=text_slash[lng][20], description=text_slash[lng][21].format(r_id, r_price, self.currency), colour=Colour.green()))
        except: pass

        if chnl_id:
            try: await interaction.guild.get_channel(chnl_id).send(embed=Embed(title=text_slash[lng][22], description=text_slash[lng][23].format(interaction.user.mention, role.mention, role_info[1])))
            except: pass
    
    
    async def profile(self, interaction: Interaction) -> None:
        lng = 1 if "ru" in interaction.locale else 0
        memb_id = interaction.user.id
                        
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                member = self.check_user(base=base, cur=cur, memb_id=memb_id)
                xp_b = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
                membs_cash = sorted(cur.execute("SELECT memb_id, money FROM users").fetchall(), key=lambda tup: tup[1], reverse=True)
                membs_xp = sorted(cur.execute("SELECT memb_id, xp FROM users").fetchall(), key=lambda tup: tup[1], reverse=True)
        l = len(membs_cash)

        # cnt_cash is a place in the rating sorded by cash
        cash = member[1]
        if membs_cash[l//2][1] < cash:
            cnt_cash = 1
            while cnt_cash < l and memb_id != membs_cash[cnt_cash-1][0]:
                cnt_cash += 1
        else:
            cnt_cash = l
            while cnt_cash > 1 and memb_id != membs_cash[cnt_cash-1][0]:
                cnt_cash -= 1

        emb1 = Embed()
        emb1.description = profile_text[lng][5].format(memb_id, memb_id)
        emb1.add_field(name=profile_text[lng][1], value=code_blocks[1].format(cash), inline=True)
        emb1.add_field(name=profile_text[lng][4], value=code_blocks[1].format(cnt_cash), inline=True)

        # cnt_cash is a place in the rating sorded by xp
        xp = member[4]
        if membs_xp[l//2][1] < xp:
            cnt_xp = 1
            while cnt_xp < l and memb_id != membs_xp[cnt_xp-1][0]:
                cnt_xp += 1
        else:
            cnt_xp = l
            while cnt_xp > 1 and memb_id != membs_xp[cnt_xp-1][0]:
                cnt_xp -= 1

        level = (xp + xp_b - 1) // xp_b
        
        emb2 = Embed()
        emb2.add_field(name=profile_text[lng][2], value=code_blocks[2].format(f"{xp}/{level * xp_b + 1}"), inline=True)
        emb2.add_field(name=profile_text[lng][3], value=code_blocks[2].format(level), inline=True)
        emb2.add_field(name=profile_text[lng][4], value=code_blocks[2].format(cnt_xp), inline=True)

        emb3 = Embed()
        if member[2] != "":
            dsc = [code_blocks[lng*5]] + [f"<@&{r}>" for r in member[2].split("#") if r != ""]
        else:
            dsc = [profile_text[lng][6]]
        emb3.description = "\n".join(dsc)

        await interaction.response.send_message(embeds=[emb1, emb2, emb3])
    

    async def work(self, interaction: Interaction) -> None:
        memb_id = interaction.user.id
        lng = 1 if "ru" in interaction.locale else 0
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                time_reload = cur.execute("SELECT value FROM server_info WHERE settings = 'w_cd'").fetchone()[0]
                member = self.check_user(base=base, cur=cur, memb_id=memb_id)
                flag: bool = False
                if not member[3]:
                    flag = True
                else:
                    lasted_time = int(time()) - member[3]
                    if lasted_time >= time_reload:
                        flag = True
                if not flag:
                    time_l = time_reload - lasted_time
                    t_l = f"{time_l // 3600}:{(time_l % 3600)//60}:{time_l % 60}"
                    await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], description=text_slash[lng][26].format(t_l)), ephemeral=True)
                    return 
                sal_l = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_l'").fetchone()[0]
                sal_r = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_r'").fetchone()[0]
                salary = randint(sal_l, sal_r)
                cur.execute('UPDATE users SET money = money + ?, work_date = ? WHERE memb_id = ?', (salary, int(time()), memb_id))
                base.commit()

                chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]
                
        await interaction.response.send_message(embed=Embed(title=text_slash[lng][27], description=text_slash[lng][28].format(salary, self.currency), colour=Colour.gold()))                
        
        if chnl_id:
            try: await interaction.guild.get_channel(chnl_id).send(embed=Embed(title=text_slash[lng][29], description=text_slash[lng][30].format(f"<@{memb_id}>", salary, self.currency)))
            except: pass
    

    async def bet(self, interaction: Interaction, amount: int) -> None:
        lng = 1 if "ru" in interaction.locale else 0
        memb_id = interaction.user.id

        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                member = self.check_user(base=base, cur=cur, memb_id=memb_id)

        if amount > member[1]:
            await interaction.response.send_message(embed=Embed(title=text_slash[lng][0], description=text_slash[lng][31].format(amount - member[1], self.currency), colour=Colour.red()), ephemeral=True)
            return

        betview = bet_slash_view(timeout=30, lng=lng, auth_id=memb_id, bet=amount)
        
        emb = Embed(title=text_slash[lng][32], description=text_slash[lng][33].format(amount, self.currency))
        await interaction.response.send_message(embed=emb, view=betview)

        if await betview.wait():
            emb.description = text_slash[lng][34]
        
        for c in betview.children:
                c.disabled = True

        if not betview.dueler:
            if betview.declined:
                emb.description = bet_text[lng][5]
            await interaction.edit_original_message(embed=emb, view=betview)
            await interaction.delete_original_message(delay=7)
            return                  

        dueler = betview.dueler

        winner = randint(0, 1)
        emb = Embed(title=text_slash[lng][35], colour=Colour.gold())

        if winner:
            loser_id = dueler
            winner_id = memb_id
            emb.description = f"<@{memb_id}> {text_slash[lng][36]} `{amount}`{self.currency}"
            
        else:
            winner_id = dueler
            loser_id = memb_id
            emb.description = f"<@{dueler}> {text_slash[lng][36]} `{amount}`{self.currency}"        

        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                cur.execute('UPDATE users SET money = money - ? WHERE memb_id = ?', (amount, loser_id))
                base.commit()
                cur.execute('UPDATE users SET money = money + ? WHERE memb_id = ?', (amount, winner_id))
                base.commit()
                chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]

        await interaction.edit_original_message(embed=emb, view=betview)
        if chnl_id:
            try: await interaction.guild.get_channel(chnl_id).send(embed=Embed(title=text_slash[lng][37], description=text_slash[lng][38].format(winner_id, amount, self.currency, loser_id)))
            except: pass
    

    async def transfer(self, interaction: Interaction, value: int, target: Member) -> None:
        memb_id = interaction.user.id
        t_id = target.id
        lng = 1 if "ru" in interaction.locale else 0
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:

                act = self.check_user(base=base, cur=cur, memb_id=memb_id)
                self.check_user(base=base, cur=cur, memb_id=t_id)

                if value > act[1]:
                    emb=Embed(title=text_slash[lng][0], description=text_slash[lng][39].format(value - act[1], self.currency), colour=Colour.red())
                    await interaction.response.send_message(embed=emb)
                    return
                
                cur.execute('UPDATE users SET money = money - ? WHERE memb_id = ?', (value, memb_id))
                base.commit()
                cur.execute('UPDATE users SET money = money + ? WHERE memb_id = ?', (value, t_id))
                base.commit()

                chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]

        emb=Embed(title=text_slash[lng][40], description=text_slash[lng][41].format(value, self.currency, f"<@{t_id}>"), colour=Colour.green())
        await interaction.response.send_message(embed=emb)
        if chnl_id:
            try: await interaction.guild.get_channel(chnl_id).send(embed=Embed(title=text_slash[lng][42], description= text_slash[lng][43].format(f"<@{memb_id}>", value, self.currency, f"<@{t_id}>")))
            except: pass

    
    async def leaders(self, interaction: Interaction) -> None:
        lng = 1 if "ru" in interaction.locale else 0

        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                self.check_user(base=base, cur=cur, memb_id=interaction.user.id)
                membs_cash = sorted(cur.execute("SELECT memb_id, money FROM users").fetchall(), key=lambda tup: tup[1], reverse=True)
                membs_xp = sorted(cur.execute("SELECT memb_id, xp FROM users").fetchall(), key=lambda tup: tup[1], reverse=True)
                xp_b = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
        
        l = len(membs_cash)

        emb = Embed(title=rating_text[lng][0], colour=Colour.dark_gray())
        
        counter = 1
        for r in membs_cash[0:min(self.in_row, l)]:
            emb.add_field(name=rating_text[lng][2].format(counter), value=f"<@{r[0]}>\n{r[1]} {self.currency}", inline=False)
            counter += 1 

        if l:
            emb.set_footer(text=rating_text[lng][1].format(1, (l + in_row - 1) // in_row))
        else:
            emb.set_footer(text=rating_text[lng][1].format(1, 1))

        rate_view = rating_slash_view(timeout=40, lng=lng, auth_id=interaction.user.id, cash_list=membs_cash, xp_list=membs_xp, xp_b=xp_b, in_row=in_row)

        await interaction.response.send_message(embed=emb, view=rate_view)
        await rate_view.wait()
        
        for c in rate_view.children:
            c.disabled = True
        await interaction.edit_original_message(view=rate_view)
    
    
    @slash_command(
        name="buy", 
        description="Makes a role purchase from the store",
        description_localizations={
            Locale.ru : "Совершает покупку роли из магазина"
        }
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
        name="store",
        description="Shows store",
        description_localizations={
            Locale.ru : "Открывает меню магазина"
        }
    )
    async def store_e(self, interaction: Interaction):
        await self.store(interaction=interaction)
     

    @slash_command(
        name="sell", 
        description="Sells the role",
        description_localizations={
            Locale.ru: "Совершает продажу роли"
        }
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
        name="profile", 
        description="Shows your profile",
        description_localizations={
            Locale.ru: "Показывает меню Вашего профиля"
        }
    )
    async def profile_e(self, interaction: Interaction):
        await self.profile(interaction=interaction)


    @slash_command(
        name="work", 
        description="Allows to gain money",
        description_localizations={
            Locale.ru: "Позволяет заработать деньги"
        }
    )
    async def work_e(self, interaction: Interaction):
        await self.work(interaction=interaction)
    

    @slash_command(
        name="duel", 
        description="Make a bet",
        description_localizations={
            Locale.ru: "Сделать ставку"
        }
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
        name="transfer", 
        description="Transfers money to another member",
        description_localizations={
            Locale.ru: "Совершает перевод валюты другому пользователю"
        }
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
        name="leaders", 
        description="Shows top members by balance",
        description_localizations={
            Locale.ru: "Показывет топ пользователей по балансу"
        }
    )
    async def leaders_e(self, interaction: Interaction):
        await self.leaders(interaction=interaction)
    

def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(slash_commands(bot, **kwargs))
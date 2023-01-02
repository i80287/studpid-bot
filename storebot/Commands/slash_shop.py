from datetime import datetime, timedelta, timezone
from sqlite3 import connect
from contextlib import closing
from random import randint
from typing import Literal
from time import time

from nextcord import Embed, Colour, ButtonStyle, SlashOption, Interaction,\
        Locale, SelectOption, slash_command, Role, Member, User
from nextcord.ui import Button, View, Select
from nextcord.ext.commands import Bot, Cog
from nextcord.abc import GuildChannel

from Tools.db_commands import check_db_member, \
    peek_role_free_number, peek_free_request_id
from Variables.vars import path_to
from config import in_row

common_text: dict[int, dict[int, str]] = {
    0: {
        0: "**`Sorry, but you can't manage menu called by another member`**",
        1: "**`Economy system and leveling system are disabled on this server`**",
        2: "**`Economy system is disabled on this server`**"
    },
    1: {
        0: "**`Извините, но Вы не можете меню, которое вызвано другим пользователем`**",
        1: "**`Экономическая система и система уровней отключены на этом сервере`**",
        2: "**`Экономическая система отключена на этом сервере`**"
    }
}

text_slash: dict[int, dict[int, str]] = {
    0: {
        0: "Error",
        1: "**`I don't have permission to manage roles on the server`**",
        2: "**`I don't have permission to manage this role. My role should be higher than this role`**",
        3: "Commands",
        4: "**`You already have this role`**",
        5: "**`This item not found. Please, check if you selected right role`**",
        6: "**`For purchasing this role you need {} `{}` more`**",
        7: "Purchase confirmation",
        8: "**`Are you sure that you want to buy`** {}?\n{} {} will be debited from your balance",
        9: "**`Purchase has expired`**",
        10: "Purchase completed",
        11: "**`If your DM are open, then purchase confirmation will be messaged you`**",
        12: "You successfully bought role `{}` on the server `{}` for `{}` {}",
        13: "Role purchase",
        14: "{} bought role {} for {} {}",
        15: "Roles for sale:",
        16: "**`You can't sell the role that you don't have`**",
        17: "**`You can't sell that role because it isn't in the list of roles available for purchase/sale on the server`**",
        18: "The sale is completed",
        19: "**`You sold role `**{}**` for {}`** {}\n**`If your DM are open, then confirmation of sale will be messaged you`**",
        20: "Confirmation of sale",
        21: "**`You sold role {} for {}`** {}",
        22: "Role sale",
        23: "{} sold role {} for {} {}",
        24: "Your balance",
        25: "**Your personal roles:**\n--- **Role** --- **Price** --- **Salary** (if it has)",
        26: "**`Please, wait {} before using this command`**",
        27: "Success",
        28: "**`You gained {}`** {}",
        29: "Work",
        30: "{} gained {} {}",
        31: "**`You can't make a bet, because you need {}`** {} **`more`**",
        32: "Bet",
        33: "**`You bet {}`** {}\n**`Now another user must make a counter bet`**",
        34: "**`Time for the counter bet has expired`**",
        35: "We have a winner!",
        36: "won",
        37: "Duel",
        38: "<@{}> gained {} {}, <@{}> lost",
        39: "**`Sorry, but for money transfering you need {}`** {} **`more`**",
        40: "Transaction completed",  # title
        41: "**`You successfully transfered {}`** {} **`to`** {}",
        42: "Transaction",
        43: "{} transfered {} {} to {}",
        44: "**`Store role number can not be less than 1`**",
        45: "**`There is no role with such number in the store`**",
        46: "**`Role is not found on the server. May be it was deleted`**",
        47: "**`You gained {}`** {} **`from the /work command and {}`** {} **`additionally from your roles`**",
    },
    1: {
        0: "Ошибка",  # title
        1: "**`У меня нет прав управлять ролями на сервере`**",
        2: "**`У меня нет прав управлять этой ролью. Моя роль должна быть выше, чем указанная Вами роль`**",
        3: "Команды",  # title
        4: "**`У Вас уже есть эта роль`**",
        5: "**`Такой товар не найден. Пожалуйста, проверьте правильность выбранной роли`**",
        6: "**`Для покупки роли Вам не хватает {} `**{}",
        7: "Подтверждение покупки",
        8: "**`Вы уверены, что хотите купить роль`** {}?\nС Вас будет списано **`{}`** {}",
        9: '**`Истекло время подтверждения покупки`**',
        10: "Покупка совершена",  # title
        11: "**`Если у Вас включена возможность получения личных сообщений от участников серверов, то подтверждение покупки будет выслано Вам в личные сообщения`**",
        12: "Вы успешно купили роль `{}` на сервере `{}` за `{}` {}",
        13: "Покупка роли",
        14: "{} купил роль {} за {} {}",
        15: "Роли на продажу:",
        16: "**`Вы не можете продать роль, которой у Вас нет`**",
        17: "**`Продажа этой роли невозможна, т.к. она не находится в списке ролей, доступных для покупки/продажи на сервере`**",
        18: "Продажа совершена",  # title
        19: "**`Вы продали роль `**{}**` за {}`** {}\n**`Если у Вас включена возможность получения личных сообщений от участников серверов, то подтверждение продажи будет выслано Вам в личные сообщения`**",
        20: "Подтверждение продажи",
        21: "**`Вы продали роль {} за {}`** {}",
        22: "Продажа роли",
        23: "{} продал роль {} за {} {}",
        24: "Ваш баланс",
        25: "**Ваши личные роли:**\n--- **Роль** --- **Цена** --- **Доход** (если есть)",
        26: "**`Пожалуйста, подождите {} перед тем, как снова использовать эту команду`**",
        27: "Успех",
        28: "**`Вы заработали {}`** {}",
        29: "Работа",
        30: "{} заработал {} {}",
        31: "**`Вы не можете сделать ставку, так как Вам не хватает {}`** {}",
        32: "Ставка",
        33: "**`Вы сделали ставку в размере {}`** {}\n**`Теперь кто-то должен принять Ваш вызов`**",
        34: "**`Истекло время ожидания встречной ставки`**",
        35: "У нас победитель!",
        36: "выиграл(a)",
        37: "Дуэль",
        38: "<@{}> заработал(a) {} {}, <@{}> - проиграл(a)",
        39: "**`Извините, но для совершения перевода Вам не хватает {}`** {}",
        40: "Перевод совершён",
        41: "**`Вы успешно перевели {}`** {} **`пользователю`** {}",
        42: "Транзакция",
        43: "{} передал {} {} пользователю {}",
        44: "**`Номер роли в магазине не может быть меньше 1`**",
        45: "**`Роли с таким номером нет в магазине`**",
        46: "**`Роль не найдена на сервере. Возможно, она была удалена`**",
        47: "**`Вы заработали {}`** {} **`от команды /work и {}`** {} **`дополнительно от ваших ролей`**",
    }
}

buy_approve_text: dict[int, dict[int, str]] = {
    0: {
        0: "Yes",
        1: "No, cancel purchase"
    },
    1: {
        0: "Да",
        1: "Нет, отменить покупку"
    }
}

store_text: dict[int, dict[int, str]] = {
    0: {
        0: "{} **•** <@&{}>\n`Price` - `{}` {}\n`Left` - `1`\n`Listed for sale:`\n*{}*\n",
        1: "{} **•** <@&{}>\n`Price` - `{}` {}\n`Left` - `{}`\n`Last listed for sale:`\n*{}*\n",
        2: "`Average passive salary per week` - `{}` {}\n",
        3: "Page {} from {}",
        4: "Sort by...",
        5: "Sort by price",
        6: "Sort by date",
        7: "Sort from...",
        8: "From the lower price / newer role",
        9: "From the higher price / older role",
        10: "Roles for sale:"

    },
    1: {
        0: "{} **•** <@&{}>\n`Цена` - `{}` {}\n`Осталось` - `1`\n`Выставленa на продажу:`\n*{}*\n",
        1: "{} **•** <@&{}>\n`Цена` - `{}` {}\n`Осталось` - `{}`\n`Последний раз выставленa на продажу:`\n*{}*\n",
        2: "`Средний пассивный доход за неделю` - `{}` {}\n",
        3: "Страница {} из {}",
        4: "Сортировать по...",
        5: "Сортировать по цене",
        6: "Сортировать по дате",
        7: "Сортировать от...",
        8: "От меньшей цены / более свежого товара",
        9: "От большей цены / более старого товара",
        10: "Роли на продажу:"
    }
}

profile_text: dict[int, dict[int, str]] = {
    0: {
        1: "Cash",
        2: "Xp",
        3: "Level",
        4: "Place in the rating",
        5: "**`Information about member:`**\n<@{}>",
        6: "**`You don't have any roles from the bot's store`**"
    },
    1: {
        1: "Кэш",
        2: "Опыт",
        3: "Уровень",
        4: "Место в рейтинге",
        5: "**`Информация о пользователе:`**\n<@{}>",
        6: "**`У Вас нет ролей из магазина бота`**"
    }
}

code_blocks: dict[int, str] = {
    0: "```\nMember's personal roles\n```",
    5: "```\nЛичные роли пользователя\n```",
    1: "```fix\n{}\n```",
    2: "```c\n{}\n```",
}

bet_text: dict[int, dict[int, str]] = {
    0: {
        0: "Make a counter bet",
        1: "Cancel bet",
        2: "**`Sorry, but you can't make counter bet for yourself`**",
        3: "**`Sorry, but you can't make counter bet, because you need at least {}`** {}",
        4: "**`Sorry, but you can't control bet made by another user`**",
        5: "**`Bet was cancelled by user`**"
    },
    1: {
        0: "Сделать встречную ставку",
        1: "Отменить ставку",
        2: "**`Извините, но Вы не можете делать встречную ставку самому себе`**",
        3: "**`Извините, но Вы не можете сделать встречную ставку, так как Вам не хватает {}`** {}",
        4: "**`Извините, но Вы не можете управлять чужой ставкой`**",
        5: "**`Ставка была отменена пользователем`**"
    }
}

rating_text: dict[int, dict[int, str]] = {
    0: {
        0: "Top members by balance",
        1: "Top members by xp",
        2: "Page {} from {}",
        3: "{} place",
        4: "{} level",
        5: "Sort by...",
        6: "Sort by cash",
        7: "Sort by xp",
    },
    1: {
        0: "Топ пользователей по балансу",
        1: "Топ пользователей по опыту",
        2: "Страница {} из {}",
        3: "{} место",
        4: "{} уровень",
        5: "Сортировать по...",
        6: "Сортировать по кэшу",
        7: "Сортировать по опыту",
    }
}


class CustomButton(Button):
    def __init__(self, label: str, custom_id: str, style=ButtonStyle.secondary, emoji=None) -> None:
        super().__init__(style=style, label=label, custom_id=custom_id, emoji=emoji)

    async def callback(self, interaction: Interaction) -> None:
        await self.view.click_b(interaction, self.custom_id)


class CustomSelect(Select):
    def __init__(self, custom_id: str, placeholder: str, opts: list) -> None:
        super().__init__(custom_id=custom_id, placeholder=placeholder, options=opts)

    async def callback(self, interaction: Interaction) -> None:
        await self.view.click_menu(interaction, self.custom_id, self.values)


class BetView(View):
    def __init__(self, timeout: int, lng: int, auth_id: int, bet: int, currency: str) -> None:
        super().__init__(timeout=timeout)
        self.bet: int = bet
        self.auth_id: int = auth_id
        self.dueler: int | None = None
        self.declined: bool = False
        self.currency: str = currency
        self.add_item(CustomButton(
            label=bet_text[lng][0],
            custom_id=f"36_{auth_id}_{randint(1, 100)}",
            style=ButtonStyle.green,
            emoji="💰"
        ))
        self.add_item(CustomButton(
            label=bet_text[lng][1],
            custom_id=f"37_{auth_id}_{randint(1, 100)}",
            style=ButtonStyle.red,
            emoji="❌"
        ))

    async def click_b(self, interaction: Interaction, c_id: str) -> None:
        memb_id: int = interaction.user.id
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0

        if c_id.startswith("36_"):
            if memb_id == self.auth_id:
                await interaction.response.send_message(embed=Embed(description=bet_text[lng][2]), ephemeral=True)
                return
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    db_cash: tuple[int] | None = cur.execute('SELECT money FROM users WHERE memb_id = ?', (memb_id,)).fetchone()
                    if not db_cash:
                        cur.execute(
                            "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, pending_requests) VALUES (?, ?, ?, ?, ?, ?)",
                            (memb_id, 0, "", 0, 0, 0))
                        base.commit()
                        cash: int = 0
                    else:
                        cash: int = db_cash[0]

            if cash < self.bet:
                emb: Embed = Embed(
                    description=bet_text[lng][3].format(self.bet - cash, self.currency),
                    colour=Colour.red()
                )
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


class StoreView(View):
    def __init__(self, timeout: int, db_store: list[tuple[int, int, int, int, int, int, int, int]], auth_id: int,
                 lng: int, in_row: int, currency: str, tz: int) -> None:
        super().__init__(timeout=timeout)
        self.db_store: list[tuple[int, int, int, int, int, int, int, int]] = db_store
        self.l: int = len(db_store)
        self.auth_id: int = auth_id
        self.in_row: int = in_row
        self.currency: str = currency
        self.tz: int = tz  # time zone of the guild
        self.sort_by_price: bool = True  # True - sort by price, False - sort by date (time)
        self.sort_reversed: bool = False  # возрастание / убывание при сортировке, False - возрастание
        self.lng: int = lng
        self.pages: int = max(1, (self.l + in_row - 1) // in_row)

        self.add_item(CustomButton(label="", custom_id=f"32_{auth_id}_{randint(1, 100)}", emoji="⏮️"))
        self.add_item(CustomButton(label="", custom_id=f"33_{auth_id}_{randint(1, 100)}", emoji="◀️"))
        self.add_item(CustomButton(label="", custom_id=f"34_{auth_id}_{randint(1, 100)}", emoji="▶️"))
        self.add_item(CustomButton(label="", custom_id=f"35_{auth_id}_{randint(1, 100)}", emoji="⏭"))

        sort_by_what_options: list[SelectOption] = [
            SelectOption(
                label=store_text[lng][5],
                value="0",
                emoji="💰",
                default=True
            ),
            SelectOption(
                label=store_text[lng][6],
                value="1",
                emoji="📅",
                default=False
            )
        ]
        self.add_item(CustomSelect(
            custom_id=f"102_{auth_id}_{randint(1, 100)}",
            placeholder=store_text[lng][4],
            opts=sort_by_what_options
        ))
        sort_how_options: list[SelectOption] = [
            SelectOption(
                label=store_text[lng][8],
                value="0",
                emoji="↗️",
                default=True
            ),
            SelectOption(
                label=store_text[lng][9],
                value="1",
                emoji="↘️",
                default=False
            )
        ]
        self.add_item(CustomSelect(custom_id=f"103_{auth_id}_{randint(1, 100)}", placeholder=store_text[lng][7],
                                   opts=sort_how_options))

    def sort_store(self) -> None:
        if self.sort_reversed:
            if self.sort_by_price:
                # Reversed sort by price, from higher to lower. 
                # If prices are equal sort by date from higher to lower (latest is higher, early date is lower)
                # tup[3] - price of the role, tup[4] - last date of adding role to the store
                self.db_store.sort(key=lambda tup: (tup[3], tup[4]), reverse=True)
            else:
                # Reversed sort by date from lower to higher (early date is lower, goes first) 
                # If dates are equal then item with lower price goes first
                # tup[3] - price of the role, tup[4] - last date of adding role to the store.
                self.db_store.sort(key=lambda tup: (tup[4], tup[3]), reverse=False)
            return
        # If sort is not reversed
        if self.sort_by_price:
            # Sort by price from lower to higher 
            # If prices are equal sort by date from higher to lower (latest is higher, early date is lower)
            # tup[3] - price of the role, tup[4] - last date of adding role to the store.
            self.db_store.sort(key=lambda tup: tup[4], reverse=True)
            self.db_store.sort(key=lambda tup: tup[3], reverse=False)
        else:
            # Sort by date from higher to lower (latest is higher, early date is lower)
            # If dates are equal then item with lower price goes first
            # tup[3] - price of the role, tup[4] - last date of adding role to the store.
            self.db_store.sort(key=lambda tup: tup[3], reverse=False)
            self.db_store.sort(key=lambda tup: tup[4], reverse=True)

    async def update_menu(self, interaction: Interaction, click: int) -> None:
        text: str = interaction.message.embeds[0].footer.text

        if not self.lng:
            t1: int = text.find('Pa')
            t2: int = text.find('fr', t1)
            page: int = int(text[t1 + 5:t2 - 1])
        else:
            t1: int = text.find('Ст')
            t2: int = text.find('из', t1)
            page: int = int(text[t1 + 9:t2 - 1])

        if click in {1, 2} and page <= 1:
            return
        elif click in {3, 4} and page >= self.pages:
            return

        if click == 1:
            page = 1
        elif click == 2:
            page -= 1
        elif click == 3:
            page += 1
        elif click == 4:
            page = self.pages

        store_list: list[str] = []
        tzinfo: timezone = timezone(timedelta(hours=self.tz))
        for role_number, r, q, p, d, s, s_t, tp in self.db_store[(page - 1) * self.in_row:min(page * self.in_row, self.l)]:
            date: str = datetime.fromtimestamp(d, tz=tzinfo).strftime("%H:%M %d-%m-%Y")
            role_info: str | None = None
            if tp == 1:
                role_info = store_text[self.lng][0].format(role_number, r, p, self.currency, date)
            elif tp == 2:
                role_info = store_text[self.lng][1].format(role_number, r, p, self.currency, q, date)
            elif tp == 3:
                role_info = store_text[self.lng][1].format(role_number, r, p, self.currency, "∞", date)
            if role_info:
                if s:
                    role_info += store_text[self.lng][2].format(s * 604800 // s_t, self.currency)
                store_list.append(role_info)

        if store_list:
            emb: Embed = Embed(title=store_text[self.lng][10], colour=Colour.dark_gray(), description='\n'.join(store_list))
            emb.set_footer(text=store_text[self.lng][3].format(page, self.pages))
            if click == 0:
                await interaction.response.edit_message(embed=emb, view=self)
            else:
                await interaction.response.edit_message(embed=emb)

    async def click_b(self, interaction: Interaction, c_id: str) -> None:
        if c_id.startswith("32_"):
            click: int = 1
        elif c_id.startswith("33_"):
            click: int = 2
        elif c_id.startswith("34_"):
            click: int = 3
        elif c_id.startswith("35_"):
            click: int = 4
        else:
            click: int = 0

        await self.update_menu(interaction=interaction, click=click)

    async def click_menu(self, interaction: Interaction, c_id: str, values: list[str]) -> None:
        if c_id.startswith("102_"):
            if values[0].isdigit() and int(values[0]):
                self.sort_by_price = False
                self.children[4].options[0].default = False
                self.children[4].options[1].default = True
            else:
                self.sort_by_price = True
                self.children[4].options[0].default = True
                self.children[4].options[1].default = False

        elif c_id.startswith("103_"):
            if values[0].isdigit() and int(values[0]):
                self.sort_reversed = True
                self.children[5].options[0].default = False
                self.children[5].options[1].default = True
            else:
                self.sort_reversed = False
                self.children[5].options[0].default = True
                self.children[5].options[1].default = False

        self.sort_store()
        await self.update_menu(interaction=interaction, click=0)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
            await interaction.response.send_message(embed=Embed(description=common_text[lng][0]), ephemeral=True)
            return False
        return True


class BuyView(View):
    def __init__(self, timeout: int, auth_id: int, lng: int) -> None:
        super().__init__(timeout=timeout)
        self.auth_id: int = auth_id
        self.value: bool = False
        self.add_item(CustomButton(
            label=buy_approve_text[lng][0],
            custom_id=f"30_{auth_id}_{randint(1, 100)}",
            style=ButtonStyle.green, emoji="✅")
        )
        self.add_item(CustomButton(
            label=buy_approve_text[lng][1],
            custom_id=f"31_{auth_id}_{randint(1, 100)}",
            style=ButtonStyle.red, emoji="❌"
        ))

    async def click_b(self, _, c_id: str) -> None:
        if c_id.startswith("30_"):
            self.value = True
            self.stop()
        elif c_id.startswith("31_"):
            self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
            await interaction.response.send_message(embed=Embed(description=common_text[lng][0]), ephemeral=True)
            return False
        return True


class RatingView(View):
    def __init__(self, timeout: int, lng: int, auth_id: int, l: int, cash_list: list[tuple[int, int]], 
                 xp_list: list[tuple[int, int]], xp_b: int, in_row: int, ec_status: int, rnk_status: int, currency: str) -> None:
        super().__init__(timeout=timeout)
        self.xp_b: int = xp_b
        self.cash_list: list[tuple[int, int]] = cash_list
        self.xp_list: list[tuple[int, int]] = xp_list
        self.pages: int = max(1, (l + in_row - 1) // in_row)
        self.currency: str = currency
        self.in_row: int = in_row
        self.auth_id: int = auth_id
        self.lng: int = lng
        # True - show ranking by cash, False - by xp
        self.sort_value: bool = True if ec_status else False        
        self.add_item(CustomButton(label="", custom_id=f"38_{auth_id}_{randint(1, 100)}", emoji="⏮️"))
        self.add_item(CustomButton(label="", custom_id=f"39_{auth_id}_{randint(1, 100)}", emoji="◀️"))
        self.add_item(CustomButton(label="", custom_id=f"40_{auth_id}_{randint(1, 100)}", emoji="▶️"))
        self.add_item(CustomButton(label="", custom_id=f"41_{auth_id}_{randint(1, 100)}", emoji="⏭"))
        if ec_status and rnk_status:
            opts: list[SelectOption] = [
                SelectOption(
                    label=rating_text[lng][6],
                    value=0,
                    emoji="💰",
                    default=True
                ),
                SelectOption(
                    label=rating_text[lng][7],
                    value=1,
                    emoji="✨",
                    default=False
                )
            ]
            self.add_item(
                CustomSelect(custom_id=f"104_{auth_id}_{randint(1, 100)}", placeholder=rating_text[lng][3], opts=opts))

    async def update_menu(self, interaction: Interaction, click: int) -> None:
        # page_text = interaction.message.embeds[0].footer.text
        # if not self.lng:
        #     t1 = page_text.find("Pa")
        #     t2 = page_text.find("fr", t1)
        #     page = int(page_text[t1+5:t2-1])
        # else:
        #     t1 = page_text.find("Ст")
        #     t2 = page_text.find("из", t1)
        #     page = int(page_text[t1+9:t2-1])

        page: int = int(interaction.message.embeds[0].footer.text.split(" ")[1])

        if click in {1, 2} and page <= 1:
            return
        elif click in {3, 4} and page >= self.pages:
            return

        if click == 1:
            page = 1
        elif click == 2:
            page -= 1
        elif click == 3:
            page += 1
        elif click == 4:
            page = self.pages

        counter: int = (page - 1) * self.in_row + 1

        if self.sort_value:
            emb: Embed = Embed(title=rating_text[self.lng][0], colour=Colour.dark_gray())
            for r in self.cash_list[(page - 1) * self.in_row:min(page * self.in_row, len(self.cash_list))]:
                emb.add_field(name=rating_text[self.lng][3].format(counter), value=f"<@{r[0]}>\n{r[1]} {self.currency}",
                              inline=False)
                counter += 1
        else:
            emb: Embed = Embed(title=rating_text[self.lng][1], colour=Colour.dark_gray())
            for r in self.xp_list[(page - 1) * self.in_row:min(page * self.in_row, len(self.xp_list))]:
                level: int = (r[1] - 1) // self.xp_b + 1
                emb.add_field(
                    name=rating_text[self.lng][3].format(counter),
                    value=f"<@{r[0]}>\n{rating_text[self.lng][4].format(level)}",
                    inline=False
                )
                counter += 1

        emb.set_footer(text=rating_text[self.lng][2].format(page, self.pages))
        if not click:
            await interaction.response.edit_message(embed=emb, view=self)
        else:
            await interaction.response.edit_message(embed=emb)

    async def click_b(self, interaction: Interaction, c_id: str) -> None:
        if c_id.startswith("38_"):
            click: int = 1
        elif c_id.startswith("39_"):
            click: int = 2
        elif c_id.startswith("40_"):
            click: int = 3
        else:
            click: int = 4

        await self.update_menu(interaction=interaction, click=click)

    async def click_menu(self, interaction: Interaction, c_id: str, values: list[str]) -> None:
        if c_id.startswith("104_"):
            if values[0].isdigit() and int(values[0]):
                self.sort_value = False
                self.children[4].options[0].default = False
                self.children[4].options[1].default = True
            else:
                self.sort_value = True
                self.children[4].options[0].default = True
                self.children[4].options[1].default = False

        await self.update_menu(interaction=interaction, click=0)

    async def interaction_check(self, interaction) -> bool:
        if interaction.user.id != self.auth_id:
            lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
            await interaction.response.send_message(embed=Embed(description=common_text[lng][0]), ephemeral=True)
            return False
        return True


class SlashCommandsCog(Cog):
    sell_to_text: dict[int, dict[int, str]] = {
        0 : {
            0: "**`You can't sell role to yourself`**",
            1: "**`You are already selling role`** {}",
            2: "**`Role sale request has been created`**",
            3: "**`You made request for sale role`** <@&{}> **`to`** <@{}> **`for {}`** {}"
        },
        1: {
            0: "**`Вы не можете продать роль самому себе`**",
            1: "**`Вы уже продаёте роль`** {}",
            2: "**`Запрос продажи роли был создан`**",
            3: "**`Вы сделали запрос о продаже роли`** <@&{}> **`пользователю`** <@{}> **`за {}`** {}"
        }
    }

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self.in_row: int = in_row

    @staticmethod
    async def can_role(interaction: Interaction, role: Role, lng: int) -> bool:
        # if not interaction.permissions.manage_roles:
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message(
                embed=Embed(
                    title=text_slash[lng][0],
                    colour=Colour.red(),
                    description=text_slash[lng][1]
                ),
                ephemeral=True
            )
            return False
        elif not role.is_assignable():
            await interaction.response.send_message(
                embed=Embed(
                    title=text_slash[lng][0],
                    colour=Colour.red(),
                    description=text_slash[lng][2]
                ),
                ephemeral=True
            )
            return False

        return True

    async def buy(self, interaction: Interaction, role: Role) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0

        if not await self.can_role(interaction=interaction, role=role, lng=lng):
            return

        member_buyer: User | Member = interaction.user
        memb_id: int = member_buyer.id
        r_id: int = role.id

        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await interaction.response.send_message(
                        embed=Embed(description=common_text[lng][2]),
                        ephemeral=True
                    )
                    return
                store: tuple[int, int, int, int] | None = cur.execute(
                    "SELECT quantity, price, salary, type FROM store WHERE role_id = ?",
                    (r_id,)
                ).fetchone()
                if not store:
                    await interaction.response.send_message(
                        embed=Embed(title=text_slash[lng][0], description=text_slash[lng][5], colour=Colour.red())
                    )
                    return
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
                buyer: tuple[int, int, str, int, int, int] = check_db_member(base=base, cur=cur, memb_id=memb_id)

        # if r_id in {int(x) for x in buyer[2].split("#") if x != ""}:
        if str(r_id) in buyer[2]:
            await interaction.response.send_message(
                embed=Embed(title=text_slash[lng][0], description=text_slash[lng][4], colour=Colour.red()),
                ephemeral=True)
            return

        buyer_cash: int = buyer[1]
        cost: int = store[1]

        if buyer_cash < cost:
            await interaction.response.send_message(
                embed=Embed(
                    title=text_slash[lng][0],
                    colour=Colour.red(),
                    description=text_slash[lng][6].format(cost - buyer_cash, currency)
                ),
                delete_after=10
            )
            return

        emb: Embed = Embed(title=text_slash[lng][7], description=text_slash[lng][8].format(role.mention, cost, currency))

        view: BuyView = BuyView(timeout=30, auth_id=memb_id, lng=lng)
        await interaction.response.send_message(embed=emb, view=view)

        c: bool = await view.wait()
        if c or not view.value:
            await interaction.delete_original_message()
            return

        role_type: int = store[3]
        await member_buyer.add_roles(role)

        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                server_lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
                cur.execute(
                    "UPDATE users SET money = money - ?, owned_roles = ? WHERE memb_id = ?",
                    (cost, buyer[2] + f"#{r_id}", memb_id)
                )
                base.commit()
                if role_type == 1:
                    rowid_to_delete: int = \
                        cur.execute("SELECT rowid FROM store WHERE role_id = ? ORDER BY last_date", (r_id,)).fetchall()[0][0]
                    cur.execute("DELETE FROM store WHERE rowid = ?", (rowid_to_delete,))
                elif role_type == 2:
                    if store[0] > 1:
                        cur.execute("UPDATE store SET quantity = quantity - 1 WHERE role_id = ?", (r_id,))
                    else:
                        cur.execute("DELETE FROM store WHERE role_id = ?", (r_id,))

                if store[2]:
                    role_members: tuple[str] | None = cur.execute(
                        "SELECT members FROM salary_roles WHERE role_id = ?",
                        (r_id,)
                    ).fetchone()
                    if role_members:
                        cur.execute(
                            "UPDATE salary_roles SET members = ? WHERE role_id = ?",
                            (role_members[0] + f"#{memb_id}", r_id)
                        )

                base.commit()
                chnl_id: int = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]

        emb.title = text_slash[lng][10]
        emb.description = text_slash[lng][11]
        await interaction.edit_original_message(embed=emb, view=None)

        try:
            await member_buyer.send(
                embed=Embed(
                    title=text_slash[lng][7],
                    description=text_slash[lng][12].format(role.name,interaction.guild.name, cost,currency),
                    colour=Colour.green()
                )
            )
        except:
            pass

        if chnl_id:
            guild_log_channel: GuildChannel | None = interaction.guild.get_channel(chnl_id)
            if guild_log_channel:
                try:
                    await guild_log_channel.send(embed=Embed(
                        title=text_slash[server_lng][13],
                        description=text_slash[server_lng][14].format(f"<@{memb_id}>", f"<@&{r_id}>", cost, currency)
                    ))
                except:
                    return

    async def store(self, interaction: Interaction) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild.id}/{interaction.guild.id}.db")) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await interaction.response.send_message(
                        embed=Embed(description=common_text[lng][2]),
                        ephemeral=True
                    )
                    return
                tz: int = cur.execute("SELECT value FROM server_info WHERE settings = 'tz'").fetchone()[0]
                db_store: list[tuple[int, int, int, int, int, int, int, int]] = cur.execute(
                    "SELECT * FROM store").fetchall()
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]

        db_l: int = len(db_store)
        l: int = db_l >> 1
        while l:
            for i in range(l, db_l):
                moving_item: tuple[int, int, int, int, int, int, int, int] = db_store[i]
                while i >= l and (db_store[i - l][3] > db_store[i][3] or (
                        db_store[i - l][3] == db_store[i][3] and db_store[i - l][4] < db_store[i][4])):
                    db_store[i] = db_store[i - l]
                    i -= l
                    db_store[i] = moving_item
            l >>= 1

        store_list: list[str] = []
        tz_info: timezone = timezone(timedelta(hours=tz))
        for role_number, r, q, p, d, s, s_t, tp in db_store[:min(in_row, db_l)]:
            date: str = datetime.fromtimestamp(d, tz=tz_info).strftime("%H:%M %d-%m-%Y")
            role_info: str | None = None
            if tp == 1:
                role_info = store_text[lng][0].format(role_number, r, p, currency, date)
            elif tp == 2:
                role_info = store_text[lng][1].format(role_number, r, p, currency, q, date)
            elif tp == 3:
                role_info = store_text[lng][1].format(role_number, r, p, currency, "∞", date)
            if role_info:
                if s:
                    role_info += store_text[lng][2].format(s * 604800 // s_t, currency)
                store_list.append(role_info)

        emb: Embed = Embed(title=text_slash[lng][15], colour=Colour.dark_gray(), description='\n'.join(store_list))

        if db_l:
            emb.set_footer(text=store_text[lng][3].format(1, (db_l + in_row - 1) // in_row))
        else:
            emb.set_footer(text=store_text[lng][3].format(1, 1))

        store_view: StoreView = StoreView(
            timeout=60,
            db_store=db_store,
            auth_id=interaction.user.id,
            lng=lng,
            in_row=in_row,
            currency=currency,
            tz=tz
        )

        await interaction.response.send_message(embed=emb, view=store_view)

        await store_view.wait()
        for button in store_view.children:
            button.disabled = True
        await interaction.edit_original_message(view=store_view)

    async def sell(self, interaction: Interaction, role: Role) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        if not await self.can_role(interaction=interaction, role=role, lng=lng):
            return
        r_id: int = role.id
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await interaction.response.send_message(
                        embed=Embed(description=common_text[lng][2]),
                        ephemeral=True
                    )
                    return
                role_info: tuple[int, int, int, int, int] | None = \
                    cur.execute("SELECT role_id, price, salary, salary_cooldown, type FROM server_roles WHERE role_id = ?", (r_id,)).fetchone()
                if not role_info:
                    await interaction.response.send_message(
                        embed=Embed(
                            title=text_slash[lng][0],
                            description=text_slash[lng][17],
                            colour=Colour.red()
                        ),
                        ephemeral=True
                    )
                    return

                memb_id: int = interaction.user.id
                user: tuple[int, int, str, int, int, int] = check_db_member(base=base, cur=cur, memb_id=memb_id)
                owned_roles: set[str] = {str_role_id for str_role_id in user[2].split("#") if str_role_id}
                str_role_id: str = str(r_id)
                if str_role_id not in owned_roles:
                    await interaction.response.send_message(
                        embed=Embed(colour=Colour.red(), title=text_slash[lng][0], description=text_slash[lng][16]),
                        ephemeral=True)
                    return
                else:
                    owned_roles.remove(str_role_id)

                r_price: int = role_info[1]
                r_sal: int = role_info[2]
                r_sal_c: int = role_info[3]
                r_type: int = role_info[4]

                sale_price_percent: int = cur.execute("SELECT value FROM server_info WHERE settings = 'sale_price_perc'").fetchone()[0]
                sale_price: int = r_price if sale_price_percent == 100 \
                    else r_price * sale_price_percent // 100

                await interaction.user.remove_roles(role)
                new_owned_roles: str = '#' + '#'.join(owned_roles) if owned_roles else ""
                cur.execute(
                    "UPDATE users SET owned_roles = ?, money = money + ? WHERE memb_id = ?",
                    (new_owned_roles, sale_price, memb_id)
                )
                base.commit()

                time_now: int = int(time())
                if r_type == 1:
                    role_free_number: int = peek_role_free_number(cur=cur)
                    cur.execute(
                        "INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (role_free_number, r_id, 1, r_price, time_now, r_sal, r_sal_c, 1)
                    )
                elif r_type == 2:
                    in_store_amount: int = cur.execute("SELECT count() FROM store WHERE role_id = ?", (r_id,)).fetchone()[0]
                    if in_store_amount:
                        cur.execute(
                            "UPDATE store SET quantity = quantity + ?, last_date = ? WHERE role_id = ?",
                            (1, time_now, r_id)
                        )
                    else:
                        role_free_number: int = peek_role_free_number(cur=cur)
                        cur.execute(
                            "INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (role_free_number, r_id, 1, r_price, time_now, r_sal, r_sal_c, 2)
                        )

                elif r_type == 3:
                    in_store_amount: int = cur.execute("SELECT count() FROM store WHERE role_id = ?", (r_id,)).fetchone()[0]
                    if in_store_amount:
                        cur.execute("UPDATE store SET last_date = ? WHERE role_id = ?", (time_now, r_id))
                    else:
                        role_free_number: int = peek_role_free_number(cur=cur)
                        cur.execute(
                            "INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (role_free_number, r_id, -404, r_price, time_now, r_sal, r_sal_c, 3)
                        )

                base.commit()

                if r_sal:
                    role_members: tuple[str] | None = cur.execute("SELECT members FROM salary_roles WHERE role_id = ?", (r_id,)).fetchone()
                    if role_members:
                        cur.execute(
                            "UPDATE salary_roles SET members = ? WHERE role_id = ?",
                            (role_members[0].replace(f"#{memb_id}", ""), r_id)
                        )
                        base.commit()

                chnl_id: int = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
                server_lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]

        emb: Embed = Embed(
            title=text_slash[lng][18],
            description=text_slash[lng][19].format(f"<@&{r_id}>", sale_price, currency),
            colour=Colour.gold()
        )
        await interaction.response.send_message(embed=emb)

        try:
            await interaction.user.send(
                embed=Embed(
                    title=text_slash[lng][20],
                    description=text_slash[lng][21].format(role.name, sale_price,currency),
                    colour=Colour.green()
                )
            )
        except:
            pass
        if chnl_id:
            guild_log_channel: GuildChannel | None = interaction.guild.get_channel(chnl_id)
            if guild_log_channel:
                try:
                    await guild_log_channel.send(embed=Embed(
                        title=text_slash[server_lng][22],
                        description=text_slash[server_lng][23].format(f"<@{memb_id}>", f"<@&{r_id}>", sale_price, currency)
                    ))
                except:
                    return

    async def sell_to(self, interaction: Interaction, role: Role, price: int, target: Member) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        if not await self.can_role(interaction=interaction, role=role, lng=lng):
            return
        memb_id: int = interaction.user.id
        target_id: int = target.id
        if memb_id == target_id:
            await interaction.response.send_message(
                embed=Embed(
                    title=text_slash[lng][0],
                    description=self.sell_to_text[lng][0],
                    colour=Colour.red()
                ),
                ephemeral=True
            )
            return
        role_id: int = role.id
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await interaction.response.send_message(
                        embed=Embed(description=common_text[lng][2]),
                        ephemeral=True
                    )
                    return
                is_role_added_to_server: int = cur.execute(
                    "SELECT count() FROM server_roles WHERE role_id = ?",
                    (role_id,)
                ).fetchone()[0]
                if not is_role_added_to_server:
                    await interaction.response.send_message(
                        embed=Embed(
                            title=text_slash[lng][0],
                            description=text_slash[lng][17],
                            colour=Colour.red()
                        ),
                        ephemeral=True
                    )
                    return

                user: tuple[int, int, str, int, int, int] = check_db_member(base=base, cur=cur, memb_id=memb_id)
                owned_roles: set[str] = {str_role_id for str_role_id in user[2].split("#") if str_role_id}
                str_role_id: str = str(role_id)
                if str_role_id not in owned_roles:
                    await interaction.response.send_message(
                        embed=Embed(
                            title=text_slash[lng][0],
                            description=text_slash[lng][16],
                            colour=Colour.red()
                        ),
                        ephemeral=True
                    )
                    return
                
                is_role_already_being_sold_by_user: int = cur.execute(
                    "SELECT count() FROM sale_requests WHERE seller_id = ? AND role_id = ?",
                    (memb_id, role_id)
                ).fetchone()[0]
                if is_role_already_being_sold_by_user:
                    await interaction.response.send_message(
                        embed=Embed(
                            title=text_slash[lng][0],
                            description=self.sell_to_text[lng][1].format(f"<@&{role_id}>"),
                            colour=Colour.red()
                        ),
                        ephemeral=True
                    )
                    return

                free_request_id: int = peek_free_request_id(cur=cur)
                cur.execute(
                    "INSERT INTO sale_requests (request_id, seller_id, target_id, role_id, price) VALUES (?, ?, ?, ?, ?)",
                    (free_request_id, memb_id, target_id, role_id, price)
                )
                base.commit()
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
        await interaction.response.send_message(
            embed=Embed(
                title=self.sell_to_text[lng][2],
                description=self.sell_to_text[lng][3].format(role_id, target_id, price, currency),
                colour=Colour.green()
            ),
            ephemeral=True
        )

    async def profile(self, interaction: Interaction) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        memb_id: int = interaction.user.id
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                member: tuple[int, int, str, int, int, int] = check_db_member(base=base, cur=cur, memb_id=memb_id)
                xp_b: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
                ec_status: int = \
                    cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]
                rnk_status: int = \
                    cur.execute("SELECT value FROM server_info WHERE settings = 'ranking_enabled'").fetchone()[0]
                if ec_status:
                    membs_cash: list[tuple[int, int]] = \
                        cur.execute("SELECT memb_id, money FROM users ORDER BY money DESC;").fetchall()
                    db_roles: set[int] = {role[0] for role in cur.execute("SELECT role_id FROM server_roles").fetchall()}
                else:
                    membs_cash: list[tuple[int, int]] = []
                    db_roles: set[int] = set()
                if rnk_status:
                    membs_xp: list[tuple[int, int]] = \
                        cur.execute("SELECT memb_id, xp FROM users ORDER BY xp DESC;").fetchall()
                else:
                    membs_xp: list[tuple[int, int]] = []

        if not (ec_status or rnk_status):
            await interaction.response.send_message(embed=Embed(description=common_text[lng][1]), ephemeral=True)
            return

        embs: list[Embed] = []
        l: int = len(membs_cash) if ec_status else len(membs_xp)
        if ec_status:
            # cnt_cash is a place in the rating sorted by cash
            cash: int = member[1]
            if membs_cash[l >> 1][1] < cash:
                cnt_cash: int = 1
                while cnt_cash < l and memb_id != membs_cash[cnt_cash - 1][0]:
                    cnt_cash += 1
            else:
                cnt_cash: int = l
                while cnt_cash > 1 and memb_id != membs_cash[cnt_cash - 1][0]:
                    cnt_cash -= 1

            emb1: Embed = Embed()
            emb1.description = profile_text[lng][5].format(memb_id, memb_id)
            emb1.add_field(name=profile_text[lng][1], value=code_blocks[1].format(cash), inline=True)
            emb1.add_field(name=profile_text[lng][4], value=code_blocks[1].format(cnt_cash), inline=True)
            embs.append(emb1)

        if rnk_status:
            # cnt_cash is a place in the rating sorted by xp
            xp: int = member[4]
            if membs_xp[l >> 1][1] < xp:
                cnt_xp: int = 1
                while cnt_xp < l and memb_id != membs_xp[cnt_xp - 1][0]:
                    cnt_xp += 1
            else:
                cnt_xp: int = l
                while cnt_xp > 1 and memb_id != membs_xp[cnt_xp - 1][0]:
                    cnt_xp -= 1

            level: int = (xp + xp_b - 1) // xp_b

            emb2: Embed = Embed()
            if not len(embs):
                emb2.description = profile_text[lng][5].format(memb_id, memb_id)
            emb2.add_field(name=profile_text[lng][2], value=code_blocks[2].format(f"{xp}/{level * xp_b + 1}"),
                           inline=True)
            emb2.add_field(name=profile_text[lng][3], value=code_blocks[2].format(level), inline=True)
            emb2.add_field(name=profile_text[lng][4], value=code_blocks[2].format(cnt_xp), inline=True)
            embs.append(emb2)

        if ec_status:
            emb3: Embed = Embed()
            on_server_roles: list[Role] = interaction.user.roles
            on_server_roles.remove(interaction.guild.default_role)
            memb_server_db_roles: set[int] | set = set(role.id for role in on_server_roles) & db_roles
            memb_roles: set[int] | set = {int(role_id) for role_id in member[2].split("#") if role_id} if member[2] else set()

            emb3.description = '\n'.join(
                [code_blocks[lng * 5]] + [f"<@&{r}>" for r in memb_server_db_roles]
            ) if memb_server_db_roles else profile_text[lng][6]

            # in case role(s) was(were) removed from user manually, we should update database
            if memb_roles != memb_server_db_roles:
                with closing(
                        connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
                    with closing(base.cursor()) as cur:
                        new_owned_roles: str = '#' + '#'.join(str(role_id) for role_id in memb_server_db_roles)\
                            if memb_server_db_roles else ""
                        cur.execute(
                            "UPDATE users SET owned_roles = ? WHERE memb_id = ?",
                            (new_owned_roles, memb_id)
                        )
                        base.commit()
                        # roles to remove from db
                        for role_id in memb_roles.difference(memb_server_db_roles):
                            if cur.execute("SELECT salary FROM server_roles WHERE role_id = ?", (role_id,)).fetchone()[0]:
                                membs: tuple[str] | None = cur.execute(
                                    "SELECT members FROM salary_roles WHERE role_id = ?",
                                    (role_id,)
                                ).fetchone()
                                if membs:
                                    cur.execute(
                                        "UPDATE salary_roles SET members = ? WHERE role_id = ?",
                                        (membs[0].replace(f"#{memb_id}", ""), role_id)
                                    )
                                    base.commit()
                        # roles to add in db
                        for role_id in memb_server_db_roles.difference(memb_roles):
                            if cur.execute("SELECT salary FROM server_roles WHERE role_id = ?", (role_id,)).fetchone()[0]:
                                membs: tuple[str] | None = cur.execute(
                                    "SELECT members FROM salary_roles WHERE role_id = ?",
                                    (role_id,)
                                ).fetchone()
                                if membs and str(memb_id) not in membs[0]:
                                    cur.execute(
                                        "UPDATE salary_roles SET members = ? WHERE role_id = ?",
                                        (membs[0] + f"#{memb_id}", role_id)
                                    )
                                base.commit()

            embs.append(emb3)

        await interaction.response.send_message(embeds=embs)

    async def work(self, interaction: Interaction) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await interaction.response.send_message(
                        embed=Embed(description=common_text[lng][2]),
                        ephemeral=True
                    )
                    return
                memb_id: int = interaction.user.id
                time_reload: int = cur.execute("SELECT value FROM server_info WHERE settings = 'w_cd'").fetchone()[0]
                member: tuple[int, int, str, int, int, int] = check_db_member(base=base, cur=cur, memb_id=memb_id)
                
                if member[3] and (lasted_time := int(time()) - member[3]) < time_reload:
                    time_l: int = time_reload - lasted_time
                    t_l: str = f"{time_l // 3600}:{(time_l % 3600) // 60}:{time_l % 60}"
                    await interaction.response.send_message(
                        embed=Embed(title=text_slash[lng][0], description=text_slash[lng][26].format(t_l)),
                        ephemeral=True)
                    return

                sal_l: int = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_l'").fetchone()[0]
                sal_r: int = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_r'").fetchone()[0]
                salary: int = randint(sal_l, sal_r)
                member_roles_ids: tuple[int] = tuple(int(role_id) for role_id in member[2].split('#') if role_id)
                if member_roles_ids:
                    query: str = "SELECT additional_salary FROM server_roles WHERE role_id IN ({})"\
                        .format(", ".join(str(role_id) for role_id in member_roles_ids))
                    memb_roles_add_salary: list[tuple[int]] = cur.execute(query).fetchall()
                    # `additional_income` may be equal to 0.
                    additional_income: int = sum(add_salary[0] for add_salary in memb_roles_add_salary)
                    salary += additional_income
                else:
                    additional_income = 0

                cur.execute(
                    "UPDATE users SET money = money + ?, work_date = ? WHERE memb_id = ?",
                    (salary, int(time()), memb_id)
                )
                base.commit()

                chnl_id: int = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
                server_lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]
        
        descr: str = text_slash[lng][28].format(salary, currency) if not additional_income \
            else text_slash[lng][47].format(salary - additional_income, currency, additional_income, currency)
        await interaction.response.send_message(
            embed=Embed(
                title=text_slash[lng][27],
                description=descr,
                colour=Colour.gold()
            )
        )

        if chnl_id:
            guild_log_channel: GuildChannel | None = interaction.guild.get_channel(chnl_id)
            if guild_log_channel:
                try:
                    await guild_log_channel.send(embed=Embed(
                        title=text_slash[server_lng][29],
                        description=text_slash[server_lng][30].format(f"<@{memb_id}>", salary, currency)
                    ))
                except:
                    return

    async def bet(self, interaction: Interaction, amount: int) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        memb_id: int = interaction.user.id

        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await interaction.response.send_message(embed=Embed(description=common_text[lng][2]),
                                                            ephemeral=True)
                    return
                member: tuple[int, int, str, int, int, int] = check_db_member(base=base, cur=cur, memb_id=memb_id)
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
                server_lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]

        if amount > member[1]:
            await interaction.response.send_message(
                embed=Embed(
                    title=text_slash[lng][0],
                    description=text_slash[lng][31].format(amount - member[1], currency), 
                    colour=Colour.red()
                ),
                ephemeral=True
            )
            return

        bet_view: BetView = BetView(timeout=30, lng=lng, auth_id=memb_id, bet=amount, currency=currency)

        emb: Embed = Embed(title=text_slash[lng][32], description=text_slash[lng][33].format(amount, currency))
        await interaction.response.send_message(embed=emb, view=bet_view)

        if await bet_view.wait():
            emb.description = text_slash[lng][34]

        for c in bet_view.children:
            c.disabled = True

        if not bet_view.dueler:
            if bet_view.declined:
                emb.description = bet_text[lng][5]
            await interaction.edit_original_message(embed=emb, view=bet_view)
            await interaction.delete_original_message(delay=7)
            return

        dueler: int = bet_view.dueler

        winner: int = randint(0, 1)
        emb = Embed(title=text_slash[lng][35], colour=Colour.gold())

        if winner:
            loser_id: int = dueler
            winner_id: int = memb_id
            emb.description = f"<@{memb_id}> {text_slash[lng][36]} `{amount}`{currency}"

        else:
            winner_id: int = dueler
            loser_id: int = memb_id
            emb.description = f"<@{dueler}> {text_slash[lng][36]} `{amount}`{currency}"

        with closing(connect(f'{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db')) as base:
            with closing(base.cursor()) as cur:
                cur.execute('UPDATE users SET money = money - ? WHERE memb_id = ?', (amount, loser_id))
                base.commit()
                cur.execute('UPDATE users SET money = money + ? WHERE memb_id = ?', (amount, winner_id))
                base.commit()
                chnl_id: int = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]

        await interaction.edit_original_message(embed=emb, view=bet_view)
        if chnl_id:
            guild_log_channel: GuildChannel | None = interaction.guild.get_channel(chnl_id)
            if guild_log_channel:
                try:
                    await guild_log_channel.send(embed=Embed(
                        title=text_slash[server_lng][37],
                        description=text_slash[server_lng][38].format(winner_id, amount, currency, loser_id)
                    ))
                except:
                    return

    async def transfer(self, interaction: Interaction, value: int, target: Member) -> None:
        memb_id: int = interaction.user.id
        t_id: int = target.id
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await interaction.response.send_message(embed=Embed(description=common_text[lng][2]),
                                                            ephemeral=True)
                    return
                act: tuple[int, int, str, int, int, int] = check_db_member(base=base, cur=cur, memb_id=memb_id)
                check_db_member(base=base, cur=cur, memb_id=t_id)
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
                if value > act[1]:
                    emb: Embed = Embed(
                        title=text_slash[lng][0],
                        description=text_slash[lng][39].format(value - act[1], currency),
                        colour=Colour.red()
                    )
                    await interaction.response.send_message(embed=emb)
                    return

                cur.execute('UPDATE users SET money = money - ? WHERE memb_id = ?', (value, memb_id))
                base.commit()
                cur.execute('UPDATE users SET money = money + ? WHERE memb_id = ?', (value, t_id))
                base.commit()

                chnl_id: int = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]
                server_lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]

        emb = Embed(
            title=text_slash[lng][40],
            description=text_slash[lng][41].format(value, currency, f"<@{t_id}>"),
            colour=Colour.green()
        )
        await interaction.response.send_message(embed=emb)
        if chnl_id:
            guild_log_channel: GuildChannel | None = interaction.guild.get_channel(chnl_id)
            if guild_log_channel:
                try:
                    await guild_log_channel.send(embed=Embed(
                        title=text_slash[server_lng][42],
                        description=text_slash[server_lng][43].format(f"<@{memb_id}>", value, currency, f"<@{t_id}>")
                    ))
                except:
                    return

    async def leaders(self, interaction: Interaction) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                check_db_member(base=base, cur=cur, memb_id=interaction.user.id)
                ec_status: int = \
                    cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]
                rnk_status: int = \
                    cur.execute("SELECT value FROM server_info WHERE settings = 'ranking_enabled'").fetchone()[0]
                if ec_status:
                    membs_cash: list[tuple[int, int]] = sorted(
                        cur.execute("SELECT memb_id, money FROM users").fetchall(), key=lambda tup: tup[1],
                        reverse=True)
                else:
                    membs_cash = []
                if rnk_status:
                    membs_xp: list[tuple[int, int]] = sorted(cur.execute("SELECT memb_id, xp FROM users").fetchall(),
                                                             key=lambda tup: tup[1], reverse=True)
                else:
                    membs_xp = []
                xp_b: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]

        if not (ec_status or rnk_status):
            await interaction.response.send_message(embed=Embed(description=common_text[lng][1]), ephemeral=True)
            return

        l: int = len(membs_cash) if ec_status else len(membs_xp)
        end: int = min(in_row, l)
        counter: int = 1
        if ec_status:
            emb: Embed = Embed(title=rating_text[lng][0], colour=Colour.dark_gray())
            for r in membs_cash[0:end]:
                emb.add_field(name=rating_text[lng][3].format(counter), value=f"<@{r[0]}>\n{r[1]} {currency}",
                              inline=False)
                counter += 1
        else:
            emb: Embed = Embed(title=rating_text[lng][1], colour=Colour.dark_gray())
            for r in membs_xp[0:end]:
                level: int = (r[1] - 1) // xp_b + 1
                emb.add_field(name=rating_text[lng][3].format(counter),
                              value=f"<@{r[0]}>\n{rating_text[lng][4].format(level)}", inline=False)
                counter += 1

        if l:
            emb.set_footer(text=rating_text[lng][2].format(1, (l + in_row - 1) // in_row))
        else:
            emb.set_footer(text=rating_text[lng][2].format(1, 1))

        rate_view: RatingView = RatingView(
            timeout=40,
            lng=lng,
            auth_id=interaction.user.id,
            l=l,
            cash_list=membs_cash,
            xp_list=membs_xp,
            xp_b=xp_b,
            in_row=in_row,
            ec_status=ec_status,
            rnk_status=rnk_status,
            currency=currency
        )

        await interaction.response.send_message(embed=emb, view=rate_view)
        await rate_view.wait()

        for c in rate_view.children:
            c.disabled = True
        await interaction.edit_original_message(view=rate_view)

    @slash_command(
        name="buy",
        description="Makes a role purchase from the store",
        description_localizations={
            Locale.ru: "Совершает покупку роли из магазина"
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
    ) -> None:
        await self.buy(interaction=interaction, role=role)

    @slash_command(
        name="buy_by_number",
        description="Makes a role purchase from the store by role number in the store",
        description_localizations={
            Locale.ru: "Совершает покупку роли из магазина по номеру роли в магазине"
        }
    )
    async def buy_by_number(
        self,
        interaction: Interaction,
        role_number: int = SlashOption(
            name="number",
            name_localizations={
                Locale.ru: "номер"
            },
            description="Number of the role that you want to buy",
            description_localizations={
                Locale.ru: "Номер роли, которую Вы хотите купить"
            },
            required=True
        )
    ) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        if role_number < 1:
            await interaction.response.send_message(
                embed=Embed(colour=Colour.red(),
                            description=text_slash[lng][44]),
                ephemeral=True
            )
            return
        role: Role | None = None
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                role_id_tuple: tuple[int] | None = cur.execute(
                    "SELECT role_id FROM store WHERE role_number = ?",
                    (role_number,)
                ).fetchone()
                if not role_id_tuple:
                    await interaction.response.send_message(
                        embed=Embed(
                            colour=Colour.red(),
                            description=text_slash[lng][45]
                        ),
                        ephemeral=True
                    )
                    return
                role = interaction.guild.get_role(role_id_tuple[0])
        if role:
            await self.buy(interaction=interaction, role=role)
        else:
            await interaction.response.send_message(
                embed=Embed(
                    colour=Colour.red(),
                    description=text_slash[lng][46]
                ),
                ephemeral=True
            )

    @slash_command(
        name="store",
        description="Shows store",
        description_localizations={
            Locale.ru: "Открывает меню магазина"
        }
    )
    async def store_e(self, interaction: Interaction) -> None:
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
    ) -> None:
        await self.sell(interaction=interaction, role=role)

    @slash_command(
        name="sell_to",
        description="Makes role sale request to the target member for the selected price",
        description_localizations={
            Locale.ru: "Делает предложение продажи роли пользователю за указанную цену"
        }
    )
    async def sell_to_e(
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
        ),
        price: int = SlashOption(
            name="price",
            name_localizations={
                Locale.ru: "цена"
            },
            description="Price of the role that is being sold",
            description_localizations={
                Locale.ru: "Цена продаваемой роли"
            },
            min_value=0,
            max_value=999999999,
            required=True
        ),
        target: Member = SlashOption(
            name="target",
            name_localizations={
                Locale.ru: "покупатель"
            },
            description="Member that is supposted to buy the role",
            description_localizations={
                Locale.ru: "Предполагаемый покупатель роли"
            },
            required=True
        )
    ) -> None:
        await self.sell_to(interaction=interaction, role=role, price=price, target=target)

    @slash_command(
        name="profile",
        description="Shows your profile",
        description_localizations={
            Locale.ru: "Показывает меню Вашего профиля"
        }
    )
    async def profile_e(self, interaction: Interaction) -> None:
        await self.profile(interaction=interaction)

    @slash_command(
        name="work",
        description="Allows to gain money",
        description_localizations={
            Locale.ru: "Позволяет заработать деньги"
        }
    )
    async def work_e(self, interaction: Interaction) -> None:
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
    ) -> None:
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
                Locale.ru: "Пользователь, которому Вы хотите перевести деньги"
            },
            required=True
        )
    ) -> None:
        await self.transfer(interaction=interaction, value=value, target=target)

    @slash_command(
        name="leaders",
        description="Shows top members by balance",
        description_localizations={
            Locale.ru: "Показывет топ пользователей по балансу"
        }
    )
    async def leaders_e(self, interaction: Interaction) -> None:
        await self.leaders(interaction=interaction)


def setup(bot: Bot) -> None:
    bot.add_cog(SlashCommandsCog(bot))

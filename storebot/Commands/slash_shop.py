from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import (
        Optional,
        Literal
    )

    from nextcord import Guild

    from storebot.storebot import StoreBot

from datetime import datetime, timedelta, timezone
from sqlite3 import connect, Cursor
from contextlib import closing
from random import randint
from os import urandom
from time import time

from nextcord import (
    Role,
    Embed,
    Locale,
    Colour,
    Member,
    TextChannel,
    ButtonStyle,
    SlashOption,
    SelectOption,
    Interaction,
    slash_command
)
from nextcord.ext.commands import Cog

from storebot.CustomComponents.view_base import ViewBase
from storebot.CustomComponents.custom_button import CustomButton
from storebot.CustomComponents.custom_select import CustomSelectWithOptions
from storebot.CustomComponents.slots_view import SlotsView
from storebot.Tools.db_commands import (
    get_member_async,
    check_member_async,
    peek_role_free_number,
    peek_free_request_id,
    delete_role_from_db,
    get_server_info_value_async,
    get_server_currency_async,
    get_server_slots_table_async
)
from storebot.constants import DB_PATH
if __debug__:
    from storebot.CustomComponents.custom_select import CustomSelect

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
        47: "**`You gained {}`** {} **`from the /work command and {}`** {} **`from your roles`**",
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
        47: "**`Вы заработали {}`** {} **`от команды /work и {}`** {} **`от Ваших ролей`**",
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
        0: "{0} **•** <@&{1}>\n`Price` - `{2:0,}` {3}\n`Left` - `1`\n`Listed for sale:`\n*{4}*\n",
        1: "{0} **•** <@&{1}>\n`Price` - `{2:0,}` {3}\n`Left` - `{4}`\n`Last listed for sale:`\n*{5}*\n",
        2: "`Average passive salary per week` - `{0:0,}` {1}\n",
        3: "Page {0} from {1}",
        4: "Sort by...",
        5: "Sort by price",
        6: "Sort by date",
        7: "Sort from...",
        8: "From the lower price / newer role",
        9: "From the higher price / older role",
        10: "Roles for sale:"

    },
    1: {
        0: "{0} **•** <@&{1}>\n`Цена` - `{2:0,}` {3}\n`Осталось` - `1`\n`Выставленa на продажу:`\n*{4}*\n",
        1: "{0} **•** <@&{1}>\n`Цена` - `{2:0,}` {3}\n`Осталось` - `{4}`\n`Последний раз выставленa на продажу:`\n*{5}*\n",
        2: "`Средний пассивный доход за неделю` - `{0:0,}` {1}\n",
        3: "Страница {0} из {1}",
        4: "Сортировать по...",
        5: "Сортировать по цене",
        6: "Сортировать по дате",
        7: "Сортировать от...",
        8: "От меньшей цены / более свежого товара",
        9: "От большей цены / более старого товара",
        10: "Роли на продажу:"
    }
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


class BetView(ViewBase):
    def __init__(self, timeout: int, lng: int, auth_id: int, bet: int, currency: str) -> None:
        super().__init__(lng=lng, author_id=auth_id, timeout=timeout)
        self.bet: int = bet
        self.dueler: Optional[int] = None
        self.declined: bool = False
        self.currency: str = currency
        self.add_item(CustomButton(
            label=bet_text[lng][0],
            custom_id=f"36_{auth_id}_" + urandom(4).hex(),
            style=ButtonStyle.green,
            emoji="💰"
        ))
        self.add_item(CustomButton(
            label=bet_text[lng][1],
            custom_id=f"37_{auth_id}_" + urandom(4).hex(),
            style=ButtonStyle.red,
            emoji="❌"
        ))

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        assert isinstance(interaction.user, Member)
        memb_id: int = interaction.user.id
        lng: int = self.lng
        if custom_id.startswith("36"):
            if memb_id == self.author_id:
                await interaction.response.send_message(embed=Embed(description=bet_text[lng][2]), ephemeral=True)
                return
            with closing(connect(DB_PATH.format(interaction.guild_id))) as base:
                with closing(base.cursor()) as cur:
                    db_cash: Optional[tuple[int]] = cur.execute("SELECT money FROM users WHERE memb_id = ?", (memb_id,)).fetchone()
                    if not db_cash:
                        cur.execute(
                            "INSERT INTO users (memb_id, money, owned_roles, work_date, xp, voice_join_time) VALUES (?, ?, ?, ?, ?, ?)",
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
            if interaction.user.id != self.author_id:
                await interaction.response.send_message(embed=Embed(description=bet_text[lng][4]), ephemeral=True)
                return
            self.declined = True
            self.stop()

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        return True


class StoreView(ViewBase):
    def __init__(self, timeout: int, db_store: list[tuple[int, int, int, int, int, int, int, int]],
                 auth_id: int, lng: int, in_row: int, currency: str, tz: int) -> None:
        super().__init__(lng=lng, author_id=auth_id, timeout=timeout)
        self.db_store: list[tuple[int, int, int, int, int, int, int, int]] = db_store
        self.l: int = len(db_store)
        self.in_row: int = in_row
        self.currency: str = currency
        self.tz: int = tz  # time zone of the guild
        self.sort_by_price: bool = True  # True - sort by price, False - sort by date (time)
        self.sort_reversed: bool = False  # возрастание / убывание при сортировке, False - возрастание
        self.pages: int = max(1, (self.l + in_row - 1) // in_row)

        self.add_item(CustomButton(label="", custom_id=f"32_{auth_id}_" + urandom(4).hex(), emoji="⏮️"))
        self.add_item(CustomButton(label="", custom_id=f"33_{auth_id}_" + urandom(4).hex(), emoji="◀️"))
        self.add_item(CustomButton(label="", custom_id=f"34_{auth_id}_" + urandom(4).hex(), emoji="▶️"))
        self.add_item(CustomButton(label="", custom_id=f"35_{auth_id}_" + urandom(4).hex(), emoji="⏭"))

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
        self.add_item(CustomSelectWithOptions(
            custom_id=f"102_{auth_id}_" + urandom(4).hex(),
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
        self.add_item(CustomSelectWithOptions(
            custom_id=f"103_{auth_id}_" + urandom(4).hex(),
            placeholder=store_text[lng][7],
            opts=sort_how_options
        ))

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
        assert interaction.message is not None
        assert interaction.message.embeds[0].footer.text is not None
        lng: int = self.lng
        text: str = interaction.message.embeds[0].footer.text
        if not lng:
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
        currency: str = self.currency
        for role_number, role_id, q, price, d, salary, salary_cooldown, role_type in self.db_store[(page - 1) * self.in_row:min(page * self.in_row, self.l)]:
            date: str = datetime.fromtimestamp(d, tz=tzinfo).strftime("%H:%M %d-%m-%Y")
            role_info: str
            match role_type:
                case 1:
                    role_info = store_text[lng][0].format(role_number, role_id, price, currency, date)
                case 2:
                    role_info = store_text[lng][1].format(role_number, role_id, price, currency, q, date)
                case 3:
                    role_info = store_text[lng][1].format(role_number, role_id, price, currency, "∞", date)
                case _:
                    continue
            if salary:
                role_info += store_text[lng][2].format(salary * 604800 // salary_cooldown, currency)
            store_list.append(role_info)

        if store_list:
            emb: Embed = Embed(title=store_text[lng][10], colour=Colour.dark_gray(), description='\n'.join(store_list))
            emb.set_footer(text=store_text[lng][3].format(page, self.pages))
            if click == 0:
                await interaction.response.edit_message(embed=emb, view=self)
            else:
                await interaction.response.edit_message(embed=emb)

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        click: int
        match int(custom_id[:2]):
            case 32:
                click = 1
            case 33:
                click = 2
            case 34:
                click = 3
            case 35:
                click = 4
            case _:
                click = 0

        await self.update_menu(interaction=interaction, click=click)

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        if custom_id.startswith("102_"):
            if values[0].isdigit() and int(values[0]):
                self.sort_by_price = False
                self.children[4].options[0].default = False # type: ignore
                self.children[4].options[1].default = True # type: ignore
            else:
                self.sort_by_price = True
                self.children[4].options[0].default = True # type: ignore
                self.children[4].options[1].default = False # type: ignore
        elif custom_id.startswith("103_"):
            if values[0].isdigit() and int(values[0]):
                self.sort_reversed = True
                self.children[5].options[0].default = False # type: ignore
                self.children[5].options[1].default = True # type: ignore
            else:
                self.sort_reversed = False
                self.children[5].options[0].default = True # type: ignore
                self.children[5].options[1].default = False # type: ignore

        self.sort_store()
        await self.update_menu(interaction=interaction, click=0)


class BuyView(ViewBase):
    def __init__(self, timeout: int, auth_id: int, lng: int) -> None:
        super().__init__(lng=lng, author_id=auth_id, timeout=timeout)
        self.value: bool = False
        self.add_item(CustomButton(
            label=buy_approve_text[lng][0],
            custom_id=f"30_{auth_id}_" + urandom(4).hex(),
            style=ButtonStyle.green, emoji="✅"
        ))
        self.add_item(CustomButton(
            label=buy_approve_text[lng][1],
            custom_id=f"31_{auth_id}_" + urandom(4).hex(),
            style=ButtonStyle.red, emoji="❌"
        ))

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        if custom_id.startswith("30_"):
            self.value = True
            self.stop()
        elif custom_id.startswith("31_"):
            self.stop()
    
    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        return


class RatingView(ViewBase):
    def __init__(self, timeout: int, lng: int, auth_id: int, l: int, cash_list: list[tuple[int, int]], 
                 xp_list: list[tuple[int, int]], xp_b: int, in_row: int, ec_status: int, rnk_status: int, currency: str) -> None:
        super().__init__(lng=lng, author_id=auth_id, timeout=timeout)
        self.xp_b: int = xp_b
        self.cash_list: list[tuple[int, int]] = cash_list
        self.xp_list: list[tuple[int, int]] = xp_list
        self.pages: int = max(1, (l + in_row - 1) // in_row)
        self.currency: str = currency
        self.in_row: int = in_row
        # True - show ranking by cash, False - by xp
        self.sort_value: bool = True if ec_status else False        
        self.add_item(CustomButton(label="", custom_id=f"38_{auth_id}_" + urandom(4).hex(), emoji="⏮️"))
        self.add_item(CustomButton(label="", custom_id=f"39_{auth_id}_" + urandom(4).hex(), emoji="◀️"))
        self.add_item(CustomButton(label="", custom_id=f"40_{auth_id}_" + urandom(4).hex(), emoji="▶️"))
        self.add_item(CustomButton(label="", custom_id=f"41_{auth_id}_" + urandom(4).hex(), emoji="⏭"))
        if ec_status and rnk_status:
            opts: list[SelectOption] = [
                SelectOption(
                    label=rating_text[lng][6],
                    value="0",
                    emoji="💰",
                    default=True
                ),
                SelectOption(
                    label=rating_text[lng][7],
                    value="1",
                    emoji="✨",
                    default=False
                )
            ]
            self.add_item(item=CustomSelectWithOptions(
                custom_id=f"104_{auth_id}_" + urandom(4).hex(), placeholder=rating_text[lng][3], opts=opts
            ))

    async def update_menu(self, interaction: Interaction, click: int) -> None:
        assert interaction.message is not None
        assert interaction.message.embeds[0].footer.text is not None
        page: int = int(interaction.message.embeds[0].footer.text.split(' ')[1])

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

        counter_start: int = (page - 1) * self.in_row + 1
        lng: int = self.lng
        if self.sort_value:
            emb: Embed = Embed(title=rating_text[lng][0], colour=Colour.dark_gray())
            for counter, role_info in enumerate(self.cash_list[((page - 1) * self.in_row):min((page * self.in_row), len(self.cash_list))], start=counter_start):
                emb.add_field(
                    name=rating_text[lng][3].format(counter),
                    value=f"<@{role_info[0]}>\n{role_info[1]:0,} {self.currency}",
                    inline=False
                )
        else:
            emb: Embed = Embed(title=rating_text[lng][1], colour=Colour.dark_gray())
            for counter, member_info in enumerate(self.xp_list[((page - 1) * self.in_row):min((page * self.in_row), len(self.xp_list))], start=counter_start):
                emb.add_field(
                    name=rating_text[lng][3].format(counter),
                    value=f"<@{member_info[0]}>\n{rating_text[lng][4].format((member_info[1] - 1) // self.xp_b + 1)}",
                    inline=False
                )

        emb.set_footer(text=rating_text[lng][2].format(page, self.pages))
        if not click:
            await interaction.response.edit_message(embed=emb, view=self)
        else:
            await interaction.response.edit_message(embed=emb)

    async def click_button(self, interaction: Interaction, custom_id: str) -> None:
        int_custom_id: int = int(custom_id[:2])
        match int_custom_id:
            case 38:
                click: int = 1
            case 39:
                click: int = 2
            case 40:
                click: int = 3
            case 41:
                click: int = 4
            case _:
                click: int = 0

        await self.update_menu(interaction=interaction, click=click)

    async def click_select_menu(self, interaction: Interaction, custom_id: str, values: list[str]) -> None:
        if custom_id.startswith("104_"):
            if values[0].isdigit() and int(values[0]):
                self.sort_value = False
                self.children[4].options[0].default = False # type: ignore
                self.children[4].options[1].default = True # type: ignore
            else:
                self.sort_value = True
                self.children[4].options[0].default = True # type: ignore
                self.children[4].options[1].default = False # type: ignore

        await self.update_menu(interaction=interaction, click=0)


class SlashCommandsCog(Cog):
    sell_to_text: dict[int, dict[int, str]] = {
        0 : {
            0: "**`You can't sell role to yourself`**",
            1: "**`You are already selling role`** <@&{}>",
            2: "**`Member`** <@{}> **`already has role`** <@&{}>",
            3: "**`Role sale request has been created`**",
            4: "**`You made request for sale role`** <@&{}> **`to`** <@{}> **`for {}`** {}"
        },
        1: {
            0: "**`Вы не можете продать роль самому себе`**",
            1: "**`Вы уже продаёте роль`** <@&{}>",
            2: "**`У пользователя`** <@{}> **`уже есть роль`** <@&{}>",
            3: "**`Запрос продажи роли был создан`**",
            4: "**`Вы сделали запрос о продаже роли`** <@&{}> **`пользователю`** <@{}> **`за {}`** {}"
        }
    }
    profile_text: dict[int, dict[int, str]] = {
        0: {
            1: "Cash",
            2: "Xp",
            3: "Level",
            4: "Place in the rating",
            5: "**`Information about member:`**\n<@{}>",
            6: "**`You don't have any roles from the bot's store`**",
            7: "**`Request id: {} role:`** <@&{}> **`price: {}`** {} **`target:`** <@{}>",
            8: "**`Request id: {} role:`** <@&{}> **`price: {}`** {} **`seller:`** <@{}>",
        },
        1: {
            1: "Кэш",
            2: "Опыт",
            3: "Уровень",
            4: "Место в рейтинге",
            5: "**`Информация о пользователе:`**\n<@{}>",
            6: "**`У Вас нет ролей из магазина бота`**",
            7: "**`id предложения: {} роль:`** <@&{}> **`цена: {}`** {} **`кому:`** <@{}>",
            8: "**`id предложения: {} роль:`** <@&{}> **`цена: {}`** {} **`продавец:`** <@{}>",
        }
    }
    code_blocks: dict[int, dict[int, str]] = {
        0: {
            0: "```\nMember's personal roles\n```",
            1: "```yaml\nRole sale requests made by you\n```",
            2: "```yaml\nRole purchase requests made for you\n```",
        },
        1: {
            0: "```\nЛичные роли пользователя\n```",
            1: "```yaml\n`Запросы продажи роли, сделанные вами\n```",
            2: "```yaml\nЗапросы покупки роли, сделанные вам\n```",
        },
        2: {
            1: "```fix\n{}\n```",
            2: "```fix\n{}\n```",
        }       
    }
    manage_requests_text: dict[int, dict[int, str]] = {
        0: {
            0: "**`You have not received role purchase/sale request with such id`**",
            1: "**`You have not received role purchase request with sush id`**",
            2: "**`The role offered to you no longer exists on the server`**",
            3: "**`For purchasing this role you need {}`** {} **`more`**",
            4: "**`At the moment you already have this role`**",
            5: "**`At the moment, the seller is not on the server`**",
            6: "**`The seller no longer has the role offered to you`**",
            7: "**`When adding/removing a role, an access rights error occurred`**",
            8: "**`You bought role`** <@&{}> **`from`** <@{}> **`for {}`** {}",
            9: "**`You deleted your role sale request for role`** <@&{}>",
            10: "**`You declined role purchase request for role`** <@&{}>",
        },
        1: {
            0: "**`Вы вас нет предложения от покупке/продаже роли c таким id`**",
            1: "**`Вам не приходило предложение покупке роли c таким id`**",
            2: "**`Продаваемой Вам роли больше нет на сервере`**",
            3: "**`Для покупки роли Вам не хватает {}`** {}",
            4: "**`На данный момент у Вас уже есть эта роль`**",
            5: "**`На данный момент продавца нет на сервере`**",
            6: "**`У продавца больше нет продаваемой вам роли`**",
            7: "**`При добавлении/изъятии роли возникла ошибка права доступа`**",
            8: "**`Вы купили роль`** <@&{}> **`у`** <@{}> **`за {}`** {}",
            9: "**`Вы удалили своё предложение продажи роли`** <@&{}>",
            10: "**`Вы отклонили предложение покупки роли`** <@&{}>",
        }
    }

    def __init__(self, bot: StoreBot) -> None:
        from storebot.config import in_row
        self.in_row: Literal[5] = in_row

    @classmethod
    async def can_role(cls, interaction: Interaction, role: Role, lng: int) -> bool:
        # if not interaction.permissions.manage_roles:
        assert interaction.guild is not None
        if not interaction.guild.me.guild_permissions.manage_roles:
            await cls.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][1])
            return False
        elif not role.is_assignable():
            await cls.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][2])
            return False

        return True

    @classmethod
    async def verify_request_id(cls, cur: Cursor, request_id: int, interaction: Interaction, memb_id: int) -> Optional[tuple[int, int, int, int]]:        
        assert interaction.locale is not None
        request: Optional[tuple[int, int, int, int]] = cur.execute(
            "SELECT seller_id, target_id, role_id, price FROM sale_requests WHERE request_id = ? AND (seller_id = ? OR target_id = ?)",
            (request_id, memb_id, memb_id)
        ).fetchone()
        if not request:
            lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
            await cls.respond_with_error_report(interaction=interaction, lng=lng, answer=cls.manage_requests_text[lng][0])
        return request

    @classmethod
    async def respond_with_error_report(cls, interaction: Interaction, lng: int, answer: str) -> None:
        await interaction.response.send_message(
            embed=Embed(
                title=text_slash[lng][0],
                description=answer, 
                colour=Colour.dark_grey()
            ),
            ephemeral=True
        )

    async def buy(self, interaction: Interaction, role: Role) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0

        if not await self.can_role(interaction=interaction, role=role, lng=lng):
            return

        member_buyer: Member = interaction.user
        memb_id: int = member_buyer.id
        r_id: int = role.id
        guild_id: int = interaction.guild_id
        with closing(connect(DB_PATH.format(guild_id))) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=common_text[lng][2])
                    return

                store: Optional[tuple[int, int, int, int]] = cur.execute(
                    "SELECT quantity, price, salary, type FROM store WHERE role_id = ?",
                    (r_id,)
                ).fetchone()

                if not store:
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][5])
                    return
                
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
        
        buyer: tuple[int, int, str, int, int, int] = await get_member_async(guild_id=guild_id, member_id=memb_id)

        # if r_id in {int(x) for x in buyer[2].split("#") if x}:
        if str(r_id) in buyer[2]:
            await self.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][4])
            return

        buyer_cash: int = buyer[1]
        cost: int = store[1]

        if buyer_cash < cost:
            await self.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][6].format(cost - buyer_cash, currency))
            return

        emb: Embed = Embed(title=text_slash[lng][7], description=text_slash[lng][8].format(role.mention, cost, currency))

        view: BuyView = BuyView(timeout=30, auth_id=memb_id, lng=lng)
        await interaction.response.send_message(embed=emb, view=view)

        c: bool = await view.wait()
        if c or not view.value:
            try:
                await interaction.delete_original_message()
            except:
                return
            return

        role_type: int = store[3]
        await member_buyer.add_roles(role)

        with closing(connect(DB_PATH.format(interaction.guild_id))) as base:
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
                    role_members: Optional[tuple[str]] = cur.execute(
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
        try:
            await interaction.edit_original_message(embed=emb, view=None)
        except:
            pass

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
        if chnl_id and isinstance(guild_log_channel := interaction.guild.get_channel(chnl_id), TextChannel):
            try:
                await guild_log_channel.send(embed=Embed(
                    title=text_slash[server_lng][13],
                    description=text_slash[server_lng][14].format(f"<@{memb_id}>", f"<@&{r_id}>", cost, currency)
                ))
            except:
                return

    async def store(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None, "guild_id"
        assert interaction.locale is not None, "locale"
        assert isinstance(interaction.user, Member), "isinstance Member"
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        with closing(connect(DB_PATH.format(interaction.guild_id))) as base:
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
        in_row: Literal[5] = self.in_row
        for role_number, r, q, p, d, salary, salary_cooldown, role_type in db_store[:min(in_row, db_l)]:
            date: str = datetime.fromtimestamp(d, tz=tz_info).strftime("%H:%M %d-%m-%Y")
            role_info: str
            match role_type:
                case 1:
                    role_info = store_text[lng][0].format(role_number, r, p, currency, date)
                case 2:
                    role_info = store_text[lng][1].format(role_number, r, p, currency, q, date)
                case 3:
                    role_info = store_text[lng][1].format(role_number, r, p, currency, "∞", date)
                case _:
                    continue
            if salary:
                role_info += store_text[lng][2].format(salary * 604800 // salary_cooldown, currency)
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
            assert isinstance(button, (CustomButton, CustomSelect)), "CustomButton, CustomSelect"
            button.disabled = True
        try:
            await interaction.edit_original_message(view=store_view)
        except:
            return

    async def sell(self, interaction: Interaction, role: Role) -> None:
        assert interaction.user is not None
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        if not await self.can_role(interaction=interaction, role=role, lng=lng):
            return
        
        r_id: int = role.id
        memb_id: int = interaction.user.id
        guild_id: int = interaction.guild_id

        user_owned_roles: list[str] = ((await get_member_async(guild_id=guild_id, member_id=memb_id))[2]).split("#")
        with closing(connect(DB_PATH.format(guild_id))) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await interaction.response.send_message(
                        embed=Embed(description=common_text[lng][2]),
                        ephemeral=True
                    )
                    return
                role_info: Optional[tuple[int, int, int, int, int]] = \
                    cur.execute("SELECT role_id, price, salary, salary_cooldown, type FROM server_roles WHERE role_id = ?", (r_id,)).fetchone()
                if not role_info:
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][17])
                    return

                owned_roles: set[str] = {str_role_id for str_role_id in user_owned_roles if str_role_id}
                str_role_id: str = str(r_id)
                if str_role_id not in owned_roles:
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][16])
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
                cur.execute("DELETE FROM sale_requests WHERE seller_id = ? AND role_id = ?", (memb_id, r_id))
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
                    role_members: Optional[tuple[str]] = cur.execute("SELECT members FROM salary_roles WHERE role_id = ?", (r_id,)).fetchone()
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
        if chnl_id and isinstance(guild_log_channel := interaction.guild.get_channel(chnl_id), TextChannel):
            try:
                await guild_log_channel.send(embed=Embed(
                    title=text_slash[server_lng][22],
                    description=text_slash[server_lng][23].format(f"<@{memb_id}>", f"<@&{r_id}>", sale_price, currency)
                ))
            except:
                return

    async def sell_to(self, interaction: Interaction, role: Role, price: int, target: Member) -> None:
        assert interaction.guild_id is not None
        assert interaction.locale is not None
        assert interaction.user is not None
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        if not await self.can_role(interaction=interaction, role=role, lng=lng):
            return
        memb_id: int = interaction.user.id
        target_id: int = target.id
        if memb_id == target_id:
            await self.respond_with_error_report(interaction=interaction, lng=lng, answer=self.sell_to_text[lng][0])
            return
        
        role_id: int = role.id
        guild_id: int = interaction.guild_id

        user_owned_roles: list[str] = ((await get_member_async(guild_id=guild_id, member_id=memb_id))[2]).split("#")
        target_owned_roles: list[str] = ((await get_member_async(guild_id=guild_id, member_id=target_id))[2]).split("#")
        with closing(connect(DB_PATH.format(guild_id))) as base:
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
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][17])
                    return

                
                str_role_id: str = str(role_id)
                if str_role_id not in user_owned_roles:
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][16])
                    return
                
                del user_owned_roles
                
                is_role_already_being_sold_by_user: int = cur.execute(
                    "SELECT count() FROM sale_requests WHERE seller_id = ? AND role_id = ?",
                    (memb_id, role_id)
                ).fetchone()[0]
                if is_role_already_being_sold_by_user:
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=self.sell_to_text[lng][1].format(str_role_id))
                    return
                
                if str_role_id in target_owned_roles:
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=self.sell_to_text[lng][2].format(target_id, str_role_id))
                    return

                del target_owned_roles

                free_request_id: int = peek_free_request_id(cur=cur)
                cur.execute(
                    "INSERT INTO sale_requests (request_id, seller_id, target_id, role_id, price) VALUES (?, ?, ?, ?, ?)",
                    (free_request_id, memb_id, target_id, role_id, price)
                )
                base.commit()
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
        
        await interaction.response.send_message(
            embed=Embed(
                title=self.sell_to_text[lng][3],
                description=self.sell_to_text[lng][4].format(str_role_id, target_id, price, currency),
                colour=Colour.green()
            ),
            ephemeral=True
        )

    async def profile(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        memb_id: int = interaction.user.id
        guild_id: int = interaction.guild_id

        db_member_info: tuple[int, int, str, int, int, int] = await get_member_async(guild_id=guild_id, member_id=memb_id)
        with closing(connect(DB_PATH.format(guild_id))) as base:
            with closing(base.cursor()) as cur:
                xp_b: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
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
                sale_role_requests: list[tuple[int, int, int, int]] = cur.execute(
                    "SELECT request_id, target_id, role_id, price FROM sale_requests WHERE seller_id = ?",
                    (memb_id,)
                ).fetchall()
                buy_role_requests: list[tuple[int, int, int, int]] = cur.execute(
                    "SELECT request_id, seller_id, role_id, price FROM sale_requests WHERE target_id = ?",
                    (memb_id,)
                ).fetchall()                

        if not (ec_status or rnk_status):
            await interaction.response.send_message(embed=Embed(description=common_text[lng][1]), ephemeral=True)
            return

        embs: list[Embed] = []
        l: int = len(membs_cash) if ec_status else len(membs_xp)
        if ec_status:
            # cnt_cash is a place in the rating sorted by cash
            cash: int = db_member_info[1]
            if membs_cash[l >> 1][1] < cash:
                cnt_cash: int = 1
                while cnt_cash < l and memb_id != membs_cash[cnt_cash - 1][0]:
                    cnt_cash += 1
            else:
                cnt_cash: int = l
                while cnt_cash > 1 and memb_id != membs_cash[cnt_cash - 1][0]:
                    cnt_cash -= 1

            emb1: Embed = Embed(description=self.profile_text[lng][5].format(memb_id, memb_id))
            emb1.add_field(name=self.profile_text[lng][1], value=self.code_blocks[2][1].format("{0:0,}".format(cash)), inline=True)
            emb1.add_field(name=self.profile_text[lng][4], value=self.code_blocks[2][1].format(cnt_cash), inline=True)
            embs.append(emb1)

        if rnk_status:
            # cnt_cash is a place in the rating sorted by xp
            xp: int = db_member_info[4]
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
                emb2.description = self.profile_text[lng][5].format(memb_id, memb_id)
            emb2.add_field(
                name=self.profile_text[lng][2],
                value=self.code_blocks[2][2].format(f"{xp:0,}/{(level * xp_b + 1):0,}"),
                inline=True
            )
            emb2.add_field(name=self.profile_text[lng][3], value=self.code_blocks[2][2].format("{0:0,}".format(level)), inline=True)
            emb2.add_field(name=self.profile_text[lng][4], value=self.code_blocks[2][2].format(cnt_xp), inline=True)
            embs.append(emb2)

        if ec_status:
            # roles_ids_on_server & roles_ids_in_db
            memb_server_db_roles: set[int] | set = set(interaction.user._roles) & db_roles
            memb_roles: set[int] | set = {int(role_id) for role_id in db_member_info[2].split("#") if role_id.isdigit()} if db_member_info[2] else set()

            embed_3_description: str = '\n'.join(
                [self.code_blocks[lng][0]] + [f"<@&{r}>" for r in memb_server_db_roles]
            ) if memb_server_db_roles else self.profile_text[lng][6]
            emb3: Embed = Embed(description=embed_3_description)

            # in case role(s) was(were) removed from user manually, we should update database
            if memb_roles != memb_server_db_roles:
                with closing(connect(DB_PATH.format(interaction.guild_id).format(interaction.guild_id))) as base:
                    with closing(base.cursor()) as cur:
                        new_owned_roles: str = '#' + '#'.join(str(role_id) for role_id in memb_server_db_roles) \
                            if memb_server_db_roles else ""
                        cur.execute(
                            "UPDATE users SET owned_roles = ? WHERE memb_id = ?",
                            (new_owned_roles, memb_id)
                        )
                        base.commit()
                        # roles to remove from db
                        for role_id in memb_roles.difference(memb_server_db_roles):
                            if cur.execute("SELECT salary FROM server_roles WHERE role_id = ?", (role_id,)).fetchone()[0]:
                                membs: Optional[tuple[str]] = cur.execute(
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
                                membs: Optional[tuple[str]] = cur.execute(
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

            if sale_role_requests:
                embed_4_description: str = self.code_blocks[lng][1] + \
                    '\n'.join(self.profile_text[lng][7].format(request_id, role_id, price, currency, target_id) \
                        for request_id, target_id, role_id, price in sale_role_requests
                    )
                embs.append(Embed(description=embed_4_description))

            if buy_role_requests:
                embed_5_description: str = self.code_blocks[lng][2] + \
                    '\n'.join(self.profile_text[lng][8].format(request_id, role_id, price, currency, seller_id) \
                        for request_id, seller_id, role_id, price in buy_role_requests
                    )
                embs.append(Embed(description=embed_5_description))

        member: Member = interaction.user
        if (avatar := member.display_avatar) is not None:
            avatar_url: str = avatar.url
            embs[0].set_thumbnail(avatar_url)
            embs[0].set_author(name=member.display_name, url=avatar_url, icon_url=avatar_url)
        
        await interaction.response.send_message(embeds=embs)

    async def accept_request(self, interaction: Interaction, request_id: int) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        guild_id: int = interaction.guild_id
        memb_id: int = interaction.user.id
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0

        db_path: str = DB_PATH.format(guild_id)
        with closing(connect(db_path)) as base:
            with closing(base.cursor()) as cur:
                purchase_request: Optional[tuple[int, int, int, int]] = await self.verify_request_id(
                    cur=cur,
                    request_id=request_id,
                    interaction=interaction,
                    memb_id=memb_id
                )
                if not purchase_request:
                    return
                
                if purchase_request[1] != memb_id:
                    await self.respond_with_error_report(
                        interaction=interaction,
                        lng=lng,
                        answer=self.manage_requests_text[lng][1]
                    )
                    return
                
                seller_id: int = purchase_request[0]
                seller_db_roles_str: str = cur.execute(
                    "SELECT owned_roles FROM users WHERE memb_id = ?",
                    (seller_id,)
                ).fetchone()[0]
        
        role_id: int = purchase_request[2]
        guild: Guild = interaction.guild
        role: Role | None = guild.get_role(role_id)
        if not role:
            await self.respond_with_error_report(
                interaction=interaction,
                lng=lng,
                answer=self.manage_requests_text[lng][2]
            )
            delete_role_from_db(guild_id=guild_id, str_role_id=str(role_id))
            return
        
        price: int = purchase_request[3]
        member_info: tuple[int, int, str, int, int, int] = await get_member_async(guild_id=guild_id, member_id=memb_id)
        if member_info[1] < price:
            await self.respond_with_error_report(
                interaction=interaction,
                lng=lng,
                answer=self.manage_requests_text[lng][3]
            )
            return

        if not await self.can_role(interaction=interaction, role=role, lng=lng):
            return

        str_member_roles: str = member_info[2]
        member_roles: set[int] = {int(str_role_id) for str_role_id in str_member_roles.split('#') if str_role_id}
        if role_id in member_roles:
            await self.respond_with_error_report(
                interaction=interaction,
                lng=lng,
                answer=self.manage_requests_text[lng][4]
            )
            return

        seller: Member | None = guild.get_member(seller_id)
        if not seller:
            await self.respond_with_error_report(
                interaction=interaction,
                lng=lng,
                answer=self.manage_requests_text[lng][5]
            )
            return
        
        seller_roles_ids: set[int] = set(seller._roles)
        # Just in case seller roles were changed manually without the bot.
        seller_db_roles_ids: set[int] = {int(str_role_id) for str_role_id in seller_db_roles_str.split('#') if str_role_id}
        seller_roles_ids.intersection_update(seller_db_roles_ids)
        del seller_db_roles_ids

        if role_id not in seller_roles_ids:
            await self.respond_with_error_report(
                interaction=interaction,
                lng=lng,
                answer=self.manage_requests_text[lng][6]
            )
            with closing(connect(db_path)) as base:
                with closing(base.cursor()) as cur:
                    cur.execute("DELETE FROM sale_requests WHERE request_id = ?", (request_id,))
                    base.commit()
            return
        seller_roles_ids.remove(role_id)

        new_seller_roles: str = '#' + '#'.join(str(r_id) for r_id in seller_roles_ids) if seller_roles_ids else ""
        str_member_roles += '#' + str(role_id)
        with closing(connect(db_path)) as base:
            with closing(base.cursor()) as cur:
                cur.execute(
                    "UPDATE users SET money = money + ?, owned_roles = ? WHERE memb_id = ?",
                    (price, new_seller_roles, seller_id)
                )
                cur.execute(
                    "UPDATE users SET money = money - ?, owned_roles = ? WHERE memb_id = ?",
                    (price, str_member_roles, memb_id)
                )
                cur.execute("DELETE FROM sale_requests WHERE request_id = ?", (request_id,))
                base.commit()
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
        
        try:
            await seller.remove_roles(role)
            await interaction.user.add_roles(role)
        except:
            await self.respond_with_error_report(
                interaction=interaction,
                lng=lng,
                answer=self.manage_requests_text[lng][7]
            )
        else:
            await interaction.response.send_message(embed=Embed(
                description=self.manage_requests_text[lng][8].format(
                    role_id, 
                    seller_id,
                    price,
                    currency
                ),
                colour=Colour.green()
            ))

    async def decline_request(self, interaction: Interaction, request_id: int) -> None:
        assert interaction.guild_id is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        memb_id: int = interaction.user.id
        with closing(connect(DB_PATH.format(interaction.guild_id))) as base:
            with closing(base.cursor()) as cur:
                request: Optional[tuple[int, int, int, int]] = await self.verify_request_id(
                    cur=cur,
                    request_id=request_id,
                    interaction=interaction,
                    memb_id=memb_id
                )
                if not request:
                    return
                cur.execute("DELETE FROM sale_requests WHERE request_id = ?", (request_id,))
                base.commit()
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        decr: str = self.manage_requests_text[lng][9] \
            if memb_id == request[0] else self.manage_requests_text[lng][10]
        await interaction.response.send_message(
            embed=Embed(
                description=decr.format(request[2]),
                colour=Colour.green()
            ),
            ephemeral=True
        )

    async def work(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        guild_id: int = interaction.guild_id
        memb_id: int = interaction.user.id

        member: tuple[int, int, str, int, int, int] = await get_member_async(guild_id, memb_id)
        with closing(connect(DB_PATH.format(guild_id))) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await interaction.response.send_message(
                        embed=Embed(description=common_text[lng][2]),
                        ephemeral=True
                    )
                    return

                time_reload: int = cur.execute("SELECT value FROM server_info WHERE settings = 'w_cd'").fetchone()[0]
                if member[3] and (lasted_time := int(time()) - member[3]) < time_reload:
                    time_l: int = time_reload - lasted_time
                    t_l: str = f"{time_l // 3600}:{(time_l % 3600) // 60}:{time_l % 60}"
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][26].format(t_l))
                    return

                sal_l: int = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_l'").fetchone()[0]
                sal_r: int = cur.execute("SELECT value FROM server_info WHERE settings = 'sal_r'").fetchone()[0]
                salary: int = randint(sal_l, sal_r)
                member_roles_ids: tuple[str] = tuple(role_id for role_id in member[2].split('#') if role_id)
                if member_roles_ids:
                    query: str = "SELECT additional_salary FROM server_roles WHERE role_id IN ({})"\
                        .format(", ".join(member_roles_ids))
                    memb_roles_add_salary: list[tuple[int]] = cur.execute(query).fetchall()
                    # `additional_income` may be equal to 0.
                    additional_income: int = sum(add_salary[0] for add_salary in memb_roles_add_salary)
                    salary += additional_income
                else:
                    additional_income: int = 0

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
        await interaction.response.send_message(embed=Embed(description=descr, colour=Colour.gold()))
        if chnl_id and isinstance(guild_log_channel := interaction.guild.get_channel(chnl_id), TextChannel):
            try:
                await guild_log_channel.send(embed=Embed(
                    title=text_slash[server_lng][29],
                    description=text_slash[server_lng][30].format(f"<@{memb_id}>", salary, currency)
                ))
            except:
                return

    async def bet(self, interaction: Interaction, amount: int) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        memb_id: int = interaction.user.id
        guild_id: int = interaction.guild_id

        member: tuple[int, int, str, int, int, int] = await get_member_async(guild_id=guild_id, member_id=memb_id)
        db_path: str = DB_PATH.format(guild_id)
        with closing(connect(db_path)) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=common_text[lng][2])
                    return

                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
                server_lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]

        if amount > member[1]:
            await self.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][31].format(amount - member[1], currency))
            return

        bet_view: BetView = BetView(timeout=30, lng=lng, auth_id=memb_id, bet=amount, currency=currency)

        emb: Embed = Embed(title=text_slash[lng][32], description=text_slash[lng][33].format(amount, currency))
        await interaction.response.send_message(embed=emb, view=bet_view)

        if await bet_view.wait():
            emb.description = text_slash[lng][34]

        for c in bet_view.children:
            assert isinstance(c, CustomButton)
            c.disabled = True

        if not bet_view.dueler:
            if bet_view.declined:
                emb.description = bet_text[lng][5]
            try:
                await interaction.edit_original_message(embed=emb, view=bet_view)
                await interaction.delete_original_message(delay=7)
            except:
                return
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

        with closing(connect(db_path)) as base:
            with closing(base.cursor()) as cur:
                cur.execute('UPDATE users SET money = money - ? WHERE memb_id = ?', (amount, loser_id))
                base.commit()
                cur.execute('UPDATE users SET money = money + ? WHERE memb_id = ?', (amount, winner_id))
                base.commit()
                chnl_id: int = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]

        try:
            await interaction.edit_original_message(embed=emb, view=bet_view)
        except:
            pass
        if chnl_id and isinstance(guild_log_channel := interaction.guild.get_channel(chnl_id), TextChannel):
            try:
                await guild_log_channel.send(embed=Embed(
                    title=text_slash[server_lng][37],
                    description=text_slash[server_lng][38].format(winner_id, amount, currency, loser_id)
                ))
            except:
                return

    async def transfer(self, interaction: Interaction, value: int, target: Member) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        memb_id: int = interaction.user.id
        t_id: int = target.id
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        guild_id: int = interaction.guild_id

        act: tuple[int, int, str, int, int, int] = await get_member_async(guild_id, memb_id)
        await check_member_async(guild_id, t_id)
        with closing(connect(DB_PATH.format(guild_id))) as base:
            with closing(base.cursor()) as cur:
                if not cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]:
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=common_text[lng][2])
                    return
                
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]
                if value > act[1]:
                    await self.respond_with_error_report(interaction=interaction, lng=lng, answer=text_slash[lng][39].format(value - act[1], currency))
                    return

                cur.execute('UPDATE users SET money = money - ? WHERE memb_id = ?', (value, memb_id))
                base.commit()
                cur.execute('UPDATE users SET money = money + ? WHERE memb_id = ?', (value, t_id))
                base.commit()

                chnl_id: int = cur.execute("SELECT value FROM server_info WHERE settings = 'log_c'").fetchone()[0]
                server_lng: int = cur.execute("SELECT value FROM server_info WHERE settings = 'lang'").fetchone()[0]

        emb: Embed = Embed(
            title=text_slash[lng][40],
            description=text_slash[lng][41].format(value, currency, f"<@{t_id}>"),
            colour=Colour.green()
        )
        await interaction.response.send_message(embed=emb)
        if chnl_id and isinstance(guild_log_channel := interaction.guild.get_channel(chnl_id), TextChannel):
            try:
                await guild_log_channel.send(embed=Embed(
                    title=text_slash[server_lng][42],
                    description=text_slash[server_lng][43].format(f"<@{memb_id}>", value, currency, f"<@{t_id}>")
                ))
            except:
                return

    async def leaders(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        guild_id: int = interaction.guild_id

        await check_member_async(guild_id=guild_id, member_id=interaction.user.id)
        with closing(connect(DB_PATH.format(guild_id))) as base:
            with closing(base.cursor()) as cur:
                ec_status: int = \
                    cur.execute("SELECT value FROM server_info WHERE settings = 'economy_enabled'").fetchone()[0]
                rnk_status: int = \
                    cur.execute("SELECT value FROM server_info WHERE settings = 'ranking_enabled'").fetchone()[0]
                if ec_status:
                    membs_cash: list[tuple[int, int]] = cur.execute("SELECT memb_id, money FROM users").fetchall()
                    membs_cash.sort(key=lambda tup: tup[1], reverse=True)
                else:
                    membs_cash = []
                if rnk_status:
                    membs_xp: list[tuple[int, int]] = cur.execute("SELECT memb_id, xp FROM users").fetchall()
                    membs_xp.sort(key=lambda tup: tup[1], reverse=True)
                else:
                    membs_xp = []
                xp_b: int = cur.execute("SELECT value FROM server_info WHERE settings = 'xp_border'").fetchone()[0]
                currency: str = cur.execute("SELECT str_value FROM server_info WHERE settings = 'currency'").fetchone()[0]

        if not (ec_status or rnk_status):
            await interaction.response.send_message(embed=Embed(description=common_text[lng][1]), ephemeral=True)
            return

        l: int = len(membs_cash) if ec_status else len(membs_xp)
        in_row: Literal[5] = self.in_row
        end: int = min(in_row, l)
        if ec_status:
            emb: Embed = Embed(title=rating_text[lng][0], colour=Colour.dark_gray())
            for counter, role_info in enumerate(membs_cash[0:end], start=1):
                emb.add_field(
                    name=rating_text[lng][3].format(counter),
                    value=f"<@{role_info[0]}>\n{role_info[1]:0,} " + currency,
                    inline=False
                )
                
        else:
            emb: Embed = Embed(title=rating_text[lng][1], colour=Colour.dark_gray())
            for counter, role_info in enumerate(membs_xp[0:end], start=1):
                emb.add_field(
                    name=rating_text[lng][3].format(counter),
                    value=f"<@{role_info[0]}>\n{rating_text[lng][4].format((role_info[1] - 1) // xp_b + 1)}",
                    inline=False
                )

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
            assert isinstance(c, (CustomButton, CustomSelectWithOptions))
            c.disabled = True
        try:
            await interaction.edit_original_message(view=rate_view)
        except:
            return

    async def slots(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        guild_id: int = interaction.guild_id
        member_id: int = interaction.user.id
        await check_member_async(guild_id=guild_id, member_id=member_id)
        if not (await get_server_info_value_async(guild_id=guild_id, key_name="slots_on")):
            await self.respond_with_error_report(
                interaction=interaction,
                lng=lng,
                answer=SlotsView.slots_view_text[lng][0]
            )
            return
        
        slots_table: dict[int, int] = await get_server_slots_table_async(guild_id=guild_id)
        currency: str = await get_server_currency_async(guild_id=guild_id)
        slots_view: SlotsView = SlotsView(
            lng=lng,
            author_id=member_id,
            timeout=180,
            guild=interaction.guild,
            slots_table=slots_table,
            currency=currency
        )
        await interaction.response.send_message(
            embed=Embed(description=SlotsView.slots_panels[lng].format(0, 0, 0)),
            view=slots_view
        )

        await slots_view.wait()
        for c in slots_view.children:
            assert isinstance(c, (CustomButton, CustomSelect))
            c.disabled = True
        try:
            await interaction.edit_original_message(view=slots_view)
        except:
            return

    @slash_command(
        name="buy",
        description="Makes a role purchase from the store",
        description_localizations={
            Locale.ru: "Совершает покупку роли из магазина"
        },
        dm_permission=False
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
        },
        dm_permission=False
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
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        if role_number < 1:
            await interaction.response.send_message(
                embed=Embed(colour=Colour.red(),
                            description=text_slash[lng][44]),
                ephemeral=True
            )
            return
        role: Optional[Role] = None
        with closing(connect(DB_PATH.format(interaction.guild_id))) as base:
            with closing(base.cursor()) as cur:
                role_id_tuple: Optional[tuple[int]] = cur.execute(
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
        },
        dm_permission=False
    )
    async def store_e(self, interaction: Interaction) -> None:
        await self.store(interaction=interaction)

    @slash_command(
        name="sell",
        description="Sells the role",
        description_localizations={
            Locale.ru: "Совершает продажу роли"
        },
        dm_permission=False
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
        },
        dm_permission=False
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
        },
        dm_permission=False
    )
    async def profile_e(self, interaction: Interaction) -> None:
        await self.profile(interaction=interaction)

    @slash_command(
        name="accept_request",
        description="Accepts role purchase request (from the /profile command)",
        description_localizations={
            Locale.ru: "Принимает предложение о покупке роли (из команды /profile)"
        },
        dm_permission=False
    )
    async def accept_request_e(
        self,
        interaction: Interaction,
        request_id: int = SlashOption(
            name="request_id",
            name_localizations={
                Locale.ru: "id_предложения"
            },
            description="id of the role purchase request (from the /profile command)",
            description_localizations={
                Locale.ru: "id предложения о покупке роли (из команды /profile)"
            },
            min_value=1,
            max_value=99999,
            required=True
        )
    ) -> None:
        await self.accept_request(interaction=interaction, request_id=request_id)

    @slash_command(
        name="decline_request",
        description="Decline or delete role purchase / sale request (from the /profile command)",
        description_localizations={
            Locale.ru: "Отменяет или удаляет предложение о покупке / продаже роли (из команды /profile)"
        },
        dm_permission=False
    )
    async def decline_request_e(
        self,
        interaction: Interaction,
        request_id: int = SlashOption(
            name="request_id",
            name_localizations={
                Locale.ru: "id_предложения"
            },
            description="id of the role purchase request / sale (from the /profile command)",
            description_localizations={
                Locale.ru: "id предложения о покупке / продаже роли (из команды /profile)"
            },
            min_value=1,
            max_value=99999,
            required=True
        )
    ) -> None:
        await self.decline_request(interaction=interaction, request_id=request_id)

    @slash_command(
        name="work",
        description="Allows to gain money",
        description_localizations={
            Locale.ru: "Позволяет заработать деньги"
        },
        dm_permission=False
    )
    async def work_e(self, interaction: Interaction) -> None:
        await self.work(interaction=interaction)
    
    @slash_command(
        name="collect",
        description="Allows to gain money",
        description_localizations={
            Locale.ru: "Позволяет заработать деньги"
        },
        dm_permission=False
    )
    async def collect(self, interaction: Interaction) -> None:
        await self.work(interaction=interaction)

    @slash_command(
        name="duel",
        description="Make a bet",
        description_localizations={
            Locale.ru: "Сделать ставку"
        },
        dm_permission=False
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
        },
        dm_permission=False
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
        },
        dm_permission=False
    )
    async def leaders_e(self, interaction: Interaction) -> None:
        await self.leaders(interaction=interaction)

    @slash_command(
        name="slots",
        description="Starts 'slots' game",
        description_localizations={
            Locale.ru: "Начинает игру в 'слоты'"
        },
        dm_permission=False
    )
    async def slots_cmd(self, interaction: Interaction) -> None:
        await self.slots(interaction=interaction)

def setup(bot: StoreBot) -> None:
    bot.add_cog(SlashCommandsCog(bot))

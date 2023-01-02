from sqlite3 import connect, Connection, Cursor
from contextlib import closing
from random import randint
from typing import Literal
from time import time

from nextcord import Embed, Message, Interaction, TextInputStyle
from nextcord.ui import TextInput, Modal

from Tools.db_commands import peek_role_free_number, peek_role_free_numbers
from Variables.vars import path_to

r_types: dict[int, dict[int, str]] = {
    0: {
        1: "Nonstacking, displayed separated",
        2: "Stacking, countable",
        3: "Stacking, infinite"
    },
    1: {
        1: "Нестакающаяся, отображается отдельно",
        2: "Cтакающаяся, конечная",
        3: "Cтакающаяся, бесконечная"
    }
}

ranking_text: dict[int, dict[int, str]] = {
    0: {
        0: "✨ Xp gained per message:\n**`{}`**",
        1: "✨ Amount of xp between adjacent levels:\n**`{}`**",
        2: "📗 Channel for the notification about new levels:\n{}",
        4: "> To manage setting press button with corresponding emoji\n",
        5: "> Press :mute: to manage channels where members can't get xp\n",
        6: "> Press 🥇 to manage roles given for levels",
        7: "Managing xp settings",
        8: "Xp per message",
        9: "Amount of xp gained by every member from one message, non-negative integer number",
        10: "Amount of xp between adjected levels",
        11: "Amount of xp members need to gain to get next level, positive integer number",
        12: "**`Xp gained per message should be non-negative integer number`**",
        13: "**`Amount of xp between adjected levels should be positive integer number`**",
        14: "**`You changed amount of xp gained from one message, now it's {}`**",
        15: "**`You changed amount of xp needed to get next level, now it's {}`**",
        16: "**`You hasn't changed anything`**",
        17: "__**channel**__ - __**id**__",
        18: "**`No channels were selected`**",
        19: "**`You added channel `**<#{}>",
        20: "**`You removed channel `**<#{}>",
        21: "**`You hasn't selected the channel yet`**",
        22: "**`This channel is already added`**",
        23: "**`This channel hasn't been added yet`**",
        24: "level",
        25: "**`No roles matched for levels`**",
        26: "Roles for level",
        27: "**`Press `**<:add01:999663315804500078>🔧**`to add / change role for the level`**\n**`Press `**<:remove01:999663428689997844>**` to remove role for the level`**",
        28: "Write the level: positive integer from 1 to 100",
        29: "**`Select role for level {}`**",
        30: "**`Bot can't give any role on the server`**",
        31: "**`From now role given for the level {} is `**<@&{}>",
        32: "**`Timeout has expired`**",
        33: "**`You removed role for level {}`**",
        34: "**`No roles matches level {}`**",
        35: "Write the level: **`positive integer from 1 to 100`**",
    },
    1: {
        0: "✨ Опыт, получаемый за одно сообщение:\n**`{}`**",
        1: "✨ Количество опыта между соседними уровнями:\n**`{}`**",
        2: "📗 Канал для оповещений о получении нового уровня:\n{}",
        4: "> Для управления настройкой нажмите на кнопку с соответствующим эмодзи\n",
        5: "> Нажмите :mute: для управления каналами, в которых пользователи не могут получать опыт\n",
        6: "> Нажмите 🥇 для управления ролями, выдаваемыми за уровни",
        7: "Управление настройками опыта",
        8: "Опыт за сообщение",
        9: "Количество опыта, получаемого пользователем за одно сообщение, целое неотрицательное число",
        10: "Количество опыта между уровнями",
        11: "Количество опыта,необходимого участникам для получения следующего уровня, целове положительное число",
        12: "**`Опыт, получаемый участником за одно сообщение, должен быть целым неотрицательным числом`**",
        13: "**`Количество опыта, который необходимо набрать участникам для получения следующего уровня, должно быть целым положительным числом`**",
        14: "**`Вы изменили количество опыта, получаемого участником за одно сообщение, теперь оно равно {}`**",
        15: "**`Вы изменили количество опыта, необходимого участнику для получения следующего уровня, теперь оно равно {}`**",
        16: "**`Вы ничего не изменили`**",
        17: "__**канал**__ - __**id**__",
        18: "**`Не выбрано ни одного канала`**",
        19: "**`Вы добавили канал `**<#{}>",
        20: "**`Вы убрали канал `**<#{}>",
        21: "**`Вы не выбрали канал`**",
        22: "**`Этот канал уже добавлен`**",
        23: "**`Этот канал ещё не был добавлен`**",
        24: "уровень",
        25: "**`Роли за уровни не назначены`**",
        26: "Роли за уровни",
        27: "**`Нажмите `**<:add01:999663315804500078>🔧**`, чтобы добавить / изменить роль за уровень`**\n**`Нажмите `**<:remove01:999663428689997844>**`, чтобы убрать роль за уровень`**",
        28: "Напишите номер уровня: положительное целое число от 1 до 100",
        29: "**`Выберите роль для уровня {}`**",
        30: "**`Бот не может выдать ни одной роли на сервере`**",
        31: "**`Теперь за уровень {} выдаётся роль `**<@&{}>",
        32: "**`Время истекло`**",
        33: "**`Вы убрали роль за уровень {}`**",
        34: "**`Уровню {} не соответствует ни одна роль`**",
        35: "Напишите номер уровня: **`положительное целое число от 1 до 100`**",
    }
}

class ManageRoleModalBase(Modal):
    manage_role_modals_text: dict[int, dict[int, str]] = { 
        0: {
            0: "Adding role",
            10: "Role's price",
            11: "Write positive integer number as price of the role",
            12: "Role's salary and cooldown for it (optional)",
            13: "If role should bring money to its owners write salary and cooldown in hours (split numbers by space)",
            14: "The same roles will be displayed in the store",
            15: "Additional income from /work (optional)",
            16: "Amount of money gained by the role owner additionally from using the /work command",
            18: "Price should be positive integer number from `1` to `999999999`",
            19: "Salary and cooldown must be two positive integer numbers separated by space, for example: `100` `24`",
            20: "Salary should be positive integer number",
            21: "Cooldown should be positive integer number from `1` to `1008`, cooldown is time in hours. For example: `24` sets cooldown to `24 hours`",
            22: "Type of displaying of the role should be one of three numbers: `1`, `2` or `3`",
            23: "If inputted, additional income from the `/work` command should be integer number from `1` to `999999999`",
            24: "You added role <@&{}> with price **`{}`**, salary **`{}`**, cooldown for it **`{}`** hours, type **`{}`**, additional income from `/work` command - **`{}`**",
            25: "Editing the role",
            26: "Print 1 if separated,nonstacking\n2 if countable,stacking\n3 if uncountable (can't run out),stacking",
            27: "How much roles must be in the store",
            28: "Print integer non-negative number. For uncountable roles print any non-negative number",
            29: "Amount of the roles in the store must be non-negative integer number from 0 to 99",
            30: "You edited role <@&{}>. Now it's price is **`{}`**, salary is **`{}`**, cooldown for it is **`{}`** hours, role's type is **`{}`**, amount of roles in the store - **`{}`**, additional income from `/work` command - **`{}`**",
        },
        1: {
            0: "Добавление роли",
            10: "Цена роли",
            11: "Укажите целое положительное число",
            12: "Доход роли и кулдаун для него (необязательно)",
            13: "Если надо, чтобы роль приносила деньги,укажите доход и его кулдаун в часах(разделите числа пробелом)",
            14: "Одинаковые роли будут отображаться в магазине",
            15: "Дополнительный доход от /work (необязательно)",
            16: "Количество валюты, дополнительно получаемое владельцем роли при вызове команды /work",
            18: "В качестве цены роли надо указать целое положительное число от `1` до `999999999`",
            19: "Заработок и кулдаун должны быть двумя положительными целыми числами, разделёнными пробелом, например, `100` `24`",
            20: "Заработок должен быть целым положительным числом",
            21: "Кулдаун должен быть целым положительным числом от `1` до `1008`, кулдаун - время в часах. Например, `24` сделает кулдаун равным `24 часам`",
            22: "В качестве типа отображения роли надо указать одно из трёх чисел: `1`, `2` или `3`",
            23: "Если указан, дополнительный заработок от команды `/work` должен быть целым положительным числом от `1` до `999999999`",
            24: "Вы добавили роль <@&{}> с ценой **`{}`**, доходом **`{}`**, его кулдауном **`{}`** час(а)(ов), типом **`{}`**, дополнительным заработком от команды `/work` - **`{}`**",
            25: "Редактирование роли",
            26: "Напишите 1,если раздельно,нестакаются\n2,если стакающися,исчисляемые\n3,если стакающиеся,бесконечные",
            27: "Сколько ролей должно быть в магазине",
            28: "Напишите целое неотрицательное число.Для бесконечных ролей можно указать любое неотрицательное число",
            29: "Количество ролей в магазине должно быть целым неотрицательным числом от 0 до 99",
            30: "Вы отредактировали роль <@&{}>. Теперь её цена - **`{}`**, доход - **`{}`**, его кулдаун - **`{}`** час(а)(ов), тип роли - **`{}`**, количество в магазине - **`{}`**, дополнительный заработок от команды `/work` - **`{}`**",
        }
    }

    def __init__(self, title: str, *, timeout: float | None = None, custom_id: str = ..., auto_defer: bool = True) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id, auto_defer=auto_defer)


class RoleAddModal(ManageRoleModalBase):
    partial_ec_text: dict[int, dict[int, str]] = {
        0: {
            18: "__**role - role id - price - salary - cooldown for salary - type - how much in the store - additional income from /work**__",
            20: "`If role isn't shown in the menu(s) down below it means that bot can't manage this role`",
        },
        1: {
            18: "__**роль - id роли - цена - заработок - кулдаун заработка - тип - сколько в магазине - дополнительный заработок от /work**__",
            20: "`Если роль не отображается ни в одном меню снизу, значит, бот не может управлять ею`",
        }
    }

    def __init__(self, timeout: int, lng: int, role: int, message: Message, auth_id: int) -> None:
        super().__init__(title=self.manage_role_modals_text[lng][0], timeout=timeout, custom_id=f"6100_{auth_id}_{randint(1, 100)}")
        self.role_id=role
        self.m: Message = message
        self.added = False
        self.price_text_input = TextInput(
            label=self.manage_role_modals_text[lng][10],
            min_length=1,
            max_length=9,
            placeholder=self.manage_role_modals_text[lng][11],
            required=True,
            custom_id=f"6101_{auth_id}_{randint(1, 100)}"
        )
        self.salary_text_input = TextInput(
            label=self.manage_role_modals_text[lng][12],
            min_length=0,
            max_length=9,
            style=TextInputStyle.paragraph,
            placeholder=self.manage_role_modals_text[lng][13],
            required=False,
            custom_id=f"6102_{auth_id}_{randint(1, 100)}"
        )
        self.r_type_text_input = TextInput(
            label=self.manage_role_modals_text[lng][14],
            min_length=1,
            max_length=1,
            style=TextInputStyle.paragraph,
            placeholder=self.manage_role_modals_text[lng][26],
            required=True,
            custom_id=f"6103_{auth_id}_{randint(1, 100)}"
        )
        self.additional_salary_text_input = TextInput(
            label=self.manage_role_modals_text[lng][15],
            style=TextInputStyle.paragraph,
            min_length=0,
            max_length=9,
            required=False,
            placeholder=self.manage_role_modals_text[lng][16]
        )    
        self.add_item(self.price_text_input)
        self.add_item(self.salary_text_input)
        self.add_item(self.r_type_text_input)
        self.add_item(self.additional_salary_text_input)

        self.price: int = 0
        self.salary: int = 0
        self.salary_cooldown: int = 0
        self.role_type: int = 1
        self.additional_salary: int = 0

    def verify_user_input(self) -> int:
        errors_bit_mask: int = 0b000000

        price: str | None = self.price_text_input.value
        if price and price.isdigit() and (price_int := int(price)) > 0:
            self.price = price_int
        else:
            errors_bit_mask |= 0b000001
        
        salary_and_cooldown: str | None = self.salary_text_input.value
        if salary_and_cooldown:
            s_ans: list[str] = salary_and_cooldown.split()
            if len(s_ans) != 2:
                errors_bit_mask |= 0b000010
            else:
                salary: str = s_ans[0]
                if salary.isdigit() and (salary_int := int(salary)) > 0:
                    self.salary = salary_int
                else:
                    errors_bit_mask |= 0b000100
                
                salary_cooldown: str = s_ans[1]
                if salary_cooldown.isdigit() and (1 <= (salary_cooldown_int := int(salary_cooldown)) <= 1008):
                    self.salary_cooldown = salary_cooldown_int * 3600
                else:
                    errors_bit_mask |= 0b001000
        
        role_type: str | None = self.r_type_text_input.value
        if role_type and role_type.isdigit() and (role_type_int := int(role_type)) in {1, 2, 3}:
            self.role_type = role_type_int
        else:
            errors_bit_mask |= 0b010000
        
        additional_salary: str | None = self.additional_salary_text_input.value
        if additional_salary:
            if additional_salary.isdigit() and (additional_salary_int := int(additional_salary)) > 0:
                self.additional_salary = additional_salary_int
            else:
                errors_bit_mask |= 0b100000

        return errors_bit_mask

    async def callback(self, interaction: Interaction) -> None:
        lng: int = 1 if "ru" in str(interaction.locale) else 0
 
        errors_bit_mask: int = self.verify_user_input()
        if errors_bit_mask:
            report: list[str] = []
            if errors_bit_mask & 0b000001:
                report.append(self.manage_role_modals_text[lng][18])
            if errors_bit_mask & 0b000010:
                report.append(self.manage_role_modals_text[lng][19])
            if errors_bit_mask & 0b000100:
                report.append(self.manage_role_modals_text[lng][20])
            if errors_bit_mask & 0b001000:
                report.append(self.manage_role_modals_text[lng][21])
            if errors_bit_mask & 0b010000:
                report.append(self.manage_role_modals_text[lng][22])
            if errors_bit_mask & 0b100000:
                report.append(self.manage_role_modals_text[lng][23])
            
            await interaction.response.send_message(
                embed=Embed(description='\n'.join(report)),
                ephemeral=True
            )
            self.stop()
            return
        
        role_id: int = self.role_id
        price: int = self.price
        salary: int = self.salary
        salary_cooldown: int = self.salary_cooldown
        role_type: int = self.role_type
        additional_salary: int = self.additional_salary
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute(
                    "INSERT OR IGNORE INTO server_roles (role_id, price, salary, salary_cooldown, type, additional_salary) VALUES(?, ?, ?, ?, ?, ?)", 
                    (role_id, price, salary, salary_cooldown, role_type, additional_salary)
                )
                base.commit()
                if salary:
                    cur.execute(
                        "INSERT OR IGNORE INTO salary_roles (role_id, members, salary, salary_cooldown, last_time) VALUES(?, ?, ?, ?, ?)", 
                        (role_id, "", salary, salary_cooldown, 0)
                    )
                    base.commit()

        dsc: list[str] = self.m.content.split("\n")
        rls = dsc[1:-2]
        dsc = [self.partial_ec_text[lng][18]]
        dsc.extend(r for r in rls)
        dsc.append(f"<@&{role_id}> - **`{role_id}`** - **`{price}`** - **`{salary}`** - **`{salary_cooldown // 3600}`** - **`{r_types[lng][role_type]}`** - **`0`** - **`{additional_salary}`**\n")
        dsc.append(self.partial_ec_text[lng][20])
        await self.m.edit(content='\n'.join(dsc))

        self.added = True
        await interaction.response.send_message(
            embed=Embed(
                description=self.manage_role_modals_text[lng][24].format(
                    role_id, 
                    price, 
                    salary, 
                    salary_cooldown // 3600, 
                    r_types[lng][role_type], 
                    additional_salary
                )
            ),
            ephemeral=True
        )
        self.stop()


class RoleEditModal(ManageRoleModalBase):
    def __init__(self, timeout: int, role: int, message: Message, lng: int, auth_id: int, price: int, salary: int, salary_cooldown: int, r_t: int, additional_salary: int, in_store: int):
        super().__init__(title=self.manage_role_modals_text[lng][25], timeout=timeout, custom_id=f"7100_{auth_id}_{randint(1, 100)}")
        self.role_id: int = role
        self.m: Message = message
        self.changed: bool = False

        self.prev_salary: int = salary
        self.prev_salary_cooldown: int = salary_cooldown
        self.prev_r_t: int = r_t
        self.prev_in_store_amount: int = in_store
        
        self.new_price: int = price
        self.new_salary: int = salary
        self.new_salary_cooldown: int = salary_cooldown
        self.new_role_type: int = r_t
        self.new_in_store_amount: int = in_store
        self.new_additional_salary: int = additional_salary
        
        self.price_text_input = TextInput(
            label=self.manage_role_modals_text[lng][10],
            min_length=1,
            max_length=9,
            placeholder=self.manage_role_modals_text[lng][11],
            default_value=str(price),
            required=True,
            custom_id=f"7101_{auth_id}_{randint(1, 100)}"
        )
        default_salary = None if not salary else f"{salary} {salary_cooldown // 3600}"
        self.salary_text_input = TextInput(
            label=self.manage_role_modals_text[lng][12],
            min_length=0,
            max_length=9,
            style=TextInputStyle.paragraph,
            placeholder=self.manage_role_modals_text[lng][13],
            default_value=default_salary,
            required=False,
            custom_id=f"7102_{auth_id}_{randint(1, 100)}"
        )
        self.r_type_text_input = TextInput(
            label=self.manage_role_modals_text[lng][14],
            min_length=1,
            max_length=1,
            style=TextInputStyle.paragraph,
            placeholder=self.manage_role_modals_text[lng][26],
            default_value=str(r_t),
            required=False,
            custom_id=f"7103_{auth_id}_{randint(1, 100)}"
        )
        self.in_store_amount_text_input = TextInput(
            label=self.manage_role_modals_text[lng][27],
            min_length=1,
            max_length=2,
            style=TextInputStyle.paragraph,
            placeholder=self.manage_role_modals_text[lng][28],
            default_value=str(in_store),
            required=True,
            custom_id=f"7104_{auth_id}_{randint(1, 100)}"
        )
        self.additional_salary_text_input = TextInput(
            label=self.manage_role_modals_text[lng][15],
            style=TextInputStyle.paragraph,
            min_length=0,
            max_length=9,
            required=False,
            default_value=str(additional_salary),
            placeholder=self.manage_role_modals_text[lng][16]
        )    
        self.add_item(self.price_text_input)
        self.add_item(self.salary_text_input)
        self.add_item(self.r_type_text_input)
        self.add_item(self.in_store_amount_text_input)
        self.add_item(self.additional_salary_text_input)

    def check_ans(self) -> int:
        errors_bit_mask: int = 0b000000

        price: str | None = self.price_text_input.value
        if price and price.isdigit() and (price_int := int(price)) > 0:
            self.new_price = price_int
        else:
            errors_bit_mask |= 0b0000001
        
        salary_and_cooldown: str | None = self.salary_text_input.value
        if salary_and_cooldown:
            s_ans: list[str] = salary_and_cooldown.split()
            if len(s_ans) != 2:
                errors_bit_mask |= 0b0000010
            else:
                salary: str = s_ans[0]
                if salary.isdigit() and (salary_int := int(salary)) > 0:
                    self.new_salary = salary_int
                else:
                    errors_bit_mask |= 0b0000100

                salary_cooldown: str =  s_ans[1]
                if salary_cooldown.isdigit() and (1 <= (salary_cooldown_int := int(salary_cooldown)) <= 1008):
                    self.new_salary_cooldown = salary_cooldown_int * 3600
                else:
                    errors_bit_mask |= 0b0001000
        
        role_type: str | None = self.r_type_text_input.value
        if role_type and role_type.isdigit() and (role_type_int := int(role_type)) in {1, 2, 3}:
            self.new_role_type = role_type_int
        else:
            errors_bit_mask |= 0b0010000

        additional_salary: str | None = self.additional_salary_text_input.value
        if additional_salary:
            if additional_salary.isdigit() and (additional_salary_int := int(additional_salary)) > 0:
                self.new_additional_salary = additional_salary_int
            else:
                errors_bit_mask |= 0b0100000

        in_store_amount: str | None = self.in_store_amount_text_input.value
        if in_store_amount and in_store_amount.isdigit() and (in_store_amount_int := int(in_store_amount)) >= 0:
            self.new_in_store_amount = in_store_amount_int
        else:
            errors_bit_mask |= 0b1000000

        return errors_bit_mask

    async def callback(self, interaction: Interaction):
        lng: int = 1 if "ru" in str(interaction.locale) else 0
        errors_bit_mask: int = self.check_ans()
        if errors_bit_mask:
            report: list[str] = []
            if errors_bit_mask & 0b0000001:
                report.append(self.manage_role_modals_text[lng][18])
            if errors_bit_mask & 0b0000010:
                report.append(self.manage_role_modals_text[lng][19])
            if errors_bit_mask & 0b0000100:
                report.append(self.manage_role_modals_text[lng][20])
            if errors_bit_mask & 0b0001000:
                report.append(self.manage_role_modals_text[lng][21])
            if errors_bit_mask & 0b0010000:
                report.append(self.manage_role_modals_text[lng][22])
            if errors_bit_mask & 0b0100000:
                report.append(self.manage_role_modals_text[lng][23])
            if errors_bit_mask & 0b1000000:
                report.append(self.manage_role_modals_text[lng][29])
            
            await interaction.response.send_message(embed=Embed(description='\n'.join(report)), ephemeral=True)
            self.stop()
            return
        
        price: int = self.new_price
        salary: int = self.new_salary
        salary_c: int = self.new_salary_cooldown
        r_type: int = self.new_role_type
        l: int = self.new_in_store_amount
        r: int = self.role_id
        new_additional_salary: int = self.new_additional_salary
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute(
                    "UPDATE server_roles SET price = ?, salary = ?, salary_cooldown = ?, type = ?, additional_salary = ? WHERE role_id = ?",
                    (price, salary, salary_c, r_type, new_additional_salary, r)
                )
                if r_type != self.prev_r_t:
                    self.update_type_and_store(base=base, cur=cur, price=price, salary=salary, salary_c=salary_c, r_type=r_type, r=r, l=l)
                else:
                    self.update_store(base=base, cur=cur, r=r, price=price, salary=salary, salary_c=salary_c, r_type=r_type, l=l, l_prev = self.prev_in_store_amount)
                if salary != self.prev_salary or salary_c != self.prev_salary_cooldown:
                    self.update_salary(base=base, cur=cur, r=r, salary=salary, salary_c=salary_c)
        
        amount_in_store: str = str(l) if r_type != 3 or not l else "∞"
        dsc: list[str] = self.m.content.split('\n')
        str_role_id: str = str(r)
        for i in range(1, len(dsc)-1):
            if str_role_id in dsc[i]:
                dsc[i] = f"<@&{r}> - **`{r}`** - **`{price}`** - **`{salary}`** - **`{salary_c // 3600}`** - **`{r_types[lng][r_type]}`** - **`{amount_in_store}`** - **`{new_additional_salary}`**"
                break
        await self.m.edit(content='\n'.join(dsc))
        self.changed = True

        await interaction.response.send_message(
            embed=Embed(
                description=self.manage_role_modals_text[lng][30].format(
                    r, 
                    price, 
                    salary, 
                    salary_c // 3600, 
                    r_types[lng][r_type], 
                    amount_in_store, 
                    new_additional_salary
                )
            ), 
            ephemeral=True
        )
        self.stop()
    
    @staticmethod
    def update_type_and_store(base: Connection, cur: Cursor, price: int, salary: int, salary_c: int, r_type: int, r: int, l: int) -> None:
        cur.execute("DELETE FROM store WHERE role_id = ?", (r,))
        base.commit()
        if not l:
            return
        t: int = int(time())
        if r_type == 3:
            free_number: int = peek_role_free_number(cur)
            cur.execute("INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                        (free_number, r, -404, price, t, salary, salary_c, 3))
        elif r_type == 2:
            free_number: int = peek_role_free_number(cur)
            cur.execute("INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                        (free_number, r, l, price, t, salary, salary_c, 2))
        elif r_type == 1:
            free_numbers: list[int] = peek_role_free_numbers(cur, l)
            inserting_roles = ((free_number, r, 1, price, t, salary, salary_c, 1) for free_number in free_numbers)
            cur.executemany(
                "INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                inserting_roles
            )
        base.commit()
    
    @staticmethod
    def update_store(base: Connection, cur: Cursor, r: int, price: int, salary: int, salary_c: int, r_type: int, l: int, l_prev: int) -> None:
        if not l:
            cur.execute("DELETE FROM store WHERE role_id = ?", (r,))
            base.commit()
            return
        t: int = int(time())
        
        if r_type == 2:
            if not l_prev:
                free_number: int = peek_role_free_number(cur)
                cur.execute("INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                            (free_number, r, l, price, t, salary, salary_c, 2))
            else:
                cur.execute("UPDATE store SET quantity = ?, price = ?, last_date = ?, salary = ?, salary_cooldown = ? WHERE role_id = ?", (l, price, t, salary, salary_c, r))
        
        elif r_type == 1:
            roles_amount_change: int = l - l_prev
            if roles_amount_change > 0:
                free_numbers: list[int] = peek_role_free_numbers(cur, roles_amount_change)
                inserting_roles = ((free_number, r, 1, price, t, salary, salary_c, 1) for free_number in free_numbers)
                cur.executemany("INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                                inserting_roles)
            elif not roles_amount_change:
                cur.execute("UPDATE store SET price = ?, last_date = ?, salary = ?, salary_cooldown = ? WHERE role_id = ?", (price, t, salary, salary_c, r))
            else:
                sorted_rls_to_delete: list[tuple[int]] = cur.execute("SELECT rowid FROM store WHERE role_id = ? ORDER BY last_date", (r,)).fetchall()[:-roles_amount_change]
                rows: str = ", ".join({str(x[0]) for x in sorted_rls_to_delete})
                cur.execute(f"DELETE FROM store WHERE rowid IN ({rows})")

        elif r_type == 3 and not l_prev:
            free_number: int = peek_role_free_number(cur)
            cur.execute("INSERT INTO store(role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                        (free_number, r, -404, price, t, salary, salary_c, 3))

        base.commit()   

    @staticmethod
    def update_salary(base: Connection, cur: Cursor, r: int, salary: int, salary_c: int) -> None:
        if not salary:
            cur.execute("DELETE FROM salary_roles WHERE role_id = ?", (r,))
            base.commit()
            return
        if not cur.execute("SELECT role_id FROM salary_roles WHERE role_id = ?", (r,)).fetchone():
            ids: set[str] = set()
            string_role_id: str = f"{r}"
            for req in cur.execute("SELECT memb_id, owned_roles FROM users").fetchall():
                if string_role_id in req[1]:
                    ids.add(f"{req[0]}")
            membs: str = "".join(f"#{memb_id}" for memb_id in ids) if ids else ""
            cur.execute("INSERT INTO salary_roles(role_id, members, salary, salary_cooldown, last_time) VALUES(?, ?, ?, ?, ?)", (r, membs, salary, salary_c, 0))
            base.commit()
            return
        cur.execute("UPDATE salary_roles SET salary = ?, salary_cooldown = ? WHERE role_id = ?", (salary, salary_c, r))
        base.commit()


class ManageMemberCashXpModal(Modal):
    mng_membs_text: dict[int, dict[int, str]] = {
        0: {
            0: "Change cash/xp",
            1: "Cash",
            2: "Xp",
            3: "Level",
            4: "Place in the rating",
            5: "**`Information about member `**<@{}>**`\nwith id {}`**",
            6: "**`Member doesn't have any roles from the bot's store`**",
            7: "**`Member already has this role`**",
            8: "**`You added role `**<@&{}>**` to the `**<@{}>",
            9: "**`Member doesn't have this role`**",
            10: "**`You removed role`**<@&{}>**` from the `**<@{}>",
            11: "Cash of the member",
            12: "Write a non-negative integer number",
            13: "Xp of the member",
            14: "**`Member's cash should be a non-negative integer number`**",
            15: "**`Member's xp should be a non-negative integer number`**",
            16: "**`You changed information about member `**<@{}>**` Now member's cash is {} and xp is {}`**",
            17: "**`You changed information about member `**<@{}>**` Now member's cash is {}`**",
            18: "**`You changed information about member `**<@{}>**` Now member's xp is {}`**",
            19: "Member management menu"
            
        },
        1: {
            0: "Изменить кэш/опыт",
            1: "Кэш",
            2: "Опыт",
            3: "Уровень",
            4: "Место в рейтинге",
            5: "**`Информация о пользователе `**<@{}>**`\nс id {}`**",
            6: "**`У пользователя нет ролей из магазина бота`**",
            7: "**`Эта роль уже есть у пользователя`**",
            8: "**`Вы добавили роль `**<@&{}>**` пользователю `**<@{}>",
            9: "**`Этой роли нет у пользователя`**",
            10: "**`Вы убрали роль `**<@&{}>**` у пользователя `**<@{}>",
            11: "Кэш пользователя",
            12: "Напишите целое неотрицательное число",
            13: "Опыт пользователя",
            14: "**`Кэш пользователя должен быть целым неотрицательным числом`**",
            15: "**`Опыт пользователя должен быть целым неотрицательным числом`**",
            16: "**`Вы изменили данные пользователя `**<@{}>**` Теперь кэш пользователя - {}, а опыт - {}`**",
            17: "**`Вы изменили данные пользователя `**<@{}>**` Теперь кэш пользователя - {}`**",
            18: "**`Вы изменили данные пользователя `**<@{}>**` Теперь опыт пользователя - {}`**",
            19: "Меню управления пользователем"
        }
    }

    def __init__(self, timeout: int, title: str, lng: int, memb_id: int, cur_money: int, cur_xp: int, auth_id: int) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=f"8100_{auth_id}_{randint(1, 100)}")
        self.is_changed: bool = False
        self.memb_id: int = memb_id

        self.st_cash: int = cur_money
        self.st_xp: int = cur_xp
        self.new_cash: int = cur_money
        self.new_xp: int = cur_xp

        self.cash_text_input: TextInput = TextInput(
            label=self.mng_membs_text[lng][11],
            placeholder=self.mng_membs_text[lng][12],
            default_value=f"{cur_money}",
            min_length=1,
            max_length=9,
            required=True,
            custom_id=f"8101_{auth_id}_{randint(1, 100)}"
        )
        self.xp_text_input: TextInput = TextInput(
            label=self.mng_membs_text[lng][13],
            placeholder=self.mng_membs_text[lng][12],
            default_value=f"{cur_xp}",
            min_length=1,
            max_length=9,
            required=True,
            custom_id=f"8102_{auth_id}_{randint(1, 100)}"
        )
        self.add_item(self.cash_text_input)
        self.add_item(self.xp_text_input)
    
    def verify_user_input(self) -> int:
        errors_bit_mask: int = 0b00
        
        cash_value: str | None = self.cash_text_input.value
        if cash_value and cash_value.isdigit() and (new_cash := int(cash_value)) >= 0:
            self.new_cash = new_cash
        else:
            errors_bit_mask |= 0b01
        
        xp_value: str | None = self.xp_text_input.value
        if xp_value and xp_value.isdigit() and (new_xp := int(xp_value)) >= 0:
            self.new_xp = new_xp
        else:
            errors_bit_mask |= 0b10

        return errors_bit_mask

    async def callback(self, interaction: Interaction) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        errors_bit_mask: int = self.verify_user_input()
        if errors_bit_mask:
            report: list[str] = []
            if errors_bit_mask & 0b01:
                report.append(self.mng_membs_text[lng][14])
            if errors_bit_mask & 0b10:
                report.append(self.mng_membs_text[lng][15])
            await interaction.response.send_message(embed=Embed(description="\n".join(report)), ephemeral=True)
            self.stop()
            return

        cash: int = self.new_cash
        xp: int = self.new_xp
        self.is_changed = True
        if cash != self.st_cash and xp != self.st_xp:
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:  
                    cur.execute("UPDATE users SET money = ?, xp = ? WHERE memb_id = ?", (cash, xp, self.memb_id))
                    base.commit()
            await interaction.response.send_message(embed=Embed(description=self.mng_membs_text[lng][16].format(self.memb_id, cash, xp)), ephemeral=True)

        elif cash != self.st_cash:
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:  
                    cur.execute("UPDATE users SET money = ? WHERE memb_id = ?", (cash, self.memb_id))
                    base.commit()
            await interaction.response.send_message(embed=Embed(description=self.mng_membs_text[lng][17].format(self.memb_id, cash)), ephemeral=True)

        elif xp != self.st_xp:
            with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
                with closing(base.cursor()) as cur:  
                    cur.execute("UPDATE users SET xp = ? WHERE memb_id = ?", (xp, self.memb_id))
                    base.commit()
            await interaction.response.send_message(embed=Embed(description=self.mng_membs_text[lng][18].format(self.memb_id, xp)), ephemeral=True)
        self.stop()


class XpSettingsModal(Modal):
    def __init__(self, timeout: int, lng: int, auth_id: int, g_id: int, cur_xp: int, cur_xpb: int) -> None:
        super().__init__(title=ranking_text[lng][7], timeout=timeout, custom_id=f"9100_{auth_id}_{randint(1, 100)}")
        self.xp_text_input = TextInput(
            label=ranking_text[lng][8],
            placeholder=ranking_text[lng][9],
            default_value=f"{cur_xp}",
            min_length=1,
            max_length=3,
            required=True,
            custom_id=f"9101_{auth_id}_{randint(1, 100)}"
        )
        self.xp_b_text_input = TextInput(
            label=ranking_text[lng][10],
            placeholder=ranking_text[lng][11],
            default_value=f"{cur_xpb}",
            min_length=1,
            max_length=5,
            required=True,
            custom_id=f"9102_{auth_id}_{randint(1, 100)}"
        )
        self.add_item(self.xp_text_input)
        self.add_item(self.xp_b_text_input)

        self.g_id: int = g_id
        self.old_xp: int = cur_xp
        self.old_xpb: int = cur_xpb
        self.new_xp: int = cur_xp
        self.new_xp_b: int = cur_xpb
        self.changed: bool = False

    def verify_user_input(self) -> int:
        errors_bit_mask: int = 0b00

        xp_value: str | None = self.xp_text_input.value
        if xp_value and xp_value.isdigit() and (xp_value_int := int(xp_value)) >= 0:
            self.new_xp = xp_value_int
        else:
            errors_bit_mask |= 0b01 

        xp_b_value: str | None = self.xp_b_text_input.value
        if xp_b_value and xp_b_value.isdigit() and (xp_b_value_int := int(xp_b_value)) >= 1:
            self.new_xp_b = xp_b_value_int
        else:
            errors_bit_mask |= 0b10
        
        return errors_bit_mask

    async def callback(self, interaction: Interaction) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        errors_bit_mask: int = self.verify_user_input()
        if errors_bit_mask:
            report: list[str] = []
            if errors_bit_mask & 0b01:
                report.append(ranking_text[lng][12])
            if errors_bit_mask & 0b10:
                report.append(ranking_text[lng][13])
            await interaction.response.send_message(embed=Embed(description="\n".join(report)), ephemeral=True)
            self.stop()
            return

        xp: int = self.new_xp
        xp_border: int = self.new_xp_b
        if self.old_xp != xp or self.old_xpb != xp_border:
            rep: list[str] = []
            with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    if self.old_xp != xp:
                        cur.execute("UPDATE server_info SET value = ? WHERE settings = 'xp_per_msg'", (xp,))
                        rep.append(ranking_text[lng][14].format(xp))
                    if self.old_xpb != xp_border:
                        cur.execute("UPDATE server_info SET value = ? WHERE settings = 'xp_border'", (xp_border,))
                        rep.append(ranking_text[lng][15].format(xp_border))
                    base.commit()
            await interaction.response.send_message(embed=Embed(description="\n".join(rep)), ephemeral=True)
            self.changed = True
        else:
            await interaction.response.send_message(embed=Embed(description=ranking_text[lng][16]), ephemeral=True)
        self.stop()


class SelectLevelModal(Modal):
    def __init__(self, lng: int, auth_id: int, timeout: int) -> None:
        super().__init__(title=ranking_text[lng][24], timeout=timeout, custom_id=f"11100_{auth_id}_{randint(1, 100)}")
        self.lng: int = lng
        self.level: int | None = None
        self.level_selection = TextInput(
            label=ranking_text[lng][24],
            style=TextInputStyle.short,
            custom_id=f"11101_{auth_id}_{randint(1, 100)}",
            min_length=1,
            max_length=3,
            required=True,
            placeholder=ranking_text[lng][28]
        )
        self.add_item(self.level_selection)
    
    def check_level(self, value: str | None) -> int:
        if value and value.isdigit() and (0 < (level := int(value)) < 101):
            return level
        return 0

    async def callback(self, interaction: Interaction) -> None:
        ans: int = self.check_level(self.level_selection.value)
        if ans:
            self.level = ans
        else:
            await interaction.response.send_message(embed=Embed(description=ranking_text[self.lng][35]), ephemeral=True)        
        self.stop()

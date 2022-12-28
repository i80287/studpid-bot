from sqlite3 import connect, Connection, Cursor
from contextlib import closing
from random import randint
from time import time

from nextcord import Embed, Interaction, TextInputStyle
from nextcord.ui import TextInput, Modal

from Variables.vars import path_to


ec_text = {
    0 : {
        0 : "Economy settings",
        1 : "💸 Money gained for message:\n**`{}`**",
        2 : "⏰ Cooldown for `/work`:\n**`{} seconds`**",
        3 : "💹 Salary from `/work`:\n**{}**",
        4 : "random integer from `{}` to `{}`",
        5 : "📙 Log channel for economic operations:\n{}",
        7 : "> To manage setting press button with\ncorresponding emoji",
        8 : "> To see and manage roles available for\npurchase/sale in the bot press 🛠️",
        9 : "**`Write amount of money gained for message (non negative integer number)`**",
        10 : "Amount of money gained from messages set to: `{}`",
        11 : "Write cooldown for `/work` command **in seconds** (integer at least 60)\nFor example, to make cooldown equalt to 240 seconds, write `240` in the chat",
        12 : "Cooldown for `/work` set to: `{}`",
        13 : "Write salary from `/work`:\nTwo non-negative numbers, second at least as much as first\nSalary will be random integer \
            between them\nIf you want salary to constant write one number\nFor example, if you write `1` `100` then salary \
            will be random integer from `1` to `100`\nIf you write `10`, then salary will always be `10`",
        14 : "**`Now salary is `**{}",
        15 : "Select channel",
        16 : "**`You chose channel `**{}",
        17 : "**`Timeout expired`**",
        18 : "__**role - role id - price - salary - cooldown for salary - type - how much in the store**__",
        19 : "No roles were added",
        20 : "`If role isn't shown in the menu(s) down below it means that bot can't manage this role`",
        21 : "**`You reseted log channel`**"
    },
    1 : {
        0 : "Настройки экономики",
        1 : "💸 Количество денег, получаемых за сообщение:\n**`{}`**",
        2 : "⏰ Кулдаун для команды `/work`:\n**`{} секунд`**",
        3 : "💹 Доход от команды `/work`:\n**{}**",
        4 : "рандомное целое число от `{}` до `{}`",
        5 : "📙 Канал для логов экономических операций:\n{}",
        7 : "> Для управления настройкой нажмите на кнопку с\nсоответствующим эмодзи",
        8 : "> Для просмотра и управления ролями, доступными\nдля покупки/продажи у бота, нажмите 🛠️",
        9 : "**`Укажите количество денег, получаемых за сообщение\n(неотрицательное целое число)`**",
        10 : "Количество денег, получаемых за одно сообщение, теперь равно: `{}`",
        11 : "Укажите кулдаун для команды `/work` **в секундах** (целое число не менее 60)\nНапример, чтобы поставить кулдаун 240 секунд, напишите в чат `240`",
        12 : "Кулдаун для команды `/work` теперь равен: `{}`",
        13 : "Укажите заработок от команды `/work`:\nДва неотрицательных числа, второе не менее первого\nЗаработок будет \
            рандомным целым числом между ними\nЕсли Вы хотите сделать заработок постоянным, укажите одно число\nНапример, \
            если Вы укажите `1` `100`, то заработок будет рандомным целым числом от `1` до `100`\nЕсли Вы укажите `10`, то \
            заработок всегда будет равен `10`",
        14 : "**`Теперь заработок: `**{}",
        15 : "Выберите канал",
        16 : "**`Вы выбрали канал `**{}",
        17 : "**`Время ожидания вышло`**",
        18 : "__**роль - id роли - цена - заработок - кулдаун заработка - тип - сколько в магазине**__",
        19 : "Не добавлено ни одной роли",
        20 : "`Если роль не отображается ни в одном меню снизу, значит, бот не может управлять ею`",
        21 : "**`Вы сбросили канал логов`**"
    }
}

ec_mr_text = { 
    0 : {
        0 : "Edit role",
        1 : "Yes",
        2 : "No",
        3 : "**`You declined removing the role `**<@&{}>",
        4 : "**`Please, wait a bit...`**",
        5 : "**`You removed role `**<@&{}>",
        6 : "Are you sure you want to delete role <@&{}> from the bot's settings?\nAll information about it will be deleted and it will be withdrawn from the store",
        7 : "**`You can't remove role that is not in the list`**",
        8 : "**`You can't edit role that is not in the list`**",
        9 : "**`This role is already in the list`**",
        10 : "Role's price",
        11 : "Write positive integer number as price of the role",
        12 : "Role's salary and cooldown for it (optional)",
        13 : "If role should bring money to its owners write salary and cooldown in hours (split numbers by space)",
        14 : "The same roles will be displayed in the store",
        15 : "Print 1 if the same roles will be separated (nonstacking) (each answer can be written in any window)",
        16 : "Print 2 if the same roles will be countable (can run out in the store) and stacking as one item",
        17 : "Print 3 if the same roles will be uncountable (can't run out in the store) and stacking as one item",
        18 : "Price must be positive integer number",
        19 : "Salary and cooldown must be two positive integer numbers separated by space, for example: `100` `24`",
        20 : "Salary should be positive integer number",
        21 : "Cooldown should be positive integer number, cooldown is time in hours. For example: `24` sets cooldown to 24 hours",
        22 : "Type of displaying of the role should be one of three numbers: `1`, `2` or `3`",
        23 : "You chose different types of displaying for the role",
        24 : "You added role <@&{}> with price **`{}`**, salary **`{}`**, cooldown for it **`{}`**, type **`{}`**",
        25 : "Editing the role",
        26 : "Print 1 if separated,nonstacking\n2 if countable,stacking\n3 if uncountable (can't run out),stacking",
        27 : "How much roles must be in the store",
        28 : "Print integer non-negative number. For uncountable roles print any non-negative number",
        29 : "Amount of the roles in the store must be non-negative integer number",
        30 : "You edited role <@&{}>. Now it's price is **`{}`**, salary is **`{}`**, cooldown for it is **`{}`**, role's type is **`{}`**, amount of roles in the store - **`{}`**",
    },
    1 : {
        0 : "Редактировать роль",
        1 : "Да",
        2 : "Нет",
        3 : "**`Вы отменили удаление роли `**<@&{}>",
        4 : "**`Пожалуйста, подождите...`**",
        5 : "**`Вы удалили роль `**<@&{}>",
        6 : "Вы уверены, что хотите удалить роль <@&{}> из настроек бота?\nВся информация о ней будет удалена и она будет изъята из магазина",
        7 : "**`Вы не можете убрать роль, которая не неходится в списке`**",
        8 : "**`Вы не можете редактировать роль, которая не неходится в списке`**",
        9 : "**`Эта роль уже находится в списке`**",
        10 : "Цена роли",
        11 : "Укажите целое положительное число",
        12 : "Доход роли и кулдаун для него (необязательно)",
        13 : "Если надо, чтобы роль приносила деньги,укажите доход и его кулдаун в часах(разделите числа пробелом)",
        14 : "Одинаковые роли будут отображаться в магазине",
        15 : "Напишите 1, если одинаковые роли будут отображаться отдельно (ответ можно написать в любом поле)",
        16 : "Напишите 2, если одинаковые роли будут стакающимеся и исчисляемыми (могут закончиться в магазине)",
        17 : "Напишите 3, если одинаковые роли будут стакающимеся и бесконечными (не могут закончиться в магазине)",
        18 : "В качестве цены роли надо указать целое положительное число",
        19 : "Заработок и кулдаун должны быть двумя положительными целыми числами, разделёнными пробелом, например, `100` `24`",
        20 : "Заработок должен быть целым положительным числом",
        21 : "Кулдаун должен быть целым положительным числом, кулдаун - время в часах. Например, `24` сделать кулдаун равным 24 часам",
        22 : "В качестве типа отображения роли надо указать одно из трёх чисел: `1`, `2` или `3`",
        23 : "Вы выбрали несколько разных типов отображения для роли",
        24 : "Вы добавили роль <@&{}> с ценой **`{}`**, доходом **`{}`**, его кулдауном **`{}`**, типом **`{}`**",
        25 : "Редактирование роли",
        26 : "Напишите 1,если раздельно,нестакаются\n2,если стакающися,исчисляемые\n3,если стакающиеся,бесконечные",
        27 : "Сколько ролей должно быть в магазине",
        28 : "Напишите целое неотрицательное число.Для бесконечных ролей можно указать любое неотрицательное число",
        29 : "Количество ролей в магазине должно быть целым неотрицательным числом",
        30 : "Вы отредактировали роль <@&{}>. Теперь её цена - **`{}`**, доход - **`{}`**, его кулдаун - **`{}`**, тип роли - **`{}`**, количество в магазине - **`{}`**",
    }
}

r_types = {
    0 : {
        1 : "Nonstacking, displayed separated",
        2 : "Stacking, countable",
        3 : "Stacking, infinite"
    },
    1 : {
        1 : "Нестакающаяся, отображается отдельно",
        2 : "Cтакающаяся, конечная",
        3 : "Cтакающаяся, бесконечная"
    }
}


class RoleAddModal(Modal):
    rl_add_modal_text = {
        0 : {
            0: "Adding role",
        },
        1: {
            0: "Добавление роли",
        },
    }

    def __init__(self, timeout: int, lng: int, role: int, m, auth_id: int):
        super().__init__(title=self.rl_add_modal_text[lng][0], timeout=timeout, custom_id=f"6100_{auth_id}_{randint(1, 100)}")
        self.role=role
        self.m = m
        self.added = False
        self.price = TextInput(
            label=ec_mr_text[lng][10],
            min_length=1,
            max_length=8,
            placeholder=ec_mr_text[lng][11],
            required=True,
            custom_id=f"6101_{auth_id}_{randint(1, 100)}"
        )
        self.salary = TextInput(
            label=ec_mr_text[lng][12],
            min_length=0,
            max_length=9,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][13],
            required=False,
            custom_id=f"6102_{auth_id}_{randint(1, 100)}"
        )
        self.r_type1 = TextInput(
            label=ec_mr_text[lng][14],
            min_length=1,
            max_length=1,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][15],
            required=False,
            custom_id=f"6103_{auth_id}_{randint(1, 100)}"
        )
        self.r_type2 = TextInput(
            label=ec_mr_text[lng][14],
            min_length=1,
            max_length=1,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][16],
            required=False,
            custom_id=f"6104_{auth_id}_{randint(1, 100)}"
        )
        self.r_type3 = TextInput(
            label=ec_mr_text[lng][14],
            min_length=1,
            max_length=1,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][17],
            required=False,
            custom_id=f"6105_{auth_id}_{randint(1, 100)}"
        )
        self.add_item(self.price)
        self.add_item(self.salary)
        self.add_item(self.r_type1)
        self.add_item(self.r_type2)
        self.add_item(self.r_type3)
        self.r_t = set()


    def check_role_type(self, r_type):
        if r_type and r_type.isdigit() and int(r_type) in {1, 2, 3}:
            self.r_t.add(int(r_type))

    def check_ans(self) -> int:
        ans: int = 0b000000

        price = self.price.value
        if not price or not price.isdigit() or int(price) <= 0:
            ans |= 0b000001
        
        cooldown_salary = self.salary.value
        if cooldown_salary:
            s_ans = cooldown_salary.split()
            if len(s_ans) != 2:
                ans |= 0b000010
            else:
                s, s_c = s_ans[0], s_ans[1]
                if not s.isdigit() or int(s) <= 0:
                    ans |= 0b000100

                if not s_c.isdigit() or int(s_c) <= 0:
                    ans |= 0b001000
        
        self.check_role_type(self.r_type1.value)
        self.check_role_type(self.r_type2.value)
        self.check_role_type(self.r_type3.value)
        if not self.r_t:
            ans |= 0b010000
        elif len(self.r_t) != 1:
            ans |= 0b100000

        return ans

    async def callback(self, interaction: Interaction):
        lng: int = 1 if "ru" in interaction.locale else 0
        ans_c: int = self.check_ans()
        if ans_c:
            rep = []
            if ans_c & 0b000001:
                rep.append(ec_mr_text[lng][18])
            if ans_c & 0b000010:
                rep.append(ec_mr_text[lng][19])
            if ans_c & 0b000100:
                rep.append(ec_mr_text[lng][20])
            if ans_c & 0b001000:
                rep.append(ec_mr_text[lng][21])
            if ans_c & 0b010000:
                rep.append(ec_mr_text[lng][22])
            if ans_c & 0b100000:
                rep.append(ec_mr_text[lng][23])
            
            await interaction.response.send_message(embed=Embed(description="\n".join(rep)), ephemeral=True)
            self.stop()
            return

        price: int = int(self.price.value)
        if self.salary.value:
            s_ans = self.salary.value.split()
            salary = int(s_ans[0])
            salary_c = int(s_ans[1]) * 3600
        else:
            salary = salary_c = 0
        r_type = int(list(self.r_t)[0])

        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("INSERT OR IGNORE INTO server_roles(role_id, price, salary, salary_cooldown, type) VALUES(?, ?, ?, ?, ?)", (self.role, price, salary, salary_c, r_type))
                base.commit()
                if salary:
                    cur.execute("INSERT OR IGNORE INTO salary_roles(role_id, members, salary, salary_cooldown, last_time) VALUES(?, ?, ?, ?, ?)", (self.role, "", salary, salary_c, 0))
                    base.commit()

        emb = self.m.embeds[0]
        dsc = emb.description.split("\n")
        rls = dsc[1:-2]
        dsc = [ec_text[lng][18]]
        for r in rls:
            dsc.append(r)
        dsc.append(f"<@&{self.role}> - **`{self.role}`** - **`{price}`** - **`{salary}`** - **`{salary_c//3600}`** - **`{r_types[lng][r_type]}`** - **`0`**")
        dsc.append("\n" + ec_text[lng][20])
        emb.description = "\n".join(dsc)
        await self.m.edit(embed=emb)

        self.added = True
        await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][24].format(self.role, price, salary, salary_c//3600, r_types[lng][r_type])), ephemeral=True)
        self.stop()


class RoleEditModal(Modal):
    def __init__(self, timeout: int, role: int, m, lng: int, auth_id: int, p: int, s: int, s_c: int, r_t: int, in_store: int):
        super().__init__(title=ec_mr_text[lng][25], timeout=timeout, custom_id=f"7100_{auth_id}_{randint(1, 100)}")
        self.role=role
        self.m = m
        self.added = False
        self.prev_r_t = r_t
        self.s = s
        self.s_c = s_c
        self.changed = False
        self.price = TextInput(
            label=ec_mr_text[lng][10],
            min_length=1,
            max_length=8,
            placeholder=ec_mr_text[lng][11],
            default_value=f"{p}",
            required=True,
            custom_id=f"7101_{auth_id}_{randint(1, 100)}"
        )
        if s == 0:
            def_s = None
        else:
            def_s = f"{s} {s_c}"
        self.salary = TextInput(
            label=ec_mr_text[lng][12],
            min_length=0,
            max_length=9,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][13],
            default_value=def_s,
            required=False,
            custom_id=f"7102_{auth_id}_{randint(1, 100)}"
        )
        self.r_type_inp = TextInput(
            label=ec_mr_text[lng][14],
            min_length=1,
            max_length=1,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][26],
            default_value=f"{r_t}",
            required=False,
            custom_id=f"7103_{auth_id}_{randint(1, 100)}"
        )
        self.in_st = TextInput(
            label=ec_mr_text[lng][27],
            min_length=1,
            max_length=2,
            style=TextInputStyle.paragraph,
            placeholder=ec_mr_text[lng][28],
            default_value=f"{in_store}",
            required=True,
            custom_id=f"7104_{auth_id}_{randint(1, 100)}"
        )
        self.add_item(self.price)
        self.add_item(self.salary)
        self.add_item(self.r_type_inp)
        self.add_item(self.in_st)

    def check_ans(self) -> int:
        ans: int = 0b000000

        price = self.price.value
        if not price or not price.isdigit() or int(price) <= 0:
            ans |= 0b000001
        
        cooldown_salary = self.salary.value
        if cooldown_salary:
            s_ans = cooldown_salary.split()
            if len(s_ans) != 2:
                ans |= 0b000010
            else:
                s, s_c = s_ans[0], s_ans[1]
                if not s.isdigit() or int(s) <= 0:
                    ans |= 0b000100
                if not s_c.isdigit() or int(s_c) <= 0:
                    ans |= 0b001000
        
        role_type = self.r_type_inp.value
        if not role_type or not role_type.isdigit() or not int(role_type) in {1, 2, 3}:
            ans |= 0b010000

        in_store_amount = self.in_st.value
        if not in_store_amount or not in_store_amount.isdigit() or int(in_store_amount) < 0:
            ans |= 0b100000

        return ans

    async def callback(self, interaction: Interaction):
        lng: int = 1 if "ru" in interaction.locale else 0
        ans_c: int = self.check_ans()
        
        if ans_c:
            rep: list = []
            if ans_c & 0b000001:
                rep.append(ec_mr_text[lng][18])
            if ans_c & 0b000010:
                rep.append(ec_mr_text[lng][19])
            if ans_c & 0b000100:
                rep.append(ec_mr_text[lng][20])
            if ans_c & 0b001000:
                rep.append(ec_mr_text[lng][21])
            if ans_c & 0b010000:
                rep.append(ec_mr_text[lng][22])
            if ans_c & 0b100000:
                rep.append(ec_mr_text[lng][29])
            
            await interaction.response.send_message(embed=Embed(description='\n'.join(rep)), ephemeral=True)
            self.stop()
            return

        price = int(self.price.value)
        if self.salary.value:
            s_ans = self.salary.value.split()
            salary = int(s_ans[0])
            salary_c = int(s_ans[1]) * 3600
        else:
            salary = salary_c = 0
        r_type = int(self.r_type_inp.value)
        l = int(self.in_st.value)
        r = self.role

        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                cur.execute("UPDATE server_roles SET price = ?, salary = ?, salary_cooldown = ?, type = ? WHERE role_id = ?", (price, salary, salary_c, r_type, r))
                if r_type != self.prev_r_t:
                    self.update_type_and_store(base=base, cur=cur, price=price, salary=salary, salary_c=salary_c, r_type=r_type, r=r, l=l)
                else:
                    self.update_store(base=base, cur=cur, r=r, price=price, salary=salary, salary_c=salary_c, r_type=r_type, l=l, l_prev = int(self.in_st.default_value))
                if salary != self.s or salary_c != self.s_c * 3600:
                    self.update_salary(base=base, cur=cur, r=r, salary=salary, salary_c=salary_c)
        
        if r_type == 3 and l:
            l = "∞"

        emb = self.m.embeds[0]
        dsc = emb.description.split("\n")
        for i in range(1, len(dsc)-1):
            if f"{r}" in dsc[i]:
                dsc[i] = f"<@&{r}> - **`{r}`** - **`{price}`** - **`{salary}`** - **`{salary_c//3600}`** - **`{r_types[lng][r_type]}`** - **`{l}`**"
        emb.description = "\n".join(dsc)
        await self.m.edit(embed=emb)
        self.changed = True

        await interaction.response.send_message(embed=Embed(description=ec_mr_text[lng][30].format(r, price, salary, salary_c // 3600, r_types[lng][r_type], l)), ephemeral=True)
        self.stop()
    
    def update_type_and_store(self, base: Connection, cur: Cursor, price: int, salary: int, salary_c: int, r_type: int, r: int, l: int):
        cur.execute("DELETE FROM store WHERE role_id = ?", (r,))
        base.commit()
        if not l:
            return
        t = int(time())
        if r_type == 3:
            free_number = self.peek_role_free_number(cur)
            cur.execute("INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                        (free_number, r, -404, price, t, salary, salary_c, 3))
        elif r_type == 2:
            free_number = self.peek_role_free_number(cur)
            cur.execute("INSERT INTO store (role_number, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                        (free_number, r, l, price, t, salary, salary_c, 2))
        elif r_type == 1:
            free_numbers = self.peek_role_free_numbers(cur, l)
            inserting_roles = ((free_number, r, 1, price, t, salary, salary_c, 1) for free_number in free_numbers)
            cur.executemany("INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", inserting_roles)
        base.commit()
        
    def update_store(self, base: Connection, cur: Cursor, r: int, price: int, salary: int, salary_c: int, r_type: int, l: int, l_prev: int):
        if not l:
            cur.execute("DELETE FROM store WHERE role_id = ?", (r,))
            base.commit()
            return
        t = int(time())
        
        if r_type == 2:
            if not l_prev:
                free_number = self.peek_role_free_number(cur)
                cur.execute("INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                            (free_number, r, l, price, t, salary, salary_c, 2))
            else:
                cur.execute("UPDATE store SET quantity = ?, price = ?, last_date = ?, salary = ?, salary_cooldown = ? WHERE role_id = ?", (l, price, t, salary, salary_c, r))
        
        elif r_type == 1:
            roles_amount_change = l - l_prev
            if roles_amount_change > 0:
                free_numbers = self.peek_role_free_numbers(cur, roles_amount_change)
                inserting_roles = ((free_number, r, 1, price, t, salary, salary_c, 1) for free_number in free_numbers)
                cur.executemany("INSERT INTO store (role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                                inserting_roles)
            elif not roles_amount_change:
                cur.execute("UPDATE store SET price = ?, last_date = ?, salary = ?, salary_cooldown = ? WHERE role_id = ?", (price, t, salary, salary_c, r))
            else:
                sorted_rls_to_delete = cur.execute("SELECT rowid FROM store WHERE role_id = ? ORDER BY last_date", (r,)).fetchall()[:-roles_amount_change]
                rows = ", ".join({str(x[0]) for x in sorted_rls_to_delete})
                cur.execute(f"DELETE FROM store WHERE rowid IN ({rows})")

        elif r_type == 3 and not l_prev:
            free_number = self.peek_role_free_number(cur)
            cur.execute("INSERT INTO store(role_number, role_id, quantity, price, last_date, salary, salary_cooldown, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                        (free_number, r, -404, price, t, salary, salary_c, 3))

        base.commit()   

    def update_salary(self, base: Connection, cur: Cursor, r: int, salary: int, salary_c: int):
        if not salary:
            cur.execute("DELETE FROM salary_roles WHERE role_id = ?", (r,))
            base.commit()
            return
        if not cur.execute("SELECT role_id FROM salary_roles WHERE role_id = ?", (r,)).fetchone():
            ids = set()
            string_role_id = f"{r}"
            for req in cur.execute("SELECT memb_id, owned_roles FROM users").fetchall():
                if string_role_id in req[1]:
                    ids.add(f"{req[0]}")
            membs = "".join(f"#{memb_id}" for memb_id in ids) if ids else ""
            cur.execute("INSERT INTO salary_roles(role_id, members, salary, salary_cooldown, last_time) VALUES(?, ?, ?, ?, ?)", (r, membs, salary, salary_c, 0))
            base.commit()
            return
        cur.execute("UPDATE salary_roles SET salary = ?, salary_cooldown = ? WHERE role_id = ?", (salary, salary_c, r))
        base.commit()

    @staticmethod
    def peek_role_free_number(cur: Cursor) -> int:
        req = cur.execute("SELECT role_number FROM store ORDER BY role_number").fetchall()
        if req:
            role_numbers = [int(r_n[0]) for r_n in req]
            if role_numbers[0] != 1:
                return 1
            for i in range(len(role_numbers) - 1):
                if role_numbers[i+1] - role_numbers[i] != 1:
                    return role_numbers[i] + 1
            return len(role_numbers) + 1
        else:
            return 1
    

    @staticmethod
    def peek_role_free_numbers(cur: Cursor, amount_of_numbers: int) -> list[int]:
        req = cur.execute("SELECT role_number FROM store").fetchall()
        if req:
            role_numbers = {r_n[0] for r_n in req}
            after_last_number =  max(role_numbers) + 1
            free_numbers = set(range(1, after_last_number)).difference(role_numbers)
            lack_numbers_len = amount_of_numbers - len(free_numbers)
            if lack_numbers_len <= 0:
                return list(free_numbers)[:amount_of_numbers]            
            free_numbers.update(range(after_last_number, after_last_number + lack_numbers_len))
            return list(free_numbers)
        else:
            return list(range(1, amount_of_numbers + 1))


class ManageMemberCashXpModal(Modal):
    mng_membs_text = {
        0 : {
            0 : "Change cash/xp",
            1 : "Cash",
            2 : "Xp",
            3 : "Level",
            4 : "Place in the rating",
            5 : "**`Information about member `**<@{}>**`\nwith id {}`**",
            6 : "**`Member doesn't have any roles from the bot's store`**",
            7 : "**`Member already has this role`**",
            8 : "**`You added role `**<@&{}>**` to the `**<@{}>",
            9 : "**`Member doesn't have this role`**",
            10 : "**`You removed role`**<@&{}>**` from the `**<@{}>",
            11 : "Cash of the member",
            12 : "Write a non-negative integer number",
            13 : "Xp of the member",
            14 : "**`Member's cash should be a non-negative integer number`**",
            15 : "**`Member's xp should be a non-negative integer number`**",
            16 : "**`You changed information about member `**<@{}>**` Now member's cash is {} and xp is {}`**",
            17 : "**`You changed information about member `**<@{}>**` Now member's cash is {}`**",
            18 : "**`You changed information about member `**<@{}>**` Now member's xp is {}`**",
            19 : "Member management menu"
            
        },
        1 : {
            0 : "Изменить кэш/опыт",
            1 : "Кэш",
            2 : "Опыт",
            3 : "Уровень",
            4 : "Место в рейтинге",
            5 : "**`Информация о пользователе `**<@{}>**`\nс id {}`**",
            6 : "**`У пользователя нет ролей из магазина бота`**",
            7 : "**`Эта роль уже есть у пользователя`**",
            8 : "**`Вы добавили роль `**<@&{}>**` пользователю `**<@{}>",
            9 : "**`Этой роли нет у пользователя`**",
            10 : "**`Вы убрали роль `**<@&{}>**` у пользователя `**<@{}>",
            11 : "Кэш пользователя",
            12 : "Напишите целое неотрицательное число",
            13 : "Опыт пользователя",
            14 : "**`Кэш пользователя должен быть целым неотрицательным числом`**",
            15 : "**`Опыт пользователя должен быть целым неотрицательным числом`**",
            16 : "**`Вы изменили данные пользователя `**<@{}>**` Теперь кэш пользователя - {}, а опыт - {}`**",
            17 : "**`Вы изменили данные пользователя `**<@{}>**` Теперь кэш пользователя - {}`**",
            18 : "**`Вы изменили данные пользователя `**<@{}>**` Теперь опыт пользователя - {}`**",
            19 : "Меню управления пользователем"
        }
    }

    def __init__(self, timeout: int, title: str, lng: int, memb_id: int, cur_money: int, cur_xp: int, auth_id: int):
        super().__init__(title=title, timeout=timeout, custom_id=f"8100_{auth_id}_{randint(1, 100)}")
        self.is_changed = False
        self.memb_id = memb_id
        self.st_cash = cur_money,
        self.st_xp = cur_xp
        self.cash = TextInput(
            label=self.mng_membs_text[lng][11],
            placeholder=self.mng_membs_text[lng][12],
            default_value=f"{cur_money}",
            min_length=1,
            max_length=9,
            required=True,
            custom_id=f"8101_{auth_id}_{randint(1, 100)}"
        )
        self.xp = TextInput(
            label=self.mng_membs_text[lng][13],
            placeholder=self.mng_membs_text[lng][12],
            default_value=f"{cur_xp}",
            min_length=1,
            max_length=9,
            required=True,
            custom_id=f"8102_{auth_id}_{randint(1, 100)}"
        )
        self.add_item(self.cash)
        self.add_item(self.xp)
    
    def check_ans(self) -> int:
        if not(self.cash.value and self.cash.value.isdigit() and int(self.cash.value) >= 0):
            ans = 1
        else:
            ans = 0        
        if not(self.xp.value and self.xp.value.isdigit() and int(self.xp.value) >= 0):
            ans += 10
        return ans

    async def callback(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        ans = self.check_ans()
        msg = []
        if ans % 2 == 1:
            msg.append(self.mng_membs_text[lng][14])
        if ans // 10 == 1:
            msg.append(self.mng_membs_text[lng][15])
        if len(msg):
            await interaction.response.send_message(embed=Embed(description="\n".join(msg)), ephemeral=True)
            self.stop()
            return

        cash = int(self.cash.value)
        xp = int(self.xp.value)
        
        self.new_cash = cash
        self.new_xp = xp
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
    ranking_text = {
        0 : {
            0 : "✨ Xp gained per message:\n**`{}`**",
            1 : "✨ Amount of xp between adjacent levels:\n**`{}`**",
            2 : "📗 Channel for the notification about new levels:\n{}",
            4 : "> To manage setting press button with corresponding emoji\n",
            5 : "> Press :mute: to manage channels where members can't get xp\n",
            6 : "> Press 🥇 to manage roles given for levels",
            7 : "Managing xp settings",
            8 : "Xp per message",
            9 : "Amount of xp gained by every member from one message, non-negative integer number",
            10 : "Amount of xp between adjected levels",
            11 : "Amount of xp members need to gain to get next level, positive integer number",
            12 : "**`Xp gained per message should be non-negative integer number`**",
            13 : "**`Amount of xp between adjected levels should be positive integer number`**",
            14 : "**`You changed amount of xp gained from one message, now it's {}`**",
            15 : "**`You changed amount of xp needed to get next level, now it's {}`**",
            16 : "**`You hasn't changed anything`**",
            17 : "__**channel**__ - __**id**__",
            18 : "**`No channels were selected`**",
            19 : "**`You added channel `**<#{}>",
            20 : "**`You removed channel `**<#{}>",
            21 : "**`You hasn't selected the channel yet`**",
            22 : "**`This channel is already added`**",
            23 : "**`This channel hasn't been added yet`**",
            24 : "level",
            25 : "**`No roles matched for levels`**",
            26 : "Roles for level",
            27 : "**`Press `**<:add01:999663315804500078>🔧**`to add / change role for the level`**\n**`Press `**<:remove01:999663428689997844>**` to remove role for the level`**",
            28 : "Write the level: positive integer from 1 to 100",
            29 : "**`Select role for level {}`**",
            30 : "**`Bot can't give any role on the server`**",
            31 : "**`From now role given for the level {} is `**<@&{}>",
            32 : "**`Timeout has expired`**",
            33 : "**`You removed role for level {}`**",
            34 : "**`No roles matches level {}`**",
            35 : "Write the level: **`positive integer from 1 to 100`**",
        },
        1 : {
            0 : "✨ Опыт, получаемый за одно сообщение:\n**`{}`**",
            1 : "✨ Количество опыта между соседними уровнями:\n**`{}`**",
            2 : "📗 Канал для оповещений о получении нового уровня:\n{}",
            4 : "> Для управления настройкой нажмите на кнопку с соответствующим эмодзи\n",
            5 : "> Нажмите :mute: для управления каналами, в которых пользователи не могут получать опыт\n",
            6 : "> Нажмите 🥇 для управления ролями, выдаваемыми за уровни",
            7 : "Управление настройками опыта",
            8 : "Опыт за сообщение",
            9 : "Количество опыта, получаемого пользователем за одно сообщение, целое неотрицательное число",
            10 : "Количество опыта между уровнями",
            11 : "Количество опыта,необходимого участникам для получения следующего уровня, целове положительное число",
            12 : "**`Опыт, получаемый участником за одно сообщение, должен быть целым неотрицательным числом`**",
            13 : "**`Количество опыта, который необходимо набрать участникам для получения следующего уровня, должно быть целым положительным числом`**",
            14 : "**`Вы изменили количество опыта, получаемого участником за одно сообщение, теперь оно равно {}`**",
            15 : "**`Вы изменили количество опыта, необходимого участнику для получения следующего уровня, теперь оно равно {}`**",
            16 : "**`Вы ничего не изменили`**",
            17 : "__**канал**__ - __**id**__",
            18 : "**`Не выбрано ни одного канала`**",
            19 : "**`Вы добавили канал `**<#{}>",
            20 : "**`Вы убрали канал `**<#{}>",
            21 : "**`Вы не выбрали канал`**",
            22 : "**`Этот канал уже добавлен`**",
            23 : "**`Этот канал ещё не был добавлен`**",
            24 : "уровень",
            25 : "**`Роли за уровни не назначены`**",
            26 : "Роли за уровни",
            27 : "**`Нажмите `**<:add01:999663315804500078>🔧**`, чтобы добавить / изменить роль за уровень`**\n**`Нажмите `**<:remove01:999663428689997844>**`, чтобы убрать роль за уровень`**",
            28 : "Напишите номер уровня: положительное целое число от 1 до 100",
            29 : "**`Выберите роль для уровня {}`**",
            30 : "**`Бот не может выдать ни одной роли на сервере`**",
            31 : "**`Теперь за уровень {} выдаётся роль `**<@&{}>",
            32 : "**`Время истекло`**",
            33 : "**`Вы убрали роль за уровень {}`**",
            34 : "**`Уровню {} не соответствует ни одна роль`**",
            35 : "Напишите номер уровня: **`положительное целое число от 1 до 100`**",
        }
    }

    def __init__(self, timeout: int, lng: int, auth_id: int, g_id: int, cur_xp: int, cur_xpb: int):
        super().__init__(title=self.ranking_text[lng][7], timeout=timeout, custom_id=f"9100_{auth_id}_{randint(1, 100)}")
        self.xp = TextInput(
            label=self.ranking_text[lng][8],
            placeholder=self.ranking_text[lng][9],
            default_value=f"{cur_xp}",
            min_length=1,
            max_length=3,
            required=True,
            custom_id=f"9101_{auth_id}_{randint(1, 100)}"
        )
        self.xp_b = TextInput(
            label=self.ranking_text[lng][10],
            placeholder=self.ranking_text[lng][11],
            default_value=f"{cur_xpb}",
            min_length=1,
            max_length=5,
            required=True,
            custom_id=f"9102_{auth_id}_{randint(1, 100)}"
        )
        self.add_item(self.xp)
        self.add_item(self.xp_b)

        self.g_id = g_id
        self.old_xp = cur_xp
        self.old_xpb = cur_xpb
        self.changed: bool = False

    def check_ans(self):
        ans = 1 if not(self.xp.value and self.xp.value.isdigit() and int(self.xp.value) >= 0) else 0
        if not(self.xp_b.value and self.xp_b.value.isdigit() and int(self.xp_b.value) >= 1):
            ans += 10
        return ans

    async def callback(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0
        ans = self.check_ans()
        rep = []
        if ans % 2 == 1:
            rep.append(self.ranking_text[lng][12])
        if ans // 10 == 1:
            rep.append(self.ranking_text[lng][13])
        if len(rep):
            await interaction.response.send_message(embed=Embed(description="\n".join(rep)), ephemeral=True)
            self.stop()
            return

        xp = int(self.xp.value)
        xpb = int(self.xp_b.value)

        if self.old_xp != xp or self.old_xpb != xpb:
            rep = []
            with closing(connect(f"{path_to}/bases/bases_{self.g_id}/{self.g_id}.db")) as base:
                with closing(base.cursor()) as cur:
                    if self.old_xp != xp:
                        cur.execute("UPDATE server_info SET value = ? WHERE settings = 'xp_per_msg'", (xp,))
                        rep.append(self.ranking_text[lng][14].format(xp))
                        self.old_xp = xp
                    if self.old_xpb != xpb:
                        cur.execute("UPDATE server_info SET value = ? WHERE settings = 'xp_border'", (xpb,))
                        rep.append(self.ranking_text[lng][15].format(xpb))
                        self.old_xpb = xpb
                    base.commit()
            await interaction.response.send_message(embed=Embed(description="\n".join(rep)), ephemeral=True)
            self.changed = True
        else:
            await interaction.response.send_message(embed=Embed(description=self.ranking_text[lng][16]), ephemeral=True)
        self.stop()


class SelectLevelModal(Modal):
    def __init__(self, lng: int, auth_id: int, timeout: int):
        super().__init__(title=self.ranking_text[lng][24], timeout=timeout, custom_id=f"11100_{auth_id}_{randint(1, 100)}")
        self.lng = lng
        self.level = None
        self.level_selection = TextInput(
            label=self.ranking_text[lng][24],
            style=TextInputStyle.short,
            custom_id=f"11101_{auth_id}_{randint(1, 100)}",
            min_length=1,
            max_length=3,
            required=True,
            placeholder=self.ranking_text[lng][28]
        )
        self.add_item(self.level_selection)
    
    def check_level(self, value: str):
        if value.isdigit() and (0 < int(value) < 101):
            return int(value)
        return None

    async def callback(self, interaction: Interaction):
        ans = self.check_level(self.level_selection.value)
        if not ans:
            await interaction.response.send_message(embed=Embed(description=self.ranking_text[self.lng][35]), ephemeral=True)
            return
        self.level = ans
        self.stop()

from asyncio import sleep
from time import time
from datetime import datetime
from contextlib import closing
from sqlite3 import connect, Connection, Cursor

from nextcord.ext import commands
from nextcord import slash_command, Interaction, Embed, ButtonStyle, Colour, Locale, SlashOption, NotFound
from nextcord.ui import Button, View

from config import path_to, bot_guilds_e, bot_guilds_r

class custom_button_p(Button):
    def __init__(self, label: str, disabled: bool, style, row: int):
        super().__init__(label=label, disabled=disabled, style=style, row=row)

    async def callback(self, interaction: Interaction):
        await super().view.click_p(interaction=interaction, label=super().label)


class custom_button(Button):
    def __init__(self, label: str, disabled: bool, style):
        super().__init__(label=label, disabled=disabled, style=style)

    async def callback(self, interaction: Interaction):
        await super().view.click(interaction=interaction, label=super().label)


class Poll(View):
    def __init__(self):
        self.thesis: str = ""
        self.n: int = 12
        self.questions: list = []
        self.timeout: int = 0
        self.m = None
        self.timestamp = None
        self.verified: bool = False
        self.anon: bool = True
        self.mult: bool = True
        self.lng: bool = 0
        self.text = {
            0 : {
                0 : "❌**`Disapproved by `**",
                1 : "✅**`Approved by `**",
                2 : "**`Channel for polls posting isn't configured`**",
                3 : "**`You voted for the {}`**",
                4 : "**`You retracked vote from the {}`**",
                5 : "**`You voted for the {} and your vote for the {} was retracked`**",
                6 : "**Winner:**",
                7 : "**Winners:**",
                8 : "**Votes for all choices:**",
                9 : "**Voters**",
                10 : "{} votes",
                11 : "**`You don't have permissions to accept/decline the polls`**",
                12 : "{} vote",
            },
            1 : {
                0 : "❌**`Отказано пользователем `**",
                1 : "✅**`Принято пользователем `**",
                2 : "**`Канал для постинга поллов не настроен`**",
                3 : "**`Вы проголосовали за вариант {}`**",
                4 : "**`Вы отозвали голос за вариант {}`**",
                5 : "**`Вы проголосовали за вариант {} и Ваш голос за {} был отозван`**",
                6 : "**Победитель:**",
                7 : "**Победители:**",
                8 : "**Количество голосов за все варианты:**",
                9 : "**Проголосовавшие:**",
                10 : "{} голосов",
                11 : "**`У вас нет прав одобрять/отклонять поллы`**",
                12 : "{} голос",
            }
        }
    

    def init_timeout(self):
        super().__init__(timeout=self.timeout)


    def init_buttons(self):
        for i in range(self.n):
            self.add_item(custom_button(label=f"{i+1}", disabled=True, style=ButtonStyle.blurple))
        self.add_item(custom_button_p(label="approve", disabled=False, style=ButtonStyle.green, row=(self.n + 4) // 5 + 1))
        self.add_item(custom_button_p(label="disapprove", disabled=False, style=ButtonStyle.red, row=(self.n + 4) // 5 + 1))


    def init_ans(self):
        self.voters = [set() for _ in range(self.n)]
    
    
    def check_moder(self, interaction: Interaction, base: Connection, cur: Cursor) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        mdrls = cur.execute("SELECT * FROM mod_roles").fetchall()
        if mdrls is None or mdrls == []:
            return False
        else:
            mdrls = {x[0] for x in mdrls}
            return any(role.id in mdrls for role in interaction.user.roles)


    async def click_p(self, interaction: Interaction, label):
        g = interaction.guild
        lng = 1 if "ru" in interaction.locale else 0
        with closing(connect(f"{path_to}/bases/bases_{g.id}/{g.id}.db")) as base:
            with closing(base.cursor()) as cur:
                
                if not self.check_moder(interaction=interaction, base=base, cur=cur):
                    await interaction.response.send_message(embed=Embed(description=self.text[lng][11]), ephemeral=True)
                    return

                if label == "disapprove":
                    for i in self.children:
                        i.disabled = True
                    emb = interaction.message.embeds[0]
                    emb.description = f"{self.text[lng][0]}{interaction.user.mention}\n" + emb.description
                    await interaction.message.edit(view=self, embed=emb)
                    self.stop()
                elif label == "approve":
                    chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'poll_c'").fetchone()[0]
                    if chnl_id != 0:
                        chnl = g.get_channel(chnl_id)     
                        self.verified = True
                        emb = interaction.message.embeds[0]
                        o_dsc = emb.description
                        emb.description = f"{self.text[lng][1]}{interaction.user.mention}\n" + emb.description
                        self.children[-1].disabled = True
                        self.children[-2].disabled = True
                        await interaction.message.edit(view=self, embed=emb)

                        i = 0
                        while i < len(self.children):
                            if "prove" in self.children[i].label:
                                self.remove_item(self.children[i])
                            else:
                                self.children[i].disabled = False
                                i += 1

                        emb.description = o_dsc
                        self.m_v = await chnl.send(view=self, embed=emb)
                    else:
                        await interaction.response.send_message(self.text[lng][2])
            
    
    async def update_votes(self, interaction: Interaction, L: int, val: bool):
        emb = interaction.message.embeds[0]
        field = emb.fields[L-1]

        text1 = emb.author.name
        t1 = text1.rfind(": ")
        total_votes = int(text1[t1+2:])

        text2 = field.value
        t2 = text2.rfind(": ")
        cur_votes = int(text2[t2+2:])

        if val:
            cur_votes += 1
            total_votes += 1
        else:
            cur_votes = max(0, cur_votes - 1)
            total_votes = max(0, total_votes - 1)
        
        emb.remove_author()
        emb.set_author(name=text1[:t1+2]+f"{total_votes}")    
        emb.set_field_at(index=L-1, name=field.name, value=text2[:t2+2]+f"{cur_votes}")
        
        await interaction.message.edit(embed=emb)
        

    async def click(self, interaction: Interaction, label: str):
        if not label.isdigit():
            return
        L = int(label)
        u_id = interaction.user.id
        lng = 1 if "ru" in interaction.locale else 0
        if u_id in self.voters[L-1]:
            await self.update_votes(interaction=interaction, L=L, val=0)
            self.voters[L-1].remove(u_id)
            try:
                await interaction.response.send_message(embed=Embed(description=self.text[lng][4].format(L)), ephemeral=True)
            except NotFound:
                sleep(1)
                try:
                    await interaction.response.send_message(embed=Embed(description=self.text[lng][4].format(L)), ephemeral=True)
                except:
                    pass
        else:    
            fl = -1
            for x in range(self.n):
                if u_id in self.voters[x]:
                    fl = x
            await self.update_votes(interaction=interaction, L=L, val=1)
            self.voters[L-1].add(u_id)
            if fl != -1 and not self.mult:
                await self.update_votes(interaction=interaction, L=fl+1, val=0)
                self.voters[fl].remove(u_id)
                try:
                    await interaction.response.send_message(embed=Embed(description=self.text[lng][5].format(L, fl+1)), ephemeral=True)
                except NotFound:
                    sleep(1)
                    try:
                        await interaction.response.send_message(embed=Embed(description=self.text[lng][5].format(L, fl+1)), ephemeral=True)
                    except:
                        pass 
                return
            try:
                await interaction.response.send_message(embed=Embed(description=self.text[lng][3].format(L)), ephemeral=True)
            except NotFound:
                sleep(1)
                try:
                    await interaction.response.send_message(embed=Embed(description=self.text[lng][3].format(L)), ephemeral=True)
                except:
                    pass
                
            
    async def on_timeout(self):
        if not self.verified:
            self.stop()
            return
        
        win = []
        mx = 0
        dsc = [""]
        lng = self.lng
        for i in range(self.n):
            if len(self.voters[i]) == 1:
                dsc.append(f"{i+1}) {self.questions[i]} - {self.text[lng][12].format(len(self.voters[i]))}")
            else:
                dsc.append(f"{i+1}) {self.questions[i]} - {self.text[lng][10].format(len(self.voters[i]))}")
            if not self.anon and len(self.voters[i]) > 0:
                dsc.append(self.text[lng][9])
                for j in self.voters[i]:
                    dsc.append(f"<@{j}>")
            if len(self.voters[i]) == mx:
                win.append(i+1)
            elif len(self.voters[i]) > mx:
                mx = len(self.voters[i])
                win.clear()
                win.append(i+1)
        
        if len(win) == 1:
            dsc[0] = f"{self.text[lng][6]}\n{win[0]}) {self.questions[win[0]-1]} - {self.text[lng][10].format(mx)}\n{self.text[lng][8]}"
        else:
            dsc[0] = f"{self.text[lng][7]}\n"
            for i in range(len(win)):
                dsc[0] += f"{win[i]}) {self.questions[win[i]-1]} - {self.text[lng][10].format(mx)}\n"
            dsc[0] += f"{self.text[lng][8]}"
        
        emb = Embed(description="\n".join(dsc))
        
        for c in self.children:
            c.disabled = True
        await self.m_v.edit(view=self, embed=emb)
        
        self.stop()


class polling(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        global bot_guilds_e
        global bot_guilds_r
        global text_4
        text_4 = {
            0 : {
                0 : "Timeout for poll has expired",
                1 : "Create poll menu",
                2 : "Write a name for the poll",
                3 : "Write a question for the poll",
                4 : "How much days the poll will be active and **in which time** it will expired? Write in format **`after_how_much_days-hours-minutes`**. \
                    You can choose no more than 21 days. \n For example **`1-18-0`** will publish poll that will expire tomorrow at 18:00",
                5 : "Will the poll be anonymous? Write **`y`**/**`yes`**/**`1`** if you want poll to be anonymous and **`n`**/**`no`**/**`0`** if not",
                6 : "How much answers will the poll have?\nChoose integer from 1 to 12",
                #7 : "Write {} answer",
                7 : "**`You can't select time for the poll less than it's now`**",
                8 : "**`You created poll and it was sent to the verification`**",
                9 : "Poll creation was cancelled",
                10 : "Verification channel isn't configured",
                11 : "Channel for polls isn't configured",
                12 : "Poll is anonymous",
                13 : "Poll isn't anonymous",
                14 : "Poll with multiple choice",
                15 : "Poll with single choice",
                16 : "Votes: 0",
                17 : "answer",
                18 : "\n**`Author: `**<@{}>"
            },
            1 : {
                0 : "Истёк таймаут создания полла",
                1 : "Меню создания полла. Напишите cancel для отмены",
                2 : "Напишите имя полла",
                3 : "Напишите вопрос или тезис полла",
                4 : "Сколько дней будет действовать полл и **в какое время** он закончится? Напишите в формате **`через_сколько_дней-часы-минуты`**. \
                    Можно указать не более 21 дня. \nНапример, **`1-18-0`** опубликует полл, который будет действовать до завтра 18:00",
                5 : "Будет ли полл анонимным? Напишите **`y`**/**`yes`**/**`да`**/**`1`**  для анонимности или **`n`**/**`no`**/**`нет`**/**`0`** иначе.",
                6 : "Сколько вариантов ответов будет у полла?\nВыберите натуральное число от 1 до 12",
                #7 : "Введите {}-й вариант ответа",
                7 : "**`Вы не можете выбрать время меньше, чем сейчас`**",
                8 : "**`Вы создали полл, и он был отправлен на верификацию`**",
                9 : "Создание полла отменено",
                10 : "Канал верификации поллов не настроен",
                11 : "Канал поллов не настроен",
                12 : "Полл анонимный",
                13 : "Полл неанонимный",
                14 : "Полл с несколькими вариантами выбора",
                15 : "Полл с одним вариантом выбора",
                16 : "Голосов: 0",
                17 : "ответ",
                18 : "\n**`Автор: `**<@{}>"
            }
        }                     
    

    async def poll(self, interaction, question, hours, minutes, anon, mult, answer1, answer2, answer3, answer4, answer5, answer6, answer7, answer8, answer9, answer10, answer11, answer12):
        lng = 1 if "ru" in interaction.locale else 0
        g = interaction.guild
        with closing(connect(f"{path_to}/bases/bases_{g.id}/{g.id}.db")) as base:
            with closing(base.cursor()) as cur:
                chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'poll_v_c'").fetchone()[0]
                if chnl_id == 0:
                    await interaction.response.send_message(embed=Embed(description=text_4[lng][9], colour=Colour.red()))
                    return
                else:
                    try:
                        chnl = g.get_channel(chnl_id)
                    except:
                        await interaction.response.send_message(embed=Embed(description=text_4[lng][9], colour=Colour.red()))
                        return
        
        if not hours and not minutes:
            await interaction.response.send_message(embed=Embed(description=text_4[lng][7], colour=Colour.dark_red()), ephemeral=True)
            return

        poll = Poll()
        poll.timestamp = datetime.fromtimestamp(int(time()) + 3600 * hours + 60 * minutes)
        poll.timeout = 3600 * hours + 60 * minutes
        poll.init_timeout()

        poll.n = 0
        if answer1 != "": poll.n += 1; poll.questions.append(answer1)
        if answer2 != "": poll.n += 1; poll.questions.append(answer2)
        if answer3 != "": poll.n += 1; poll.questions.append(answer3)
        if answer4 != "": poll.n += 1; poll.questions.append(answer4)
        if answer5 != "": poll.n += 1; poll.questions.append(answer5)
        if answer6 != "": poll.n += 1; poll.questions.append(answer6)
        if answer7 != "": poll.n += 1; poll.questions.append(answer7)
        if answer8 != "": poll.n += 1; poll.questions.append(answer8)
        if answer9 != "": poll.n += 1; poll.questions.append(answer9)
        if answer10 != "": poll.n += 1; poll.questions.append(answer10)
        if answer11 != "": poll.n += 1; poll.questions.append(answer11)
        if answer12 != "": poll.n += 1; poll.questions.append(answer12)
        poll.thesis = question
        
        if anon in ["да", "yes"]:
            poll.anon = True
        else:
            poll.anon = False
        
        if mult in ["да", "yes"]:
            poll.mult = True
        else:
            poll.mult = False

        emb = Embed()

        for i in range(poll.n):
            emb.add_field(name=f"{i+1} {text_4[lng][17]}", value=f"{poll.questions[i]}\n{text_4[lng][16]}")
        emb.timestamp=poll.timestamp
        emb.set_author(name=text_4[lng][16])
        if poll.anon:
            f = f"\n**`{text_4[lng][12]}`**"
        else:
            f = f"\n**`{text_4[lng][13]}`**"
        if poll.mult:
            f += f"\n**`{text_4[lng][14]}`**"
        else:
            f += f"\n**`{text_4[lng][15]}`**"
        
        f += text_4[lng][18].format(interaction.user.id)

        emb.description = f"**{poll.thesis}**{f}"

        poll.lng = lng
        poll.init_timeout()
        poll.init_buttons()
        poll.init_ans()
        m = await chnl.send(view=poll, embed=emb)
        poll.m = m
        await interaction.response.send_message(embed=Embed(description=text_4[lng][8], colour=Colour.dark_purple()), ephemeral=True)
        


    @slash_command(
        name="полл",
        name_localizations={
            Locale.en_GB: "poll",
            Locale.en_US: "poll"
        },
        description="создаёт новый полл",
        description_localizations={
            Locale.en_GB: "creates new poll",
            Locale.en_US: "creates new poll"
        },
        guild_ids=bot_guilds_r,
        force_global=False  
    )
    async def poll_r(
        self, 
        interaction: Interaction,
        question: str = SlashOption(
            name="вопрос",
            name_localizations={
                Locale.en_GB: "question",
                Locale.en_US: "question"
            },
            description="вопрос или тезис полла",
            description_localizations={
                Locale.en_GB: "question or thesis of the poll",
                Locale.en_US: "question or thesis of the poll"
            },
            required=True
        ),
        hours: int = SlashOption(
            name="часы",
            name_localizations={
                Locale.en_GB: "hours",
                Locale.en_US: "hours"
            },
            description="через сколько часов истечёт полл",
            description_localizations={
                Locale.en_GB: "after how much hours the poll will expire",
                Locale.en_US: "after how much hours the poll will expire",
            },
            required=True,
            min_value=0,
            max_value=504
        ),
        minutes: int = SlashOption(
            name="минуты",
            name_localizations={
                Locale.en_GB: "minutes",
                Locale.en_US: "minutes"
            },
            description="через сколько минут истечёт полл (дополнительно к часам)",
            description_localizations={
                Locale.en_GB: "after how much minutes the poll will expire (additional to hours)",
                Locale.en_US: "after how much minutes the poll will expire (additional to hours)"
            },
            required=True,
            min_value=0,
            max_value=59
        ),
        anon: str = SlashOption(
            name="анонимность",
            name_localizations={
                Locale.en_GB: "anonymous",
                Locale.en_US: "anonymous"
            },
            description="будет ли полл анонимным для голосующих?",
            description_localizations={
                Locale.en_GB: "will the poll be anonymous for voters?",
                Locale.en_US: "will the poll be anonymous for voters?"
            },
            required=True,
            choices=["да", "нет"],
            choice_localizations={
                "да": {
                    Locale.en_GB: "yes",
                    Locale.en_US: "yes"
                },
                "нет": {
                    Locale.en_GB: "no",
                    Locale.en_US: "no"
                },
            }
        ),
        mult: str = SlashOption(
            name="мультивыбор",
            name_localizations={
                Locale.en_GB: "multivote",
                Locale.en_US: "multivote"
            },
            description="будет ли полл мульти выборным? (т.е. пользователи могу выбрать несколько вариатов ответа)",
            description_localizations={
                Locale.en_GB: "will the poll be multivoted? (e.g. users can choose many answers)",
                Locale.en_US: "will the poll be multivoted? (e.g. users can choose many answers)"
            },
            required=True,
            choices=["да", "нет"],
            choice_localizations={
                "да": {
                    Locale.en_GB: "yes",
                    Locale.en_US: "yes"
                },
                "нет": {
                    Locale.en_GB: "no",
                    Locale.en_US: "no"
                }
            }
        ),
        answer1: str = SlashOption(
            name="ответ1",
            name_localizations={
                Locale.en_GB: "answer1",
                Locale.en_US: "answer1"
            },
            description="Напишите 1-й вариант ответа полла",
            description_localizations={
                Locale.en_GB: "Write 1 answer of the poll",
                Locale.en_US: "Write 1 answer of the poll"
            },
            required=True
        ),
        answer2: str = SlashOption(
            name="ответ2",
            name_localizations={
                Locale.en_GB: "answer2",
                Locale.en_US: "answer2"
            },
            description="Напишите 2-й вариант ответа полла",
            description_localizations={
                Locale.en_GB: "Write 2 answer of the poll",
                Locale.en_US: "Write 2 answer of the poll"
            },
            required=True
        ),
        answer3: str = SlashOption(
            name="ответ3",
            name_localizations={
                Locale.en_GB: "answer3",
                Locale.en_US: "answer3"
            },
            description="Напишите 3-й вариант ответа полла (необязательно)",
            description_localizations={
                Locale.en_GB: "Write 3 answer of the poll (optional, not necessary)",
                Locale.en_US: "Write 3 answer of the poll (optional, not necessary)"
            },
            required=False,
            default=""
        ),
        answer4: str = SlashOption(
            name="ответ4",
            name_localizations={
                Locale.en_GB: "answer4",
                Locale.en_US: "answer4"
            },
            description="Напишите 4-й вариант ответа полла (необязательно)",
            description_localizations={
                Locale.en_GB: "Write 4 answer of the poll (optional, not necessary)",
                Locale.en_US: "Write 4 answer of the poll (optional, not necessary)"
            },
            required=False,
            default=""
        ),
        answer5: str = SlashOption(
            name="ответ5",
            name_localizations={
                Locale.en_GB: "answer5",
                Locale.en_US: "answer5"
            },
            description="Напишите 5-й вариант ответа полла (необязательно)",
            description_localizations={
                Locale.en_GB: "Write 5 answer of the poll (optional, not necessary)",
                Locale.en_US: "Write 5 answer of the poll (optional, not necessary)"
            },
            required=False,
            default=""
        ),
        answer6: str = SlashOption(
            name="ответ6",
            name_localizations={
                Locale.en_GB: "answer6",
                Locale.en_US: "answer6"
            },
            description="Напишите 6-й вариант ответа полла (необязательно)",
            description_localizations={
                Locale.en_GB: "Write 6 answer of the poll (optional, not necessary)",
                Locale.en_US: "Write 6 answer of the poll (optional, not necessary)"
            },
            required=False,
            default=""
        ),
        answer7: str = SlashOption(
            name="ответ7",
            name_localizations={
                Locale.en_GB: "answer7",
                Locale.en_US: "answer7"
            },
            description="Напишите 7-й вариант ответа полла (необязательно)",
            description_localizations={
                Locale.en_GB: "Write 7 answer of the poll (optional, not necessary)",
                Locale.en_US: "Write 7 answer of the poll (optional, not necessary)"
            },
            required=False,
            default=""
        ),
        answer8: str = SlashOption(
            name="ответ8",
            name_localizations={
                Locale.en_GB: "answer8",
                Locale.en_US: "answer8"
            },
            description="Напишите 8-й вариант ответа полла (необязательно)",
            description_localizations={
                Locale.en_GB: "Write 8 answer of the poll (optional, not necessary)",
                Locale.en_US: "Write 8 answer of the poll (optional, not necessary)"
            },
            required=False,
            default=""
        ),
        answer9: str = SlashOption(
            name="ответ9",
            name_localizations={
                Locale.en_GB: "answer9",
                Locale.en_US: "answer9"
            },
            description="Напишите 9-й вариант ответа полла (необязательно)",
            description_localizations={
                Locale.en_GB: "Write 9 answer of the poll (optional, not necessary)",
                Locale.en_US: "Write 9 answer of the poll (optional, not necessary)"
            },
            required=False,
            default=""
        ),
        answer10: str = SlashOption(
            name="ответ10",
            name_localizations={
                Locale.en_GB: "answer10",
                Locale.en_US: "answer10"
            },
            description="Напишите 10-й вариант ответа полла (необязательно)",
            description_localizations={
                Locale.en_GB: "Write 10 answer of the poll (optional, not necessary)",
                Locale.en_US: "Write 10 answer of the poll (optional, not necessary)"
            },
            required=False,
            default=""
        ),
        answer11: str = SlashOption(
            name="ответ11",
            name_localizations={
                Locale.en_GB: "answer11",
                Locale.en_US: "answer11"
            },
            description="Напишите 11-й вариант ответа полла (необязательно)",
            description_localizations={
                Locale.en_GB: "Write 11 answer of the poll (optional, not necessary)",
                Locale.en_US: "Write 11 answer of the poll (optional, not necessary)"
            },
            required=False,
            default=""
        ),
        answer12: str = SlashOption(
            name="ответ12",
            name_localizations={
                Locale.en_GB: "answer12",
                Locale.en_US: "answer12"
            },
            description="Напишите 12-й вариант ответа полла (необязательно)",
            description_localizations={
                Locale.en_GB: "Write 12 answer of the poll (optional, not necessary)",
                Locale.en_US: "Write 12 answer of the poll (optional, not necessary)"
            },
            required=False,
            default=""
        )
    ):
        await self.poll(interaction, question, hours, minutes, anon, mult, answer1, answer2, answer3, answer4, answer5, answer6, answer7, answer8, answer9, answer10, answer11, answer12)

    @slash_command(
        name="poll",
        name_localizations={
            Locale.ru: "полл"
        },
        description="creates new poll",
        description_localizations={
            Locale.ru: "создаёт новый полл"
        },
        guild_ids=bot_guilds_e,
        force_global=True     
    )
    async def poll_e(
        self, 
        interaction: Interaction,
        question: str = SlashOption(
            name="question",
            name_localizations={
                Locale.ru: "вопрос"
            },
            description="question or thesis of the poll",
            description_localizations={
                Locale.ru: "вопрос или тезис полла"
            },
            required=True
        ),
        hours: int = SlashOption(
            name="hours",
            name_localizations={
                Locale.ru: "часы"
            },
            description="after how much hours the poll will expire",
            description_localizations={
                Locale.ru: "через сколько часов истечёт полл"
            },
            required=True,
            min_value=0,
            max_value=504
        ),
        minutes: int = SlashOption(
            name="minutes",
            name_localizations={
                Locale.ru: "минуты"
            },
            description="after how much minutes the poll will expire (additional to hours)",
            description_localizations={
                Locale.ru: "через сколько минут истечёт полл (дополнительно к часам)"
            },
            required=True,
            min_value=0,
            max_value=59
        ),
        anon: str = SlashOption(
            name="anonymous",
            name_localizations={
                Locale.ru: "анонимность"
            },
            description="will the poll be anonymous for voters?",
            description_localizations={
                Locale.ru: "будет ли полл анонимным для голосующих?"
            },
            required=True,
            choices=["yes", "no"],
            choice_localizations={
                "yes": {
                    Locale.ru: "да"
                },
                "no": {
                    Locale.ru: "нет"
                },
            }
        ),
        mult: str = SlashOption(
            name="multivote",
            name_localizations={
                Locale.ru: "мультивыбор"
            },
            description="will the poll be multivoted? (e.g. users can choose many answers)",
            description_localizations={
                Locale.ru: "будет ли полл мульти выборным? (т.е. пользователи могу выбрать несколько вариатов ответа)"
            },
            required=True,
            choices=["yes", "no"],
            choice_localizations={
                "yes": {
                    Locale.ru: "да"
                },
                "no": {
                    Locale.ru: "нет"
                },
            }
        ),
        answer1: str = SlashOption(
            name="answer1",
            name_localizations={
                Locale.ru: "ответ1"
            },
            description="Write 1 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 1-й вариант ответа полла"
            },
            required=True
        ),
        answer2: str = SlashOption(
            name="answer2",
            name_localizations={
                Locale.ru: "ответ2"
            },
            description="Write 2 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 2-й вариант ответа полла"
            },
            required=True
        ),
        answer3: str = SlashOption(
            name="answer3",
            name_localizations={
                Locale.ru: "ответ3"
            },
            description="Write 3 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 3-й вариант ответа полла"
            },
            required=False,
            default=""
        ),
        answer4: str = SlashOption(
            name="answer4",
            name_localizations={
                Locale.ru: "ответ4"
            },
            description="Write 4 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 4-й вариант ответа полла"
            },
            required=False,
            default=""
        ),
        answer5: str = SlashOption(
            name="answer5",
            name_localizations={
                Locale.ru: "ответ5"
            },
            description="Write 5 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 5-й вариант ответа полла"
            },
            required=False,
            default=""
        ),
        answer6: str = SlashOption(
            name="answer6",
            name_localizations={
                Locale.ru: "ответ6"
            },
            description="Write 6 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 6-й вариант ответа полла"
            },
            required=False,
            default=""
        ),
        answer7: str = SlashOption(
            name="answer7",
            name_localizations={
                Locale.ru: "ответ7"
            },
            description="Write 7 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 7-й вариант ответа полла"
            },
            required=False,
            default=""
        ),
        answer8: str = SlashOption(
            name="answer8",
            name_localizations={
                Locale.ru: "ответ8"
            },
            description="Write 8 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 8-й вариант ответа полла"
            },
            required=False,
            default=""
        ),
        answer9: str = SlashOption(
            name="answer9",
            name_localizations={
                Locale.ru: "ответ9"
            },
            description="Write 9 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 9-й вариант ответа полла"
            },
            required=False,
            default=""
        ),
        answer10: str = SlashOption(
            name="answer10",
            name_localizations={
                Locale.ru: "ответ10"
            },
            description="Write 10 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 10-й вариант ответа полла"
            },
            required=False,
            default=""
        ),
        answer11: str = SlashOption(
            name="answer11",
            name_localizations={
                Locale.ru: "ответ11"
            },
            description="Write 11 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 11-й вариант ответа полла"
            },
            required=False,
            default=""
        ),
        answer12: str = SlashOption(
            name="answer12",
            name_localizations={
                Locale.ru: "ответ12"
            },
            description="Write 12 answer of the poll",
            description_localizations={
                Locale.en_US: "Напишите 12-й вариант ответа полла"
            },
            required=False,
            default=""
        )
    ):
        await self.poll(interaction, question, hours, minutes, anon, mult, answer1, answer2, answer3, answer4, answer5, answer6, answer7, answer8, answer9, answer10, answer11, answer12)


def setup(bot, **kwargs):
    bot.add_cog(polling(bot, **kwargs))
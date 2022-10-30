from sqlite3 import connect, Connection, Cursor
from contextlib import closing
from datetime import datetime
from asyncio import sleep
from time import time

from nextcord import slash_command, Interaction, Embed, ButtonStyle, Colour, Locale, SlashOption, NotFound
from nextcord.ext.commands import Cog, Bot
from nextcord.ui import Button, View

from Variables.vars import path_to

polls_text = {
    0 : {               
        0 : "**`Poll creation was cancelled because polls verification channel isn't configured`**",
        1 : "**`You can't select time for the poll less than it's now`**",
        2 : "answer",
        3 : "Votes: 0",
        4 : "Poll is anonymous",
        5 : "Poll isn't anonymous",
        6 : "Poll with multiple choice",
        7 : "Poll with single choice",
        8 : "\n**`Author: `**<@{}>",
        9 : "**`You created poll and it was sent to the verification`**"
    },
    1 : {
        0 : "**`Создание полла отменено, потому что канал верификации поллов не настроен`**",
        1 : "**`Вы не можете выбрать время меньше, чем сейчас`**",
        2 : "ответ",
        3 : "Голосов: 0",
        4 : "Полл анонимный",
        5 : "Полл неанонимный",
        6 : "Полл с несколькими вариантами выбора",
        7 : "Полл с одним вариантом выбора",                
        8 : "\n**`Автор: `**<@{}>",
        9 : "**`Вы создали полл, и он был отправлен на верификацию`**"
    }
}    


poll_class_text = {
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


class cutom_button_with_row(Button):
    def __init__(self, label: str, disabled: bool, style: ButtonStyle, row: int):
        super().__init__(label=label, disabled=disabled, style=style, row=row)

    async def callback(self, interaction: Interaction):
        await super().view.click_row_button(interaction=interaction, label=super().label)


class custom_button(Button):
    def __init__(self, label: str, disabled: bool, style: ButtonStyle):
        super().__init__(label=label, disabled=disabled, style=style)
    
    async def callback(self, interaction: Interaction):
        await super().view.click(interaction=interaction, label=super().label)


class Poll(View):
    def __init__(self, bot):
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
        self.bot = bot    

    def init_timeout(self):
        super().__init__(timeout=self.timeout)

    def init_buttons(self):
        for i in range(self.n):
            self.add_item(custom_button(label=f"{i+1}", disabled=True, style=ButtonStyle.blurple))
        self.add_item(cutom_button_with_row(label="approve", disabled=False, style=ButtonStyle.green, row=(self.n + 4) // 5 + 1))
        self.add_item(cutom_button_with_row(label="disapprove", disabled=False, style=ButtonStyle.red, row=(self.n + 4) // 5 + 1))

    def init_ans(self):
        self.voters = [set() for _ in range(self.n)]

    def check_moder(self, interaction: Interaction, base: Connection, cur: Cursor) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        mdrls = cur.execute("SELECT * FROM mod_roles").fetchall()
        if not mdrls:
            return False
        else:
            mdrls = {x[0] for x in mdrls}
            return any(role.id in mdrls for role in interaction.user.roles)

    async def click_row_button(self, interaction: Interaction, label):
        g = interaction.guild
        lng = 1 if "ru" in interaction.locale else 0

        with closing(connect(f"{path_to}/bases/bases_{g.id}/{g.id}.db")) as base:
            with closing(base.cursor()) as cur:

                if not self.check_moder(interaction=interaction, base=base, cur=cur):
                    await interaction.response.send_message(embed=Embed(description=poll_class_text[lng][11]), ephemeral=True)
                    return
                
                chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'poll_c'").fetchone()[0]

        if label == "disapprove":
            for i in self.children:
                i.disabled = True
            emb = interaction.message.embeds[0]
            emb.description = f"{poll_class_text[lng][0]}{interaction.user.mention}\n" + emb.description
            await interaction.message.edit(view=self, embed=emb)
            self.stop()

        elif label == "approve":
            if chnl_id:

                chnl = g.get_channel(chnl_id)     
                
                emb = interaction.message.embeds[0]
                o_dsc = emb.description
                emb.description = f"{poll_class_text[lng][1]}{interaction.user.mention}\n" + emb.description
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
                
                self.verified = True
                self.bot.current_polls += 1

            else:
                await interaction.response.send_message(poll_class_text[lng][2])
    
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
                await interaction.response.send_message(embed=Embed(description=poll_class_text[lng][4].format(L)), ephemeral=True)
            except NotFound:
                sleep(1)
                try:
                    await interaction.response.send_message(embed=Embed(description=poll_class_text[lng][4].format(L)), ephemeral=True)
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
                    await interaction.response.send_message(embed=Embed(description=poll_class_text[lng][5].format(L, fl+1)), ephemeral=True)
                except NotFound:
                    sleep(1)
                    try:
                        await interaction.response.send_message(embed=Embed(description=poll_class_text[lng][5].format(L, fl+1)), ephemeral=True)
                    except:
                        pass 
                return
            try:
                await interaction.response.send_message(embed=Embed(description=poll_class_text[lng][3].format(L)), ephemeral=True)
            except NotFound:
                sleep(1)
                try:
                    await interaction.response.send_message(embed=Embed(description=poll_class_text[lng][3].format(L)), ephemeral=True)
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
                dsc.append(f"{i+1}) {self.questions[i]} - {poll_class_text[lng][12].format(len(self.voters[i]))}")
            else:
                dsc.append(f"{i+1}) {self.questions[i]} - {poll_class_text[lng][10].format(len(self.voters[i]))}")
            if not self.anon and len(self.voters[i]) > 0:
                dsc.append(poll_class_text[lng][9])
                for j in self.voters[i]:
                    dsc.append(f"<@{j}>")
            if len(self.voters[i]) == mx:
                win.append(i+1)
            elif len(self.voters[i]) > mx:
                mx = len(self.voters[i])
                win.clear()
                win.append(i+1)
        
        if len(win) == 1:
            dsc[0] = f"{poll_class_text[lng][6]}\n{win[0]}) {self.questions[win[0]-1]} - {poll_class_text[lng][10].format(mx)}\n{poll_class_text[lng][8]}"
        else:
            dsc[0] = f"{poll_class_text[lng][7]}\n"
            for i in range(len(win)):
                dsc[0] += f"{win[i]}) {self.questions[win[i]-1]} - {poll_class_text[lng][10].format(mx)}\n"
            dsc[0] += f"{poll_class_text[lng][8]}"
        
        emb = Embed(description="\n".join(dsc))
        
        for c in self.children:
            c.disabled = True
        await self.m_v.edit(view=self, embed=emb)
        
        self.bot.current_polls -= 1

        self.stop()


class PollCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    

    @slash_command(
        name="poll",
        description="creates new poll",
        description_localizations={
            Locale.ru: "создаёт новый опрос (полл)"
        } 
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
                Locale.ru: "Напишите 1-й вариант ответа полла"
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
                Locale.ru: "Напишите 2-й вариант ответа полла"
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
                Locale.ru: "Напишите 3-й вариант ответа полла"
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
                Locale.ru: "Напишите 4-й вариант ответа полла"
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
                Locale.ru: "Напишите 5-й вариант ответа полла"
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
                Locale.ru: "Напишите 6-й вариант ответа полла"
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
                Locale.ru: "Напишите 7-й вариант ответа полла"
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
                Locale.ru: "Напишите 8-й вариант ответа полла"
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
                Locale.ru: "Напишите 9-й вариант ответа полла"
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
                Locale.ru: "Напишите 10-й вариант ответа полла"
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
                Locale.ru: "Напишите 11-й вариант ответа полла"
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
                Locale.ru: "Напишите 12-й вариант ответа полла"
            },
            required=False,
            default=""
        )
    ):
        lng = 1 if "ru" in interaction.locale else 0
        g = interaction.guild
        with closing(connect(f"{path_to}/bases/bases_{g.id}/{g.id}.db")) as base:
            with closing(base.cursor()) as cur:
                chnl_id = cur.execute("SELECT value FROM server_info WHERE settings = 'poll_v_c'").fetchone()[0]
                if not chnl_id:
                    await interaction.response.send_message(embed=Embed(description=polls_text[lng][0], colour=Colour.red()), ephemeral=True)
                    return
                elif not g.get_channel(chnl_id):
                    await interaction.response.send_message(embed=Embed(description=polls_text[lng][0], colour=Colour.red()), ephemeral=True)
                    return
                else:
                    chnl = g.get_channel(chnl_id)
        
        if not hours and not minutes:
            await interaction.response.send_message(embed=Embed(description=polls_text[lng][1], colour=Colour.dark_red()), ephemeral=True)
            return

        poll = Poll(bot=self.bot)
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
            emb.add_field(name=f"{i+1} {polls_text[lng][2]}", value=f"{poll.questions[i]}\n{polls_text[lng][3]}")
        emb.timestamp=poll.timestamp
        emb.set_author(name=polls_text[lng][3])
        if poll.anon:
            f = f"\n**`{polls_text[lng][4]}`**"
        else:
            f = f"\n**`{polls_text[lng][5]}`**"
        if poll.mult:
            f += f"\n**`{polls_text[lng][6]}`**"
        else:
            f += f"\n**`{polls_text[lng][7]}`**"
        
        f += polls_text[lng][8].format(interaction.user.id)

        emb.description = f"**{poll.thesis}**{f}"

        poll.lng = lng
        poll.init_timeout()
        poll.init_buttons()
        poll.init_ans()
        m = await chnl.send(view=poll, embed=emb)
        poll.m = m
        await interaction.response.send_message(embed=Embed(description=polls_text[lng][9], colour=Colour.dark_purple()), ephemeral=True)


def setup(bot: Bot):
    bot.add_cog(PollCog(bot))
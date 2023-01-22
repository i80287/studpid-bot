from typing import Literal
from random import randint
from asyncio import sleep
from os import path

from nextcord import Embed, Locale, Interaction, Game, Status, \
    slash_command, TextInputStyle, Permissions, TextChannel, Guild
from nextcord.ext.commands import command, is_owner, Context, Cog
from nextcord.ui import Modal, TextInput
from nextcord.abc import GuildChannel

from storebot import StoreBot
from Variables.vars import CWD_PATH


class FeedbackModal(Modal):
    feedback_text: dict[int, dict[int, str]] = {
        0 : {
            0 : "Feedback",
            1 : "What problems did you get while using the bot? What new would you want to see in bot's functional?",
            2 : "**`Thanks a lot for your feedback!\nIt was delivered to the bot's support server`**",
            3 : "**`We're so sorry, but during the creation of feedback something went wrong. You can get help on the support server`**"        
        },
        1 : {
            0 : "Отзыв",
            1 : "Какие проблемы возникли у Вас при использовании бота? Чтобы бы Вы хотели добавить?",
            2 : "**`Спасибо большое за Ваш отзыв! Он был доставлен на сервер поддержки`**",
            3 : "**`Извнините, при создании фидбэка что-то пошло не так. Вы можете получить помощь/оставить отзыв на сервере поддержки`**"
        }
    }

    def __init__(self, bot: StoreBot, lng: int, auth_id: int) -> None:
        super().__init__(title=self.feedback_text[lng][0], timeout=1200, custom_id=f"10100_{auth_id}_{randint(1, 100)}")
        self.bot: StoreBot = bot
        self.feedback = TextInput(
            label=self.feedback_text[lng][0],
            placeholder=self.feedback_text[lng][1],
            custom_id=f"10101_{auth_id}_{randint(1, 100)}",
            required=True,
            style=TextInputStyle.paragraph,
            min_length=2
        )
        self.add_item(self.feedback)
        
    
    async def callback(self, interaction: Interaction) -> None:    

        dsc: tuple[str, str, str] = (
            f"`Guild: {interaction.guild.name} - {interaction.guild_id}`",
            f"`Author: {interaction.user.name} - {interaction.user.id}`",
            feedback if (feedback := self.feedback.value) else ""
        )

        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        chnl: GuildChannel = self.bot.get_channel(self.bot.bot_feedback_channel)
        if chnl:
            await chnl.send(embed=Embed(description="\n".join(dsc)))
        else:
            await interaction.response.send_message(embed=Embed(description=self.feedback_text[lng][3]), content="https://discord.gg/4kxkPStDaG", ephemeral=True)
            return
        
        await interaction.response.send_message(embed=Embed(description=self.feedback_text[lng][2]), ephemeral=True)
        self.stop()


class BasicComandsCog(Cog):
    u_ec_cmds: dict[int, list[tuple[str, str]]] = {
        0 : [
            ("`/store`", "Show store"),
            ("`/buy`", "Make a role purchase"),
            ("`/buy_by_number`", "Make a role purchase. Role is selected by number in the store"),
            ("`/sell`", "Sell the role"),
            ("`/sell_to`", "Sell the role to the selected member by selected price"),
            ("`/accept_request`", "Accept role purchase request made by another member for you"),
            ("`/decline_request`", "Decline role purchase request made by another member for you or delete you role sale request"),
            ("`/leaders`", "Show top members by balance/xp"),
        ],
        1 : [
            ("`/store`", "Открывает меню магазина"),
            ("`/buy`", "Совершает покупку роли"),
            ("`/buy_by_number`", "Совершает покупку роли. Роль выбирается по номеру из магазина."),
            ("`/sell`", "Совершает продажу роли"),
            ("`/sell_to`", "Создаёт запрос продажи роли указанному участнику за указанную цену"),
            ("`/accept_request`", "Принимает запрос покупки роли, сделанный Вам другим участником"),
            ("`/decline_request`", "Отклоняет запрос покупки роли, сделанный Вам другим участником, или отменяет Ваш запрос продажи роли"),
            ("`/leaders`", "Показывет топ пользователей по балансу/опыту"),
        ],
    }
    u_pers_cmds: dict[int, list[tuple[str, str]]] = {
        0 : [
            ("`/profile`", "Show your profile"), 
            ("`/work`", "Start working, so you get salary"),
            ("`/transfer`", "Transfer money to another member"), 
            ("`/duel`", "Make a bet"),
        ],
        1 : [
            ("`/profile`", "Показывает меню Вашего профиля"), 
            ("`/work`", "Начинает работу, за которую Вы полчите заработок"),
            ("`/transfer`", "Совершает перевод валюты другому пользователю"), 
            ("`/duel`", "Делает ставку"),
        ]
    }
    u_other_cmds: dict[int, list[tuple[str, str]]] = {
        0 : [
            ("`/poll`", "Make a poll"), 
            ("`/server`", "Show information about the server"),
            ("`/emoji`", "Show information about the emoji"),
        ],
        1 : [
            ("`/poll`", "Создаёт полл (опрос)"), 
            ("`/server`", "Показывает информацию о сервере"),
            ("`/emoji`", "Показывает информацию о эмодзи"),
        ]
    }
    m_cmds: dict[int, list[tuple[str, str]]] = {
        0 : [
            ("`/guide`", "Show guide about bot's system"), 
            ("`/settings`", "Call bot's settings menu"),
        ],
        1 : [
            ("`/guide`", "Показывает гайд о системе бота"), 
            ("`/settings`", "Вызывает меню настроек бота"),
        ]
    }
    guide_text: dict[int, dict[int, str]] = {
        0 : {
            0 : "The guide",
            1 : "Economic operations with the roles",
            2 : "In order to make role able to be bought and sold on the server and it could bring money you should add it to the list of roles, available for the purchase/sale in the \
                menu **`/settings`** -> \"💰\" -> \"🛠️\". Also in this menu you can manage added roles",
            3 : "Bot devides roles on three types:",
            4 : "1, 2 and 3",
            5 : "Type 1",
            6 : "\"Nonstacking\" roles, that are not stacking in the store (are shown as different items in the store)",
            7 : "Type 2",
            8 : "\"Stacking\" roles that are stacking in the store (are shown as one item with quantity)",
            9 : "Type 3",
            10 : "\"Infinite\" roles that can't run out in the store (you can buy them endless times)",
            11 : "Salary of the roles",
            12 : "Each role can have passive salary: once per every cooldown time, set in the menu **`/settings`** -> \"💰\" -> \"🛠️\", members that have this role on their balance will \
                gain money (salary) that is selected in the menu **`/settings`** -> \"💰\" -> \"🛠️\"",
            13 : "Work",
            14 : "Members can gain money by using **`/work`** command. Amount of gained money is set in the menu **`/settings`** -> \"💰\" -> \"💹\". Cooldown \
                for the command is set in the menu **`/settings`** -> \"💰\" -> \"⏰\"",
            15 : "Rank system",
            16 : "For each message member gains amount of xp set in the menu **`/settings`** -> \"📈\" -> \"✨\" After achieving \"border\" of the level set in the menu \
                **`/settings`** -> \"📈\" -> \"✨\" member's level growths. For each new level bot can add role (and for old - remove, if new role is added) set in the menu \
                **`/settings`** -> \"📈\" -> \"🥇\" for each level separately",
            17 : "Money for messages",
            18 : "Besides the xp member can gain money for every message. Amount of money gained from message is set in the menu **`/settings`** -> \"💰\" -> \"💸\"\
                If you want to turn off this function you can make this value equal to 0",
            19 : "Polls",
            20 : "Members can create polls via **`/poll`**. They can be open/anonymous and have one/multiple choice. After creation poll will be posted in verification channel set \
                in the menu **`/settings`** -> \"📊\" -> \"🔎\". After being approved by moderator poll will be posted in channel for publishing polls set in the \
                menu **`/settings`** -> \"📊\" -> \"📰\""
        },
        1 : {
            0 : "Гайд",
            1 : "Экономические операции с ролями",
            2 : "Чтобы роль можно было покупать и продавать на сервере, а также она могла приносить заработок, нужно добавить её в список ролей, \
                доступных для покупки/продажи на сервере при помоши меню **`/settings`** -> \"💰\" -> \"🛠️\". В этом же меню можно и управлять добавленными ролями",
            3 : "Бот делит роли на 3 типа:",
            4 : "1, 2 и 3",
            5 : "Тип 1",
            6 : "\"Нестакающиеся\" роли, которые не стакаются в магазине (т.е. отображаются как отдельные товары)",
            7 : "Тип 2",
            8 : "\"Стакающиеся\" роли, которые стакаются в магазине (т.е. отображаются как один товар с указанным количеством)",
            9 : "Тип 3",
            10 : "\"Бесконечные\" роли, которые не заканчиваются в магазине (т.е. их можно купить бесконечное количество раз)",
            11 : "Заработок роли",
            12 : "Каждая роль может иметь пассивный заработок: раз в некоторое установленное время, установленное в меню **`/settings`** -> \"💰\" -> \"🛠️\", участники, на балансе \
                которых находится эта роль, получают заработок, установленный для каждой роли отдельно в меню **`/settings`** -> \"💰\" -> \"🛠️\"",
            13 : "Работа",
            14 : "Пользователи могут получать деньги за использование команды **`/work`**. Заработок от команды устанавливается в меню **`/settings`** -> \"💰\" -> \"💹\". Кулдаун команды \
                устанавливается в меню **`/settings`** -> \"💰\" -> \"⏰\"",
            15 : "Система рангов",
            16 : "За каждое сообщение на сервере пользователь получает количество опыта, установленное в меню **`/settings`** -> \"📈\" -> \"✨\" По достижении \"границы\" уровня, \
                установленной в меню **`/settings`** -> \"📈\" -> \"✨\", уровень пользователя повышается. За каждый новый уровень бот может выдавать роль (а за пройденный - снимать, \
                если выдана новая), установленную в меню **`/settings`** -> \"📈\" -> \"🥇\" для каждого уровня отдельно",
            17 : "Деньги за сообщения",
            18 : "За каждое сообщение пользователь получает не только опыт, но и деньги. Количество денег, получаемое за сообщение, устанавливается в меню **`/settings`** -> \"💰\" -> \"💸\"\
                Если Вы хотите отключить эту функцию, Вы можете установить это значение равным нулю",
            19 : "Поллы",
            20 : "Пользователи могут создавать поллы (опросы) при помощи **`/poll`**. Они могут быть открытыми/анонимными и содержать один или несколько вариантов выбора. После создания \
                полл будет отправлен на верификацию в канал, установленный в меню **`/settings`** -> \"📊\" -> \"🔎\". Если полл будет одобрен модератором, то он будет отправлен в \
                канал для публикаций, установленный в меню  **`/settings`** -> \"📊\" -> \"📰\""
        }
    }
    text_help_view: dict[int, dict[int, str]] = {
        0 : {
            0 : "User's commands",
            1 : "Mod's commands",
            2 : "Economy",
            3 : "Personal",
            4 : "Other",
        },
        1 : {
            0 : "Команды пользователей",
            1 : "Команды модераторов",
            2 : "Экономика",
            3 : "Персональные",
            4 : "Остальные",
        }
    }

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot

    @slash_command(
        name="guide",
        description="show guide about bot's system",
        description_localizations={
            Locale.ru: "показывает гайд о системе бота"
        },
        dm_permission=False
    )
    async def guide(self, interaction: Interaction) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        emb: Embed = Embed(title=self.guide_text[lng][0])
        for i in range(1, 20, 2):
            emb.add_field(name=self.guide_text[lng][i], value=self.guide_text[lng][i+1], inline=False)
        await interaction.response.send_message(embed=emb)

    @slash_command(
        name="help", 
        description="Calls menu with commands",
        description_localizations={
            Locale.ru : "Вызывает меню команд"
        },
        dm_permission=False
    )
    async def help(self, interaction: Interaction) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        emb1: Embed = Embed(title=self.text_help_view[lng][0], description=self.text_help_view[lng][2])
        emb2: Embed = Embed(description=self.text_help_view[lng][3])
        emb3: Embed = Embed(description=self.text_help_view[lng][4])
        emb4: Embed = Embed(title=self.text_help_view[lng][1])
        for n, v in self.u_ec_cmds[lng]:
            emb1.add_field(name=n, value=v, inline=False)
        for n, v in self.u_pers_cmds[lng]:
            emb2.add_field(name=n, value=v, inline=False)
        for n, v in self.u_other_cmds[lng]:
            emb3.add_field(name=n, value=v, inline=False)
        for n, v in self.m_cmds[lng]:
            emb4.add_field(name=n, value=v, inline=False)
        await interaction.response.send_message(embeds=[emb1, emb2, emb3, emb4])

    @slash_command(
        name="feedback",
        description="Sends a feedback to the support server",
        description_localizations={
            Locale.ru: "Отправляет отзыв на сервер поддержки"
        },
        dm_permission=False,
        default_member_permissions=Permissions.administrator.flag
    )
    async def feedback(self, interaction: Interaction) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        mdl: FeedbackModal = FeedbackModal(bot=self.bot, lng=lng, auth_id=interaction.user.id)
        await interaction.response.send_modal(modal=mdl)

    @command(aliases=["sunload_access_level_two", "s_a_l_2"])
    @is_owner()
    async def _salt(self, ctx: Context, chnl: TextChannel) -> None:
        self.bot.bot_feedback_channel = chnl.id
        await ctx.reply(embed=Embed(description=f"New feedback channel is <#{self.bot.bot_feedback_channel}>"), mention_author=False, delete_after=5)

    @command(name="load")
    @is_owner()
    async def _load(self, ctx: Context, extension) -> None:
        if path.exists(f"{CWD_PATH}/Commands/{extension}.py"):
            self.bot.load_extension(f"Commands.{extension}")
            await sleep(1)
            await self.bot.sync_all_application_commands()
            await sleep(1)
            emb: Embed = Embed(description=f"**Loaded `{extension}`**")
        else:
            emb: Embed = Embed(description=f"**`{extension}` not found**")
        await ctx.reply(embed=emb, mention_author=False, delete_after=5)
    
    @command(name="unload")
    @is_owner()
    async def _unload(self, ctx: Context, extension) -> None:
        if path.exists(f"{CWD_PATH}/Commands/{extension}.py"):
            self.bot.unload_extension(f"Commands.{extension}")
            await sleep(1)
            await self.bot.sync_all_application_commands()
            await sleep(1)
            emb: Embed = Embed(description=f"**Unloaded `{extension}`**")
        else:
            emb: Embed = Embed(description=f"**`{extension}` not found**")
        await ctx.reply(embed=emb, mention_author=False, delete_after=5)

    @command(name="reload")
    @is_owner()
    async def _reload(self, ctx: Context, extension) -> None:
        if path.exists(f"{CWD_PATH}/Commands/{extension}.py"):
            await ctx.reply(embed=Embed(description="Started reloading"), mention_author=False, delete_after=5)
            self.bot.unload_extension(f"Commands.{extension}")
            self.bot.load_extension(f"Commands.{extension}")
            await sleep(1)
            await self.bot.sync_all_application_commands()
            await sleep(1)
            emb: Embed = Embed(description=f"**Reloaded `{extension}`**")
        else:
            emb: Embed = Embed(description=f"**`{extension}` not found**")
        await ctx.reply(embed=emb, mention_author=False, delete_after=5)

    @command(aliases=["statistic", "statistics"])
    @is_owner()
    async def _statistic(self, ctx: Context) -> None:
        async with self.bot.lock:
            description: list[str] = \
                ["```guild - id - member_count```"] + \
                [fr"{{{guild.name}}}-{{{guild.id}}}-{{{guild.member_count}}}" for guild in self.bot.guilds.copy()] + \
                [f"\n**`Total guilds: {len(self.bot.guilds)}`**", f"\n**`Currently active polls: {len(self.bot.current_polls)}`**"]
        emb: Embed = Embed(description='\n'.join(description))
        await ctx.reply(embed=emb, mention_author=False, delete_after=15)

    @command(name="update_status")
    @is_owner()
    async def update_status(self, ctx: Context, *text) -> None:
        if text == "default":
            await self.bot.change_presence(activity=Game(f"/help on {len(self.bot.guilds)} servers"), status=Status.online)
        else:
            await self.bot.change_presence(activity=Game(' '.join(text)), status=Status.dnd)
        await ctx.reply(embed=Embed(description=f"**`Changed status to {' '.join(text)}`**"), mention_author=False)
    
    @command(name="shutdown")
    @is_owner()
    async def shutdown(self, ctx: Context) -> None:
        from Commands.voice_handler import VoiceHandlerCog
        cog: Cog | None = self.bot.cogs.get("VoiceHandlerCog")
        
        if not isinstance(cog, VoiceHandlerCog):
            return
        
        k: int = 0
        async with self.bot.lock:
            for guild_id, members_dict in self.bot.members_in_voice.items():
                guild: Guild | None = self.bot.get_guild(guild_id)
                if not guild:
                    continue
                for member_id, member in members_dict.items():
                    await cog.process_member_on_bot_shutdown(
                        guild=guild,
                        member_id=member_id,
                        member=member
                    )
                    k += 1

        await ctx.reply(embed=Embed(description=f"**`Processed {k} members`**"), mention_author=False)


def setup(bot: StoreBot) -> None:
    bot.add_cog(BasicComandsCog(bot))
